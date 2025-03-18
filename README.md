# PiVision Lab

PiVision Lab is an open-source project for the Raspberry Pi AI Camera using the IMX500 sensor. This software allows users to load, switch, and configure AI models for real-time object detection.

## Features
- Load and switch between different AI models.
- Visualize object detection results in real-time.
- Enable or disable specific object detection.
- Includes five AI models from the Raspberry Pi repository.

## Compatible AI Models
The following models are available in the `imx500Models/` directory:

- `imx500_network_efficientdet_lite0_pp.rpk`
- `imx500_network_nanodet_plus_416x416_pp.rpk`
- `imx500_network_nanodet_plus_416x416.rpk`
- `imx500_network_ssd_mobilenetv2_fpnlite_320x320_pp.rpk`
- `imx500_network_yolov8n_pp.rpk`

## Installation
### Requirements
- Raspberry Pi
- Raspberry Pi AI Camera with IMX500 sensor
- Python 3.x

### Dependencies
```sh
chmod +x requirements.sh
sudo ./requirements.sh
```

⚠ **Warning!**

In `requirements.sh`, line 3 executes the following command:
```sh
rm /usr/lib/python3.11/EXTERNALLY-MANAGED*
```
The `EXTERNALLY-MANAGED` file is sometimes present in Python installations (especially on Linux systems) to indicate that Python is managed externally by the system package manager (e.g., `apt` in Ubuntu). This file prevents direct installation of Python packages using `pip`.

By removing this file, the restriction on direct `pip` installations is disabled. This is useful if you want to install Python packages without interference from the system package manager.

If this does not cause any issues, leave it as is. Otherwise, you can modify `requirements.sh` by commenting out line 3:
```sh
# rm /usr/lib/python3.11/EXTERNALLY-MANAGED*
```

## Running the Application
To start PiVision Lab, run:
```sh
python app.py
```

## Project Structure
```
📂 PiVision-Lab
 ├── 📂 controller/        # Application logic
 ├── 📂 img/               # UI images/icons
 ├── 📂 imx500Models/      # Preloaded AI models
 ├── 📂 model/             # Camera model handling
 ├── 📂 style/             # UI styles (QSS)
 ├── 📂 view/              # UI components
 ├── app.py               # Main application entry
 ├── requirements.txt      # Dependencies
 ├── README.md             # Documentation
 ├── LICENSE               # Project license
```

## How It Works
1. Select an AI model from the dropdown list.
2. Load the model onto the IMX500 sensor.
3. Real-time detection starts with the selected model.
4. Enable or disable objects to filter specific detections.

## Contributing
We welcome contributions! Feel free to:
- Report issues or request features.
- Fork the project and submit a pull request.

## Upcoming Features
- Option to load custom AI models.
- Command-line interface mode (no GUI required).

## License
This project is licensed under the MIT License.
