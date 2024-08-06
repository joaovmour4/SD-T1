import rpyc
from rpyc.utils.server import ThreadPoolServer
import shutil, os

class MyService(rpyc.Service):
    def on_connect(self, conn):
        print('Conexão estabelecida')
    def on_disconnect(self, conn):
        print('Conexão encerrada')
    def exposed_add(self, x, y):
        return x + y
    def exposed_send_file(self, filePath):
        if filePath:
            if not os.path.exists('./files'):
                os.makedirs('./files')
            dest_path = os.path.join('./files', os.path.basename(filePath))
            shutil.move(filePath, dest_path)
            return True
        else:
            return False
    def exposed_download_file(self, file, dest_path):
        if file and dest_path:
            final_path = os.path.join(dest_path, os.path.basename(file))
            shutil.copy(file, final_path)
            return True
        else:
            return False
        

if __name__ == '__main__':
    port = 12345
    server = ThreadPoolServer(MyService, port=port)
    print(f'Server listening on port {port}')
    server.start()
