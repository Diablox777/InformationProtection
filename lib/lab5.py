import random
import hashlib
from sys import byteorder
from math import ceil
import collections
import tkinter as tk
from tkinter import messagebox, ttk
from lab4 import *  # Предположительно, здесь находятся необходимые криптографические функции

# Определение вариантов голосования
VOTING_OPTIONS = {"No": 0, "Yes": 1, "Abstain": 2}
VOTING_OPTIONS_COUNT = len(VOTING_OPTIONS)

# Система голосования (серверная часть)
class VotingServer:
    def __init__(self):
        self.P, self.Q = self.generate_primes()  # Генерация простых чисел P и Q
        self.N = self.P * self.Q  # Модуль для RSA
        self.D, self.C = self.generate_private_public_keys()  # Генерация приватного и публичного ключа
        self.voted = set()  # Множество проголосовавших
        self.blanks = []  # Список для хранения голосов

    def generate_primes(self):
        # Генерация простых чисел P и Q
        while True:
            P = random.getrandbits(512)
            if check_prime(P):
                break
        while True:
            Q = random.getrandbits(512)
            if check_prime(Q):
                break
        return P, Q  # Возвращаем P и Q как атрибуты

    def generate_private_public_keys(self):
        # Генерация публичного и приватного ключей
        phi = (self.P - 1) * (self.Q - 1)  # Эйлерова функция от N
        D = generate_coprime(phi)
        C = gcd_modified(D, phi)[1]
        while C < 0:
            C += phi
        return D, C

    def get_results(self):
        # Подсчет голосов
        vote_counts = collections.Counter()
        for blank in self.blanks:
            vote_counts[blank[0] & VOTING_OPTIONS_COUNT] += 1
        return vote_counts

# Хэширование с использованием SHA3
def hash_sha3(value: int) -> int:
    byte_data = value.to_bytes(ceil(value.bit_length() / 8), byteorder=byteorder)
    return int.from_bytes(hashlib.sha3_256(byte_data).digest(), byteorder=byteorder)

# Вычисление обратного числа по модулю
def modular_inverse(a: int, mod: int) -> int:
    inv = gcd_modified(a, mod)[1]
    return inv if inv >= 0 else inv + mod

# Осуществление голосования
def cast_vote(voter_name: str, choice: str, server: VotingServer, result_output: tk.Text):
    if voter_name in server.voted:
        result_output.insert(tk.END, f'Голос от избирателя {voter_name} уже есть.\n')
        return

    random_value = random.getrandbits(256)
    vote_value = VOTING_OPTIONS[choice]
    vote_packet = (random_value << 257) | vote_value  # Формирование пакета для голосования
    r = generate_coprime(server.N)
    h = hash_sha3(vote_packet)
    h_prime = h * pow_module(r, server.D, server.N) % server.N

    server.voted.add(voter_name)
    s_prime = pow_module(h_prime, server.C, server.N)
    s = s_prime * modular_inverse(r, server.N) % server.N

    if hash_sha3(vote_packet) == pow_module(s, server.D, server.N):
        server.blanks.append((vote_packet, s))
        result_output.insert(tk.END, f'Голос от {voter_name} принят.\n')
    else:
        result_output.insert(tk.END, f'Голос от {voter_name} отклонён.\n')

# Графическое приложение для голосования
class VotingApp:
    def __init__(self, root):
        self.root = root
        self.server = VotingServer()
        self.initialize_ui()

    def initialize_ui(self):
        self.root.title("Протокол «Слепая подпись»")
        self.root.attributes('-fullscreen', True)  # Полноэкранный режим
        self.root.configure(bg="#e0f7fa")

        # Заголовок интерфейса
        title_label = tk.Label(self.root, text="Электронное голосование", font=("Arial", 24, "bold"), fg="#00796b", bg="#e0f7fa")
        title_label.pack(pady=20)

        # Поле для ввода имени
        self.name_input = tk.Entry(self.root, font=("Arial", 14), fg="#00796b", bd=2, relief="solid")
        self.name_input.insert(0, "Введите имя избирателя")
        self.name_input.pack(pady=10, ipadx=10, ipady=5)

        # Выпадающий список с вариантами голосования
        self.vote_choice = tk.StringVar(value="Yes")
        options = ["Yes", "No", "Abstain"]
        self.vote_dropdown = tk.OptionMenu(self.root, self.vote_choice, *options)
        self.vote_dropdown.config(font=("Arial", 14), width=20, relief="solid")
        self.vote_dropdown.pack(pady=10)

        # Кнопка для отправки голосования
        self.vote_button = tk.Button(self.root, text="Проголосовать", font=("Arial", 14), bg="#00796b", fg="white", relief="raised", command=self.submit_vote)
        self.vote_button.pack(pady=20)

        # Вывод отчета
        self.result_output = tk.Text(self.root, font=("Arial", 12), width=70, height=10, wrap=tk.WORD, state=tk.DISABLED, bd=2, relief="solid", bg="#ffffff")
        self.result_output.pack(pady=10)

        # Отображение результатов голосования
        self.result_label = tk.Label(self.root, text="Результат голосования:", font=("Arial", 18, "bold"), fg="#00796b", bg="#e0f7fa")
        self.result_label.pack(pady=10)

        self.result_display = tk.Text(self.root, font=("Arial", 12), width=70, height=6, wrap=tk.WORD, state=tk.DISABLED, bd=2, relief="solid", bg="#ffffff")
        self.result_display.pack(pady=10)

        # Отображение ключевых чисел
        self.keys_output_label = tk.Label(self.root, text="Ключевые числа:", font=("Arial", 14, "bold"), fg="#00796b", bg="#e0f7fa")
        self.keys_output_label.pack(pady=10)

        self.keys_output = tk.Text(self.root, font=("Arial", 12), width=70, height=6, wrap=tk.WORD, state=tk.DISABLED, bd=2, relief="solid", bg="#ffffff")
        self.keys_output.pack(pady=10)

    def submit_vote(self):
        voter_name = self.name_input.get().strip()
        vote_choice = self.vote_choice.get()

        if not voter_name or voter_name == "Введите имя избирателя":
            messagebox.showerror("Ошибка", "Пожалуйста, введите имя избирателя.")
            return

        cast_vote(voter_name, vote_choice, self.server, self.result_output)
        self.update_results()

    def update_results(self):
        # Обновление результатов голосования
        vote_counts = self.server.get_results()
        self.result_display.config(state=tk.NORMAL)
        self.result_display.delete(1.0, tk.END)
        self.result_display.insert(tk.END, f"За: {vote_counts[1]}\n")
        self.result_display.insert(tk.END, f"Против: {vote_counts[0]}\n")
        self.result_display.insert(tk.END, f"Воздержались: {vote_counts[2]}\n")
        self.result_display.config(state=tk.DISABLED)

        # Обновление списка проголосовавших
        self.result_output.config(state=tk.NORMAL)
        self.result_output.insert(tk.END, "\nПроголосовавшие:\n")
        for voter in self.server.voted:
            self.result_output.insert(tk.END, f"{voter}\n")
        self.result_output.config(state=tk.DISABLED)

        # Обновление вывода ключевых чисел
        self.keys_output.config(state=tk.NORMAL)
        self.keys_output.delete(1.0, tk.END)
        self.keys_output.insert(tk.END, f"N: {self.server.N}\n")
        self.keys_output.insert(tk.END, f"D: {self.server.D}\n")
        self.keys_output.insert(tk.END, f"C: {self.server.C}\n")
        self.keys_output.config(state=tk.DISABLED)

# Запуск приложения
if __name__ == "__main__":
    root = tk.Tk()
    app = VotingApp(root)
    root.mainloop()
