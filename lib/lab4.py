import tkinter as tk
from tkinter import messagebox
from lab3 import *
import random
from collections import Counter

def gen_deck() -> dict:
    suits = ['♠', '♣', '♥', '♦']
    faces = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    
    cards = []
    for suit in suits:
        for face in faces:
            cards.append(str(suit + face))
    return {i: cards[i - 2] for i in range(2, 54)}

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

def determine_winner(hands, table):
    hand_ranks = [get_hand_rank(hand, table) for hand in hands]
    winner_index = max(range(len(hand_ranks)), key=lambda i: hand_ranks[i])
    return winner_index, hand_ranks

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

def display_results(hands, table, winner_index):
    result_frame.delete(1.0, tk.END)
    for i, hand in enumerate(hands):
        if i == winner_index:
            result_frame.insert(tk.END, f"Player {i + 1} Hand: {', '.join(hand)}\n", "winner")
        else:
            result_frame.insert(tk.END, f"Player {i + 1} Hand: {', '.join(hand)}\n")
    result_frame.insert(tk.END, f"\nTable Cards: {', '.join(table.values())}\n")

def start_game():
    try:
        players_num = int(players_entry.get())
        if players_num < 2:
            raise ValueError("Число игроков должно быть больше одного.")
        mental_poker(players_num)
    except ValueError as e:
        messagebox.showerror("Ошибка", str(e))

# Создаем графический интерфейс
root = tk.Tk()
root.title("Mental Poker Game")
root.geometry("600x500")
root.configure(bg="#2E3440")

# Заголовок
title_label = tk.Label(root, text="Mental Poker Game", font=("Helvetica", 18, "bold"), fg="#88C0D0", bg="#2E3440")
title_label.pack(pady=(20, 10))

# Поле ввода числа игроков
input_frame = tk.Frame(root, bg="#3B4252", padx=20, pady=10)
input_frame.pack(pady=(0, 10))

players_label = tk.Label(input_frame, text="Number of Players:", font=("Helvetica", 12), fg="#E5E9F0", bg="#3B4252")
players_label.grid(row=0, column=0, padx=5, pady=5)

players_entry = tk.Entry(input_frame, font=("Helvetica", 12), width=5)
players_entry.grid(row=0, column=1, padx=5, pady=5)

# Кнопка запуска игры
start_button = tk.Button(root, text="Start Game", command=start_game, font=("Helvetica", 12), bg="#4C566A", fg="#D8DEE9")
start_button.pack(pady=10)

# Результаты игры
result_frame = tk.Text(root, font=("Helvetica", 12), width=60, height=15, bg="#3B4252", fg="#D8DEE9", bd=0, padx=10, pady=10, wrap="word")
result_frame.tag_configure("winner", foreground="#A3BE8C", font=("Helvetica", 12, "bold"))
result_frame.pack(pady=10)

# Устанавливаем стиль и отступы для основного окна
root.option_add("*Font", "Helvetica 12")
root.option_add("*Label.Font", "Helvetica 12")
root.option_add("*Entry.Font", "Helvetica 12")
root.option_add("*Button.Font", "Helvetica 12 bold")
root.option_add("*Button.Background", "#4C566A")
root.option_add("*Button.Foreground", "#D8DEE9")

root.mainloop()
