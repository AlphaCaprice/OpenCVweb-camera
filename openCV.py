import sys
import numpy as np
import window
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QRadioButton, QButtonGroup, QVBoxLayout
from PyQt5.QtGui import QPixmap, QImage, QTransform
from PyQt5.QtCore import QThread, Qt
import cv2

class App(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        #super().__init__()
        self.ui = window.Ui_MainWindow()
        self.ui.setupUi(self)
        self.title = 'PyQt5 Video'
        self.filter = [cv2.COLOR_BGR2RGB]
        self.initUI()
        self.initButtonDict()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.addButtonGroup()

        self.th = Thread(self)
        self.th.changePixmap.connect(self.setImage)
        self.th.start()
        self.show()

    def addButtonGroup(self):
        self.ui.button_group = QButtonGroup()
        self.ui.button_group.addButton(self.ui.radioButton_1)
        self.ui.button_group.addButton(self.ui.radioButton_2)
        self.ui.button_group.addButton(self.ui.radioButton_3)
        self.ui.button_group.addButton(self.ui.radioButton_4)
        self.ui.button_group.addButton(self.ui.radioButton_5)
        self.ui.button_group.addButton(self.ui.radioButton_6)
        self.ui.button_group.addButton(self.ui.radioButton_7)
        self.ui.button_group.buttonClicked.connect(self._on_radio_button_clicked)

    def initButtonDict(self):
        self.button_dict = {
            self.ui.radioButton_1: [cv2.COLOR_BGR2RGB],
            self.ui.radioButton_2: [cv2.COLOR_BGR2HSV],
            self.ui.radioButton_3: [cv2.COLOR_BGR2GRAY],
            self.ui.radioButton_4: [cv2.COLOR_BGR2LUV],
            self.ui.radioButton_5: [cv2.COLOR_BGR2RGB, "blur9"],
            self.ui.radioButton_6: [cv2.COLOR_BGR2RGB, "negative"],
            self.ui.radioButton_7: [cv2.COLOR_BGR2BGRA, "self"],

        }

    def _on_radio_button_clicked(self, button):
        print(button)
        self.filter = self.button_dict[button]
        self.th.terminate()
        self.th = Thread(self)
        self.th.changePixmap.connect(self.setImage)
        self.th.start()

    @QtCore.pyqtSlot(QImage)
    def setImage(self, image):
        self.ui.label.setPixmap(QPixmap.fromImage(image))

class Thread(QThread):
    changePixmap = QtCore.pyqtSignal(QImage)
    color_format_dict = {
        cv2.COLOR_BGR2RGB: QImage.Format_RGB888,
        cv2.COLOR_BGR2HSV: QImage.Format_RGB888,
        cv2.COLOR_BGR2GRAY: QImage.Format_Grayscale8,
        cv2.COLOR_BGR2LUV: QImage.Format_RGB888,
        cv2.COLOR_BGR2BGRA: QImage.Format_RGB888
    }

    def __init__(self, app):
        super().__init__()
        self.filter = app.filter
        self.colors = (app.ui.label_B_num.text(), app.ui.label_G_num.text(), app.ui.label_R_num.text(), 1)
        self.overlay = np.full((480, 640, 4), self.colors, dtype='uint8')

    def apply_color_overlay(self, frame, intensity=0.7):
        cv2.addWeighted(self.overlay, intensity, frame, 1.0, 0, frame)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2RGB)
        return frame

    def run(self):
        cap = cv2.VideoCapture(0)
        filter_size = len(self.filter)

        while True:
            ret, frame = cap.read()
            if ret:
                rgbImage = cv2.cvtColor(frame, self.filter[0])
                if filter_size > 1:
                    if (self.filter[1] == "blur9"):
                        rgbImage = cv2.GaussianBlur(rgbImage,(9,9),0)
                    elif (self.filter[1] == "negative"):
                        rgbImage = cv2.bitwise_not(rgbImage)
                    elif (self.filter[1] == "self"):
                        rgbImage = self.apply_color_overlay(rgbImage)
                    else:
                        pass
                convertToQtFormat = QImage(rgbImage.data, rgbImage.shape[1], rgbImage.shape[0],
                                           self.color_format_dict[self.filter[0]])
                # Отзеркаливание и увеличение изображения
                p = convertToQtFormat.scaled(640*1.5, 480*1.5, Qt.KeepAspectRatio).transformed(QTransform().scale(-1, 1))
                self.changePixmap.emit(p)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())

