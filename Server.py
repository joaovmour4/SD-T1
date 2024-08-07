import rpyc
from rpyc.utils.server import ThreadPoolServer
import shutil, os
import glob

class MyService(rpyc.Service):
    def on_connect(self, conn):
        print('Conexão estabelecida')
    def on_disconnect(self, conn):
        print('Conexão encerrada')

    def exposed_send_file(self, filePath):
        if filePath:
            dest_path = os.path.join('./files', os.path.basename(filePath))
            shutil.copy(filePath, dest_path)
            if os.path.basename(filePath) in interest_list:
                print('Novo registro da lista de interesses adicionado.')
            return True
        else:
            return False
        
    def exposed_get_files(self):
        files = os.listdir('./files/')
        return files

    def exposed_download_file(self, file, dest_path):
        if file and dest_path:
            path_file = os.path.join('./files', file)
            final_path = os.path.join(dest_path, os.path.basename(file))
            shutil.copy(path_file, final_path)
            return True
        else:
            return False
    
    def exposed_insert_interest_list(self, file_name):
        files = os.listdir('./files/')
        if file_name not in files:
            interest_list.append(file_name)
            return False
        else:
            return file_name
    
    def exposed_get_interest_list(self):
        return interest_list
        

if __name__ == '__main__':
    if not os.path.exists('./files'):
        os.makedirs('./files')
    port = 12345
    interest_list = []
    server = ThreadPoolServer(MyService, port=port)
    print(f'Server listening on port {port}')
    server.start()
