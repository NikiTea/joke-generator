#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Генератор анекдотов про программистов
Шутки с юмором для поднятия настроения!
"""

import random
import time
import sys

# ANSI коды для цветного текста (работают на большинстве терминалов)
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Коллекция анекдотов
JOKES = [
    """Программист приходит домой с двумя батонами хлеба.
Жена спрашивает:
— Зачем два?
— Ты же сказала: купи батон хлеба, если будут яйца — возьми два!
— А яйца были?
— Были.
— Так где же они?
— Так ты же сказала взять два батона!""",

    """Заходит программист в бар. Бармен:
— Вам как обычно?
— Null pointer exception!
Бармен в панике:
— Но... вы же всегда заказывали пиво!
— А, извините, это на работе случилось. Одно пиво, пожалуйста.""",

    """— Дорогая, я на работе!
— Уже 3 часа ночи! Что ты там делаешь?
— Компилируется...
— И долго ещё?
— Ещё 2%...""",

    """Три программиста идут по улице. Вдруг один говорит:
— Пошли в бар!
Второй:
— true
Третий:
— false
Они прошли мимо бара.""",

    """— Сколько программистов нужно, чтобы вкрутить лампочку?
— Ноль. Это аппаратная проблема.""",

    """Программист за рулём. Жена звонит:
— Дорогой, будь осторожен! По радио сказали, что по трассе едет лихач!
— Один?! Тут их сотни!""",

    """Bug — это не ошибка, это недокументированная фича!""",

    """— Почему программисты путают Хэллоуин и Рождество?
— Потому что OCT 31 = DEC 25!""",

    """Жена программисту:
— Сходи в магазин, купи батон колбасы. Если будут яйца — купи десяток.
Программист возвращается с 10 батонами колбасы.
— Ты что творишь?!
— Яйца были.""",

    """Настоящий программист пишет код, который может понять только он.
Через полгода он становится настоящим дешифровщиком."""
]

ASCII_ART = r"""
    ___________
   /           \
  /   ^     ^   \
 |      ___      |
 |     /   \     |
  \    \___/    /
   \___________/
   
   😄 АНЕКДОТ! 😄
"""

def print_colored(text, color):
    """Печать цветного текста"""
    print(f"{color}{text}{Colors.ENDC}")

def print_header():
    """Вывод заголовка программы"""
    print_colored("=" * 60, Colors.OKCYAN)
    print_colored(ASCII_ART, Colors.WARNING)
    print_colored("🎭  ГЕНЕРАТОР АНЕКДОТОВ ПРО ПРОГРАММИСТОВ  🎭", Colors.HEADER + Colors.BOLD)
    print_colored("=" * 60, Colors.OKCYAN)
    print()

def animate_text(text, delay=0.03):
    """Анимация печати текста"""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def display_joke():
    """Показать случайный анекдот"""
    joke = random.choice(JOKES)
    
    print_colored("\n┌" + "─" * 58 + "┐", Colors.OKGREEN)
    
    # Разбиваем анекдот на строки и выводим с отступами
    lines = joke.split('\n')
    for line in lines:
        print_colored(f"│ {line:<56} │", Colors.OKBLUE)
    
    print_colored("└" + "─" * 58 + "┘\n", Colors.OKGREEN)

def show_menu():
    """Показать меню"""
    print_colored("\n🎯 Что будем делать?", Colors.OKCYAN + Colors.BOLD)
    print("  1 - Показать анекдот")
    print("  2 - Показать случайный анекдот с анимацией")
    print("  3 - Показать все анекдоты")
    print("  0 - Выход")
    print_colored("─" * 40, Colors.OKCYAN)

def display_joke_animated():
    """Показать анекдот с анимацией"""
    joke = random.choice(JOKES)
    
    print_colored("\n" + "─" * 60, Colors.OKGREEN)
    animate_text(joke, delay=0.02)
    print_colored("─" * 60 + "\n", Colors.OKGREEN)

def display_all_jokes():
    """Показать все анекдоты"""
    print_colored(f"\n📚 Всего анекдотов в коллекции: {len(JOKES)}\n", Colors.WARNING + Colors.BOLD)
    
    for i, joke in enumerate(JOKES, 1):
        print_colored(f"\n{'═' * 60}", Colors.OKCYAN)
        print_colored(f"  Анекдот #{i}", Colors.HEADER + Colors.BOLD)
        print_colored(f"{'═' * 60}", Colors.OKCYAN)
        print(joke)
        
        if i < len(JOKES):
            time.sleep(0.5)

def main():
    """Основная функция программы"""
    print_header()
    
    while True:
        show_menu()
        
        try:
            choice = input(f"{Colors.OKGREEN}Ваш выбор: {Colors.ENDC}").strip()
            
            if choice == '1':
                display_joke()
                
            elif choice == '2':
                print_colored("\n⏳ Загрузка анекдота...", Colors.WARNING)
                time.sleep(0.5)
                display_joke_animated()
                
            elif choice == '3':
                display_all_jokes()
                
            elif choice == '0':
                print_colored("\n👋 До встречи! Пусть ваш код будет без багов! 🐛\n", Colors.HEADER + Colors.BOLD)
                break
                
            else:
                print_colored("\n❌ Неверный выбор! Попробуйте снова.", Colors.FAIL)
                
        except KeyboardInterrupt:
            print_colored("\n\n👋 Прервано пользователем. До встречи!\n", Colors.WARNING)
            break
        except Exception as e:
            print_colored(f"\n❌ Произошла ошибка: {e}", Colors.FAIL)

if __name__ == "__main__":
    main()
