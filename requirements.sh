apt update && sudo apt full-upgrade -y

rm /usr/lib/python3.11/EXTERNALLY-MANAGED*

apt install -y imx500-all python3-opencv python3-munkres python3-pip libcap-dev libcamera-dev libcamera-apps
apt install -y libx11-xcb1 libxcb-keysyms1 libxcb-image0 libxcb-shm0 libxcb-icccm4 libxcb-render-util0 libxcb-xinerama0 libxcb-randr0 libxcb-xfixes0 libxcb-shape0 libxcb-sync1 libxcb-present0 libxcb-cursor0

echo "Installing Python Packages"
pip install model_compression_toolkit --break-system-packages
pip install imx500-converter[pt] --break-system-packages
pip install PySide6
pip install picamera2

echo "All dependencies are installed :D"
