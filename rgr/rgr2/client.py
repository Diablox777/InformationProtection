import json
import socket
import signal
import random
from logic import *
import tkinter as tk
from tkinter import messagebox

t = 1

class Server:
    def __init__(self, host: str = "localhost", port: int = 3000):
        self._host = host
        self._port = port
        self._buffer_size = 1024

        p = q = gen_prime(1 << 23, (1 << 24) - 1)
        while p == q:
            q = gen_prime(1 << 23, (1 << 24) - 1)

        self.n = p * q
        
        print(f"\t{p = }", f"\t{q = }", f"\t{self.n = }", '*' * 30, sep='\n')
        
        # Загрузка зарегистрированных пользователей
        try:
            with open("users.json", "r") as f:
                self._registered_users = json.load(f)
            print("✅ Файл users.json найден!")
        except FileNotFoundError:
            with open("users.json", "w") as f:
                self._registered_users = dict()
                json.dump(self._registered_users, f)
            print("❗Не удалось открыть файл users.json, создаю новый")

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((self._host, self._port))
        sock.listen()
        print("🟢 Сервер функционирует")
        
        while True:
            conn, addr = sock.accept()
            print(f"\n🟡 Совершена попытка подключения: {addr}")
            
            try:
                conn.send((bytes(str(self.n), encoding="utf8")))
                print(f"Клиент {addr} отправлено n")
                
                data = conn.recv(self._buffer_size).decode("utf8")
                
                if data == "{register}":
                    name = conn.recv(self._buffer_size).decode("utf8")
                    v = int(conn.recv(self._buffer_size).decode("utf8"))
                    
                    if name not in self._registered_users.keys():
                        print(f"🟢 Клиент {addr} зарегистрировался с именем '{name}' и ключом v = {v}")
                        self._registered_users[name] = v
                        with open("users.json", "w") as f:
                            json.dump(self._registered_users, f)
                        conn.send((bytes("success", encoding="utf8")))
                    else:
                        print(f"🔴 Имя '{name}' уже зарегистрировано")
                        conn.send((bytes("already registered", encoding="utf8")))

                elif data == "{auth}":
                    name = conn.recv(self._buffer_size).decode("utf8")
                    
                    if name not in self._registered_users:
                        conn.send((bytes("fail", encoding="utf8")))  # Отказ в авторизации
                        print(f"🔴 Аутентификация '{name}' не пройдена.")
                        continue
                    
                    v = self._registered_users[name]
                    
                    print(f"🟡 Клиент {addr} пытается авторизироваться под именем '{name}'")                
    
                    for i in range(t):
                        x = int(conn.recv(self._buffer_size).decode("utf8"))

                        e = random.randint(0, 1)
                        conn.send((bytes(str(e), encoding="utf8")))

                        y = int(conn.recv(self._buffer_size).decode("utf8"))

                        y2 = exponentiation_modulo(y, 2, self.n)
                        xv = x * exponentiation_modulo(v, e, self.n) % self.n
                        
                        print(f"{i + 1}.\n\t{x = }\n\t{e = }\n\t{y = }\n\t--\n\ty^2 % n = {y2}\n\tx * v^e % n = {xv}")
                        
                        if y2 == xv:
                            print(f"(success) y^2 == x * v^e % n\n")
                            if i == t - 1:
                                print(f"🟢 Аутентификация '{name}' пройдена успешно")
                                conn.send((bytes("success", encoding="utf8")))
                            else:
                                conn.send((bytes("check", encoding="utf8")))
                        else:
                            print(f"(fail) y^2 != x * v^e % n\n")
                            conn.send((bytes("fail", encoding="utf8")))
                            print(f"🔴 Аутентификация '{name}' не пройдена")
                            break

            except Exception as e:
                print(f"🔴 Произошла ошибка при обработке запроса: {e}")

            finally:
                conn.close()
                print(f"🔴 Соединение с клиентом потеряно {addr}")

class ClientApp:
    def __init__(self, master):
        self.master = master
        master.title("Client App")

        self.name_label = tk.Label(master, text="Введите имя пользователя:")
        self.name_label.pack()

        self.name_entry = tk.Entry(master)
        self.name_entry.pack()

        self.register_button = tk.Button(master, text="Зарегистрироваться", command=self.register)
        self.register_button.pack()

        self.auth_button = tk.Button(master, text="Авторизоваться", command=self.auth)
        self.auth_button.pack()

        self.status_label = tk.Label(master, text="")
        self.status_label.pack()

        # Создание сокета для подключения к серверу
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect_to_server(self):
        try:
            self.sock.connect(("localhost", 3000))
            return True
        except Exception as e:
            messagebox.showerror("Ошибка подключения", str(e))
            return False

    def register(self):
        if not self.connect_to_server():
            return
        
        name = self.name_entry.get()
        
        if not name:
            messagebox.showwarning("Предупреждение", "Введите имя пользователя.")
            return
        
        try:
            n = int(self.sock.recv(1024).decode("utf8"))
            print(f"🟢 С сервера получено n")
   
            self.sock.send((bytes("{register}", encoding="utf8")))
            self.sock.send((bytes(name, encoding="utf8")))
            
            s = gen_mutually_prime_big(n)
            v = exponentiation_modulo(s, 2, n)

            self.sock.send((bytes(str(v), encoding="utf8")))

            status = self.sock.recv(1024).decode("utf8")
            
            if status == "success":
                messagebox.showinfo("Успех", "Пользователь успешно зарегистрирован.")
            elif status == "already registered":
                messagebox.showwarning("Предупреждение", "Пользователь под этим именем уже зарегистрирован.")
        
        except Exception as e:
            messagebox.showerror("Ошибка регистрации", str(e))
        
    def auth(self):
        if not self.connect_to_server():
            return
        
        name = self.name_entry.get()
        
        if not name:
            messagebox.showwarning("Предупреждение", "Введите имя пользователя.")
            return
        
        try:
            self.sock.send((bytes("{auth}", encoding="utf8")))
            
            n = int(self.sock.recv(1024).decode("utf8"))
            print(f"🟢 С сервера получено n")
            
            self.sock.send((bytes(name, encoding="utf8")))
            
            while True:
                r = random.randrange(1, n - 1)
                x = exponentiation_modulo(r, 2, n)
                self.sock.send((bytes(str(x), encoding="utf8")))
                
                e_response = self.sock.recv(1024).decode("utf8")

                if not e_response:  
                    messagebox.showerror("Ошибка соединения", "Соединение с сервером было разорвано.")
                    break
                
                e = int(e_response)

                y = r * s ** e % n

                self.sock.send((bytes(str(y), encoding="utf8")))

                status_response = self.sock.recv(1024).decode("utf8")

                if status_response == "success":
                    messagebox.showinfo("Успех", "Авторизация пройдена успешно.")
                    break
                elif status_response == "fail":
                    messagebox.showerror("Ошибка авторизации", "Отказ в авторизации.")
                    break
                elif status_response == "check":
                    time.sleep(0.1)  

        except Exception as e:
            messagebox.showerror("Ошибка авторизации", str(e))

    def close_connection(self):
        print("🔴 Закрытие соединения с сервером...")
        self.sock.close()

if __name__ == '__main__':
    root = tk.Tk()
    client_app = ClientApp(root)
    
    root.mainloop()
