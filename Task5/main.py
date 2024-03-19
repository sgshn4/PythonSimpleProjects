import sys
import gui
from PyQt5.QtWidgets import QApplication


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = gui.MainWindow()
    sys.exit(app.exec_())
