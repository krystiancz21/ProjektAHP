from ttkbootstrap import Style
from tkinter import ttk, Menu, StringVar
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
import numpy as np
from tkinter import Canvas
import time
from itertools import combinations
import ahpy_swd as ahpy

frame3 = None

def get_variants_count(frame):
    mb = ttk.Menubutton(frame, text='Liczba wariantów', style='info.Outline.TMenubutton')
    menu = Menu(mb)  # create menu
    option_var = StringVar()  # add options
    for option in range(3, 11):
        menu.add_radiobutton(label=str(option), value=option, variable=option_var)

    mb['menu'] = menu  # associate menu with menubutton
    mb.grid(row=0, column=0, padx=5, pady=10)
    return option_var


def convertValue(val):
    if val > 80:
        return 1
    elif val > 60:
        return 3
    elif val > 40:
        return 5
    elif val > 20:
        return 7
    else:
        return 9


def get_criteria_count(frame):
    mb = ttk.Menubutton(frame, text='Liczba kryteriów', style='info.Outline.TMenubutton')
    menu = Menu(mb)  # create menu
    criteria_cnt = StringVar()  # add options
    for option in range(1, 9):
        menu.add_radiobutton(label=str(option), value=option, variable=criteria_cnt)

    mb['menu'] = menu  # associate menu with menubutton
    mb.grid(row=3, column=0, padx=5, pady=10)
    return criteria_cnt


def print_variants():
    selected_value_label.config(text="Warianty: " + ", ".join(variants))


def print_criteria():
    criteria_label.config(text="Kryteria: " + ", ".join(criteria))


def add_variant(max_size):
    if len(variants) < int(max_size.get()):
        variants.append(input_field.get())
        input_field.delete(0, 'end')
        print_variants()
        if len(variants) == int(max_size.get()):
            button.grid_remove()
            input_field.grid_remove()


def add_criteria(max_size):
    if len(criteria) < int(max_size.get()):
        criteria.append(input_criteria.get())
        input_criteria.delete(0, 'end')
        print_criteria()
        if len(criteria) == int(max_size.get()):
            button2.grid_remove()
            input_criteria.grid_remove()

def update_sliders(option_cnt, variant, criteria):
    comparison_data = {}
    slider_values = []

    for widget in scrollable_frame.winfo_children():
        widget.destroy()

    variants_count = int(option_cnt.get())
    sliders_count = int((variants_count * (variants_count - 1)) / 2)

    variant_combinations = list(combinations(variant, 2))

    for criterion in criteria:
        ttk.Label(scrollable_frame, text=f'Kryterium: {criterion}').pack()

        for i in range(sliders_count):
            frame = ttk.Frame(scrollable_frame)
            frame.pack(side="top", fill="x", padx=5, pady=5)

            label = ttk.Label(frame, text=f'{variant_combinations[i][0]} - {variant_combinations[i][1]}')
            label.pack(side="top")

            slider = ttk.Scale(frame, from_=0, to=100, orient='horizontal', value=50, length=200)
            slider.pack(side="left")

            slider_values.append(slider)

            value_label = ttk.Label(frame, text='')
            value_label.pack(side="left")

            def make_scalerSlider(slider, label):
                def scalerSlider(e):
                    label.config(text=f'{int(slider.get())}')

                return scalerSlider

            slider.config(command=make_scalerSlider(slider, value_label))

    button = ttk.Button(scrollable_frame, text="Oblicz",
                        command=lambda: submit(variant_combinations, comparison_data, slider_values, len(criteria)))
    button.pack()

def submit(variant_combinations, comparison_data, slider_values, criteria_count):
    global frame3

    for widget in frame3.winfo_children():
        widget.destroy()

    variants_count = len(variant_combinations)

    for j in range(criteria_count):
        matrix = [[1] * variants_count for _ in range(variants_count)]
        idx1 = 0
        idx2 = 0
        builderVar = variants_count - 1
        matrixLvl = builderVar - 1

        for i in range(variants_count):
            value = slider_values[j*variants_count + i].get()
            if value < 0:
                value = 1 / -value
            elif value == 0:
                value = 1
            value = convertValue(value)
            comparison_data[variant_combinations[i]] = value

            if i == builderVar:
                builderVar += matrixLvl
                matrixLvl -= 1
                idx1 += 1
                idx2 = idx1 + 1
            else:
                idx2 += 1

            matrix[idx1][idx2] = round(float(value), 2)
            matrix[idx2][idx1] = round(float(1 / value), 2)

        ahp = ahpy.Compare(name='AHP', comparisons=comparison_data, precision=3, random_index='saaty')

        # Dodaj etykiety z wynikami
        ttk.Label(frame3, text=f"Kryterium {j+1}").pack()
        ttk.Label(frame3, text="Wektor wag: " + str(ahp.target_weights)).pack()
        ttk.Label(frame3, text="CR: " + str(ahp.consistency_ratio)).pack()
        ttk.Label(frame3, text="CI: " + str(ahp.consistency_index.real)).pack()
        ttk.Label(frame3, text="Macierz wyborów:").pack()
        for row in matrix:
            ttk.Label(frame3, text=str(row)).pack()

    # Przełącz na kartę z wynikami
    notebook.select(frame3)

###################
style = Style(theme='superhero')
window = style.master
window.title("AHP Application")
window.geometry("500x400")

# Inicjalizacja listy przechowującej wartości suwaków
slider_values = []

# Utwórz notebook (kontener na karty)
notebook = ttk.Notebook(window)
notebook.pack(fill='both', expand=True)

# Utwórz pierwszą kartę
frame1 = ttk.Frame(notebook)
notebook.add(frame1, text='Inputs')

option_var = get_variants_count(frame1)
variants = []

criteria_cnt = get_criteria_count(frame1)
criteria = []

# add variants - input and button
input_field = ttk.Entry(frame1)
input_field.grid(row=1, column=0, padx=5, pady=10)
button = ttk.Button(frame1, text="Dodaj wariant", command=lambda: add_variant(option_var))
button.grid(row=1, column=1, padx=5, pady=10)

# add criteria - input and button
input_criteria = ttk.Entry(frame1)
input_criteria.grid(row=4, column=0, padx=5, pady=10)
button2 = ttk.Button(frame1, text="Dodaj kryterium", command=lambda: add_criteria(criteria_cnt))
button2.grid(row=4, column=1, padx=5, pady=10)

# Utwórz etykietę do wyświetlania wybranych wariantów
selected_value_label = ttk.Label(frame1, text="")
selected_value_label.grid(row=2, column=0, columnspan=2, padx=5, pady=10)

criteria_label = ttk.Label(frame1, text="")
criteria_label.grid(row=5, column=0, columnspan=2, padx=5, pady=10)

###################

# Utwórz drugą kartę
frame2 = ttk.Frame(notebook)
notebook.add(frame2, text='Sliders')

# Utwórz Canvas i pasek przewijania
canvas = Canvas(frame2)
scrollbar = ttk.Scrollbar(frame2, orient='vertical', command=canvas.yview)
scrollable_frame = ttk.Frame(canvas)

# Powiąż pasek przewijania z Canvas
scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(
        scrollregion=canvas.bbox("all")
    )
)
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

# Utwórz przycisk do aktualizacji slidów
# update_button = ttk.Button(frame2, text="Aktualizuj slidery", command=update_sliders)
update_button = ttk.Button(frame2, text="Aktualizuj slidery", command=lambda: update_sliders(option_var, variants,  criteria))
update_button.pack()

# Upakuj Canvas i pasek przewijania
canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

###################
frame3 = ttk.Frame(notebook)
notebook.add(frame3, text='Results')

window.mainloop()


# def update_sliders(option_cnt, variant):
#     comparison_data = {}
#     slider_values = []
#
#     for widget in scrollable_frame.winfo_children():
#         widget.destroy()
#
#     variants_count = int(option_cnt.get())
#     sliders_count = int((variants_count * (variants_count - 1)) / 2)
#
#     variant_combinations = list(combinations(variant, 2))
#
#     for i in range(sliders_count):
#         frame = ttk.Frame(scrollable_frame)
#         frame.pack(side="top", fill="x", padx=5, pady=5)
#
#         label = ttk.Label(frame, text=f'{variant_combinations[i][0]} - {variant_combinations[i][1]}')
#         label.pack(side="top")
#
#         slider = ttk.Scale(frame, from_=0, to=100, orient='horizontal', value=50, length=200)
#         slider.pack(side="left")
#
#         slider_values.append(slider)
#
#         value_label = ttk.Label(frame, text='')
#         value_label.pack(side="left")
#
#         def make_scalerSlider(slider, label):
#             def scalerSlider(e):
#                 label.config(text=f'{int(slider.get())}')
#
#             return scalerSlider
#
#         slider.config(command=make_scalerSlider(slider, value_label))
#
#     button = ttk.Button(scrollable_frame, text="Oblicz",
#                         command=lambda: submit(variant_combinations, comparison_data, slider_values))
#     button.pack()

# def update_sliders(option_cnt, variant, criteria):
#     comparison_data = {}
#     slider_values = []
#
#     for widget in scrollable_frame.winfo_children():
#         widget.destroy()
#
#     variants_count = int(option_cnt.get())
#     sliders_count = int((variants_count * (variants_count - 1)) / 2)
#
#     variant_combinations = list(combinations(variant, 2))
#
#     for criterion in criteria:
#         ttk.Label(scrollable_frame, text=f'Kryterium: {criterion}').pack()
#
#         for i in range(sliders_count):
#             frame = ttk.Frame(scrollable_frame)
#             frame.pack(side="top", fill="x", padx=5, pady=5)
#
#             label = ttk.Label(frame, text=f'{variant_combinations[i][0]} - {variant_combinations[i][1]}')
#             label.pack(side="top")
#
#             slider = ttk.Scale(frame, from_=0, to=100, orient='horizontal', value=50, length=200)
#             slider.pack(side="left")
#
#             slider_values.append(slider)
#
#             value_label = ttk.Label(frame, text='')
#             value_label.pack(side="left")
#
#             def make_scalerSlider(slider, label):
#                 def scalerSlider(e):
#                     label.config(text=f'{int(slider.get())}')
#
#                 return scalerSlider
#
#             slider.config(command=make_scalerSlider(slider, value_label))
#
#     button = ttk.Button(scrollable_frame, text="Oblicz",
#                         command=lambda: submit(variant_combinations, comparison_data, slider_values, len(criteria)))
#     button.pack()

# def submit(variant_combinations, comparison_data, slider_values):
#     # Czyść zawartość karty "Results"
#     global frame3
#
#     for widget in frame3.winfo_children():
#         widget.destroy()
#
#     variants_count = len(variant_combinations)
#     matrix = [[1] * variants_count for _ in range(variants_count)]
#     idx1 = 0
#     idx2 = 0
#     builderVar = variants_count - 1
#     matrixLvl = builderVar - 1
#
#     for i, slider in enumerate(slider_values):
#         value = slider.get()
#         if value < 0:
#             value = 1 / -value
#         elif value == 0:
#             value = 1
#         value = convertValue(value)
#         comparison_data[variant_combinations[i]] = value
#
#         if i == builderVar:
#             builderVar += matrixLvl
#             matrixLvl -= 1
#             idx1 += 1
#             idx2 = idx1 + 1
#         else:
#             idx2 += 1
#
#         matrix[idx1][idx2] = round(float(value), 2)
#         matrix[idx2][idx1] = round(float(1 / value), 2)
#
#     ahp = ahpy.Compare(name='AHP', comparisons=comparison_data, precision=3, random_index='saaty')
#
#     # Utwórz trzecią kartę
#     # frame3 = ttk.Frame(notebook)
#     # notebook.add(frame3, text='Results')
#
#     # Dodaj etykiety z wynikami
#     ttk.Label(frame3, text="Wektor wag: " + str(ahp.target_weights)).pack()
#     ttk.Label(frame3, text="CR: " + str(ahp.consistency_ratio)).pack()
#     ttk.Label(frame3, text="CI: " + str(ahp.consistency_index.real)).pack()
#     ttk.Label(frame3, text="Macierz wyborów:").pack()
#     for row in matrix:
#         ttk.Label(frame3, text=str(row)).pack()
#
#     # Przełącz na kartę z wynikami
#     notebook.select(frame3)

# def submit(variant_combinations, comparison_data, slider_values, criteria_count):
#     global frame3
#
#     for widget in frame3.winfo_children():
#         widget.destroy()
#
#     variants_count = len(variant_combinations)
#     matrix = [[1] * variants_count for _ in range(variants_count)]
#     idx1 = 0
#     idx2 = 0
#     builderVar = variants_count - 1
#     matrixLvl = builderVar - 1
#
#     for j in range(criteria_count):
#         for i in range(variants_count):
#             value = slider_values[j*variants_count + i].get()
#             if value < 0:
#                 value = 1 / -value
#             elif value == 0:
#                 value = 1
#             value = convertValue(value)
#             comparison_data[variant_combinations[i]] = value
#
#             if i == builderVar:
#                 builderVar += matrixLvl
#                 matrixLvl -= 1
#                 idx1 += 1
#                 idx2 = idx1 + 1
#             else:
#                 idx2 += 1
#
#             matrix[idx1][idx2] = round(float(value), 2)
#             matrix[idx2][idx1] = round(float(1 / value), 2)
#
#         ahp = ahpy.Compare(name='AHP', comparisons=comparison_data, precision=3, random_index='saaty')
#
#         # Dodaj etykiety z wynikami
#         ttk.Label(frame3, text=f"Kryterium {j+1}").pack()
#         ttk.Label(frame3, text="Wektor wag: " + str(ahp.target_weights)).pack()
#         ttk.Label(frame3, text="CR: " + str(ahp.consistency_ratio)).pack()
#         ttk.Label(frame3, text="CI: " + str(ahp.consistency_index.real)).pack()
#         ttk.Label(frame3, text="Macierz wyborów:").pack()
#         for row in matrix:
#             ttk.Label(frame3, text=str(row)).pack()
#
#     # Przełącz na kartę z wynikami
#     notebook.select(frame3)
