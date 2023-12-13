from ttkbootstrap import Style
from tkinter import ttk, Menu, StringVar
from tkinter import Canvas
from itertools import combinations
import ahpy_swd as ahpy

scrollable_frame3 = None
scrollable_frame4 = None

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
    if val > 160:
        return 1 / 9
    elif val > 140:
        return 1 / 7
    elif val > 120:
        return 1 / 5
    elif val > 100:
        return 1 / 3
    elif val > 80:
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

            slider = ttk.Scale(frame, from_=0, to=180, orient='horizontal', value=90, length=250)
            slider.pack(side="left")

            slider_values.append(slider)

            value_label = ttk.Label(frame, text='')
            value_label.pack(side="left")

            def make_scalerSlider(slider, label):
                return lambda e: label.config(text=f'{int(slider.get())}')

            slider.config(command=make_scalerSlider(slider, value_label))

    button = ttk.Button(scrollable_frame, text="Oblicz",
                        command=lambda: submit(variants_count, variant_combinations, comparison_data, slider_values, len(criteria), criteria))
    button.pack()

def submit(variants_cnt, variant_combinations, comparison_data, slider_values, criteria_count, criteria):
    global scrollable_frame3, scrollable_frame4

    for widget in scrollable_frame3.winfo_children():
        widget.destroy()

    for widget in scrollable_frame4.winfo_children():
        widget.destroy()

    variants_count = variants_cnt
    ahp_weights = []

    for j in range(criteria_count):
        matrix = [[1] * variants_count for _ in range(variants_count)]
        idx1 = 0
        idx2 = 0
        builderVar = variants_count - 1
        matrixLvl = builderVar - 1

        for i in range(variants_count * (variants_count - 1) // 2):
            value = slider_values[j * len(variant_combinations) + i].get()
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

        sorted_weights = sorted(ahp.target_weights.items(), key=lambda x: x[0])
        sorted_dict = dict(sorted_weights)
        ahp_weights.append(sorted_dict)

        # Dodaj etykiety z wynikami
        ttk.Label(scrollable_frame3, text=f"Kryterium: {criteria[j]}").pack()
        ttk.Label(scrollable_frame3, text="Wektor wag: " + str(ahp.target_weights)).pack()
        ttk.Label(scrollable_frame3, text="CR: " + str(ahp.consistency_ratio)).pack()
        ttk.Label(scrollable_frame3, text="CI: " + str(ahp.consistency_index.real)).pack()
        ttk.Label(scrollable_frame3, text="Macierz wyborów:").pack()
        for row in matrix:
            ttk.Label(scrollable_frame3, text=str(row)).pack()


    # print(ahp_weights)
    sum_dict = {key: 0 for key in ahp_weights[0]}
    count_dict = {key: 0 for key in ahp_weights[0]}

    for weight_dict in ahp_weights:
        for key, values in weight_dict.items():
            # Jeśli wartość to lista, dodaj każdy element do sumy
            if isinstance(values, list):
                sum_dict[key] += sum(values)
                count_dict[key] += len(values)
            else:
                sum_dict[key] += values
                count_dict[key] += 1

    average_dict = {key: sum_dict[key] / count_dict[key] for key in sum_dict}

    sorted_average = sorted(average_dict.items(), key=lambda x: x[1], reverse=True)

    # Dodaj tytuł do karty frame4
    title_label = ttk.Label(scrollable_frame4, text="Najbardziej pożądane warianty")
    title_label.pack()
    for key, value in sorted_average:
        rounded_value = round(value, 3)
        ttk.Label(scrollable_frame4, text=f"Średnia dla {key}: {rounded_value}").pack()

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
update_button = ttk.Button(frame2, text="Aktualizuj slidery", command=lambda: update_sliders(option_var, variants,  criteria))
update_button.pack()

# Upakuj Canvas i pasek przewijania
canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

###################
frame3 = ttk.Frame(notebook)
notebook.add(frame3, text='Results')

# Utwórz Canvas i pasek przewijania
canvas_frame3 = Canvas(frame3)
scrollbar_frame3 = ttk.Scrollbar(frame3, orient='vertical', command=canvas_frame3.yview)
scrollable_frame3 = ttk.Frame(canvas_frame3)

# Powiąż pasek przewijania z Canvas
scrollable_frame3.bind(
    "<Configure>",
    lambda e: canvas_frame3.configure(
        scrollregion=canvas_frame3.bbox("all")
    )
)
canvas_frame3.create_window((0, 0), window=scrollable_frame3, anchor="nw")
canvas_frame3.configure(yscrollcommand=scrollbar_frame3.set)

# Upakuj Canvas i pasek przewijania
canvas_frame3.pack(side="left", fill="both", expand=True)
scrollbar_frame3.pack(side="right", fill="y")

###################
frame4 = ttk.Frame(notebook)
notebook.add(frame4, text='Summary results')

# Utwórz Canvas i pasek przewijania
canvas_frame4 = Canvas(frame4)
scrollbar_frame4 = ttk.Scrollbar(frame4, orient='vertical', command=canvas_frame4.yview)
scrollable_frame4 = ttk.Frame(canvas_frame4)

# Powiąż pasek przewijania z Canvas
scrollable_frame4.bind(
    "<Configure>",
    lambda e: canvas_frame4.configure(
        scrollregion=canvas_frame4.bbox("all")
    )
)
canvas_frame4.create_window((0, 0), window=scrollable_frame4, anchor="nw")
canvas_frame4.configure(yscrollcommand=scrollbar_frame4.set)

# Upakuj Canvas i pasek przewijania
canvas_frame4.pack(side="left", fill="both", expand=True)
scrollbar_frame4.pack(side="right", fill="y")


window.mainloop()
