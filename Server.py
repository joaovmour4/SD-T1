import rpyc
import time, datetime
import threading
from rpyc.utils.server import ThreadPoolServer
import shutil, os
import glob

class MyService(rpyc.Service):
    def __init__(self):
        self.start_expiration_checker()

    def on_connect(self, conn):
        print('Conexão estabelecida')
    def on_disconnect(self, conn):
        print('Conexão encerrada')

    def exposed_send_file(self, filePath):
        if filePath:
            dest_path = os.path.join('./files', os.path.basename(filePath))
            shutil.copy(filePath, dest_path)
            if os.path.basename(filePath) in interest_list.keys():
                self.notify_client(os.path.basename(filePath))
            return True
        else:
            return False
    
    def notify_client(self, file):
        def notify(file):
            time.sleep(3)
            conn = rpyc.connect('localhost', 12346)
            conn.root.notify_file(file)
            conn.close()
            del interest_list[file]
        threading.Thread(target=notify, args=(file,), daemon=True).start()
        
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
    
    def exposed_insert_interest_list(self, file_name, duration_in_seconds):
        expiration_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=duration_in_seconds)
        files = os.listdir('./files/')
        if file_name not in files:
            interest_list[file_name] = expiration_time
            return False
        else:
            return file_name
    
    def exposed_get_interest_list(self):
        return interest_list.keys()
    
    def check_expired_interests(self):
        while True:
            now = datetime.datetime.now(datetime.timezone.utc)
            expired_keys = [file for file, exp_time in interest_list.items() if exp_time <= now]
            for file in expired_keys:
                del interest_list[file]
                print(f"Interesse '{file}' removido após expiração.")
            # Verifica a cada 10 segundos
            time.sleep(10)
    
    def start_expiration_checker(self):
        threading.Thread(target=self.check_expired_interests, daemon=True).start()
        

if __name__ == '__main__':
    if not os.path.exists('./files'):
        os.makedirs('./files')
    port = 12345
    interest_list = {}
    server = ThreadPoolServer(MyService, port=port)
    print(f'Server listening on port {port}')
    server.start()
