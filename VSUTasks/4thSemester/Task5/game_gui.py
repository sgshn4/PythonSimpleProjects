from PyQt5.QtWidgets import QWidget,  QPushButton, QTableWidget, QHBoxLayout, QVBoxLayout, QLabel
from PyQt5.QtWidgets import QTableWidgetItem, QMessageBox, QAction, QMainWindow, QDialog, QSpinBox
from PyQt5.QtGui import QColor
from PyQt5 import QtCore

import game
import settings


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Spy Game')

        # Menu bar
        self.main_widget = GameWindow(parent=self)
        self.setCentralWidget(self.main_widget)
        bar = self.menuBar()
        game_menu = bar.addMenu('Game')
        settings_action = QAction('Settings', self)
        about_action = QAction('About', self)
        game_menu.addAction(settings_action)
        game_menu.addAction(about_action)
        settings_action.triggered.connect(self.settings_triger)

        self.show()

    def settings_triger(self):
        dialog = CustomDialog()
        dialog.exec()


class CustomDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Settings')
        self.setFixedSize(300, 100)

        # Widgets init
        self.layout = QVBoxLayout()
        self.hbox = QHBoxLayout()
        self.label = QLabel('Map grid: ')
        self.width = QSpinBox()
        self.height = QSpinBox()
        self.button = QPushButton('Save')

        # Widgets settings
        self.width.setMinimum(2)
        self.width.setMaximum(20)
        self.width.setSingleStep(1)
        self.width.setValue(settings.get_parameter('game_w'))
        self.height.setMinimum(2)
        self.height.setMaximum(20)
        self.height.setSingleStep(1)
        self.height.setValue(settings.get_parameter('game_h'))
        self.button.clicked.connect(self.submit)

        # Widgets adding to screen
        self.layout.addWidget(self.label)
        self.hbox.addWidget(self.width)
        self.hbox.addWidget(self.height)
        self.layout.addLayout(self.hbox)
        self.layout.addWidget(self.button)

        self.setLayout(self.layout)

    def submit(self):
        settings.set_parameter('game_w', int(self.width.text()))
        settings.set_parameter('game_h', int(self.height.text()))
        self.close()


class GameWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        # Window settings
        self.game = game.Game(settings.get_parameter('game_w'), settings.get_parameter('game_h'))
        self.game.randomize_map()


        # Widgets init
        hbox = QHBoxLayout()
        vbox = QVBoxLayout()
        game_title = QLabel('Spy')
        self.score_label = QLabel('Score: $$$')
        reset_button = QPushButton('Reset')


        # Widgets settings
        self.table_widget = QTableWidget()
        self.table_widget.cellClicked.connect(self.cell_clicked)
        self.table_widget.verticalHeader().hide()
        self.reload_table()
        self.table_widget.horizontalHeader().hide()
        self.update_widgets()
        reset_button.clicked.connect(self.reset_button_clicked)

        # Widgets adding to screen
        vbox.addStretch()
        vbox.addWidget(game_title)
        vbox.addWidget(self.score_label)
        vbox.addWidget(reset_button)
        vbox.addStretch()

        hbox.addStretch()
        hbox.addWidget(self.table_widget)
        hbox.addStretch()
        hbox.addLayout(vbox)

        self.setLayout(hbox)

    def update_widgets(self):
        # Score label
        self.score_label.setText(f'Score: {self.game.score}')
        # Table
        for i in range(len(self.game.game_map)):
            self.table_widget.setColumnWidth(i, 40)
            self.table_widget.setRowHeight(i, 40)
            for j in range(len(self.game.game_map[i])):
                self.table_widget.setItem(i, j, QTableWidgetItem(str(self.game.game_map[i][j])))
                self.table_widget.item(i, j).setTextAlignment(QtCore.Qt.AlignCenter)
                self.table_widget.item(i, j).setSelected(False)
                self.table_widget.item(i, j).setFlags(
                    self.table_widget.item(i, j).flags() & ~QtCore.Qt.ItemFlag.ItemIsEditable)  # Turn off edit ability
                if self.game.game_map[i][j] == '*':
                    self.table_widget.item(i, j).setBackground(QColor(0, 0, 200))
                if i == self.game.y and j == self.game.x:
                    self.table_widget.item(i, j).setBackground(QColor(200, 0, 0))

    def cell_clicked(self, r, c):
        self.game.make_move(c, r)
        self.update_widgets()
        self.check_lose()

    def reset_button_clicked(self):
        self.reload_table()

    def reload_table(self):
        self.game.map_w = settings.get_parameter('game_w')
        self.game.map_h = settings.get_parameter('game_h')
        self.table_widget.setFixedWidth(self.game.map_w * 40 + 2)
        self.table_widget.setFixedHeight(self.game.map_h * 40 + 2)
        self.table_widget.setColumnCount(self.game.map_w)
        self.table_widget.setRowCount(self.game.map_h)

        self.game.randomize_map()
        self.update_widgets()
    def check_lose(self):
        if self.game.is_lose:
            self.dialog = QMessageBox(self)
            self.dialog.setWindowTitle(' ')
            self.dialog.setText(f'You Lose! \n Score: {self.game.score}')
            self.dialog.exec()

    def show_window_2(self, action):  # открытие 2  окна
        if action == self.newAction:
            print('Hi')
