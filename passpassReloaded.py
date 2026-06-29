from PyQt6.QtWidgets import QLabel, QTextEdit, QScrollArea, QToolButton, QApplication, QListWidget, QStackedWidget, QHBoxLayout, QFileDialog, QWidget, QVBoxLayout, QMainWindow, QPushButton, QLineEdit
from PyQt6.QtCore import QPropertyAnimation, pyqtProperty, QEasingCurve, Qt
from PyQt6.QtGui import QColor
import sys, string, json

alphabet = ' éèçïäüöîûâÿ£¤°' + string.punctuation + string.ascii_letters + string.digits

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
    path, _ = QFileDialog.getOpenFileName(window, "Open file", "", "PassPass file save (*.ppss)")
    if path:
        infos_to_load = {'password': AnimatedInput('Password...', 30, True), 'func': AnimatedButton('Open', lambda: sub_open_ppss(path, infos_to_load['password'].text()))}
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
            datas = decrypt(file_infos, master)[len_to_take:]
            window.open_window(DetailWindow(path, master, 576, 324, json.loads(datas) if datas != '' else []))
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
    infos_to_create = {'name': AnimatedInput('Name...'), 'password': AnimatedInput('Password...', 30, True), 'func': AnimatedButton('Create', lambda: create_ppss(infos_to_create['name'].text(), infos_to_create['password'].text()))}
    button_create = AnimatedButton('Create a safe', lambda: window.sub_window('Create a safe', 350, 150, infos_to_create))
    button_open = AnimatedButton("Open a safe", open_ppss)

    layout.addWidget(button_create)
    layout.addWidget(button_open)
def save_add(name, email, passw, passw2, note):
    if name != '' and passw != '' and passw == passw2:
        items = window.sub.items.copy()
        items.append({'name': name, 'email': email, 'password': passw, 'note': note})
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
    infos_to_add = {'name': AnimatedInput('Name...'), 'email': AnimatedInput('Email...'), 'password': AnimatedInput('Password...', 30, True), 'passwordToo': AnimatedInput('Repeat...', 30, True), 'note': AnimatedTextArea('Note...', 80, 250), 'func': AnimatedButton('Add', lambda: save_add(infos_to_add['name'].text(), infos_to_add['email'].text(), infos_to_add['password'].text(), infos_to_add['passwordToo'].text(), infos_to_add['note'].toPlainText()))}
    window.sub.sub_window('Add a password', 350, 300, infos_to_add)
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
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(page)
        all_inputs = {'name': AnimatedInput('Name...'), 'email': AnimatedInput('Email...'), 'password': AnimatedInput('Password...', 30, True), 'repeat': AnimatedInput('Repeat...', 30, True), 'note': AnimatedTextArea('Note...', 80, 250)}
        for key, input in all_inputs.items():
            layout.addWidget(input)
            if key != 'repeat':
                input.setText(item[key])
            else:
                input.setText(item['password'])
        return scroll
    def sub_window(self, title='Pass Pass', width=100, height=100, infos=[]):
        self.sub = MainWindow(title, width, height)
        container = QWidget()
        layout = QVBoxLayout(container)
        self.sub.setCentralWidget(container)
        for info in infos.values():
            layout.addWidget(info)
        self.sub.show()
        self.hide()
class AnimatedTextArea(QTextEdit):
    def __init__(self, placeholder, height=80, limit=50, parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setFixedHeight(height)
        self._color = QColor("#35a721")
        self._update_style()

        self.textChanged.connect(lambda: self.limit_text(limit))

        self.anim = QPropertyAnimation(self, b"color")
        self.anim.setDuration(300)
        self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)
    def limit_text(self, limit):
        text = self.toPlainText()
        if len(text) > limit:
            self.setText(text[:limit])
            cursor = self.textCursor()
            cursor.movePosition(cursor.MoveOperation.End)
            self.setTextCursor(cursor)
    def get_color(self):
        return self._color
    def set_color(self, value):
        self._color = value
        self._update_style()
    color = pyqtProperty(QColor, get_color, set_color)
    def _update_style(self):
        self.setStyleSheet(f"""
            QTextEdit {{
                background-color: {self._color.name()};
                border-radius: 8px;
                padding: 4px;
                color: #000000;
                font-size: 14px;
            }}
        """)
    def enterEvent(self, event):
        self._animate_to(QColor("#60e05c"))
    def leaveEvent(self, event):
        self._animate_to(QColor("#35a721"))
    def _animate_to(self, target):
        self.anim.stop()
        self.anim.setStartValue(self._color)
        self.anim.setEndValue(target)
        self.anim.start()
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
                color: #ffffff;
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
    def __init__(self, placeholder, height=30, password=False, parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self._color = QColor("#35a721")
        self.setFixedHeight(height)
        self._update_style()

        self.anim = QPropertyAnimation(self, b"color")
        self.anim.setDuration(600)
        self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        if password:
            self.setEchoMode(QLineEdit.EchoMode.Password)
            self.add_eye_pass()
    def add_eye_pass(self):
        self.eye_btn = QToolButton(self)
        self.eye_btn.setText('◯')
        self.eye_btn.setCheckable(True)
        self.eye_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.eye_btn.setStyleSheet(f"""
            QToolButton {{
                border: none;
                background: transparent;
                font-size: 14px;
                font-family: 'Segoe UI Symbol';
                color: #000000;
            }}
        """)
        self.eye_btn.toggled.connect(self.toggle_view)
    def toggle_view(self, check):
        if check:
            self.setEchoMode(QLineEdit.EchoMode.Normal)
            self.eye_btn.setText('⬤')
        else:
            self.setEchoMode(QLineEdit.EchoMode.Password)
            self.eye_btn.setText('◯')
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'eye_btn'):
            btn_w = 28
            btn_h = self.height() - 8
            self.eye_btn.setFixedSize(btn_w, btn_h)
            self.eye_btn.move(self.width() - btn_w - 4, 4)
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
