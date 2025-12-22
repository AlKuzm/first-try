import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import math

# Настройка страницы
st.set_page_config(page_title="Pallet Calc 2025", layout="wide")

st.title("🚛 Калькулятор загрузки паллет")
st.sidebar.header("⚙️ Параметры загрузки")

# --- ВВОД ДАННЫХ В БОКОВОЙ ПАНЕЛИ ---
with st.sidebar:
    st.subheader("Прицеп")
    t_len = st.number_input("Длина прицепа (мм)", value=13600)
    t_wid = st.number_input("Ширина прицепа (мм)", value=2450)
    t_hgt = st.number_input("Высота прицепа (мм)", value=2600)
    t_load = st.number_input("Грузоподъемность (кг)", value=22000)
    
    st.subheader("Паллета")
    p_len = st.number_input("Длина паллеты (мм)", value=1200)
    p_wid = st.number_input("Ширина паллеты (мм)", value=800)
    p_hgt = st.number_input("Высота паллеты с грузом (мм)", value=1400)
    p_weight = st.number_input("Вес паллеты (кг)", value=500)
    
    st.subheader("Заказ")
    req_count = st.number_input("Сколько паллет нужно перевезти?", value=40)
    gap = st.number_input("Технологический зазор (мм)", value=20)

# --- ЛОГИКА РАСЧЕТА ---
# Вариант 1: Вдоль
cols1, rows1 = (t_len - gap) // p_len, (t_wid - gap) // p_wid
total1 = cols1 * rows1

# Вариант 2: Поперек
cols2, rows2 = (t_len - gap) // p_wid, (t_wid - gap) // p_len
total2 = cols2 * rows2

if total1 >= total2:
    num_x, num_y, p_x_dim, p_y_dim = cols1, rows1, p_len, p_wid
else:
    num_x, num_y, p_x_dim, p_y_dim = cols2, rows2, p_wid, p_len

layers = t_hgt // p_hgt
limit_space = int((num_x * num_y) * layers)
limit_weight = int(t_load // p_weight)
max_per_trip = min(limit_space, limit_weight)

trips = math.ceil(req_count / max_per_trip) if max_per_trip > 0 else 0
to_load_now = min(req_count, max_per_trip)

# Центровка
off_x = (t_len - (num_x * p_x_dim)) / 2
off_y = (t_wid - (num_y * p_y_dim)) / 2

# --- ИНТЕРФЕЙС И ВЫВОД ---
col1, col2, col3 = st.columns(3)
col1.metric("Влезет в 1 авто", f"{max_per_trip} шт")
col2.metric("Всего рейсов", f"{trips}")
col3.metric("Вес рейса", f"{to_load_now * p_weight} кг")

if max_per_trip < req_count:
    st.warning(f"⚠️ Внимание: вся партия не влезает. Показана схема для первого рейса ({to_load_now} шт).")

# --- ОТРИСОВКА (Matplotlib) ---
fig, axes = plt.subplots(1, 3, figsize=(15, 5))

def is_present(ix, iy, iz):
    idx = iz * (num_x * num_y) + ix * num_y + iy
    return idx < to_load_now

# Вид сверху
axes[0].set_title("Вид сверху")
axes[0].add_patch(Rectangle((0, 0), t_len, t_wid, color='none', ec='black', lw=2))
for ix in range(int(num_x)):
    for iy in range(int(num_y)):
        if is_present(ix, iy, 0):
            axes[0].add_patch(Rectangle((off_x + ix*p_x_dim, off_y + iy*p_y_dim), p_x_dim, p_y_dim, fc='#3498db', ec='black', alpha=0.7))
axes[0].set_xlim(-500, t_len + 500)
axes[0].set_ylim(-500, t_wid + 500)
axes[0].set_aspect('equal')

# Вид сбоку
axes[1].set_title("Вид сбоку")
axes[1].add_patch(Rectangle((0, 0), t_len, t_hgt, color='none', ec='black', lw=2))
for ix in range(int(num_x)):
    for iz in range(int(layers)):
        if is_present(ix, 0, iz):
            axes[1].add_patch(Rectangle((off_x + ix*p_x_dim, iz*p_hgt), p_x_dim, p_hgt, fc='#2ecc71', ec='black', alpha=0.7))
axes[1].set_xlim(-500, t_len + 500)
axes[1].set_ylim(0, t_hgt + 500)

# Вид сзади
axes[2].set_title("Вид сзади")
axes[2].add_patch(Rectangle((0, 0), t_wid, t_hgt, color='none', ec='black', lw=2))
for iy in range(int(num_y)):
    for iz in range(int(layers)):
        if is_present(0, iy, iz):
            axes[2].add_patch(Rectangle((off_y + iy*p_y_dim, iz*p_hgt), p_y_dim, p_hgt, fc='#e74c3c', ec='black', alpha=0.7))
axes[2].set_xlim(-200, t_wid + 200)
axes[2].set_ylim(0, t_hgt + 500)

st.pyplot(fig)

# Таблица данных
with st.expander("Посмотреть детализацию"):
    st.write(f"Эффективность объема: {(to_load_now * p_len * p_wid * p_hgt) / (t_len * t_wid * t_hgt) * 100:.1f}%")
    st.write(f"Свободное место по длине: {t_len - (num_x * p_x_dim)} мм")
    st.write(f"Свободное место по ширине: {t_wid - (num_y * p_y_dim)} мм")
