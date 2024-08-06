from tkinter import *
from tkinter import messagebox, filedialog, Frame
import rpyc

def get_files():
    conn = rpyc.connect('localhost', 12345)
    call = conn.root.get_files()
    result = list(call)
    conn.close()
    return result

def send_archive():
    file_path = filedialog.askopenfilename()
    if file_path:
        conn = rpyc.connect("localhost", 12345)
        result = conn.root.send_file(file_path)
        if result:
            messagebox.showinfo(
            title="Sucesso",
            message=f'O arquivo foi enviado com sucesso.')
        else:
            messagebox.showinfo(
            title="Falha",
            message=f'Devido a um erro, o arquivo não foi enviado.')
    conn.close()

def download_file(file):
    if file:
        dest_dir = filedialog.askdirectory(title='Selecione o diretório de destino', initialdir='C:/')
        if dest_dir:
            conn = rpyc.connect('localhost', 12345)
            result = conn.root.download_file(file, dest_dir)
            if result:
                messagebox.showinfo(
                title="Sucesso",
                message=f'Download efetuado com sucesso.')
        else:
            messagebox.showinfo(
            title="Falha",
            message=f'Devido a um erro, o download não foi concluído.')
    conn.close()


class Menu:
    def __init__(self, frame, root):
        self.root = root
        self.frame = frame
        self.menu_frame = Frame(self.root)
        self.back_button = Button(self.menu_frame, text="Voltar", command=self.show_frame)
        self.uploadMenuButton = Button(frame, text="Upload de arquivo", width=36, command=lambda: self.set_menu('upload'))
        self.searchFileButton = Button(frame, text="Buscar arquivo", width=36, command=self.set_menu)
        self.downloadFileButton = Button(frame, text="Download de arquivo", width=36, command=lambda: self.set_menu('download'))
        self.show_frame()

    # Remove os elementos do Menu principal e renderiza o menu selecionado
    def set_menu(self, menu):
        self.unshow_frame()
        self.menu_frame = Frame(self.root, padx=15, pady=15)
        self.menu_frame.grid_rowconfigure(3, weight=1)
        self.menu_frame.grid_columnconfigure(1, weight=1)
        self.menu_frame.grid()
        Button(self.menu_frame, text="Voltar", command=self.show_frame).grid(row=0, column=0)
        if menu == 'upload':
            Label(self.menu_frame, text="Selecione o arquivo:").grid(row=2, column=1)
            Button(self.menu_frame, text="Upload", width=26, command=send_archive).grid(row=2, column=2)
        elif menu == 'download':
            grid_i = 1
            files = get_files()
            frame = Frame(self.menu_frame, padx=15, pady=15)
            container = Frame(frame, padx=15, pady=15, borderwidth=2, relief='ridge')
            for file in files:
                Label(container, text=file, width=35).grid(row=grid_i, column=1)
                Button(container, text='Download', width=15, command=lambda f=file: download_file(f)).grid(row=grid_i, column=2)
                grid_i+=1
            frame.grid(column=1)
            container.grid(columnspan=2)
        Entry(self.menu_frame).grid(row=3, column=1)
        Button(self.menu_frame, text='Lista de Interesse' ).grid(row=3, column=3)

    # Renderiza o menu principal na tela
    def show_frame(self):
        self.menu_frame.destroy()
        self.frame.grid()
        self.uploadMenuButton.grid(row=2, column=0)
        self.searchFileButton.grid(row=3, column=0)
        self.downloadFileButton.grid(row=4, column=0)
    
    # Remove os elementos de menu da tela
    def unshow_frame(self):
        self.frame.grid_forget()

if __name__=='__main__':
    # Configs do tela principal Tkinter (Frame Root)
    window = Tk()
    window.title("Arquivos")
    window.geometry("600x400")
    # window.config(padx=15, pady=15)

    # Inicializando a classe Menu com seu próprio frame
    menu = Menu(Frame(window, padx=150, pady=150), root=window)

    window.mainloop()