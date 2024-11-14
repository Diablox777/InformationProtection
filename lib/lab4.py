import tkinter as tk
from tkinter import messagebox
from collections import Counter
import random
from lab3 import *  # Для импортирования функций, таких как generate_prime, pow_module и т.д.

# Список возможных имен для игроков
names = ["Alice", "Bob", "Charlie", "David", "Eve", "Frank", "Grace", "Heidi", "Ivy", "Jack",
         "Kathy", "Leo", "Mona", "Nick", "Olivia", "Paul", "Quincy", "Rachel", "Sam", "Tina",
         "Ursula", "Vera", "Wendy", "Xander", "Yara", "Zane", "Aaron", "Beatrice", "Carl", "Diana"]

# Генерация колоды карт
def gen_deck() -> dict:
    suits = ['♠', '♣', '♥', '♦']
    faces = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    
    cards = []
    for suit in suits:
        for face in faces:
            cards.append(str(suit + face))
    return {i: cards[i - 2] for i in range(2, 54)}

# Значение карты
def card_value(card):
    face = card[1:]
    if face in '23456789':
        return int(face)
    elif face == '10':
        return 10
    elif face == 'J':
        return 11
    elif face == 'Q':
        return 12
    elif face == 'K':
        return 13
    elif face == 'A':
        return 14

# Определение ранга руки
def get_hand_rank(hand, table):
    all_cards = hand + list(table.values())
    values = sorted([card_value(card) for card in all_cards], reverse=True)
    suits = [card[0] for card in all_cards]
    
    counts = Counter(values)
    flush = len(set(suits)) == 1
    straight = all([values[i] - values[i+1] == 1 for i in range(len(values) - 1)])
    
    if straight and flush and values[0] == 14:
        return (9, values)
    if straight and flush:
        return (8, values)
    if 4 in counts.values():
        return (7, values)
    if 3 in counts.values() and 2 in counts.values():
        return (6, values)
    if flush:
        return (5, values)
    if straight:
        return (4, values)
    if 3 in counts.values():
        return (3, values)
    if list(counts.values()).count(2) == 2:
        return (2, values)
    if 2 in counts.values():
        return (1, values)
    return (0, values)

# Определение победителя
def determine_winner(hands, table):
    hand_ranks = [get_hand_rank(hand, table) for hand in hands]
    winner_index = max(range(len(hand_ranks)), key=lambda i: hand_ranks[i])
    return winner_index, hand_ranks

# Игра
def mental_poker(players_num):
    while True:
        q = generate_prime(0, 10 ** 9)
        p = 2 * q + 1
        if check_prime(p):
            break

    C = [generate_coprime(p-1) for _ in range(players_num)]
    D = [gcd_modified(C_temp, p-1)[1] + (p - 1) if gcd_modified(C_temp, p-1)[1] < 0 else gcd_modified(C_temp, p-1)[1] for C_temp in C]

    origin_deck = gen_deck()
    deck_keys = list(origin_deck.keys())

    for i in range(players_num):
        deck_keys = [pow_module(j, C[i], p) for j in deck_keys]
        random.shuffle(deck_keys)

    hands = [[] for _ in range(players_num)]
    for i in range(players_num):
        for _ in range(2):
            card = deck_keys.pop(0)
            hands[i].append(card)

    table = deck_keys[:5]
    for i in range(players_num):
        table = [pow_module(card, D[i], p) for card in table]
    table = {key: origin_deck[key] for key in table}

    for i in range(players_num):
        for j in range(players_num):
            if i != j:
                hands[i] = [pow_module(card, D[j], p) for card in hands[i]]
        hands[i] = [origin_deck[pow_module(card, D[i], p)] for card in hands[i]]

    winner_index, ranks = determine_winner(hands, table)
    display_results(hands, table, winner_index)

# Рисование карты на холсте с цветом для красных карт
def draw_card(canvas, x, y, card, is_winner=False):
    width, height = 80, 120
    canvas.create_rectangle(x, y, x + width, y + height, fill="white", outline="black")
    
    suit, value = card[0], card[1:]

    # Определение цвета текста в зависимости от масти
    text_color = "red" if suit in ['♥', '♦'] else "black"

    canvas.create_text(x + width / 2, y + 20, text=value, font=("Helvetica", 16, "bold"), fill=text_color)
    canvas.create_text(x + width / 2, y + height - 20, text=suit, font=("Helvetica", 20, "bold"), fill=text_color)

    if is_winner:
        canvas.create_rectangle(x, y, x + width, y + height, outline="gold", width=3)

# Отображение результатов
def display_results(hands, table, winner_index):
    canvas.delete("all")  # Очистить холст перед рисованием новых карт

    shuffled_names = random.sample(names, len(hands))

    x_offset = 10
    y_offset = 10

    # Отображаем карты каждого игрока
    for i, hand in enumerate(hands):
        draw_card(canvas, x_offset, y_offset, hand[0], is_winner=(i == winner_index))
        x_offset += 90
        draw_card(canvas, x_offset, y_offset, hand[1], is_winner=(i == winner_index))
        x_offset += 90
        y_offset += 130
        x_offset = 10

    # Отображаем карты на столе
    y_offset += 20  # Добавляем пространство после карт игроков
    x_offset = 10
    for card in table.values():
        draw_card(canvas, x_offset, y_offset, card)
        x_offset += 90

# Начало игры
def start_game():
    try:
        players_num = int(players_entry.get())
        if players_num < 2:
            raise ValueError("Число игроков должно быть больше одного.")
        mental_poker(players_num)
    except ValueError as e:
        messagebox.showerror("Ошибка", str(e))

# Интерфейс
root = tk.Tk()
root.title("Mental Poker Game")
root.geometry("1920x1080")
root.configure(bg="#2E3440")

title_label = tk.Label(root, text="Mental Poker Game", font=("Helvetica", 18, "bold"), fg="#88C0D0", bg="#2E3440")
title_label.pack(pady=(20, 10))

input_frame = tk.Frame(root, bg="#3B4252", padx=20, pady=10)
input_frame.pack(pady=(0, 10))

players_label = tk.Label(input_frame, text="Number of Players:", font=("Helvetica", 12), fg="#E5E9F0", bg="#3B4252")
players_label.grid(row=0, column=0, padx=5, pady=5)

players_entry = tk.Entry(input_frame, font=("Helvetica", 12), width=5)
players_entry.grid(row=0, column=1, padx=5, pady=5)

start_button = tk.Button(root, text="Start Game", command=start_game, font=("Helvetica", 12), bg="#4C566A", fg="#D8DEE9")
start_button.pack(pady=10)

# Создаем холст один раз
canvas = tk.Canvas(root, width=1280, height=800, bg="#006400")
canvas.pack(pady=10)

root.mainloop()
