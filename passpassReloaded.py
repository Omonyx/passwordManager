from PyQt6.QtWidgets import QLabel, QCheckBox, QTextEdit, QScrollArea, QToolButton, QApplication, QListWidget, QStackedWidget, QHBoxLayout, QFileDialog, QWidget, QVBoxLayout, QMainWindow, QPushButton, QLineEdit
from PyQt6.QtCore import QPropertyAnimation, pyqtProperty, QEasingCurve, Qt
from PyQt6.QtGui import QColor, QIntValidator, QIcon
import sys, string, json, random, os

alphabet = ' éèçïäüöîûâÿ£¤°' + string.punctuation + string.ascii_letters + string.digits

def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)
def generator(personal_alphabet, length):
    pwd = ""
    i = 0
    while i < length:
        pwd += random.choice(personal_alphabet)
        i = i + 1
    return pwd
def generate_password(input, check_list, length):
    personal_alphabet = ''
    all_alphabet = [string.ascii_lowercase, string.ascii_uppercase, string.digits, '!"#$%&\'*+,-./:;=?@\\^_`|~£¤°', '<>{}[]', 'éèçïäüöîûâÿ', ' ']
    if length != '':
        for i, check in enumerate(check_list):
            if check:
                personal_alphabet += all_alphabet[i]
        if personal_alphabet != '':
            input.setText(generator(personal_alphabet, int(length)))
            input.sub.close()
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
        infos_to_load = {'password': AnimatedInput('Password...', 128, generator=False, password=True), 'func': AnimatedButton('Open', lambda: sub_open_ppss(path, infos_to_load['password'].text()))}
        window.sub_window('Open a safe', 350, 150, infos_to_load)
def sub_open_ppss(path, master):
    if master != '':
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
    else:
        print('Missing master password !')
def create_ppss(name, master):
    if name != '' and master != '':
        filename = name
        with open('./' + filename + '.ppss', 'w') as f:
            filename = get_real_filename(filename, len(master))
            f.write(encrypt(filename, master))
        window.sub.close()
        window.show()
def originalWindow():
    infos_to_create = {'name': AnimatedInput('Name...'), 'password': AnimatedInput('Password...', 128, password=True), 'func': AnimatedButton('Create', lambda: create_ppss(infos_to_create['name'].text(), infos_to_create['password'].text()))}
    button_create = AnimatedButton('Create a safe', lambda: window.sub_window('Create a safe', 350, 150, infos_to_create))
    button_open = AnimatedButton("Open a safe", open_ppss)

    layout.addWidget(button_create)
    layout.addWidget(button_open)
def save_add(name, username, email, passw, passw2, note):
    if name != '' and passw != '' and passw == passw2:
        items = window.sub.items.copy()
        items.append({'name': name, 'username': username, 'email': email, 'password': passw, 'note': note})
        with open(window.sub.path, 'w') as f:
            filename = link_to_name(window.sub.path)
            filename = get_real_filename(filename, len(window.sub.master))
            f.write(encrypt(filename + json.dumps(items), window.sub.master))
        window.sub.items = items
        window.sub.get_items()
        window.sub.sub.close()
        window.sub.show()
def link_to_name(link):
    return link.split('/')[-1].split('.')[0]
def get_real_filename(filename, master_length):
    real_filename = filename
    if len(filename) < master_length:
        for i in range(master_length - len(filename)):
            real_filename += filename[i]
    return real_filename
def add_new_pass():
    infos_to_add = {'name': AnimatedInput('Name...'), 'username': AnimatedInput('Username...'), 'email': AnimatedInput('Email...'), 'password': AnimatedInput('Password...', 128, password=True), 'passwordToo': AnimatedInput('Repeat...', 128, generator=False, password=True), 'note': AnimatedTextArea('Note...', 80, 250), 'func': AnimatedButton('Add', lambda: save_add(infos_to_add['name'].text(), infos_to_add['username'].text(), infos_to_add['email'].text(), infos_to_add['password'].text(), infos_to_add['passwordToo'].text(), infos_to_add['note'].toPlainText()))}
    window.sub.sub_window('Add a password', 350, 350, infos_to_add)
def save_change(old_name, name, username, email, passw, passw2, note):
    if name != '' and passw != '' and passw == passw2:
        for i in range(len(window.sub.items)):
            if window.sub.items[i]['name'] == old_name:
                window.sub.items[i] = {'name': name, 'username': username, 'email': email, 'password': passw, 'note': note}
                with open(window.sub.path, 'w') as f:
                    filename = link_to_name(window.sub.path)
                    filename = get_real_filename(filename, len(window.sub.master))
                    f.write(encrypt(filename + json.dumps(window.sub.items), window.sub.master))
                window.sub.get_items()
                break
def delete_item(name):
    for i in range(len(window.sub.items)):
        if window.sub.items[i]['name'] == name:
            del window.sub.items[i]
            with open(window.sub.path, 'w') as f:
                filename = link_to_name(window.sub.path)
                filename = get_real_filename(filename, len(window.sub.master))
                f.write(encrypt(filename + json.dumps(window.sub.items), window.sub.master))
            window.sub.get_items()
            break

class MainWindow(QMainWindow):
    def __init__(self, title='Pass Pass', width=100, height=100):
        super().__init__()
        self.setWindowTitle(title)
        self.setWindowIcon(QIcon(resource_path("./ppss_logo.ico")))
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
        self.setWindowIcon(QIcon(resource_path("./ppss_logo.ico")))
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
        text_name = QLabel(f'<h1>{item['name']}</h1>')
        text_name.setStyleSheet("""
            QLabel {
                padding: 0px 0px 20px 5px;
            }
        """)
        layout.addWidget(text_name)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(page)
        func_widget = QWidget()
        func_layout = QHBoxLayout(func_widget)
        all_inputs = {'name': AnimatedInput('Name...'), 'username': AnimatedInput('Username...'), 'email': AnimatedInput('Email...'), 'password': AnimatedInput('Password...', 128, password=True), 'repeat': AnimatedInput('Repeat...', 128, generator=False, password=True), 'note': AnimatedTextArea('Note...', 80, 250), 'func': func_widget}
        func_layout.addWidget(AnimatedButton('Save', lambda: save_change(item['name'], all_inputs['name'].text(), all_inputs['username'].text(), all_inputs['email'].text(), all_inputs['password'].text(), all_inputs['repeat'].text(), all_inputs['note'].toPlainText())))
        func_layout.addWidget(AnimatedButton('Delete', lambda: delete_item(item['name']), "#a72121", "#e05c5c"))
        for key, input in all_inputs.items():
            layout.addWidget(input)
            if key == 'repeat':
                input.setText(item['password'])
            elif key == 'func':
                pass
            else:
                input.setText(item[key])
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

class AnimatedBase:
    def init_animation(self, colora, colorb, duration=600):
        self._color = QColor(colora)
        self.colora = colora
        self.colorb = colorb
        self.anim = QPropertyAnimation(self, b"color")
        self.anim.setDuration(duration)
        self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._update_style()
    @pyqtProperty(QColor)
    def color(self):
        return self._color
    @color.setter
    def color(self, value):
        self._color = value
        self._update_style()
    def enterEvent(self, event):
        self._animate_to(QColor(self.colorb))
    def leaveEvent(self, event):
        self._animate_to(QColor(self.colora))
    def _animate_to(self, target):
        self.anim.stop()
        self.anim.setStartValue(self._color)
        self.anim.setEndValue(target)
        self.anim.start()
class AnimatedTextArea(QTextEdit, AnimatedBase):
    def __init__(self, placeholder, height=80, limit=50, colora='#35a721', colorb='#60e05c', parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setFixedHeight(height)
        self.textChanged.connect(lambda: self.limit_text(limit))
        self.init_animation(colora, colorb)
    def limit_text(self, limit):
        text = self.toPlainText()
        if len(text) > limit:
            self.setText(text[:limit])
            cursor = self.textCursor()
            cursor.movePosition(cursor.MoveOperation.End)
            self.setTextCursor(cursor)
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
class AnimatedButton(QPushButton, AnimatedBase):
    def __init__(self, text, func, colora='#35a721', colorb='#60e05c', parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clicked.connect(func)
        self.init_animation(colora, colorb)
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
class AnimatedInput(QLineEdit, AnimatedBase):
    def __init__(self, placeholder, maxChar=50, height=30, password=False, generator=True, onlyNumber=False, colora='#35a721', colorb='#60e05c', parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setFixedHeight(height)
        self.setMaxLength(maxChar)
        self.init_animation(colora, colorb)

        if onlyNumber:
            validator = QIntValidator()
            self.setValidator(validator)
        if password:
            self.setEchoMode(QLineEdit.EchoMode.Password)
            self._add_eye_pass()
            if generator:
                self._add_die_pass()
    def _add_die_pass(self):
        self.die_btn = QToolButton(self)
        self.die_btn.setText('⇄')
        self.die_btn.setCheckable(True)
        self.die_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.die_btn.setStyleSheet(f"""
            QToolButton {{
                border: none;
                background: transparent;
                font-size: 14px;
                font-family: 'Segoe UI Symbol';
                color: #000000;
            }}
        """)
        self.die_btn.toggled.connect(self.open_randomer)
    def open_randomer(self):
        self.sub = MainWindow('Generate a random password', 500, 250)
        container = QWidget()
        sub_container = QWidget()
        optionA_widget = QWidget()
        optionB_widget = QWidget()
        optionA_layout = QVBoxLayout(optionA_widget)
        optionB_layout = QVBoxLayout(optionB_widget)
        button_gen = AnimatedButton('Generate', lambda: generate_password(self, [infos_gen['lower_case'].isChecked(), infos_gen['upper_case'].isChecked(), infos_gen['digits'].isChecked(), infos_gen['special'].isChecked(), infos_gen['brackets'].isChecked(), infos_gen['latin'].isChecked(), infos_gen['space'].isChecked()], infos_gen['length'].text()))
        layout = QVBoxLayout(container)
        sub_layout = QHBoxLayout(sub_container)
        layout.addWidget(sub_container)
        sub_layout.addWidget(optionA_widget)
        sub_layout.addWidget(optionB_widget)
        layout.addWidget(button_gen)

        self.sub.setCentralWidget(container)
        infos_gen = {'length': AnimatedInput('Password Length...', 3, onlyNumber=True), 'lower_case': QCheckBox('Lowercase'), 'upper_case': QCheckBox('Uppercase'), 'digits': QCheckBox('Digits'), 'special': QCheckBox('Special characters'), 'brackets': QCheckBox('Brackets'), 'latin': QCheckBox('Latin supp.'), 'space': QCheckBox('Space')}
        for i, info in enumerate(infos_gen.values()):
            if i < len(infos_gen.values()) // 2:
                optionA_layout.addWidget(info)
            else:
                optionB_layout.addWidget(info)
        self.sub.show()
    def _add_eye_pass(self):
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
        if hasattr(self, 'die_btn'):
            btn_w = 28
            btn_h = self.height() - 8
            self.die_btn.setFixedSize(btn_w, btn_h)
            self.die_btn.move(self.width() - btn_w - 22, 4)
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
