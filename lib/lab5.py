import random
import hashlib
from sys import byteorder
from math import ceil
import collections
import tkinter as tk
from tkinter import messagebox, ttk
from lab4 import *

# Оригинальная серверная логика
voting_options = {"No": 0, "Yes": 1, "Abstain": 2}
voting_options_count = len(voting_options)

class Server:
    def __init__(self):
        while P := random.getrandbits(512):
            if check_prime(P):
                break
        while Q := random.getrandbits(512):
            if check_prime(Q):
                break
        self.N = P * Q
        phi = (P - 1) * (Q - 1)
        self.D = generate_coprime(phi)
        self.C = gcd_modified(self.D, phi)[1]
        while self.C < 0:
            self.C += phi
        self.voted = set()
        self.blanks = list()

    def get_result(self):
        counter = collections.Counter()
        for blank in self.blanks:
            counter[blank[0] & voting_options_count] += 1
        return counter


def my_sha(n: int) -> int:
    return int.from_bytes(hashlib.sha3_256(n.to_bytes(ceil(n.bit_length() / 8), byteorder=byteorder)).digest(),
                          byteorder=byteorder)


def inverse(n: int, p: int) -> int:
    inv = gcd_modified(n, p)[1]
    if inv < 0:
        inv += p
    return inv


def vote(name, choice, server, result_output):
    if name in server.voted:
        result_output.insert(tk.END, f'Голос от избирателя {name} уже есть.\n')
        return

    rnd = random.getrandbits(256)
    v = voting_options[choice]
    n = rnd << 257 | v
    r = generate_coprime(server.N)
    h = my_sha(n)
    _h = h * pow_module(r, server.D, server.N) % server.N

    server.voted.add(name)
    _s = pow_module(_h, server.C, server.N)
    s = _s * inverse(r, server.N) % server.N

    if my_sha(n) == pow_module(s, server.D, server.N):
        server.blanks.append((n, s))
        result_output.insert(tk.END, f'Голос от {name} принят.\n')
    else:
        result_output.insert(tk.END, f'Голос от {name} отклонён.\n')


class VotingApp:
    def __init__(self, root):
        self.root = root
        self.server = Server()
        self.init_ui()

    def init_ui(self):
        self.root.title("Протокол «Слепая подпись»")
        self.root.attributes('-fullscreen', True)  # Окно на весь экран
        self.root.configure(bg="#e0f7fa")  # Легкий голубой фон

        # Заголовок
        title_label = tk.Label(self.root, text="Электронное голосование", font=("Arial", 24, "bold"), fg="#00796b", bg="#e0f7fa")
        title_label.pack(pady=20)

        # Поле для имени
        self.name_input = tk.Entry(self.root, font=("Arial", 14), fg="#00796b", bd=2, relief="solid")
        self.name_input.insert(0, "Введите имя избирателя")
        self.name_input.pack(pady=10, ipadx=10, ipady=5)

        # Выбор варианта
        self.vote_combo = tk.StringVar()
        self.vote_combo.set("Yes")
        vote_options = ["Yes", "No", "Abstain"]
        self.vote_dropdown = tk.OptionMenu(self.root, self.vote_combo, *vote_options)
        self.vote_dropdown.config(font=("Arial", 14), width=20, relief="solid")
        self.vote_dropdown.pack(pady=10)

        # Кнопка для голосования
        self.vote_button = tk.Button(self.root, text="Проголосовать", font=("Arial", 14), bg="#00796b", fg="white", relief="raised", command=self.on_vote_click)
        self.vote_button.pack(pady=20)

        # Вывод отчета
        self.result_output = tk.Text(self.root, font=("Arial", 12), width=70, height=10, wrap=tk.WORD, state=tk.DISABLED, bd=2, relief="solid", bg="#ffffff")
        self.result_output.pack(pady=10)

        # Результат голосования
        self.result_label = tk.Label(self.root, text="Результат голосования:", font=("Arial", 18, "bold"), fg="#00796b", bg="#e0f7fa")
        self.result_label.pack(pady=10)

        self.result_display = tk.Text(self.root, font=("Arial", 12), width=70, height=6, wrap=tk.WORD, state=tk.DISABLED, bd=2, relief="solid", bg="#ffffff")
        self.result_display.pack(pady=10)

        # Окно для отображения ключевых чисел
        self.keys_output_label = tk.Label(self.root, text="Ключевые числа:", font=("Arial", 14, "bold"), fg="#00796b", bg="#e0f7fa")
        self.keys_output_label.pack(pady=10)

        self.keys_output = tk.Text(self.root, font=("Arial", 12), width=70, height=6, wrap=tk.WORD, state=tk.DISABLED, bd=2, relief="solid", bg="#ffffff")
        self.keys_output.pack(pady=10)

    def on_vote_click(self):
        name = self.name_input.get().strip()
        choice = self.vote_combo.get()

        if name == "" or name == "Введите имя избирателя":
            messagebox.showerror("Ошибка", "Пожалуйста, введите имя избирателя.")
            return

        vote(name, choice, self.server, self.result_output)
        
        # Обновление результатов
        self.update_results()

    def update_results(self):
        counter = self.server.get_result()
        self.result_display.config(state=tk.NORMAL)
        self.result_display.delete(1.0, tk.END)
        self.result_display.insert(tk.END, f"За: {counter[1]}\n")
        self.result_display.insert(tk.END, f"Против: {counter[0]}\n")
        self.result_display.insert(tk.END, f"Воздержались: {counter[2]}\n")
        self.result_display.config(state=tk.DISABLED)

        # Обновляем список проголосовавших
        self.result_output.config(state=tk.NORMAL)
        self.result_output.insert(tk.END, "\nПроголосовавшие:\n")
        for voter in self.server.voted:
            self.result_output.insert(tk.END, f"{voter}\n")
        self.result_output.config(state=tk.DISABLED)

        # Отображение ключевых чисел
        self.keys_output.config(state=tk.NORMAL)
        self.keys_output.delete(1.0, tk.END)
        self.keys_output.insert(tk.END, f"N: {self.server.N}\n")
        self.keys_output.insert(tk.END, f"D: {self.server.D}\n")
        self.keys_output.insert(tk.END, f"C: {self.server.C}\n")
        self.keys_output.config(state=tk.DISABLED)


if __name__ == "__main__":
    root = tk.Tk()
    app = VotingApp(root)
    root.mainloop()
