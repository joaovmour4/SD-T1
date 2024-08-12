import rpyc
import time, datetime
import threading
from rpyc.utils.server import ThreadPoolServer
import shutil, os
from glob import glob
from pathlib import Path

class MyService(rpyc.Service):
    def __init__(self):
        self.start_expiration_checker() 
        # No momento da inicialização do serviço RPyC, inicia-se a função de verificação de expiração 
        #   dos registros da lista de interesses

    def on_connect(self, conn):
        print('Conexão estabelecida')
    def on_disconnect(self, conn):
        print('Conexão encerrada')

    # Função exposta pelo RPyC para realizar upload de arquivo
    def exposed_send_file(self, filePath):
        if filePath: # Executa somente caso o cliente informe um arquivo
            dest_path = os.path.join('./files', os.path.basename(filePath))
            shutil.copy(filePath, dest_path) # Salva o arquivo na base de dados local /files
            if os.path.basename(filePath) in interest_list.keys(): 
                self.notify_client(os.path.basename(filePath)) 
                # invoca o procedimento remoto de notificação presente no cliente quando 
                #   o arquivo está na lista de interesses 
            return True
        else: # Retornos de True ou False para exibição de respostas ao cliente
            return False
    
    # Método interno, não disponível para utilização via RPyC
    def notify_client(self, file): 
        # Realiza a conexão com o cliente, aciona o método de notificação e o remove da lista de interesses
        def notify(file): 
            time.sleep(3)
            conn = rpyc.connect('localhost', 12346)
            conn.root.notify_file(file)
            conn.close()
            del interest_list[file]

        threading.Thread(target=notify, args=(file,), daemon=True).start()
        # Cria uma Thread para a execução do serviço de notificações, já que com a execução contínua 
        #   ele travaria a execução do servidor RPyC
        
    # Método exposto pelo RPyC que retorna todos os arquivos na base de dados
    def exposed_get_files(self): 
        files = os.listdir('./files/')
        return files
    
    # Método exposto que busca e retorna todos os arquivos na base de dados com suas características como tamanho
    def exposed_get_info_files(self):
        dir = Path('./files')
        files = []
        for file in dir.glob('*'):
            if file.is_file():
                files.append((os.path.basename(file), file.stat().st_size,))
                # Adiciona a lista 'files' uma tupla contendo o nome do arquivo e seu tamanho
        return files

    # Método exposto para realizar o download dos arquivos
    def exposed_download_file(self, file, dest_path):
        if file and dest_path: # Realiza o método apenas se o cliente informar arquivo e diretório destino
            path_file = os.path.join('./files', file)
            final_path = os.path.join(dest_path, os.path.basename(file))
            shutil.copy(path_file, final_path)
            return True
        else:
            return False
    
    # Método exposto para inserir registros na lista de interesses
    def exposed_insert_interest_list(self, file_name, duration_in_seconds):
        expiration_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=duration_in_seconds)
        # Calcula o tempo em que o registro deve expirar
        files = os.listdir('./files/')
        if file_name not in files:
            interest_list[file_name] = expiration_time
            return False # Realiza o registro na lista de interesses apenas se o 
        else:            #  arquivo não constar na base de dados
            return file_name
    
    # Método exposto para remover registros da lista de interesses
    def exposed_remove_interest_list(self, file_name):
        if file_name in interest_list:
            del interest_list[file_name]
            return True
        return False
    
    # Método exposto que retorna os registros na lista de interesses
    def exposed_get_interest_list(self):
        return interest_list.keys()
    
    # Método interno que verifica a cada 10 segundos se há registros expirados na lista de interesses
    def check_expired_interests(self):
        while True:
            now = datetime.datetime.now(datetime.timezone.utc)
            expired_keys = [file for file, exp_time in interest_list.items() if exp_time <= now]
            # Verifica e retorna em uma lista, apenas registros expirados com base no tempo atual
            for file in expired_keys:
                del interest_list[file] # Remove registros expirados
                print(f"Interesse '{file}' removido após expiração.")
            # Verifica a cada 10 segundos
            time.sleep(10)
    
    # Método interno que aciona a verificação de registros expirados atribuindo a uma thread
    def start_expiration_checker(self):
        threading.Thread(target=self.check_expired_interests, daemon=True).start()
        

if __name__ == '__main__':
    if not os.path.exists('./files'):
        os.makedirs('./files')
    port = 12345
    interest_list = {}
    server = ThreadPoolServer(MyService, port=port) # Server que utiliza pool de threads
    print(f'Server listening on port {port}')
    server.start()
