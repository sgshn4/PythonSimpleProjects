from PyQt5.QtWidgets import QWidget, QDesktopWidget, QPushButton, QListWidget, QHBoxLayout, QVBoxLayout, QLabel

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.resize(1280, 720)
        self.center()
        self.setWindowTitle('Spy Game')

        hbox = QHBoxLayout()
        list_widget = QListWidget()
        vbox = QVBoxLayout()
        game_title = QLabel('Spy')
        boxes_label = QLabel('$$$')
        goal_label = QLabel('$$$')
        score_label = QLabel('Score: $$$')
        reset_button = QPushButton('Reset')
        vbox.addWidget(game_title)
        vbox.addWidget(boxes_label)
        vbox.addWidget(goal_label)
        vbox.addWidget(score_label)
        vbox.addWidget(reset_button)

        hbox.addWidget(list_widget)
        hbox.addLayout(vbox)

        self.setLayout(hbox)

        self.show()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())