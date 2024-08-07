from tkinter import *
from tkinter import messagebox, filedialog, Frame, Entry
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
            Button(frame, text='Lista de Interesse', command=lambda: InterestList(self.root)).grid(row=grid_i, column=1, sticky='e')

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

class InterestList:
    def __init__(self, root):
        self.interest_list = []
        self.root = root
        self.window = Toplevel(master=root)
        self.window.title('Tabela de Interesses')
        self.fill_fields()
    
    def remove(self, file):
        self.interest_list.remove(file)
    
    def add(self, file, container):
        container.destroy()
        conn = rpyc.connect("localhost", 12345)
        result = conn.root.insert_interest_list(file)
        if not result:
            messagebox.showinfo(
                title="Lista de Interesses",
                message=f'O arquivo foi inserido na lista de interesses com sucesso.')
        else:
            messagebox.showinfo(
                title="Arquivo encontrado.",
                message=f'O arquivo solicitado foi encontrado nos registros: {result}.')
        conn.close()
        self.fill_fields()
    
    def fill_fields(self):
        conn = rpyc.connect("localhost", 12345)
        result = conn.root.get_interest_list()
        self.interest_list = list(result)
        frame = Frame(self.window, padx=15, pady=15)
        container = Frame(frame, padx=15, pady=15, borderwidth=2, relief='ridge')
        frame.grid()
        container.grid(columnspan=2)
        if self.interest_list:
            for index, file in enumerate(self.interest_list):
                Label(container, text=file, width=35).grid(row=index, column=0)
                Button(container, text='Remover', width=15, command=lambda f=file: self.remove(f)).grid(row=index, column=1)
        else:
            Label(container, text='Não há arquivos na lista de interesse.').grid()
        grid_size = frame.grid_size()
        interest_entry = Entry(frame)
        interest_entry.grid(row=grid_size[1], column=0, sticky='w')
        add_button = Button(frame, text='Adicionar', command= lambda: self.add(interest_entry.get(), frame))
        add_button.grid(row=grid_size[1], column=1, sticky='e')


if __name__=='__main__':
    # Configs do tela principal Tkinter (Frame Root)
    window = Tk()
    window.title("Arquivos")
    window.geometry("600x400")

    # Inicializando a classe Menu com seu próprio frame
    menu = Menu(Frame(window, padx=150, pady=150), root=window)

    window.mainloop()