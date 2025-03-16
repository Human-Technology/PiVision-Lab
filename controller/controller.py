import os
from model.camera_model import Camera

class Controller:
    """
    Main application controller.
    Responsible for managing the user interface and the AI 
    camera with the IMX500 sensor.
    """
    def __init__(self, window):
        """
        Initializes the controller.

        Parameters:
        - window: Reference to the application's main window.
        """
        self.window = window

        # Connect window events to the corresponding methods
        self.window.windows_closed.connect(self.handle_close)
        self.window.mainPanel.item_checked.connect(self.handle_item_checked)
        self.window.mainPanel.item_unchecked.connect(self.handle_item_unchecked)

        # Camera instance (initialized in start())
        self.camera = None

        # Define the path where the AI ​​models are stored
        current_dir = os.path.dirname(os.path.abspath(__file__))  # Current scripts directory
        self.pathModels = os.path.join(current_dir, "../imx500Models") # Path to the models folder

        self.add_models()# Add available models to the interface

        # Conectar el botón de iniciar a la función start()
        self.window.mainPanel.btn_iniciar.clicked.connect(self.start)

    def getListModels(self):
        """
        Gets a list of available models in the models folder.

        Returns:
        - List of available .rpk file names.
        """
        models = [f for f in os.listdir(self.pathModels) if f.endswith('.rpk')]
        return models
    
    def add_models(self):
        """
        Adds the detected models to the combo box in the graphical interface.
        """
        if self.getListModels:
            self.window.mainPanel.comboModels.addItems(self.getListModels())
    
    def start(self):
        """
        Starts object detection with the selected model.
        """
        # Get the selected model from the interface
        model = f"{self.pathModels}/{self.window.mainPanel.comboModels.currentText()}"

        # Initialize the camera with the selected model
        self.camera = Camera(model)

        # Configure interface elements
        self.window.mainPanel.set_items(self.camera.labels)
        self.window.mainPanel.btn_iniciar.setText("Stop")
        self.window.mainPanel.btn_iniciar.clicked.disconnect()
        self.window.mainPanel.btn_iniciar.clicked.connect(self.stop)
        self.window.mainPanel.comboModels.setEnabled(False)
        
        # Start the timer to update the image in real time
        self.window.mainPanel.timer.start(30) # 30 ms interval
        self.window.mainPanel.timer.timeout.connect(lambda: self.camera.update_frame(self.window.mainPanel.image_label))

    def stop(self):
        """
        Stops object detection and resets the interface.
        """
        self.window.mainPanel.btn_iniciar.setText("Start")
        self.window.stopTimer()
        self.camera.closeCamera()
        self.window.mainPanel.comboModels.setEnabled(True)
        self.window.mainPanel.btn_iniciar.clicked.disconnect()
        self.window.mainPanel.btn_iniciar.clicked.connect(self.start)
        self.window.mainPanel.listObjects.clear()

    def handle_close(self):
        """
        Handles the application close event, ensuring the camera closes properly.
        """
        self.camera.closeCamera()

    def handle_item_checked(self, text):
        """
        Adds an object to the allowed detection list.

        Parameters:
        - text: Name of the object to allow in detection.
        """
        list = self.camera.allowed_labels.copy()
        list.append(text)
        self.camera.set_allow_labels(list)

    def handle_item_unchecked(self, text):
        """
        Removes an object from the allowed detection list.

        Parameters:
        - text: Name of the object to exclude from detection.
        """
        list = self.camera.allowed_labels.copy()
        list.remove(text)
        self.camera.set_allow_labels(list)
