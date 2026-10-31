#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Генератор анекдотов про программистов
Шутки с юмором для поднятия настроения!

Работает в терминале, без сторонних библиотек.
Анимации: градиентный логотип, побуквенная печать, загрузка, смешнометр.
Во время печати можно нажать любую клавишу, чтобы сразу показать весь текст.
"""

import os
import sys
import time
import math
import random
import shutil
import atexit
import textwrap

IS_WIN = os.name == "nt"
if IS_WIN:
    import msvcrt
else:
    import termios
    import tty
    import select

# Включаем поддержку ANSI-цветов в консоли Windows и UTF-8 вывод
if IS_WIN:
    os.system("")
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# Интерактивный режим (стрелки, пропуск анимации) — только в настоящем терминале.
# JOKE_FAST=1 отключает задержки (удобно для проверки).
INTERACTIVE = sys.stdin.isatty() and sys.stdout.isatty()
ANIMATE = sys.stdout.isatty() and not os.environ.get("JOKE_FAST")


# ─────────────────────────── Цвета и вывод ───────────────────────────

RESET = "\033[0m"
BOLD = "\033[1m"
ITALIC = "\033[3m"
HIDE_CURSOR = "\033[?25l"
SHOW_CURSOR = "\033[?25h"
CLEAR = "\033[2J\033[H"
CLEAR_LINE = "\033[2K\r"

NEON = [(255, 95, 170), (170, 95, 255), (80, 200, 255)]
SUNSET = [(255, 215, 90), (255, 130, 80), (240, 70, 140)]
MINT = [(90, 255, 180), (80, 200, 255)]
LAUGH = [(120, 230, 120), (255, 215, 90), (255, 90, 110)]
SPEAKERS = [(125, 205, 255), (255, 175, 115)]
TEXT = (232, 232, 242)
MUTED = (125, 125, 150)


def fg(r, g, b):
    return f"\033[38;2;{r};{g};{b}m"


def out(s):
    sys.stdout.write(s)
    sys.stdout.flush()


def mix(c1, c2, t):
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))


def pick(stops, t):
    """Цвет из градиента stops в точке t ∈ [0, 1]"""
    t = max(0.0, min(1.0, t))
    seg = t * (len(stops) - 1)
    i = min(int(seg), len(stops) - 2)
    return mix(stops[i], stops[i + 1], seg - i)


def wave(t):
    """Треугольная волна 0→1→0, чтобы градиент зацикливался без скачков"""
    t %= 1.0
    return 1 - abs(2 * t - 1)


def gradient(text, stops=NEON, phase=0.0, bold=False):
    n = max(len(text) - 1, 1)
    parts = [BOLD] if bold else []
    for i, ch in enumerate(text):
        if ch == " ":
            parts.append(ch)
        else:
            parts.append(fg(*pick(stops, wave(i / n * 0.5 + phase))) + ch)
    parts.append(RESET)
    return "".join(parts)


def term_width():
    return shutil.get_terminal_size((80, 24)).columns


def center_pad(width):
    return " " * max(0, (term_width() - width) // 2)


# ─────────────────────────── Клавиатура ───────────────────────────

_old_term = None
_skip = False  # пользователь попросил пропустить текущую анимацию


def setup_terminal():
    global _old_term
    if INTERACTIVE and not IS_WIN:
        fd = sys.stdin.fileno()
        _old_term = termios.tcgetattr(fd)
        tty.setcbreak(fd)
    out(HIDE_CURSOR)
    atexit.register(restore_terminal)


def restore_terminal():
    if _old_term is not None:
        termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, _old_term)
    out(RESET + SHOW_CURSOR)


def poll_key(timeout=0.0):
    """Вернуть нажатую клавишу или None, если за timeout ничего не нажали"""
    if not INTERACTIVE:
        time.sleep(timeout)
        return None
    if IS_WIN:
        end = time.time() + timeout
        while True:
            if msvcrt.kbhit():
                ch = msvcrt.getwch()
                if ch in ("\x00", "\xe0"):
                    return {"H": "UP", "P": "DOWN", "K": "LEFT", "M": "RIGHT"}.get(msvcrt.getwch(), None)
                break
            if time.time() >= end:
                return None
            time.sleep(0.01)
    else:
        if not select.select([sys.stdin], [], [], timeout)[0]:
            return None
        ch = sys.stdin.read(1)
        if ch == "\x1b" and select.select([sys.stdin], [], [], 0.03)[0]:
            seq = sys.stdin.read(2)
            return {"[A": "UP", "[B": "DOWN", "[D": "LEFT", "[C": "RIGHT"}.get(seq, None)
    if ch == "\x03":
        raise KeyboardInterrupt
    return {"\r": "ENTER", "\n": "ENTER", "\x1b": "ESC", " ": "SPACE"}.get(ch, ch)


def check_skip():
    global _skip
    if not _skip and INTERACTIVE and poll_key(0) is not None:
        _skip = True
    return _skip


def pause(seconds):
    """Задержка, которую можно прервать нажатием клавиши"""
    if not ANIMATE or _skip:
        return
    end = time.time() + seconds
    while time.time() < end:
        if check_skip():
            return
        time.sleep(min(0.01, max(0, end - time.time())))


def wait_key(hint="нажмите любую клавишу, чтобы продолжить"):
    """Пульсирующая подсказка и ожидание клавиши"""
    if not INTERACTIVE:
        print()
        return "ENTER"
    pad = center_pad(len(hint) + 2)
    t = 0.0
    while True:
        b = 0.35 + 0.65 * wave(t)
        out(CLEAR_LINE + pad + fg(*mix((40, 40, 55), (200, 200, 225), b)) + "↵ " + ITALIC + hint + RESET)
        key = poll_key(0.04)
        if key:
            out(CLEAR_LINE)
            return key
        t += 0.025


# ─────────────────────────── Анекдоты ───────────────────────────

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

LOADING_MESSAGES = [
    "Компилирую юмор",
    "Ищу баги в шутке",
    "Подключаюсь к серверу смеха",
    "Разогреваю нейроны",
    "Делаю git pull анекдотов",
    "Собираю шутку из исходников",
]

_bag = []


def next_random_joke():
    """Случайный анекдот без повторов, пока не закончится вся коллекция"""
    global _bag
    if not _bag:
        _bag = list(range(len(JOKES)))
        random.shuffle(_bag)
    return _bag.pop()


# ─────────────────────────── Логотип ───────────────────────────

FONT = {
    "А": [" ███ ", "█   █", "█████", "█   █", "█   █"],
    "Н": ["█   █", "█   █", "█████", "█   █", "█   █"],
    "Е": ["█████", "█    ", "████ ", "█    ", "█████"],
    "К": ["█   █", "█  █ ", "███  ", "█  █ ", "█   █"],
    "Д": [" ███ ", " █ █ ", " █ █ ", "█████", "█   █"],
    "О": [" ███ ", "█   █", "█   █", "█   █", " ███ "],
    "Т": ["█████", "  █  ", "  █  ", "  █  ", "  █  "],
}
LOGO = ["  ".join(FONT[ch][row] for ch in "АНЕКДОТ") for row in range(5)]
LOGO_W = len(LOGO[0])
SUBTITLE = "генератор анекдотов про программистов"


def logo_lines(phase=0.0, reveal=None, shine=None):
    """Строки логотипа: градиент, блик (shine — колонка) и появление по колонкам"""
    pad = center_pad(LOGO_W)
    lines = []
    for row, line in enumerate(LOGO):
        parts = [pad, BOLD]
        for x, ch in enumerate(line):
            if ch == " " or (reveal is not None and x > reveal):
                parts.append(" ")
                continue
            c = pick(NEON, wave(x / LOGO_W * 0.5 + row * 0.03 + phase))
            if shine is not None:
                d = abs(x - shine - row)
                if d < 5:
                    c = mix(c, (255, 255, 255), (1 - d / 5) * 0.8)
            parts.append(fg(*c) + ch)
        parts.append(RESET)
        lines.append("".join(parts))
    return lines


def draw_logo(**kw):
    out("\n".join(logo_lines(**kw)) + "\n")


def redraw_logo(**kw):
    out(f"\033[{len(LOGO)}A")
    draw_logo(**kw)


def draw_rule(width, stops=NEON, animated=True):
    """Линия, которая растёт из центра в стороны"""
    pad = center_pad(width)
    if not ANIMATE or not animated:
        out(pad + gradient("─" * width, stops) + "\n")
        return
    half = width // 2
    for k in range(0, half + 1, 2):
        seg = "─" * (2 * k)
        out(CLEAR_LINE + pad + " " * (half - k) + gradient(seg, stops))
        time.sleep(0.008)
    out(CLEAR_LINE + pad + gradient("─" * width, stops) + "\n")


def header(animated=False):
    if term_width() < LOGO_W + 2:
        out("\n" + center_pad(len(SUBTITLE)) + gradient(SUBTITLE.upper(), bold=True) + "\n\n")
        return
    out("\n")
    draw_logo()
    out("\n" + center_pad(len(SUBTITLE)) + gradient(SUBTITLE, SUNSET) + "\n")
    draw_rule(LOGO_W, animated=animated)


def intro():
    out(CLEAR)
    if not ANIMATE or term_width() < LOGO_W + 2:
        header()
        return
    out("\n")
    # Появление логотипа слева направо
    for k in range(0, LOGO_W + 6, 2):
        if k:
            out(f"\033[{len(LOGO)}A")
        draw_logo(reveal=k, shine=k - 4, phase=k / LOGO_W)
        time.sleep(0.016)
    # Переливание с бликом
    frames = 45
    for f in range(frames):
        redraw_logo(phase=1 + f / 60, shine=f / frames * (LOGO_W + 20) - 10)
        time.sleep(0.02)
    redraw_logo()
    # Подзаголовок печатается по буквам
    out("\n" + center_pad(len(SUBTITLE)))
    colored = [fg(*pick(SUNSET, wave(i / len(SUBTITLE) * 0.5))) + ch for i, ch in enumerate(SUBTITLE)]
    for ch in colored:
        out(ch)
        time.sleep(0.025)
    out(RESET + "\n")
    draw_rule(LOGO_W)


# ─────────────────────────── Анимации ───────────────────────────

SPINNER = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"


def loader(duration=1.3):
    """Спиннер + полоса загрузки со смешной подписью"""
    msg = random.choice(LOADING_MESSAGES)
    bar_w = 22
    width = len(msg) + bar_w + 14
    pad = center_pad(width)
    if not ANIMATE:
        out(pad + fg(*MINT[0]) + "✔ " + msg + RESET + "\n")
        return
    start = time.time()
    i = 0
    while True:
        p = min(1.0, (time.time() - start) / duration)
        eased = 1 - (1 - p) ** 3
        filled = int(eased * bar_w)
        bar = gradient("━" * filled, MINT) + fg(60, 60, 80) + "━" * (bar_w - filled) + RESET
        dots = "." * (i // 4 % 4)
        spin = fg(*pick(NEON, wave(i / 30))) + SPINNER[i % len(SPINNER)] + RESET
        out(CLEAR_LINE + pad + spin + " " + fg(*TEXT) + f"{msg}{dots:<3} " + bar
            + fg(*MUTED) + f" {int(eased * 100):3d}%" + RESET)
        if p >= 1:
            break
        i += 1
        time.sleep(0.03)
    out(CLEAR_LINE + pad + fg(*MINT[0]) + BOLD + "✔ " + RESET + fg(*TEXT) + msg + " — готово!" + RESET + "\n")


def card_width():
    return max(36, min(68, term_width() - 4))


def draw_border(text_parts, delay=0.003):
    """Печать рамки по символу (text_parts — список уже раскрашенных символов)"""
    for part in text_parts:
        out(part)
        pause(delay)


def type_line(prefix, text, colors, pad_to, suffix, slow=False):
    """Побуквенная печать строки с мигающим курсором и паузами на знаках препинания"""
    out(prefix)
    base = 0.034 if slow else 0.022
    for i, ch in enumerate(text):
        out(colors[i] + ch)
        if ANIMATE and not check_skip():
            out(fg(255, 255, 255) + "▌" + "\b")
            if ch in ".!?":
                pause(0.22)
            elif ch in ",:;—":
                pause(0.09)
            elif ch == " ":
                pause(base * 0.5)
            else:
                pause(base * random.uniform(0.6, 1.4))
    out(RESET + " " * (pad_to - len(text)) + suffix)


def show_card(joke, title, slow=False):
    """Карточка с анекдотом: рамка рисуется, текст печатается по буквам"""
    global _skip
    _skip = False
    W = card_width()
    inner = W - 4
    pad = center_pad(W)
    left_c, right_c = NEON[0], NEON[-1]
    L = fg(*left_c) + "│" + RESET
    R = fg(*right_c) + "│" + RESET

    def border_color(x):
        return fg(*pick(NEON, x / (W - 1)))

    # Верхняя рамка с заголовком
    t = f" {title} "
    top = ["╭", "─", "─"] + list(t) + ["─"] * (W - 4 - len(t)) + ["╮"]
    parts = []
    for x, ch in enumerate(top):
        if 3 <= x < 3 + len(t):
            parts.append(BOLD + fg(255, 255, 255) + ch + RESET)
        else:
            parts.append(border_color(x) + ch + RESET)
    out(pad)
    draw_border(parts)
    out("\n" + pad + L + " " * (W - 2) + R + "\n")

    # Текст: реплики разных героев — разными цветами, концовка — радугой
    raw_lines = joke.split("\n")
    speaker = 0
    for li, raw in enumerate(raw_lines):
        is_punch = li == len(raw_lines) - 1 and len(raw_lines) > 1
        if raw.startswith("—"):
            color = SPEAKERS[speaker % 2]
            speaker += 1
        else:
            color = TEXT
        wrapped = textwrap.wrap(raw, inner) or [""]
        for wi, line in enumerate(wrapped):
            if is_punch:
                colors = [BOLD + fg(*pick(SUNSET, wave(i / max(len(line), 1) * 0.5))) for i in range(len(line))]
            else:
                colors = [fg(*color)] * len(line)
                if wi == 0 and line.startswith("—"):
                    colors[0] = fg(*NEON[1])
            if is_punch and wi == 0:
                pause(0.35)  # драматическая пауза перед концовкой
            type_line(pad + L + " ", line, colors, inner, " " + R + "\n", slow=slow or is_punch)
        pause(0.12)

    # Нижняя рамка
    out(pad + L + " " * (W - 2) + R + "\n" + pad)
    bottom = ["╰"] + ["─"] * (W - 2) + ["╯"]
    draw_border([border_color(x) + ch + RESET for x, ch in enumerate(bottom)])
    out("\n")


def laugh_meter():
    """Смешнометр: полоса заполняется до случайного значения"""
    value = random.randint(62, 100)
    bar_w = 28
    label = "Смешнометр "
    W = card_width()
    pad = center_pad(W)

    def render(v):
        filled = int(v / 100 * bar_w)
        cells = "".join(fg(*pick(LAUGH, i / (bar_w - 1))) + "█" for i in range(filled))
        rest = fg(55, 55, 75) + "░" * (bar_w - filled)
        return CLEAR_LINE + pad + "  " + fg(*TEXT) + label + cells + rest + RESET + fg(*MUTED) + f" {int(v):3d}%" + RESET

    if ANIMATE:
        steps = 40
        for s in range(steps + 1):
            p = s / steps
            v = value * (1 - (1 - p) ** 3)
            # небольшой «перелёт» стрелки в конце для живости
            if p > 0.8:
                v += math.sin((p - 0.8) * 5 * math.pi) * 4 * (1 - p) * 5
            out(render(max(0, min(100, v))))
            time.sleep(0.022)
    out(render(value))

    if value < 75:
        reaction, stops = "😏  Ну, такое...", [(180, 180, 200), (140, 140, 170)]
    elif value < 90:
        reaction, stops = "😄  Неплохо!", MINT
    else:
        reaction, stops = "🤣  ХА-ХА-ХА! Шедевр!", SUNSET
    out("   ")
    for i, ch in enumerate(reaction):
        out(BOLD + fg(*pick(stops, i / max(len(reaction) - 1, 1))) + ch)
        if ANIMATE:
            time.sleep(0.03)
    out(RESET + "\n\n")


# ─────────────────────────── Экраны ───────────────────────────

MENU = [
    ("1", "🎲", "Случайный анекдот"),
    ("2", "🔢", "Анекдот по номеру"),
    ("3", "📚", "Все анекдоты подряд"),
    ("0", "🚪", "Выход"),
]
MENU_HINT = "↑↓ — выбор · Enter — открыть · или просто нажмите цифру"


def menu_lines(selected, phase):
    pad = center_pad(34)
    lines = [pad + BOLD + gradient("🎯 Что будем делать?", SUNSET, bold=True), ""]
    for i, (num, icon, label) in enumerate(MENU):
        if i == selected:
            arrow = fg(*pick(NEON, wave(phase * 2))) + "❯" + RESET
            lines.append(f"{pad} {arrow} {BOLD}{fg(255, 255, 255)}{num}{RESET}  {icon}  "
                         + gradient(label, NEON, phase, bold=True))
        else:
            lines.append(f"{pad}   {fg(*MUTED)}{num}  {icon}  {label}{RESET}")
    lines.append("")
    lines.append(center_pad(len(MENU_HINT)) + fg(90, 90, 115) + ITALIC + MENU_HINT + RESET)
    return lines


def menu(selected):
    """Меню со стрелками; выбранный пункт переливается. Возвращает (цифра, индекс)"""
    out(CLEAR)
    header()
    out("\n")
    if not INTERACTIVE:
        out("\n".join(menu_lines(selected, 0)) + "\n")
        out(SHOW_CURSOR)
        try:
            choice = input(fg(*MINT[0]) + "  Ваш выбор: " + RESET).strip()
        except EOFError:
            choice = "0"
        out(HIDE_CURSOR)
        return choice, selected

    lines = menu_lines(selected, 0)
    out("\n".join(lines) + "\n")
    phase = 0.0
    while True:
        key = poll_key(0.04)
        if key == "UP":
            selected = (selected - 1) % len(MENU)
        elif key == "DOWN":
            selected = (selected + 1) % len(MENU)
        elif key in ("ENTER", "SPACE", "RIGHT"):
            return MENU[selected][0], selected
        elif key in ("ESC", "q", "й"):
            return "0", selected
        elif key is not None and any(key == m[0] for m in MENU):
            idx = [m[0] for m in MENU].index(key)
            return key, idx
        phase += 0.02
        out(f"\033[{len(lines)}A")
        lines = menu_lines(selected, phase)
        out("\n".join(CLEAR_LINE + l for l in lines) + "\n")


def joke_screen(index, title=None, slow=False, with_loader=True):
    out(CLEAR + "\n")
    if with_loader:
        loader()
        out("\n")
    show_card(JOKES[index], title or f"Анекдот #{index + 1}", slow=slow)
    out("\n")
    laugh_meter()


def random_joke():
    joke_screen(next_random_joke())
    wait_key()


def pick_number():
    """Выбор номера анекдота: стрелки ←→ и превью первой строки"""
    if not INTERACTIVE:
        out(CLEAR)
        header()
        out(SHOW_CURSOR)
        try:
            raw = input(fg(*MINT[0]) + f"\n  Номер анекдота (1–{len(JOKES)}): " + RESET).strip()
        except EOFError:
            raw = ""
        out(HIDE_CURSOR)
        if raw.isdigit() and 1 <= int(raw) <= len(JOKES):
            return int(raw) - 1
        out(fg(255, 90, 110) + "\n  ❌ Такого номера нет!\n" + RESET)
        return None

    out(CLEAR)
    header()
    out("\n")
    sel = 0
    phase = 0.0
    hint = f"←→ — листать · 1–9, 0 (=10) — сразу · Enter — читать · Esc — назад"
    first = True
    while True:
        chips = []
        for i in range(len(JOKES)):
            n = f"{i + 1:>2}"
            if i == sel:
                chips.append(BOLD + fg(20, 20, 30) + "\033[48;2;%d;%d;%dm" % pick(NEON, wave(phase)) + f" {n} " + RESET)
            else:
                chips.append(fg(*MUTED) + f" {n} " + RESET)
        row_w = len(JOKES) * 4 + (len(JOKES) - 1)
        preview = JOKES[sel].split("\n")[0]
        maxp = card_width() - 6
        if len(preview) > maxp:
            preview = preview[:maxp - 1] + "…"
        block = [
            center_pad(28) + gradient("🔢 Выберите номер анекдота", SUNSET, bold=True),
            "",
            center_pad(row_w) + " ".join(chips),
            "",
            center_pad(len(preview) + 2) + fg(*TEXT) + ITALIC + "«" + preview + "»" + RESET,
            "",
            center_pad(len(hint)) + fg(90, 90, 115) + ITALIC + hint + RESET,
        ]
        if not first:
            out(f"\033[{len(block)}A")
        first = False
        out("\n".join(CLEAR_LINE + b for b in block) + "\n")

        key = poll_key(0.04)
        phase += 0.02
        if key in ("LEFT", "UP"):
            sel = (sel - 1) % len(JOKES)
        elif key in ("RIGHT", "DOWN"):
            sel = (sel + 1) % len(JOKES)
        elif key in ("ENTER", "SPACE"):
            return sel
        elif key == "ESC":
            return None
        elif key is not None and key.isdigit():
            return (int(key) - 1) % 10


def joke_by_number():
    index = pick_number()
    if index is not None:
        joke_screen(index, slow=True)
    wait_key()


def all_jokes():
    """Слайд-шоу всех анекдотов с навигацией"""
    i = 0
    while 0 <= i < len(JOKES):
        out(CLEAR + "\n")
        dots = " ".join((fg(*pick(NEON, k / (len(JOKES) - 1))) + "●") if k <= i else (fg(60, 60, 80) + "○")
                        for k in range(len(JOKES)))
        out(center_pad(len(JOKES) * 2 - 1) + dots + RESET + "\n\n")
        show_card(JOKES[i], f"Анекдот {i + 1} из {len(JOKES)}")
        out("\n")
        if not INTERACTIVE:
            i += 1
            continue
        key = wait_key("→ дальше · ← назад · Esc — в меню")
        if key == "ESC":
            return
        i += -1 if key in ("LEFT", "UP") else 1
        i = max(i, 0)
    if INTERACTIVE:
        out(center_pad(30) + gradient("🎉 Это были все анекдоты!", SUNSET, bold=True) + "\n\n")
        wait_key()


def goodbye(interrupted=False):
    global _skip
    _skip = False
    out(CLEAR)
    out("\n")
    if term_width() >= LOGO_W + 2:
        draw_logo()
    text = "Прервано. До встречи!" if interrupted else "До встречи! Пусть ваш код будет без багов!"
    out("\n" + center_pad(len(text) + 3))
    for i, ch in enumerate(text):
        out(BOLD + fg(*pick(SUNSET, i / (len(text) - 1))) + ch)
        if ANIMATE:
            time.sleep(0.03)
    out(RESET + " 🐛\n")
    if ANIMATE and term_width() >= LOGO_W + 2:
        # логотип переливается и рассыпается
        frames = 50
        for f in range(frames + 1):
            fade = 1 - f / frames
            lines = logo_lines(phase=f / 30, shine=f / frames * (LOGO_W + 20) - 10)
            if fade < 0.5:
                glyph = "▓" if fade > 0.32 else ("▒" if fade > 0.16 else "░")
                lines = [l.replace("█", glyph) for l in lines]
            if f == frames:
                lines = [""] * len(LOGO)
            out(f"\033[{len(LOGO) + 2}A" + "\n".join(CLEAR_LINE + l for l in lines) + "\n\033[2B")
            time.sleep(0.03)
        # в конце логотип собирается обратно
        for k in range(0, LOGO_W + 6, 3):
            out(f"\033[{len(LOGO) + 2}A" + "\n".join(CLEAR_LINE + l for l in logo_lines(reveal=k, shine=k - 4))
                + "\n\033[2B")
            time.sleep(0.012)
    out("\n")


def main():
    """Основная функция программы"""
    setup_terminal()
    try:
        intro()
        if INTERACTIVE:
            pause(0.4)
        selected = 0
        while True:
            choice, selected = menu(selected)
            if choice == "1":
                random_joke()
            elif choice == "2":
                joke_by_number()
            elif choice == "3":
                all_jokes()
            elif choice == "0":
                goodbye()
                break
            else:
                out(fg(255, 90, 110) + "\n  ❌ Неверный выбор! Попробуйте снова.\n" + RESET)
                time.sleep(0.8 if ANIMATE else 0)
    except KeyboardInterrupt:
        goodbye(interrupted=True)
    finally:
        restore_terminal()


if __name__ == "__main__":
    main()
