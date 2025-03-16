is_package_installed() {
    dpkg -l "$1" &> /dev/null
    return $?
}

install_package() {
    if ! is_package_installed "$1"; then
        echo "Installing $1..."
        sudo apt install -y "$1"
    else
        echo "$1 It is already installed."
    fi
}

sudo apt update && sudo apt full-upgrade -y

install_package "imx500-all"
install_package "python3-opencv"
install_package "python3-munkres"
install_package "python3-pip"

echo "Installing Python Packages"
pip install model_compression_toolkit --break-system-packages
pip install imx500-converter[pt] --break-system-packages
pip install Flask
pip install picamera2

echo "All dependencies are installed :D"