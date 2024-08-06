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
    def exposed_sendFile(self, filePath):
        if filePath:
            if not os.path.exists('./files'):
                os.makedirs('./files')
            dest_path = os.path.join('./files', os.path.basename(filePath))
            shutil.move(filePath, dest_path)
            return True
        else:
            return False
        

if __name__ == '__main__':
    port = 12345
    server = ThreadPoolServer(MyService, port=port)
    print(f'Server listening on port {port}')
    server.start()
