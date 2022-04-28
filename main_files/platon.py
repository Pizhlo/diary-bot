import random

h = ["камень", "ножницы", "бумага"]
choice = random.choice(h)

p = input("Сделайте выбор: ")

print('Мой выбор: ', choice)

if choice == p:
    print("Ничья")

if choice == "камень" and p == "ножницы":
    print("Вы выиграли")

if choice == "камень" and p == "бумага":
    print("Вы проиграли")

if choice == "ножницы" and p == "бумага":
    print("Вы проиграли")

if choice == "ножницы" and p == "камень":
    print("Вы выиграли")

if choice == "бумага" and p == "ножницы":
    print("Вы выиграли")

if choice == "бумага" and p == "камень":
    print("Вы проиграли")