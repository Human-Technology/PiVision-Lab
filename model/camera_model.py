import sys
import logging
from pathlib import Path
from functools import lru_cache
import cv2
import numpy as np
from picamera2 import MappedArray, Picamera2
from picamera2.devices import IMX500
from picamera2.devices.imx500 import (NetworkIntrinsics, postprocess_nanodet_detection)
from PySide6.QtGui import QImage, QPixmap
import time

# Logger configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class Camera:
    def __init__(self, model: str, threshold: float = 0.55, iou: float = 0.65, max_detections: int = 10, 
                 controls: dict = None, resolution: tuple = None, fps: int = 30, use_gui: bool = True):
        """
        Initializes the camera with optimized settings for Raspberry Pi.
         Args:
            model (str): Path to the object detection model.
            threshold (float): Confidence threshold for object detection.
            iou (float): Intersection over Union threshold for non-max suppression.
            max_detections (int): Maximum number of detections to display.
            controls (dict): Camera control settings.
            resolution (tuple): Camera resolution (width, height).
            fps (int): Frames per second.
            use_gui (bool): Indicates whether to show the camera preview.
        """
        if not Path(model).exists():
            raise FileNotFoundError(f"The model {model} does not exist.")
        
        # Configuración inicial de parámetros
        self.model = model
        self.threshold = threshold
        self.iou = iou
        self.max_detections = max_detections
        self.controls = controls or {"FrameRate": fps}
        self.use_gui = use_gui
        self.is_running = False
        self.last_detections = []     

        try:
            # Load the model
            self.imx500 = IMX500(self.model)
            self.intrinsics = self.imx500.network_intrinsics
            input_w, input_h = self.imx500.get_input_size()
            logger.info(f"Model input size: {input_w}x{input_h}")

            # Dynamically adjust the camera resolution to match what the model expects
            self.resolution = (input_w, input_h) if resolution is None else resolution  # Dynamic adjustment
            logger.info(f"Camera resolution: {self.resolution[0]}x{self.resolution[1]}")

            # Initialize the Raspberry Pi camera
            self.picam2 = Picamera2(self.imx500.camera_num)
            config = self.picam2.create_preview_configuration(
                main={"size": self.resolution},
                controls=self.controls,
                buffer_count=12
            )
            self.imx500.show_network_fw_progress_bar()
            self.picam2.start(config, show_preview=False)
            self.is_running = True
        except Exception as e:
            logger.error(f"Error initializing the camera: {e}")
            raise RuntimeError(f"Failed to initialize the camera: {e}")              

        if self.intrinsics.preserve_aspect_ratio:
            self.imx500.set_auto_aspect_ratio()

        self.last_results = None
        self.picam2.pre_callback = self.draw_detections
        self.labels = self.get_labels()
        self.allowed_labels = self.labels.copy()
        logger.info(f"Loaded labels: {self.labels}")
        logger.info("Camera started successfully")

    def set_allow_labels(self, labels_to_detect: list):
        """
        Updates the allowed labels for real-time detection

        Args:
            labels_to_detect (list): List of allowed labels
        """
        if not labels_to_detect:
            logger.warning("Allowed labels list is empty, disabling filtering")
            self.allowed_labels = self.labels.copy()
        else:
            invalid_labels = [label for label in labels_to_detect if label not in self.labels]
            if invalid_labels:
                logger.warning(f"Invalid labels: {invalid_labels}, ignoring.")
            self.allowed_labels = [label for label in labels_to_detect if label in self.labels]
        logger.info(f"Updated allowed labels: {self.allowed_labels}")

    def parse_detections(self, metadata: dict):
        """
        Process the detections obtained from the model.
        Args:
            metadata (dict): Metadata from the camera capture.
        """
        bbox_normalization = self.intrinsics.bbox_normalization
        np_outputs = self.imx500.get_outputs(metadata, add_batch=True)
        input_w, input_h = self.imx500.get_input_size()
        
        if np_outputs is None:
            #logger.warning("No se obtuvieron salidas del modelo.")
            return self.last_detections
        
        try:
            if self.intrinsics.postprocess == "nanodet":
                boxes, scores, classes = postprocess_nanodet_detection(
                    outputs=np_outputs[0], conf=self.threshold, iou_thres=self.iou, max_out_dets=self.max_detections
                )[0]
                from picamera2.devices.imx500.postprocess import scale_boxes
                boxes = scale_boxes(boxes, 1, 1, input_h, input_w, False, False)
            else:
                boxes, scores, classes = np_outputs[0][0], np_outputs[1][0], np_outputs[2][0]
                if bbox_normalization:
                    boxes = boxes / input_h
                boxes = np.array_split(boxes, 4, axis=1)
                boxes = zip(*boxes)

            filtered_detections = []
            for box, score, category in zip(boxes, scores, classes):
                if score <= self.threshold:
                    continue

                try:
                    label = self.labels[int(category)]
                except (IndexError, ValueError):
                    logger.warning(f"Categoria invalida {category}, ignorando deteccion")
                    continue

                if label in self.allowed_labels:
                    detection = Detection(box, category, score, metadata, self.imx500, self.picam2)
                    filtered_detections.append(detection)
            self.last_detections = filtered_detections
            return self.last_detections
        except Exception as e:
            logger.error(f"Error processing detections: {e}")
            return self.last_detections
    
    @lru_cache
    def get_labels(self):
        """
        Returns the labels of the object detection model.
        """
        labels = self.intrinsics.labels
        #Filtra etiquetas vacias o que sean solo "-"
        if self.intrinsics.ignore_dash_labels:
            labels = [label for label in labels if label and label != "-"]
        return labels

    def draw_detections(self, request, stream="main"):
        """
        Draws the detections on the camera preview.
        Args:
            request (dict): Metadata from the camera capture.
            stream (str): Stream name.
        """
        detections = self.last_results
        if detections is None:
            return
        labels = self.labels
        with MappedArray(request, stream) as m:
            for detection in detections:
                try:
                    x, y, w, h = detection.box
                    label = f"{labels[int(detection.category)]} ({detection.conf:.2f})" if labels and 0 <= int(detection.category) < len(labels) else f"Unknown ({detection.conf:.2f})"
                    (text_width, text_height), baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                    text_x = x + 5
                    text_y = y + 15

                    overlay = m.array.copy()
                    cv2.rectangle(overlay, (text_x, text_y - text_height), (text_x + text_width, text_y + baseline), (255, 255, 255), cv2.FILLED)
                    alpha = 0.30
                    cv2.addWeighted(overlay, alpha, m.array, 1 - alpha, 0, m.array)
                    cv2.putText(m.array, label, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
                    cv2.rectangle(m.array, (x, y), (x + w, y + h), (0, 255, 0, 0), thickness=2)
                except (IndexError, ValueError) as e:
                        logger.warning(f"Invalid index for category {detection.category}: {e}, using 'Unknown'")
                        continue
            if self.intrinsics.preserve_aspect_ratio:
                b_x, b_y, b_w, b_h = self.imx500.get_roi_scaled(request)
                color = (255, 0, 0)
                cv2.putText(m.array, "ROI", (b_x + 5, b_y + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
                cv2.rectangle(m.array, (b_x, b_y), (b_x + b_w, b_y + b_h), (255, 0, 0, 0))
    
    def closeCamera(self):
        """
        Closes the camera."
        """
        if not self.is_running:
            logger.warning("The camera is already closed.")
            return
        try:
            self.is_running = False
            if self.picam2:
                self.picam2.stop()
                time.sleep(0.1)
                self.picam2.close()
            if self.imx500:
                del self.imx500
                self.imx500 = None
            logger.info("Camera closed successfully")
        except Exception as e:
            logger.error(f"Error closing the camera: {e}")
            raise

    def update_frame(self, image_label):
        """
        Updates the camera frame.
        Args:
            image_label (QLabel): Label to display the camera frame.
        """
        if not self.is_running:
            logger.warning("The camera is not active.")
            return
        try:
            self.last_results = self.parse_detections(self.picam2.capture_metadata())
            frame = self.picam2.capture_array()
            if self.use_gui and image_label:
                height, width, channels = frame.shape
                if channels == 3 and frame.flags['C_CONTIGUOUS']:
                    q_format = QImage.Format_RGB888
                elif channels == 4 and frame.flags['C_CONTIGUOUS']:
                    q_format = QImage.Format_RGBA8888
                else:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB if channels == 3 else cv2.COLOR_BGRA2RGBA)
                    q_format = QImage.Format_RGB888 if channels == 3 else QImage.Format_RGBA8888
                q_image = QImage(frame.data, width, height, width * channels, q_format)
                pixmap = QPixmap.fromImage(q_image)
                image_label.setPixmap(pixmap)
            elif not self.use_gui:
                if (len(self.last_results) > 0):
                    for result in self.last_results:
                        label = f"{self.labels[int(result.category)]} ({result.conf:.2f})"
                        print(f"Detected {label}")
        except Exception as e:
            logger.error(f"Error updating the frame: {e}")


class Detection:
    """
    Represents a detected object.
    """
    def __init__(self, coords, category, conf, metadata, imx500_instance, picam2_instance):
        """
        Initializes the detection.
        Args:
            coords (tuple): Coordinates of the detection.
            category (int): Category of the detection.
            conf (float): Confidence level of the detection.
            metadata (dict): Metadata from the camera capture.
            imx500_instance (IMX500): Instance of the IMX500 class.
            picam2_instance (Picamera2): Instance of the Picamera2 class.
        """
        self.category = category
        self.conf = conf
        self.box = imx500_instance.convert_inference_coords(coords, metadata, picam2_instance)
