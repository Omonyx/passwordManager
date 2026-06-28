from PyQt6.QtWidgets import QLabel, QApplication, QListWidget, QStackedWidget, QHBoxLayout, QFileDialog, QWidget, QVBoxLayout, QMainWindow, QPushButton, QLineEdit
from PyQt6.QtCore import QPropertyAnimation, pyqtProperty, QEasingCurve, Qt
from PyQt6.QtGui import QColor
import sys, string, json

alphabet = ' ' + string.punctuation + string.ascii_letters + string.digits

def vigenere(message, key, direction=1):
    key_index = 0
    encrypted_message = ''
    for char in message:
        key_char = key[key_index % len(key)]
        key_index += 1
        offset = alphabet.index(key_char)
        index = alphabet.find(char)
        new_index = (index + offset*direction) % len(alphabet)
        encrypted_message += alphabet[new_index]
    return encrypted_message
def decrypt(message, key):
    return vigenere(message, key, -1)
def encrypt(message, key):
    return vigenere(message, key)
def open_ppss():
    path, _ = QFileDialog.getOpenFileName(
        window,
        "Open file",
        "",
        "PassPass file save (*.ppss)"
    )
    if path:
        infos_to_load = {'password': AnimatedInput('Password...', True), 'func': AnimatedButton('Open', lambda: sub_open_ppss(path, infos_to_load['password'].text()))}
        window.sub_window('Open a safe', 350, 150, infos_to_load)
def sub_open_ppss(path, master):
    with open(path, 'r') as f:
        name = link_to_name(path)
        file_infos = f.read()
        if decrypt(file_infos[:len(name)], master) == name:
            window.sub.close()
            if len(name) < len(master):
                len_to_take = len(master)
            else:
                len_to_take = len(name)
            window.open_window(DetailWindow(path, master, 576, 324, json.loads(decrypt(file_infos, master)[len_to_take:])))
            window.sub.show()
            window.hide()
        else:
            print('Wrong master password !')
def create_ppss(name, master):
    if name != '' and master != '':
        filename = name
        with open('./' + filename + '.ppss', 'w') as f:
            if len(filename) < len(master):
                for i in range(len(master) - len(filename)):
                    filename += filename[i]
            f.write(encrypt(filename, master))
        window.sub.close()
        window.show()
def originalWindow():
    infos_to_create = {'name': AnimatedInput('Name...'), 'password': AnimatedInput('Password...', True), 'func': AnimatedButton('Create', lambda: create_ppss(infos_to_create['name'].text(), infos_to_create['password'].text()))}
    button_create = AnimatedButton('Create a safe', lambda: window.sub_window('Create a safe', 350, 150, infos_to_create))
    button_open = AnimatedButton("Open a safe", open_ppss)

    layout.addWidget(button_create)
    layout.addWidget(button_open)
def save_add(name, email, passw, passw2):
    if name != '' and passw != '' and passw == passw2:
        items = window.sub.items.copy()
        items.append({'name': name, 'email': email, 'password': passw})
        with open(window.sub.path, 'w') as f:
            filename = link_to_name(window.sub.path)
            if len(filename) < len(window.sub.master):
                for i in range(len(window.sub.master) - len(filename)):
                    filename += filename[i]
            f.write(encrypt(filename + json.dumps(items), window.sub.master))
        window.sub.items = items
        window.sub.get_items()
        window.sub.sub.close()
        window.sub.show()
def link_to_name(link):
    return link.split('/')[-1].split('.')[0]
def add_new_pass():
    infos_to_add = {'name': AnimatedInput('Name...'), 'email': AnimatedInput('Email...'), 'password': AnimatedInput('Password...', True), 'passwordToo': AnimatedInput('Repeat...', True), 'func': AnimatedButton('Add', lambda: save_add(infos_to_add['name'].text(), infos_to_add['email'].text(), infos_to_add['password'].text(), infos_to_add['passwordToo'].text()))}
    window.sub.sub_window('Add a password', 300, 250, infos_to_add)
class MainWindow(QMainWindow):
    def __init__(self, title='Pass Pass', width=100, height=100):
        super().__init__()
        self.setWindowTitle(title)
        self.setFixedSize(width, height)
        self.sub = None
    def sub_window(self, title='Pass Pass', width=100, height=100, infos=[]):
        self.sub = MainWindow(title, width, height)
        container = QWidget()
        layout = QVBoxLayout(container)
        self.sub.setCentralWidget(container)
        for info in infos.values():
            layout.addWidget(info)
        self.sub.show()
        self.hide()
    def open_window(self, w):
        self.sub = w
    def closeEvent(self, event):
        if window.sub:
            window.sub.show()
        event.accept()
class DetailWindow(QMainWindow):
    def __init__(self, path, master, width=200, height=100, items=[]):
        super().__init__()
        title = link_to_name(path)
        self.setWindowTitle(title)
        self.setFixedSize(width, height)
        self.items = items
        self.path = path
        self.master = master

        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        self.setCentralWidget(container)

        sub_container = QWidget()
        sub_layout = QVBoxLayout(sub_container)
        sub_layout.setContentsMargins(20, 20, 20, 20)

        self.lister = QListWidget()
        self.stacker = QStackedWidget()
        sub_container.setFixedWidth(150)
        self.get_items()

        self.lister.currentRowChanged.connect(self.stacker.setCurrentIndex)
        self.lister.setCurrentRow(0)

        layout.addWidget(sub_container)
        button_test = AnimatedButton('Add', add_new_pass)
        sub_layout.addWidget(button_test)
        sub_layout.addWidget(self.lister)
        layout.addWidget(self.stacker)
    def get_items(self):
        self.lister.clear()
        while self.stacker.count() > 0:
            widget = self.stacker.widget(0)
            self.stacker.removeWidget(widget)
            widget.deleteLater()
        for item in self.items:
            self.lister.addItem(item['name'])
            self.stacker.addWidget(self.make_page(item))
    def make_page(self, item):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        layout.addWidget(QLabel(f'<h1>{item['name']}</h1>'))
        all_inputs = {'name': AnimatedInput(f'{item['name']}'), 'password': AnimatedInput(f'{item['name']}', True)}
        for key, input in all_inputs.items():
            layout.addWidget(input)
            input.setText(item[key])
        return page
    def sub_window(self, title='Pass Pass', width=100, height=100, infos=[]):
        self.sub = MainWindow(title, width, height)
        container = QWidget()
        layout = QVBoxLayout(container)
        self.sub.setCentralWidget(container)
        for info in infos.values():
            layout.addWidget(info)
        self.sub.show()
        self.hide()
class AnimatedButton(QPushButton):
    def __init__(self, text, func, parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clicked.connect(func)
        self._color = QColor("#35a721")
        self._update_style()

        self.anim = QPropertyAnimation(self, b"color")
        self.anim.setDuration(600)
        self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)
    @pyqtProperty(QColor)
    def color(self):
        return self._color
    @color.setter
    def color(self, value):
        self._color = value
        self._update_style()
    def _update_style(self):
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self._color.name()};
                color: white;
                border-radius: 8px;
                padding: 10px 24px;
                font-size: 14px;
                border: none;
            }}
        """)
    def enterEvent(self, event):
        self._animate_to(QColor("#60e05c"))
    def leaveEvent(self, event):
        self._animate_to(QColor("#35a721"))
    def _animate_to(self, target_color):
        self.anim.stop()
        self.anim.setStartValue(self._color)
        self.anim.setEndValue(target_color)
        self.anim.start()
class AnimatedInput(QLineEdit):
    def __init__(self, placeholder, password=False, parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setEchoMode(QLineEdit.EchoMode.Password if password else QLineEdit.EchoMode.Normal)
        self._color = QColor("#35a721")
        self._update_style()

        self.anim = QPropertyAnimation(self, b"color")
        self.anim.setDuration(600)
        self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)
    def get_color(self):
        return self._color
    def set_color(self, value):
        self._color = value
        self._update_style()
    color = pyqtProperty(QColor, get_color, set_color)
    def _update_style(self):
        self.setStyleSheet(f"""
            QLineEdit {{
                background-color: {self._color.name()};
                border: none;
                border-radius: 8px;
                padding: 4px;
                font-size: 14px;
                color: #000000;
            }}
        """)
    def enterEvent(self, event):
        self._animate_to(QColor("#60e05c"))
    def leaveEvent(self, event):
        self._animate_to(QColor("#35a721"))
    def _animate_to(self, target_color):
        self.anim.stop()
        self.anim.setStartValue(self._color)
        self.anim.setEndValue(target_color)
        self.anim.start()

app = QApplication(sys.argv)
window = MainWindow('Pass Pass', 350, 150)
container = QWidget()
layout = QVBoxLayout(container)
layout.setContentsMargins(20, 20, 20, 20)
layout.setSpacing(10)

originalWindow()

window.setCentralWidget(container)
window.show()
sys.exit(app.exec())
