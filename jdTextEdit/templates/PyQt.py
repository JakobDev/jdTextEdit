from PyQt5.QtWidgets import QApplication, QWidget
import sys

class MyWindow(QWidget):
    def __init__(self):
        super().__init__()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MyWindow()
    w.show()
    sys.exit(app.exec())
