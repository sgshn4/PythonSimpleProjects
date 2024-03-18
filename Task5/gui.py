from PyQt5.QtWidgets import QWidget, QDesktopWidget, QPushButton, QTableWidget, QHBoxLayout, QVBoxLayout, QLabel
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtGui import QColor
import game


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.resize(1280, 720)
        self.game = game.Game(10, 10)
        self.game.randomize_map()
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        self.setWindowTitle('Spy Game')

        hbox = QHBoxLayout()
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(self.game.map_w)
        self.table_widget.setRowCount(self.game.map_h)
        self.update_table()
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

        hbox.addWidget(self.table_widget)
        hbox.addLayout(vbox)

        self.setLayout(hbox)
        self.show()

    def update_table(self):
        for i in range(len(self.game.game_map)):
            self.table_widget.setColumnWidth(i, 30)
            for j in range(len(self.game.game_map[i])):
                self.table_widget.setItem(i, j, QTableWidgetItem(str(self.game.game_map[i][j])))
                self.table_widget.cellPressed[int, int].connect(self.cell_clicked)
                if self.game.game_map[i][j] == '*':
                    self.table_widget.item(i, j).setBackground(QColor(200, 0, 0))

    def cell_clicked(self, r, c):
        self.game.make_move(r, c)

