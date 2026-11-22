#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
make_assets.py  -  Tạo bộ ảnh SVG chủ đề "Phòng thí nghiệm x Game 8-bit"
cho Profile README trên GitHub.

* Chỉ dùng thư viện chuẩn của Python -> KHÔNG cần cài thêm gì.
* Workflow (.github/workflows/profile.yml) tự gọi file này mỗi lần chạy.
* Muốn đổi chữ / chỉ số / kỹ năng: sửa phần "CẤU HÌNH" ngay bên dưới,
  rồi commit. Workflow tự chạy lại và ảnh được cập nhật sau ~1 phút.
* Chạy thử trên máy:   python3 scripts/make_assets.py
"""
import html
import math
import os
import pathlib
import random
import re
import unicodedata

# ======================================================================
# 0) BẢNG MÀU (ít khi cần đổi)
# ======================================================================
PANEL = "#0b1020"
PANEL2 = "#121a3d"
BORDER = "#2a3560"
TEXT = "#c9d1d9"
MUTED = "#8b95b8"
DIM = "#46507a"
CYAN = "#00e5ff"
GREEN = "#39ff14"
PINK = "#ff3cac"
PURPLE = "#a78bfa"
ORANGE = "#ff9f1c"
YELLOW = "#ffd60a"
RED = "#ff4d6d"

FONT = "'SF Mono','Menlo','Consolas','DejaVu Sans Mono','Courier New',monospace"

# ======================================================================
# 1) CẤU HÌNH - SỬA Ở ĐÂY CHO RA "CHẤT" CỦA BẠN
# ======================================================================
CONFIG = {
    # Tên hiển thị trên banner / thẻ nhân vật. Để "" = dùng username GitHub.
    "name": "",
    # Ký hiệu "nguyên tố" trên thẻ nhân vật (1-2 chữ). Để "" = 2 chữ cái đầu của tên.
    "symbol": "",
    # Dòng chữ nhỏ dưới banner (viết thường, gõ thoải mái).
    "tagline": "Turning curiosity into reactions, and reactions into code.",
    # Dòng "gõ chữ" trên banner. Chữ pixel chỉ có A-Z, 0-9 và vài ký hiệu
    # (. , - : ! + > < / _ = ( ) ' ? & * %). Tiếng Việt có dấu sẽ tự bỏ dấu.
    "subtitle": "CHEMISTRY + CHEMICAL ENGINEERING",
    "rank": "NEWBIE ALCHEMIST",   # danh hiệu dưới thanh XP
    "level": 1,                   # cấp độ
    "xp": 0.30,                   # thanh XP, từ 0.0 đến 1.0
    # Các dòng thông tin trên thẻ nhân vật (tối đa 4 dòng)
    "info": [
        ("CLASS", "Aspiring Chemical Engineer"),
        ("MAJOR", "Chemistry / Chemical Engineering"),
        ("STATUS", "Learning in public"),
        ("QUEST", "Master reactions & code"),
    ],
    # Chỉ số kiểu game: (tên, điểm 0-10, màu). Tự chấm cho vui nhé!
    "attributes": [
        ("CHEMISTRY", 9, GREEN),
        ("CODING", 6, CYAN),
        ("MATH", 8, PURPLE),
        ("LAB SKILLS", 9, ORANGE),
        ("CURIOSITY", 10, PINK),
    ],
    "attributes_note": "(self-rated, for fun)",
}

# Cây kỹ năng: (ký hiệu, tên, trạng thái, màu, tiến độ 0-1 nếu đang học)
#   trạng thái: "unlocked" = đã có | "learning" = đang học | "locked" = chưa mở khoá
# Học được gì thì đổi "locked" -> "learning" -> "unlocked" là xong!
SKILLS_CODE = [
    ("Ht", "HTML", "unlocked", CYAN, 1.0),
    ("Cs", "CSS", "unlocked", CYAN, 1.0),
    ("Js", "JavaScript", "learning", CYAN, 0.35),
    ("Gt", "Git", "unlocked", PURPLE, 1.0),
    ("Gh", "GitHub", "unlocked", PURPLE, 1.0),
    ("Py", "Python", "unlocked", ORANGE, 0),
    ("Ml", "MATLAB", "locked", ORANGE, 0),
    ("Lx", "LaTeX", "locked", ORANGE, 0),
]
SKILLS_SCIENCE = [
    ("Gc", "Gen Chem", "learning", GREEN, 0.60),
    ("Ls", "Lab Safety", "unlocked", GREEN, 1.0),
    ("Oc", "Organic", "locked", GREEN, 0),
    ("Td", "Thermo", "locked", GREEN, 0),
    ("Re", "Reactor Eng", "locked", PINK, 0),
    ("Pd", "Proc Design", "locked", PINK, 0),
    ("Pc", "Proc Control", "locked", PINK, 0),
    ("Ap", "Aspen Plus", "locked", YELLOW, 0),
]

# Các phương trình chạy chữ ở đáy banner (đã cân bằng - dân hoá soi kỹ lắm đó!)
EQUATIONS = [
    ("2 H2 + O2 \u2192 2 H2O", ""),
    ("CH4 + 2 O2 \u2192 CO2 + 2 H2O", ""),
    ("N2 + 3 H2 \u2192 2 NH3", "Haber process"),
    ("NaOH + HCl \u2192 NaCl + H2O", ""),
    ("C6H12O6 + 6 O2 \u2192 6 CO2 + 6 H2O", "cellular respiration"),
    ("2 Na + 2 H2O \u2192 2 NaOH + H2", "careful!"),
]

# ======================================================================
# 2) CHỮ PIXEL 5x7 (kiểu máy game 8-bit) - không phụ thuộc font của máy
# ======================================================================
_F = {
    "A": "01110 10001 10001 11111 10001 10001 10001",
    "B": "11110 10001 10001 11110 10001 10001 11110",
    "C": "01110 10001 10000 10000 10000 10001 01110",
    "D": "11110 10001 10001 10001 10001 10001 11110",
    "E": "11111 10000 10000 11110 10000 10000 11111",
    "F": "11111 10000 10000 11110 10000 10000 10000",
    "G": "01110 10001 10000 10111 10001 10001 01111",
    "H": "10001 10001 10001 11111 10001 10001 10001",
    "I": "01110 00100 00100 00100 00100 00100 01110",
    "J": "00111 00010 00010 00010 00010 10010 01100",
    "K": "10001 10010 10100 11000 10100 10010 10001",
    "L": "10000 10000 10000 10000 10000 10000 11111",
    "M": "10001 11011 10101 10101 10001 10001 10001",
    "N": "10001 11001 10101 10011 10001 10001 10001",
    "O": "01110 10001 10001 10001 10001 10001 01110",
    "P": "11110 10001 10001 11110 10000 10000 10000",
    "Q": "01110 10001 10001 10001 10101 10010 01101",
    "R": "11110 10001 10001 11110 10100 10010 10001",
    "S": "01111 10000 10000 01110 00001 00001 11110",
    "T": "11111 00100 00100 00100 00100 00100 00100",
    "U": "10001 10001 10001 10001 10001 10001 01110",
    "V": "10001 10001 10001 10001 10001 01010 00100",
    "W": "10001 10001 10001 10101 10101 11011 10001",
    "X": "10001 10001 01010 00100 01010 10001 10001",
    "Y": "10001 10001 01010 00100 00100 00100 00100",
    "Z": "11111 00001 00010 00100 01000 10000 11111",
    "0": "01110 10001 10011 10101 11001 10001 01110",
    "1": "00100 01100 00100 00100 00100 00100 01110",
    "2": "01110 10001 00001 00010 00100 01000 11111",
    "3": "11110 00001 00001 01110 00001 00001 11110",
    "4": "00010 00110 01010 10010 11111 00010 00010",
    "5": "11111 10000 11110 00001 00001 10001 01110",
    "6": "00110 01000 10000 11110 10001 10001 01110",
    "7": "11111 00001 00010 00100 01000 01000 01000",
    "8": "01110 10001 10001 01110 10001 10001 01110",
    "9": "01110 10001 10001 01111 00001 00010 01100",
    " ": "00000 00000 00000 00000 00000 00000 00000",
    ".": "00000 00000 00000 00000 00000 01100 01100",
    ",": "00000 00000 00000 00000 01100 00100 01000",
    "-": "00000 00000 00000 11111 00000 00000 00000",
    ":": "00000 01100 01100 00000 01100 01100 00000",
    "!": "00100 00100 00100 00100 00100 00000 00100",
    "+": "00000 00100 00100 11111 00100 00100 00000",
    ">": "10000 01000 00100 00010 00100 01000 10000",
    "<": "00001 00010 00100 01000 00100 00010 00001",
    "/": "00001 00001 00010 00100 01000 10000 10000",
    "_": "00000 00000 00000 00000 00000 00000 11111",
    "=": "00000 00000 11111 00000 11111 00000 00000",
    "(": "00010 00100 01000 01000 01000 00100 00010",
    ")": "01000 00100 00010 00010 00010 00100 01000",
    "'": "00100 00100 01000 00000 00000 00000 00000",
    "?": "01110 10001 00001 00010 00100 00000 00100",
    "&": "01100 10010 10100 01000 10101 10010 01101",
    "*": "00000 10101 01110 11111 01110 10101 00000",
    "%": "11001 11010 00010 00100 01000 01011 10011",
    "[": "01110 01000 01000 01000 01000 01000 01110",
    "]": "01110 00010 00010 00010 00010 00010 01110",
}
FONT5X7 = {k: v.split() for k, v in _F.items()}


def ascii_up(s):
    """Bỏ dấu tiếng Việt + viết hoa, để chữ pixel không bị khuyết ký tự."""
    s = str(s).replace("\u0111", "d").replace("\u0110", "D")
    s = unicodedata.normalize("NFKD", s)
    return "".join(c for c in s if not unicodedata.combining(c)).upper()


def esc(s):
    return html.escape(str(s), quote=True)


def fnum(v):
    return ("%.2f" % v).rstrip("0").rstrip(".")


def px_width(text, px, spacing=1):
    n = len(text)
    return (n * (5 + spacing) - spacing) * px if n else 0


def px_char_path(ch, x, y, px):
    rows = FONT5X7.get(ch.upper(), FONT5X7[" "])
    d = []
    for r, bits in enumerate(rows):
        c = 0
        while c < 5:
            if bits[c] == "1":
                start = c
                while c < 5 and bits[c] == "1":
                    c += 1
                n = c - start
                d.append("M%s %sh%sv%sh-%sz" % (
                    fnum(x + start * px), fnum(y + r * px),
                    fnum(n * px), fnum(px), fnum(n * px)))
            else:
                c += 1
    return "".join(d)


def px_text(text, x, y, px, fill, spacing=1, extra="", delay=None, step=0.06):
    """Chữ pixel. Nếu có delay: từng chữ hiện dần như đang gõ phím."""
    cw = (5 + spacing) * px
    if delay is None:
        d = "".join(px_char_path(ch, x + i * cw, y, px) for i, ch in enumerate(text))
        return '<path d="%s" fill="%s" %s/>' % (d, fill, extra)
    parts = []
    for i, ch in enumerate(text):
        d = px_char_path(ch, x + i * cw, y, px)
        if not d:
            continue
        parts.append(
            '<path d="%s" fill="%s" opacity="0" %s>'
            '<set attributeName="opacity" to="1" begin="%.2fs"/></path>'
            % (d, fill, extra, delay + i * step))
    return "".join(parts)


# ======================================================================
# 3) CÁC KHỐI DÙNG CHUNG
# ======================================================================
GLOW = ('<filter id="glow" x="-30%" y="-30%" width="160%" height="160%">'
        '<feGaussianBlur stdDeviation="3.4" result="b"/>'
        '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')
GLOW2 = ('<filter id="glow2" x="-30%" y="-30%" width="160%" height="160%">'
         '<feGaussianBlur stdDeviation="1.6" result="b"/>'
         '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')
SCAN = ('<pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse">'
        '<rect width="4" height="1" fill="#000" opacity=".22"/></pattern>')


def svg_doc(w, h, defs, body, title, desc=""):
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" '
        'viewBox="0 0 %d %d" role="img" aria-label="%s">\n'
        '<title>%s</title><desc>%s</desc>\n<defs>%s</defs>\n'
        '<g font-family="%s">%s</g>\n</svg>\n'
        % (w, h, w, h, esc(title), esc(title), esc(desc), defs, FONT, body))


def hex_pattern(pid, s=18, stroke="#00e5ff", opacity=0.10):
    w = math.sqrt(3) * s
    h = 3 * s

    def hexpath(cx, cy):
        pts = []
        for k in range(6):
            a = math.radians(-90 + 60 * k)
            pts.append((cx + s * math.cos(a), cy + s * math.sin(a)))
        return "M" + "L".join("%.2f %.2f" % p for p in pts) + "Z"

    d = hexpath(w / 2, s) + hexpath(0, 2.5 * s) + hexpath(w, 2.5 * s)
    return ('<pattern id="%s" width="%.3f" height="%.3f" patternUnits="userSpaceOnUse">'
            '<path d="%s" fill="none" stroke="%s" stroke-opacity="%s" stroke-width="1"/></pattern>'
            % (pid, w, h, d, stroke, opacity))


def corners(w, h, color=CYAN, m=14, l=22):
    d = ("M%d %dV%dH%d M%d %dH%dV%d M%d %dV%dH%d M%d %dH%dV%d" % (
        m, m + l, m, m + l,
        w - m - l, m, w - m, m + l,
        w - m, h - m - l, h - m, w - m - l,
        m + l, h - m, m, h - m - l))
    return ('<path d="%s" fill="none" stroke="%s" stroke-width="2" '
            'stroke-opacity=".85" stroke-linecap="square"/>' % (d, color))


def stars(w, h, n=18, seed=11, bottom=60):
    rnd = random.Random(seed)
    out = []
    for _ in range(n):
        x = rnd.randint(16, w - 24)
        y = rnd.randint(16, h - bottom)
        s = rnd.choice([2, 2, 3])
        col = rnd.choice([CYAN, PINK, "#ffffff", YELLOW, GREEN])
        dur = rnd.uniform(1.8, 4.2)
        beg = rnd.uniform(0, 3)
        out.append(
            '<rect x="%d" y="%d" width="%d" height="%d" fill="%s" opacity=".15">'
            '<animate attributeName="opacity" values=".1;.95;.1" dur="%.1fs" '
            'begin="%.1fs" repeatCount="indefinite"/></rect>'
            % (x, y, s, s, col, dur, beg))
    return "".join(out)


def window_buttons(x=16, y=15):
    return "".join(
        '<rect x="%d" y="%d" width="9" height="9" fill="%s"/>' % (x + i * 14, y, c)
        for i, c in enumerate([PINK, YELLOW, GREEN]))


# ======================================================================
# 4) BANNER
# ======================================================================
FLASK_OUTLINE = "M-17 0 L-17 60 L-66 168 Q-72 186 -54 188 L54 188 Q72 186 66 168 L17 60 L17 0"


def flask_big():
    defs = (
        '<clipPath id="fl"><path d="%s Z"/></clipPath>'
        '<linearGradient id="liq" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="%s" stop-opacity=".95"/>'
        '<stop offset="1" stop-color="%s" stop-opacity=".85"/></linearGradient>'
        % (FLASK_OUTLINE, GREEN, CYAN))
    wave = "M-100 118 q20 -7 40 0 " + "t40 0 " * 7 + "V200 H-100 Z"
    bubbles = ""
    for x, r, beg, dur in [(-32, 3.5, 0.0, 3.2), (-8, 2.5, 0.9, 2.6), (16, 4, 0.3, 3.6),
                           (36, 3, 1.4, 2.9), (-46, 2.2, 1.9, 3.0), (2, 2, 2.2, 2.4)]:
        bubbles += (
            '<circle cx="%d" cy="182" r="%s" fill="#eafff2" fill-opacity=".85">'
            '<animate attributeName="cy" values="182;124" dur="%ss" begin="%ss" repeatCount="indefinite"/>'
            '<animate attributeName="opacity" values="0;.9;0" dur="%ss" begin="%ss" repeatCount="indefinite"/>'
            '</circle>' % (x, r, dur, beg, dur, beg))
    puffs = ""
    for x, beg, dur in [(-3, 0, 3.4), (6, 1.2, 3.0), (-8, 2.0, 3.8)]:
        puffs += (
            '<circle cx="%d" cy="-8" r="2" fill="none" stroke="#fff" stroke-opacity=".6">'
            '<animate attributeName="cy" values="-8;-56" dur="%ss" begin="%ss" repeatCount="indefinite"/>'
            '<animate attributeName="r" values="2;7" dur="%ss" begin="%ss" repeatCount="indefinite"/>'
            '<animate attributeName="opacity" values=".7;0" dur="%ss" begin="%ss" repeatCount="indefinite"/>'
            '</circle>' % (x, dur, beg, dur, beg, dur, beg))
    body = (
        '<ellipse cx="0" cy="190" rx="86" ry="9" fill="%s" opacity=".25" filter="url(#glow2)"/>'
        '<g clip-path="url(#fl)">'
        '<g><animateTransform attributeName="transform" type="translate" from="0 0" to="-80 0" '
        'dur="2.6s" repeatCount="indefinite"/>'
        '<path d="%s" fill="url(#liq)" opacity=".92"/></g>%s</g>'
        '<path d="%s" fill="#fff" fill-opacity=".05" stroke="#fff" stroke-opacity=".7" '
        'stroke-width="3" stroke-linejoin="round"/>'
        '<rect x="-23" y="-9" width="46" height="9" rx="3" fill="#fff" fill-opacity=".12" '
        'stroke="#fff" stroke-opacity=".75" stroke-width="2.5"/>'
        '<path d="M-58 160 L-30 100 M-9 8 L-9 52" stroke="#fff" stroke-opacity=".35" '
        'stroke-width="3.5" stroke-linecap="round" fill="none"/>%s'
        % (GREEN, wave, bubbles, FLASK_OUTLINE, puffs))
    return defs, body


def benzene_backdrop(cx, cy, r):
    verts = [(cx + r * math.cos(math.radians(60 * k)), cy + r * math.sin(math.radians(60 * k)))
             for k in range(6)]
    poly = "M" + "L".join("%.1f %.1f" % p for p in verts) + "Z"
    r2 = r * 0.78
    inner = [(cx + r2 * math.cos(math.radians(60 * k)), cy + r2 * math.sin(math.radians(60 * k)))
             for k in range(6)]
    dbl = ""
    for k in (0, 2, 4):
        (x1, y1), (x2, y2) = inner[k], inner[(k + 1) % 6]
        a = (x1 + (x2 - x1) * 0.14, y1 + (y2 - y1) * 0.14)
        b = (x1 + (x2 - x1) * 0.86, y1 + (y2 - y1) * 0.86)
        dbl += "M%.1f %.1fL%.1f %.1f" % (a[0], a[1], b[0], b[1])
    return (
        '<g opacity=".9"><animateTransform attributeName="transform" type="rotate" '
        'from="0 %d %d" to="360 %d %d" dur="90s" repeatCount="indefinite"/>'
        '<path d="%s" fill="none" stroke="%s" stroke-opacity=".20" stroke-width="3" stroke-linejoin="round"/>'
        '<path d="%s" fill="none" stroke="%s" stroke-opacity=".16" stroke-width="3" stroke-linecap="round"/></g>'
        % (cx, cy, cx, cy, poly, CYAN, dbl, PINK))


def water_molecule(x, y):
    return (
        '<g transform="translate(%d,%d)"><g>'
        '<animateTransform attributeName="transform" type="translate" values="0 0;0 -7;0 0" '
        'dur="4.5s" repeatCount="indefinite"/>'
        '<path d="M0 0L-15 12M0 0L15 12" stroke="#9fb3ff" stroke-width="2.5" stroke-linecap="round"/>'
        '<circle cx="-15" cy="12" r="5.5" fill="#eaf1ff"/><circle cx="15" cy="12" r="5.5" fill="#eaf1ff"/>'
        '<circle cx="0" cy="0" r="9" fill="%s"/>'
        '<circle cx="-3" cy="-3" r="2.5" fill="#fff" fill-opacity=".6"/></g></g>' % (x, y, RED))


def eq_runs(eq, note=""):
    runs = []
    for tok in eq.split(" "):
        if tok == "\u2192":
            runs.append(("\u2192", False, GREEN))
        elif tok == "+":
            runs.append(("+", False, MUTED))
        elif tok.isdigit():
            runs.append((tok, False, YELLOW))
        else:
            for part in re.findall(r"[A-Za-z()]+|\d+", tok):
                runs.append((part, part.isdigit(), TEXT))
        runs.append((" ", False, TEXT))
    if note:
        runs.append(("(%s)" % note, False, MUTED))
        runs.append((" ", False, TEXT))
    return runs


def runs_to_tspans(runs):
    out, lowered = [], False
    for text, sub, color in runs:
        t = esc(text)
        if sub:
            out.append('<tspan fill="%s" dy="3" font-size="9">%s</tspan>' % (color, t))
            lowered = True
        elif lowered:
            out.append('<tspan fill="%s" dy="-3">%s</tspan>' % (color, t))
            lowered = False
        else:
            out.append('<tspan fill="%s">%s</tspan>' % (color, t))
    return "".join(out)


def ticker(w, y):
    runs, width = [], 0.0
    for eq, note in EQUATIONS:
        r = eq_runs(eq, note)
        runs += r + [("\u2022", False, PINK), ("   ", False, TEXT)]
    for text, sub, _ in runs:
        width += len(text) * (5.6 if sub else 7.9)
    dur = (w + width) / 55.0
    return (
        '<g><animateTransform attributeName="transform" type="translate" from="%d 0" to="-%d 0" '
        'dur="%.1fs" repeatCount="indefinite"/>'
        '<text x="0" y="%d" font-size="13" xml:space="preserve">%s</text></g>'
        % (w, int(width), dur, y, runs_to_tspans(runs)))


def make_banner(user):
    W, H = 900, 300
    name = ascii_up(CONFIG["name"] or user)
    sub = ascii_up(CONFIG["subtitle"])
    px = 10
    while px > 2 and px_width(name, px) > 590:
        px -= 1
    x0 = 48
    title_y = 80
    sub_y = title_y + 7 * px + 24
    tag_y = sub_y + 21 + 32

    flask_defs, flask_body = flask_big()
    defs = (
        GLOW + GLOW2 + SCAN + hex_pattern("hex") + flask_defs +
        '<clipPath id="bn"><rect width="%d" height="%d" rx="20"/></clipPath>'
        '<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">'
        '<stop offset="0" stop-color="#060a18"/><stop offset=".55" stop-color="#0e1233"/>'
        '<stop offset="1" stop-color="#1b0f3e"/></linearGradient>'
        '<radialGradient id="gl" cx=".14" cy=".35" r=".55"><stop offset="0" stop-color="%s" stop-opacity=".22"/>'
        '<stop offset="1" stop-color="%s" stop-opacity="0"/></radialGradient>'
        '<radialGradient id="gr" cx=".88" cy=".5" r=".5"><stop offset="0" stop-color="%s" stop-opacity=".25"/>'
        '<stop offset="1" stop-color="%s" stop-opacity="0"/></radialGradient>'
        '<radialGradient id="vig" cx=".5" cy=".5" r=".75"><stop offset=".6" stop-color="#000" stop-opacity="0"/>'
        '<stop offset="1" stop-color="#000" stop-opacity=".55"/></radialGradient>'
        % (W, H, PINK, PINK, CYAN, CYAN))

    # chữ "gõ phím": thanh con trỏ chạy theo từng ký tự
    cw = 6 * 3
    n = len(sub)
    t0, step = 1.3, 0.05
    xs = ";".join(str(x0 + i * cw) for i in range(n + 1))
    kt = ";".join("%.4f" % (i / n) for i in range(n + 1)) if n else "0;1"
    cursor = (
        '<rect x="%d" y="%d" width="12" height="21" fill="%s">'
        '<animate attributeName="x" values="%s" keyTimes="%s" calcMode="discrete" '
        'dur="%.2fs" begin="%.2fs" fill="freeze"/>'
        '<animate attributeName="opacity" values="1;0;1" dur="0.9s" repeatCount="indefinite"/></rect>'
        % (x0, sub_y, GREEN, xs, kt, n * step, t0))

    body = (
        '<g clip-path="url(#bn)">'
        '<rect width="%d" height="%d" fill="url(#bg)"/>'
        '<rect width="%d" height="%d" fill="url(#gl)"/><rect width="%d" height="%d" fill="url(#gr)"/>'
        '<rect width="%d" height="%d" fill="url(#hex)"/>'
        % (W, H, W, H, W, H, W, H)
        + benzene_backdrop(792, 150, 118)
        + stars(W, H)
        + water_molecule(668, 58)
        + '<g transform="translate(792,52)">%s</g>' % flask_body
        # nhãn PLAYER 1 + READY!
        + px_text("PLAYER 1", x0, 36, 3, YELLOW)
        + '<g>%s<animate attributeName="opacity" values="1;1;0;0;1" keyTimes="0;.5;.51;.99;1" '
          'dur="1.2s" repeatCount="indefinite"/></g>'
          % px_text("READY!", x0 + px_width("PLAYER 1", 3) + 26, 36, 3, GREEN)
        # tên: bóng hồng + chữ cyan phát sáng
        + px_text(name, x0 + 5, title_y + 5, px, PINK, delay=0.2, step=0.07)
        + px_text(name, x0, title_y, px, CYAN, delay=0.2, step=0.07, extra='filter="url(#glow)"')
        # dòng phụ gõ chữ
        + px_text(sub, x0, sub_y, 3, GREEN, delay=t0, step=step)
        + cursor
        + '<text x="%d" y="%d" font-size="15" fill="%s" opacity="0">%s'
          '<animate attributeName="opacity" from="0" to="1" dur=".8s" begin="3.2s" fill="freeze"/></text>'
          % (x0, tag_y, MUTED, esc(CONFIG["tagline"]))
        # dải chạy phương trình hoá học
        + '<rect y="%d" width="%d" height="%d" fill="#000" opacity=".38"/>' % (H - 38, W, 38)
        + '<path d="M0 %d H%d" stroke="%s" stroke-opacity=".35"/>' % (H - 38, W, CYAN)
        + '<g clip-path="url(#tk)">%s</g>' % ticker(W, H - 14)
        + '<rect width="%d" height="%d" fill="url(#scan)"/>' % (W, H)
        + '<rect width="%d" height="%d" fill="url(#vig)"/>' % (W, H)
        + corners(W, H)
        + '</g>'
        + '<rect x=".5" y=".5" width="%d" height="%d" rx="20" fill="none" stroke="%s"/>' % (W - 1, H - 1, BORDER))
    defs += '<clipPath id="tk"><rect y="%d" width="%d" height="38"/></clipPath>' % (H - 38, W)
    return svg_doc(W, H, defs, body, "%s - Chemistry x Game profile banner" % name,
                   "Animated pixel-art banner with a bubbling flask and scrolling chemical equations")


# ======================================================================
# 5) THẺ NHÂN VẬT (CHARACTER SHEET)
# ======================================================================
def icon_slot(x, y, inner, color):
    return ('<g transform="translate(%d,%d)"><rect width="40" height="40" rx="8" fill="#0f1634" '
            'stroke="%s" stroke-opacity=".65"/>%s</g>' % (x, y, color, inner))


def icon_flask():
    return ('<path d="M15 9V17L8 31Q7 34 10 34H30Q33 34 32 31L25 17V9" fill="none" stroke="#dfe7ff" '
            'stroke-width="1.8" stroke-linejoin="round"/>'
            '<rect x="13" y="6.5" width="14" height="3" rx="1.5" fill="#dfe7ff"/>'
            '<path d="M11 26L29 26L31.4 31Q32 34 30 34H10Q8 34 8.6 31Z" fill="%s" fill-opacity=".9"/>'
            '<circle cx="18" cy="29" r="1.4" fill="#fff"><animate attributeName="cy" values="31;23" dur="2.2s" '
            'repeatCount="indefinite"/><animate attributeName="opacity" values="0;1;0" dur="2.2s" '
            'repeatCount="indefinite"/></circle>' % GREEN)


def icon_atom():
    ell = "".join(
        '<ellipse cx="20" cy="20" rx="14" ry="5.5" fill="none" stroke="%s" stroke-width="1.4" '
        'transform="rotate(%d 20 20)"/>' % (CYAN, a) for a in (0, 60, 120))
    return ('<g><animateTransform attributeName="transform" type="rotate" from="0 20 20" to="360 20 20" '
            'dur="14s" repeatCount="indefinite"/>%s<circle cx="20" cy="20" r="3" fill="%s"/></g>' % (ell, YELLOW))


def icon_benzene():
    pts = "".join("%s%.1f %.1f" % ("M" if k == 0 else "L", 20 + 12 * math.cos(math.radians(30 + 60 * k)),
                                   20 + 12 * math.sin(math.radians(30 + 60 * k))) for k in range(6))
    return ('<path d="%sZ" fill="none" stroke="%s" stroke-width="2" stroke-linejoin="round"/>'
            '<circle cx="20" cy="20" r="6.2" fill="none" stroke="%s" stroke-opacity=".85" stroke-width="1.6"/>'
            % (pts, PURPLE, PURPLE))


def icon_code():
    return ('<text x="20" y="25.5" font-size="15" font-weight="700" text-anchor="middle" fill="%s">'
            '&lt;/&gt;</text>' % GREEN)


def make_player_card(user):
    W, H = 900, 300
    name = CONFIG["name"] or user
    NAME = ascii_up(name)
    sym = CONFIG["symbol"] or re.sub(r"[^A-Z0-9]", "", ascii_up(name))[:2].capitalize() or "Xx"
    sym = sym[:1].upper() + sym[1:2].lower()
    defs = GLOW + GLOW2 + SCAN + hex_pattern("hex", s=16, opacity=0.07)

    parts = []
    parts.append('<rect x=".5" y=".5" width="%d" height="%d" rx="14" fill="%s" stroke="%s"/>'
                 % (W - 1, H - 1, PANEL, BORDER))
    parts.append('<rect x="1" y="1" width="%d" height="%d" rx="13" fill="url(#hex)"/>' % (W - 2, H - 2))
    parts.append('<path d="M1 14Q1 1 14 1H%dQ%d 1 %d 14V40H1Z" fill="%s"/>' % (W - 14, W - 1, W - 1, PANEL2))
    parts.append(window_buttons())
    parts.append(px_text("CHARACTER SHEET", 66, 10, 3, CYAN, extra='filter="url(#glow2)"'))
    lv = "LV.%d" % CONFIG["level"]
    parts.append(px_text(lv, W - 24 - px_width(lv, 3), 10, 3, YELLOW))

    # --- thẻ "nguyên tố" ---
    tx, ty = 36, 62
    parts.append('<rect x="%d" y="%d" width="150" height="150" rx="12" fill="#0e1430"/>' % (tx, ty))
    parts.append('<rect x="%d" y="%d" width="150" height="150" rx="12" fill="%s" fill-opacity=".14"/>' % (tx, ty, GREEN))
    parts.append('<rect x="%d" y="%d" width="150" height="150" rx="12" fill="none" stroke="%s" stroke-width="2.5" '
                 'filter="url(#glow2)"><animate attributeName="opacity" values=".55;1;.55" dur="3s" '
                 'repeatCount="indefinite"/></rect>' % (tx, ty, GREEN))
    parts.append('<text x="%d" y="%d" font-size="13" fill="%s">01</text>' % (tx + 12, ty + 22, MUTED))
    parts.append('<g><animateTransform attributeName="transform" type="translate" values="0 0;0 -4;0 0" '
                 'dur="3.6s" repeatCount="indefinite"/>'
                 '<text x="%d" y="%d" font-size="68" font-weight="700" text-anchor="middle" fill="%s" '
                 'filter="url(#glow)">%s</text></g>' % (tx + 75, ty + 98, CYAN, esc(sym)))
    parts.append('<text x="%d" y="%d" font-size="12" font-weight="700" text-anchor="middle" fill="%s" '
                 'letter-spacing="1">%s</text>' % (tx + 75, ty + 130, TEXT, esc(NAME if len(NAME) <= 15 else NAME[:14] + "\u2026")))

    # --- thanh XP ---
    parts.append(px_text("XP", tx, 226, 2, MUTED))
    parts.append('<rect x="%d" y="225" width="122" height="12" rx="2" fill="#1a2350" stroke="%s"/>' % (tx + 28, BORDER))
    fillw = max(2, int(122 * min(1.0, max(0.0, CONFIG["xp"]))))
    parts.append('<rect x="%d" y="225" width="0" height="12" rx="2" fill="%s"><animate attributeName="width" '
                 'from="0" to="%d" dur="1.4s" begin=".8s" fill="freeze"/></rect>' % (tx + 28, GREEN, fillw))
    parts.append('<text x="%d" y="262" font-size="11" font-weight="700" fill="%s" letter-spacing="1">LV.%d  %s</text>'
                 % (tx, YELLOW, CONFIG["level"], esc(CONFIG["rank"])))

    # --- cột thông tin ---
    ix = 218
    parts.append(px_text(NAME, ix + 3, 63, 5, PINK) if px_width(NAME, 5) <= 380 else "")
    parts.append(px_text(NAME, ix, 60, 5, "#ffffff", extra='filter="url(#glow2)"') if px_width(NAME, 5) <= 380 else
                 '<text x="%d" y="94" font-size="%d" font-weight="700" fill="#fff">%s</text>'
                 % (ix, max(11, min(26, int(380 / (len(NAME) * 0.62)))), esc(NAME)))
    y = 130
    for label, value in CONFIG["info"][:4]:
        parts.append('<rect x="%d" y="%d" width="7" height="7" fill="%s" transform="rotate(45 %d %d)"/>'
                     % (ix, y - 10, GREEN, ix + 3, y - 6))
        parts.append('<text x="%d" y="%d" font-size="12" fill="%s" letter-spacing="1">%s</text>'
                     % (ix + 16, y, MUTED, esc(label)))
        parts.append('<text x="%d" y="%d" font-size="14" fill="%s">%s</text>' % (ix + 92, y, TEXT, esc(value)))
        y += 27
    parts.append('<text x="%d" y="%d" font-size="12" fill="%s" letter-spacing="1">ITEMS</text>' % (ix, 252, MUTED))
    for i, (inner, col) in enumerate([(icon_flask(), GREEN), (icon_atom(), CYAN),
                                      (icon_benzene(), PURPLE), (icon_code(), GREEN)]):
        parts.append(icon_slot(ix + 92 + i * 50, 228, inner, col))

    # --- cột chỉ số ---
    ax = 626
    parts.append(px_text("ATTRIBUTES", ax, 58, 2, MUTED))
    for r, (label, val, col) in enumerate(CONFIG["attributes"][:5]):
        by = 98 + r * 34
        parts.append('<text x="%d" y="%d" font-size="12" fill="%s">%s</text>' % (ax, by, TEXT, esc(label)))
        for s in range(10):
            sx = ax + 86 + s * 14
            parts.append('<rect x="%d" y="%d" width="11" height="14" fill="#1a2350"/>' % (sx, by - 12))
            if s < val:
                parts.append('<rect x="%d" y="%d" width="11" height="14" fill="%s" opacity="0">'
                             '<set attributeName="opacity" to="1" begin="%.2fs"/></rect>'
                             % (sx, by - 12, col, 0.9 + r * 0.18 + s * 0.05))
        parts.append('<text x="%d" y="%d" font-size="12" font-weight="700" fill="%s">%02d</text>'
                     % (ax + 86 + 10 * 14 + 4, by, col, val))
    if CONFIG.get("attributes_note"):
        parts.append('<text x="%d" y="%d" font-size="10" fill="%s">%s</text>'
                     % (ax, 272, DIM, esc(CONFIG["attributes_note"])))

    parts.append('<rect width="%d" height="%d" rx="14" fill="url(#scan)" opacity=".7"/>' % (W, H))
    return svg_doc(W, H, defs, "".join(parts), "%s - character sheet" % NAME,
                   "RPG-style character sheet with level, XP bar and attribute bars")


# ======================================================================
# 6) CÂY KỸ NĂNG = BẢNG TUẦN HOÀN KỸ NĂNG
# ======================================================================
def skill_tile(x, y, idx, sym, name, status, color, prog, delay):
    w, h = 92, 104
    cx = x + w / 2
    g = ['<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur=".45s" begin="%.2fs" fill="freeze"/>' % delay]
    if status == "locked":
        g.append('<rect x="%d" y="%d" width="%d" height="%d" rx="10" fill="#0e1430" stroke="%s" '
                 'stroke-width="1.5" stroke-dasharray="5 4"/>' % (x, y, w, h, DIM))
        sym_col, name_col, num_col = DIM, "#5d6a99", "#3b456e"
        g.append('<g transform="translate(%d,%d)"><rect y="6" width="12" height="9" rx="2" fill="#5d6a99"/>'
                 '<path d="M2.5 6V4.2a3.5 3.5 0 0 1 7 0V6" fill="none" stroke="#5d6a99" stroke-width="1.8"/></g>'
                 % (x + w - 22, y + 8))
        glow = ""
    else:
        a = ".20" if status == "unlocked" else ".10"
        g.append('<rect x="%d" y="%d" width="%d" height="%d" rx="10" fill="#0e1430"/>' % (x, y, w, h))
        g.append('<rect x="%d" y="%d" width="%d" height="%d" rx="10" fill="%s" fill-opacity="%s"/>' % (x, y, w, h, color, a))
        pulse = ('<animate attributeName="opacity" values=".35;.95;.35" dur="3s" begin="%.2fs" '
                 'repeatCount="indefinite"/>' % delay) if status == "unlocked" else ""
        g.append('<rect x="%d" y="%d" width="%d" height="%d" rx="10" fill="none" stroke="%s" stroke-width="2.5" '
                 'filter="url(#glow2)" opacity="%s">%s</rect>'
                 % (x, y, w, h, color, ".9" if status == "unlocked" else ".45", pulse))
        g.append('<rect x="%d" y="%d" width="%d" height="%d" rx="10" fill="none" stroke="%s" stroke-width="1.5"/>'
                 % (x, y, w, h, color))
        sym_col, name_col, num_col = color, TEXT, MUTED
        glow = ' filter="url(#glow2)"'
        if status == "unlocked":
            g.append('<path d="M%d %dl3.6 3.8l7-8.2" fill="none" stroke="%s" stroke-width="2.2" '
                     'stroke-linecap="round" stroke-linejoin="round"/>' % (x + w - 22, y + 15, color))
        else:
            g.append('<g transform="translate(%d,%d)"><circle r="5.5" fill="none" stroke="%s" stroke-width="1.6"/>'
                     '<path d="M0 -5.5A5.5 5.5 0 0 1 0 5.5Z" fill="%s"/></g>' % (x + w - 16, y + 14, color, color))
    g.append('<text x="%d" y="%d" font-size="11" fill="%s">%02d</text>' % (x + 9, y + 17, num_col, idx))
    g.append('<text x="%s" y="%d" font-size="34" font-weight="700" text-anchor="middle" fill="%s"%s>%s</text>'
             % (fnum(cx), y + 63, sym_col, glow, esc(sym)))
    g.append('<text x="%s" y="%d" font-size="11" text-anchor="middle" fill="%s">%s</text>'
             % (fnum(cx), y + 85, name_col, esc(name)))
    if status == "learning":
        bx, by, bw = x + 14, y + h - 12, w - 28
        g.append('<rect x="%d" y="%d" width="%d" height="5" rx="1" fill="#1a2350"/>' % (bx, by, bw))
        g.append('<rect x="%d" y="%d" width="%d" height="5" rx="1" fill="%s"><animate attributeName="opacity" '
                 'values=".6;1;.6" dur="1.6s" repeatCount="indefinite"/></rect>'
                 % (bx, by, max(3, int(bw * prog)), color))
    g.append("</g>")
    return "".join(g)


def make_skills():
    W, H = 900, 384
    defs = GLOW + GLOW2 + SCAN + hex_pattern("hex", s=16, opacity=0.07)
    parts = [
        '<rect x=".5" y=".5" width="%d" height="%d" rx="14" fill="%s" stroke="%s"/>' % (W - 1, H - 1, PANEL, BORDER),
        '<rect x="1" y="1" width="%d" height="%d" rx="13" fill="url(#hex)"/>' % (W - 2, H - 2),
        '<path d="M1 14Q1 1 14 1H%dQ%d 1 %d 14V40H1Z" fill="%s"/>' % (W - 14, W - 1, W - 1, PANEL2),
        window_buttons(),
        px_text("SKILL TREE", 66, 10, 3, CYAN, extra='filter="url(#glow2)"'),
        '<text x="%d" y="26" font-size="12" text-anchor="end" fill="%s">periodic table of skills - '
        'unlock new elements as you level up</text>' % (W - 24, MUTED),
    ]
    idx, delay = 1, 0.15
    rows = [("CODE", CYAN, SKILLS_CODE, 78), ("SCIENCE", GREEN, SKILLS_SCIENCE, 222)]
    for label, col, skills, ty in rows:
        lw = px_width(label, 2)
        parts.append(px_text(label, 40, ty - 22, 2, col))
        parts.append('<path d="M%d %dH%d" stroke="%s" stroke-opacity=".35" stroke-width="2" '
                     'stroke-dasharray="2 6"/>' % (40 + lw + 12, ty - 15, W - 40, col))
        for i, (sym, nm, st, c, pr) in enumerate(skills[:8]):
            parts.append(skill_tile(40 + i * 104, ty, idx, sym, nm, st, c, pr, delay))
            idx += 1
            delay += 0.07
    ly = 352
    parts.append('<rect x="40" y="%d" width="13" height="13" rx="3" fill="none" stroke="%s" stroke-width="1.6"/>'
                 '<path d="M43 %dl2.6 2.8l4.6-5.4" fill="none" stroke="%s" stroke-width="1.8" stroke-linecap="round"/>'
                 '<text x="60" y="%d" font-size="11" fill="%s">UNLOCKED</text>' % (ly - 10, CYAN, ly - 3, CYAN, ly, MUTED))
    parts.append('<g transform="translate(166,%d)"><circle r="6" fill="none" stroke="%s" stroke-width="1.6"/>'
                 '<path d="M0 -6A6 6 0 0 1 0 6Z" fill="%s"/></g>'
                 '<text x="180" y="%d" font-size="11" fill="%s">LEARNING</text>' % (ly - 4, CYAN, CYAN, ly, MUTED))
    parts.append('<rect x="284" y="%d" width="13" height="13" rx="3" fill="none" stroke="%s" stroke-width="1.5" '
                 'stroke-dasharray="3 2"/><text x="304" y="%d" font-size="11" fill="%s">LOCKED</text>'
                 % (ly - 10, DIM, ly, MUTED))
    parts.append('<rect width="%d" height="%d" rx="14" fill="url(#scan)" opacity=".7"/>' % (W, H))
    return svg_doc(W, H, defs, "".join(parts), "Skill tree - periodic table of skills",
                   "Grid of element-style tiles showing unlocked, learning and locked skills")


# ======================================================================
# 7) TIÊU ĐỀ MỤC + ĐƯỜNG KẺ CÔNG THỨC CẤU TẠO
# ======================================================================
def make_header(label, color):
    W, H = 900, 46
    t = ascii_up(label)
    px = 3
    tw = px_width(t, px)
    x0 = 46
    body = (
        '<rect x=".5" y=".5" width="%d" height="%d" rx="10" fill="%s" stroke="%s"/>' % (W - 1, H - 1, PANEL, BORDER)
        + '<rect x="1" y="1" width="6" height="%d" rx="3" fill="%s"/>' % (H - 2, color)
        + '<path d="%s" fill="%s"><animate attributeName="opacity" values="1;0;1" dur="1.1s" '
          'repeatCount="indefinite"/></path>' % (px_char_path(">", 20, 12, px), color)
        + px_text(t, x0, 12, px, color, extra='filter="url(#glow2)"')
        + '<path d="M%d 23H%d" stroke="%s" stroke-opacity=".45" stroke-width="2" stroke-dasharray="2 6"/>'
          % (x0 + tw + 16, W - 40, color)
        + '<rect x="%d" y="18" width="10" height="10" fill="%s" transform="rotate(45 %d 23)"/>'
          % (W - 32, color, W - 27)
        + '<rect width="%d" height="%d" rx="10" fill="url(#scan)" opacity=".8"/>' % (W, H))
    return svg_doc(W, H, GLOW + GLOW2 + SCAN, body, label, "Section header")


def make_divider():
    W, H = 900, 40
    n, step = 34, 24
    pts = [(52 + i * step, 26 if i % 2 == 0 else 14) for i in range(n + 1)]
    d = "M" + "L".join("%d %d" % p for p in pts)
    dbl = ""
    for i in (3, 4, 11, 12, 19, 20, 27, 28):
        (x1, y1), (x2, y2) = pts[i], pts[i + 1]
        dbl += "M%d %dL%d %d" % (x1 + 2, y1 + 5, x2 + 2, y2 + 5)
    body = (
        '<rect x=".5" y="4.5" width="%d" height="31" rx="10" fill="%s" stroke="%s"/>' % (W - 1, PANEL, BORDER)
        + '<text x="14" y="30" font-size="13" fill="%s" xml:space="preserve">H'
        '<tspan dy="3" font-size="9">3</tspan><tspan dy="-3">C</tspan></text>' % MUTED
        + '<text x="%d" y="%d" font-size="13" fill="%s" font-weight="700">OH</text>'
          % (52 + n * step + 4, pts[-1][1] + 4, PINK)
        + '<path d="%s" fill="none" stroke="%s" stroke-opacity=".30" stroke-width="2" stroke-linejoin="round"/>' % (d, CYAN)
        + '<path d="%s" fill="none" stroke="%s" stroke-opacity=".30" stroke-width="2"/>' % (dbl, CYAN)
        + '<path d="%s" fill="none" stroke="%s" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" '
          'pathLength="1000" stroke-dasharray="55 945" filter="url(#glow2)">'
          '<animate attributeName="stroke-dashoffset" from="0" to="-1000" dur="5s" repeatCount="indefinite"/></path>'
          % (d, GREEN))
    return svg_doc(W, H, GLOW2, body, "divider", "Skeletal-formula style divider with a moving highlight")


# ======================================================================
# 8) CON RẮN: thêm nền tối để hợp giao diện game (cả khi GitHub để nền sáng)
# ======================================================================
def style_snake(src, dst, pad=18):
    p = pathlib.Path(src)
    if not p.exists():
        print("  (bỏ qua) chưa có %s" % src)
        return False
    s = p.read_text(encoding="utf-8")
    m = re.search(r"<svg\b[^>]*>", s)
    if not m:
        print("  (bỏ qua) %s không phải SVG hợp lệ" % src)
        return False
    tag = m.group(0)
    vb = re.search(r'viewBox="([^"]+)"', tag)
    if not vb:
        print("  (bỏ qua) %s không có viewBox" % src)
        return False
    x, y, w, h = [float(v) for v in vb.group(1).replace(",", " ").split()]
    nx, ny, nw, nh = x - pad, y - pad, w + 2 * pad, h + 2 * pad
    new_tag = tag.replace(vb.group(0), 'viewBox="%s %s %s %s"' % (fnum(nx), fnum(ny), fnum(nw), fnum(nh)))
    for attr, old, new in (("width", w, nw), ("height", h, nh)):
        am = re.search(r'\b%s="([\d.]+)"' % attr, new_tag)
        if am:
            new_tag = new_tag.replace(am.group(0), '%s="%s"' % (attr, fnum(float(am.group(1)) * new / old)))
    rect = ('<rect x="%s" y="%s" width="%s" height="%s" rx="16" fill="%s" stroke="%s"/>'
            % (fnum(nx), fnum(ny), fnum(nw), fnum(nh), PANEL, BORDER))
    out = s.replace(tag, new_tag + rect, 1)
    pathlib.Path(dst).write_text(out, encoding="utf-8")
    if os.path.abspath(src) != os.path.abspath(dst):
        p.unlink()
    return True


# ======================================================================
# 9) CHẠY
# ======================================================================
def write(path, content):
    pathlib.Path(path).write_text(content, encoding="utf-8")
    print("  + %-28s %6.1f KB" % (path, len(content.encode("utf-8")) / 1024))


def main():
    out = pathlib.Path(os.environ.get("PROFILE_OUT", "profile"))
    out.mkdir(parents=True, exist_ok=True)
    user = os.environ.get("PROFILE_USER") or os.environ.get("GITHUB_REPOSITORY_OWNER") or "player1"
    print("Tạo ảnh cho: %s -> %s/" % (user, out))
    write(out / "banner.svg", make_banner(user))
    write(out / "player-card.svg", make_player_card(user))
    write(out / "skills.svg", make_skills())
    write(out / "divider.svg", make_divider())
    for slug, label, col in [("stats", "LIVE STATS", GREEN), ("snake", "SNAKE.EXE", PINK),
                             ("quests", "QUEST LOG", YELLOW), ("levels", "FEATURED LEVELS", CYAN)]:
        write(out / ("h-%s.svg" % slug), make_header(label, col))
    if style_snake(out / "snake-raw.svg", out / "snake.svg"):
        print("  + snake.svg (đã thêm nền tối)")
    print("Xong!")


if __name__ == "__main__":
    main()
