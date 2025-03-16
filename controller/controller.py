import os
from model.camera_model import Camera

class Controller:

    def __init__(self, window):
        self.window = window
        self.window.windows_closed.connect(self.handle_close)
        self.window.mainPanel.item_checked.connect(self.handle_item_checked)
        self.window.mainPanel.item_unchecked.connect(self.handle_item_unchecked)
        self.camera = None
        current_dir = os.path.dirname(os.path.abspath(__file__))  # Directorio del script
        self.pathModels = os.path.join(current_dir, "../imx500Models")  # Ruta relativa        self.add_models()
        self.add_models()
        self.window.mainPanel.btn_iniciar.clicked.connect(self.start)

    def getListModels(self):
        models = [f for f in os.listdir(self.pathModels) if f.endswith('.rpk')]
        return models
    
    def add_models(self):
        if self.getListModels:
            self.window.mainPanel.comboModels.addItems(self.getListModels())
    
    def start(self):
        model = f"{self.pathModels}/{self.window.mainPanel.comboModels.currentText()}"
        self.camera = Camera(model)
        self.window.mainPanel.set_items(self.camera.labels)
        self.window.mainPanel.btn_iniciar.setText("Detener")
        self.window.mainPanel.btn_iniciar.clicked.disconnect()
        self.window.mainPanel.btn_iniciar.clicked.connect(self.stop)
        self.window.mainPanel.comboModels.setEnabled(False)

        self.window.mainPanel.timer.start(30)
        self.window.mainPanel.timer.timeout.connect(lambda: self.camera.update_frame(self.window.mainPanel.image_label))

    def stop(self):
        self.window.mainPanel.btn_iniciar.setText("Iniciar")
        self.window.stopTimer()
        self.camera.closeCamera()
        self.window.mainPanel.comboModels.setEnabled(True)
        self.window.mainPanel.btn_iniciar.clicked.disconnect()
        self.window.mainPanel.btn_iniciar.clicked.connect(self.start)
        self.window.mainPanel.listObjects.clear()

    def handle_close(self):
        self.camera.closeCamera()

    def handle_item_checked(self, text):
        list = self.camera.allowed_labels.copy()
        list.append(text)
        self.camera.set_allow_labels(list)

    def handle_item_unchecked(self, text):
        list = self.camera.allowed_labels.copy()
        list.remove(text)
        self.camera.set_allow_labels(list)
