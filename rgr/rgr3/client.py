import random
from lib import *
import socket

random.seed(1)

class Client:
    def __init__(self, name: str):
        self.name = name
        self._buffer_size = 1024
        
    def register(self, host: str = "localhost", port: int = 3012):
        print(f"\033[94m[INFO] Попытка соединения с сервером для регистрации пользователя с ником '{self.name}'...\033[0m")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        print(f"\033[92m[INFO] Соединение с сервером установлено\033[0m")
        n = int(sock.recv(self._buffer_size).decode("utf8"))
        print(f"\033[94m[INFO] С сервера получено n\033[0m")
   
        sock.send((bytes("{register}", encoding="utf8")))
        sock.send((bytes(self.name, encoding="utf8")))
        
        self.s = gen_mutually_prime_big(n)
        v = exponentiation_modulo(self.s, 2, n)

        sock.send((bytes(str(v), encoding="utf8")))

        status = sock.recv(self._buffer_size).decode("utf8")
        if status == "success":
            print(f"\033[92mВы были успешно зарегистрированы\033[0m")
        elif status == "already registered":
            print(f"\033[91mПользователь с никнеймом '{self.name}' уже зарегистрирован\033[0m")
        
        print(f"\033[94m[INFO] Соединение с сервером разорвано\033[0m\n")
        sock.close()

    def auth(self, host: str = "localhost", port: int = 3012):
        print(f"\033[94m[INFO] Попытка соединения с сервером для авторизации пользователя с ником '{self.name}'...\033[0m")
        sock = socket.socket()
        sock.connect((host, port))
        print(f"\033[92m[INFO] Соединение с сервером установлено\033[0m")
        
        sock.send((bytes("{auth}", encoding="utf8")))
        
        n = int(sock.recv(self._buffer_size).decode("utf8"))
        print(f"\033[94m[INFO] С сервера получено n\033[0m")
        
        sock.send((bytes(self.name, encoding="utf8")))
        
        while True:
            r = random.randrange(1, n - 1)
            x = exponentiation_modulo(r, 2, n)
            sock.send((bytes(str(x), encoding="utf8")))
            
            e = int(sock.recv(self._buffer_size).decode("utf8"))

            y = r * self.s ** e % n

            sock.send((bytes(str(y), encoding="utf8")))

            status = sock.recv(self._buffer_size).decode("utf8")
            if status == "success":
                print("\033[92mАвторизация пройдена успешно\033[0m")
                break
            elif status == "fail":
                print("\033[91mВ авторизации отказано. Аутентификация не пройдена\033[0m")
                break
            elif status == "check":
                pass

        print(f"\033[94m[INFO] Соединение с сервером разорвано\033[0m\n")
        sock.close()


if __name__ == '__main__':
    alice = Client('Alice')
    alice.register()
    alice.auth()

    # Мошенник, пытающийся авторизоваться как Alice
    cheater = Client('Alice')
    cheater.s = 1000
    cheater.auth()
