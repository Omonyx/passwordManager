import customtkinter as ctk, random, string, os, json
from tkinter import filedialog

alphabet = ' ' + string.punctuation + string.ascii_letters + string.digits

def gen_password(length, special='true'):
    simple_alphabet = string.ascii_letters + string.digits
    pwd = ""
    i = 0
    while i < length:
        if special == 'true':
            pwd += random.choice(alphabet)
        else:
            pwd += random.choice(simple_alphabet)
        i = i + 1
    return pwd
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
def import_file_datas(path=None):
    if path:
        file_imported = path
    else:
        file_imported = filedialog.askopenfilename(title="Import password data", filetypes=[("Password data (.ppss)", "*.ppss"), ("Tous les fichiers", "*.*")])
    if file_imported:
        file_name = file_imported.split('/')[-1].split('.')[0]
        with open(file_imported, 'r', encoding='utf-8') as file:
            code = file.read()[:len(file_name)]
        master_pass_access = ctk.CTkInputDialog(text=f"Enter the master password of {file_name}", title="Security")
        master_pass = master_pass_access.get_input()
        if master_pass and code == encrypt(file_name, master_pass) and decrypt(code, master_pass) == file_name:
            tabs.add(f'{file_name}')
            tabs.pack()
            build_database(file_imported, master_pass)
        else:
            PopUp('root', 'Error', '150x100', 'Master password wrong !')
def create_file(name, master, window):
    if not os.path.exists(f"{name}.ppss"):
        with open(f'{name}.ppss', 'w') as file:
            file.write(encrypt(name, master))
        window.destroy()
        import_file_datas(f'./{name}.ppss')
    else:
        PopUp(root, 'Problem...', '200x100', 'This database already exist...')
def create_file_request():
    infos_getter = ctk.CTkToplevel()
    infos_getter.title('Create a new password database')
    infos_getter.geometry('250x150')
    infos_getter.grab_set()
    file_named = ctk.StringVar()
    file_pass = ctk.StringVar()
    name_file = ctk.CTkEntry(infos_getter, textvariable=file_named, placeholder_text='Name', width=175, height=20)
    master_password = ctk.CTkEntry(infos_getter, textvariable=file_pass, placeholder_text='Password', width=175, height=20)
    button_create = ctk.CTkButton(infos_getter, border_width=2, fg_color="#000000", text_color="#ffffff", border_color="#3C3C3C", hover_color="#1E1E1E", text="Create database", font=("Monospace", 18), cursor="hand2", command=lambda: create_file(file_named.get(), file_pass.get(), infos_getter))
    name_file.pack()
    master_password.pack()
    button_create.pack()
def open_one(one):
    opened = ctk.CTkToplevel()
    opened.title(one['name'])
    opened.geometry('150x100')
    opened.grab_set()
    ctk.CTkLabel(opened, text=f'Password : {one['password']}').pack()
    ctk.CTkLabel(opened, text=f'Note : {one['description']}').pack()
def add_one(filename, password, parent):
    new_one = ctk.CTkToplevel()
    new_one.title('Add a new password')
    new_one.geometry('400x200')
    new_one.grab_set()
    pass_name_var = ctk.StringVar()
    pass_pass_var = ctk.StringVar()
    pass_description_var = ctk.StringVar()
    pass_name = ctk.CTkEntry(new_one, textvariable=pass_name_var, placeholder_text='Name', width=175, height=20)
    pass_pass = ctk.CTkEntry(new_one, textvariable=pass_pass_var, placeholder_text='Password', width=175, height=20)
    pass_description = ctk.CTkEntry(new_one, textvariable=pass_description_var, placeholder_text='Description', width=175, height=20)
    button_add = ctk.CTkButton(new_one, border_width=2, fg_color="#000000", text_color="#ffffff", border_color="#3C3C3C", hover_color="#1E1E1E", text="Create database", font=("Monospace", 18), cursor="hand2", command=lambda: rewrite_file(filename, password, pass_name_var.get(), pass_pass_var.get(), pass_description_var.get(), parent, new_one))
    ctk.CTkButton(new_one, text='Random', width=50, border_width=2, fg_color="#000000", text_color="#ffffff", border_color="#3C3C3C", hover_color="#1E1E1E", command=lambda: pass_pass_var.set(gen_password(random.randint(8, 16)))).place(x=300, y=20)
    pass_name.pack()
    pass_pass.pack()
    pass_description.pack()
    button_add.pack()
def rewrite_file(filename, master, n, p, d, parent, window):
    for widget in parent.winfo_children():
        widget.destroy()
    window.destroy()
    adding = {'name': n, 'password': p, 'description': d}
    with open(f'./{filename}.ppss', 'r') as f:
        old_text = decrypt(f.read(), master)[len(filename) + 1:-1]
    separator = ',' if old_text != '' else ''
    infos = filename + '[' + old_text + separator + json.dumps(adding) + ']'
    with open(f'./{filename}.ppss', 'w') as f:
        f.write(encrypt(infos, master))
    build_database(f'./{filename}.ppss', master, parent)
def build_database(path, password, parent=None):
    filename = path.split('/')[-1].split('.')[0]
    with open(path, 'r') as f:
        infos = decrypt(f.read()[len(filename):], password)
        background = ctk.CTkScrollableFrame(tabs.tab(filename), width=100, height=100) if parent == None else parent
        if infos != '':
            infos = json.loads(infos)
            for elt in infos:
                ctk.CTkButton(background, text=f'{elt['name']}', border_width=2, fg_color="#000000", text_color="#ffffff", border_color="#3C3C3C", hover_color="#1E1E1E", cursor='hand2', font=('Monospace', 18), command=lambda element=elt: open_one(element)).pack()
            background.pack()
        ctk.CTkButton(tabs.tab(filename), text='Add', border_width=2, fg_color="#000000", text_color="#ffffff", border_color="#3C3C3C", hover_color="#1E1E1E", cursor='hand2', font=('Monospace', 18), command=lambda: add_one(filename, password, background)).pack() if parent == None else []

class App(ctk.CTk):
    def __init__(self, title, dimension):
        super().__init__()
        self.title(title)
        self.geometry(dimension)
        self.resizable(width=False, height=False)
        self.configure(fg_color="#1D1D1D")
        self.actived = False
    def activerter(self):
        super().__init__()
        if self.actived:
            self.actived = False
            self.withdraw()
        else:
            self.actived = True
            self.deiconify()
            self.lift()
class PopUp(ctk.CTkToplevel):
    def __init__(self, master, title, dimension, message):
        super().__init__(master)
        self.title(title)
        self.geometry(dimension)
        self.grab_set()
        self.label = ctk.CTkLabel(self, text=message).pack(pady=20)
        self.button = ctk.CTkButton(self, text="Ok", border_width=2, command=self.destroyer).pack()
    def destroyer(self):
        self.destroy()

root = App("Passpass", "800x340")
tabs = ctk.CTkTabview(root, width=700, height=300, text_color="#ffffff", segmented_button_fg_color="#000000", segmented_button_selected_color="#3C3C3C", segmented_button_selected_hover_color="#3C3C3C", segmented_button_unselected_color="#000000", segmented_button_unselected_hover_color="#1E1E1E")
tabs.add("Main")
tabs.pack()

button_import = ctk.CTkButton(tabs.tab('Main'), border_width=2, fg_color="#000000", text_color="#ffffff", border_color="#3C3C3C", hover_color="#1E1E1E", text="Import file", font=("Monospace", 18), cursor="hand2", command=import_file_datas)
button_create = ctk.CTkButton(tabs.tab('Main'), border_width=2, fg_color="#000000", text_color="#ffffff", border_color="#3C3C3C", hover_color="#1E1E1E", text="Create", font=("Monospace", 18), cursor="hand2", command=create_file_request)
button_import.pack()
button_create.pack()

root.mainloop()
