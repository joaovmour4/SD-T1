from tkinter import *
from tkinter import messagebox, filedialog
import rpyc

def send_archive():
    file_path = filedialog.askopenfilename()
    if file_path:
        conn = rpyc.connect("localhost", 12345)
        result = conn.root.sendFile(file_path)
        if result:
            messagebox.showinfo(
            title="Sucesso",
            message=f'O arquivo foi enviado com sucesso.')
        else:
            messagebox.showinfo(
            title="Falha",
            message=f'Devido a um erro, o arquivo não foi enviado.')
    conn.close()

def remove(widgets):
    for widget in widgets:
        widget.grid_remove()

def add(widgets):
    for i in range(len(widgets)):
        widgets[i].grid(row=2, column=i)

def setMenu(menu):
    if menu == 'upload':
        add(upload_widgets)
        for menuButton in menus:
            menuButton.grid_remove()


def main_menu():
    uploadMenuButton = Button(text="Upload de arquivo", width=36, command=lambda: setMenu('upload'))
    uploadMenuButton.grid(row=2, column=0)
    searchFileButton = Button(text="Buscar arquivo", width=36, command=setMenu)
    searchFileButton.grid(row=3, column=0)
    downloadFileButton = Button(text="Download de arquivo", width=36, command=setMenu)
    downloadFileButton.grid(row=4, column=0)
    return [uploadMenuButton, searchFileButton, downloadFileButton]




if __name__=='__main__':
    window = Tk()
    window.title("Arquivos")
    window.geometry("600x400")
    window.config(padx=150, pady=150)

    menus = main_menu()

    # Labels
    x_label = Label(text="Selecione o arquivo:")
    add_button = Button(text="Upload", width=36, command=send_archive)

    upload_widgets = [x_label, add_button]

    window.mainloop()