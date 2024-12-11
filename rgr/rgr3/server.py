import json
from lib import *
import socket
import signal


class Server:
    def __init__(self, host: str = "localhost", port: int = 3012):
        self._host = host
        self._port = port
        self._buffer_size = 1024

        p = q = gen_prime(1 << 1023, (1 << 1024) - 1)
        while p == q:
            q = gen_prime(1 << 1023, (1 << 1024) - 1)

        self.n = p * q
        
        print(f"\t{p = }", f"\t{q = }", f"\t{self.n = }", '*' * 30, sep='\n')
        
        try:
            with open("registered_users.json", "r") as f:
                self._registered_users = json.load(f)
            print("\033[92m[INFO] Загружена база с пользователями\033[0m")
        except FileNotFoundError:
            with open("registered_users.json", "w") as f:
                self._registered_users = dict()
                json.dump(self._registered_users, f)
            print("\033[91m[ERROR] Не удалось загрузить базу с пользователями. Была создана новая\033[0m")

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((self._host, self._port))
        sock.listen()
        print("\033[92m[INFO] Сервер запущен\033[0m")
        
        while True:
            conn, addr = sock.accept()
            print(f"\n\033[94m[INFO] Установлено новое соединение: {addr}\033[0m")
            
            conn.send((bytes(str(self.n), encoding="utf8")))

            print(f"\033[94m[INFO] Пользователю {addr} отправлено n\033[0m")
            
            data = conn.recv(self._buffer_size).decode("utf8")
            
            if data == "{register}":
                name = conn.recv(self._buffer_size).decode("utf8")
                v = int(conn.recv(self._buffer_size).decode("utf8"))
                
                if name not in self._registered_users.keys():
                    print(f"\033[92m[INFO] Пользователь {addr} зарегистрировался с никнеймом '{name}' и ключом {v}\033[0m")
                    self._registered_users[name] = v
                    with open("registered_users.json", "w") as f:
                        json.dump(self._registered_users, f)
                    conn.send((bytes("success", encoding="utf8")))
                else:
                    print(f"\033[91m[ERROR] Никнейм '{name}' уже зарегистрирован\033[0m")
                    conn.send((bytes("already registered", encoding="utf8")))

            
            if data == "{auth}":
                name = conn.recv(self._buffer_size).decode("utf8")
                v = self._registered_users[name]
                
                print(f"\033[94m[INFO] Пользователь {addr} пытается авторизироваться под никнеймом '{name}'\033[0m")

                print(f"\033[94m[INFO] Аутентификация:\033[0m")
                
                t = 20
                for i in range(t):
                    x = int(conn.recv(self._buffer_size).decode("utf8"))

                    e = random.randint(0, 1)
                    conn.send((bytes(str(e), encoding="utf8")))

                    y = int(conn.recv(self._buffer_size).decode("utf8"))

                    y2 = exponentiation_modulo(y, 2, self.n)
                    xv = x * exponentiation_modulo(v, e, self.n) % self.n
                    print(f"{i + 1}.\n\t{x=}\n\t{e=}\n\t{y=}\n\t--\n\ty^2 % n = {y2}\n\tx * v^e % n = {xv}")
                    
                    if y2 == xv:
                        print(f"\t(success) y^2 == x * v^e % n\n")
                        if i + 1 == t:
                            print(f"\033[92m[INFO] Аутентификация '{name}' пройдена успешно\033[0m")
                            conn.send((bytes("success", encoding="utf8")))
                        else:
                            conn.send((bytes("check", encoding="utf8")))
                    else:
                        print(f"\t(fail) y^2 != x * v^e % n\n")
                        conn.send((bytes("fail", encoding="utf8")))
                        print(f"\033[91m[INFO] Аутентификация '{name}' не пройдена. Пользователь {addr} получает бан по ip\033[0m")
                        break

            conn.close()
            print(f"\033[94m[INFO] Соединение разорвано\033[0m")

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    server = Server()
    server.run()
