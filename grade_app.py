import tkinter as tk
import os
import grade_package.gui_functions as gui

from tkinter import messagebox 
from tkinter import font
from tkinter.messagebox import showinfo
from tkinter import ttk


class PeachButton(tk.Button):
    PEACH_COLORS = {
        'Peach': '#FFDAB9',
        'Salmon': '#FA8072',
        'Moccasin': '#FFE4B5',
        'Peach Puff': '#FFDAB9',
        'Apricot': '#FDD5B1',
        'Tuscany': '#E3C8B9',
        'Blush': '#DEA5A4'
    }
    def __init__(self, master=None, color_name='Apricot', **kwargs):

        # Инициализируем родительский класс Button
        super().__init__(master, **kwargs)

        # Задаем параметры кнопки
        self.color_name = color_name
        self.default_bg_color = self.PEACH_COLORS[color_name]
        self.hover_bg_color = self.PEACH_COLORS['Salmon']  # Цвет фона при наведении

        # Устанавливаем начальные значения
        self.configure(
            bg=self.default_bg_color,
            fg='#4B5A5E',
            font=font.Font(family="Helvetica", size=11, weight="bold"),
            bd=3,
            relief=tk.FLAT,
            padx=5,
            pady=5
        )

        # Добавляем эффект при наведении (hover effect)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, e):
        """Изменяет цвет фона при наведении курсора."""
        self.config(bg=self.hover_bg_color)

    def on_leave(self, e):
        """Возвращает исходный цвет фона при уходе курсора."""
        self.config(bg=self.default_bg_color)

root = tk.Tk()
root.title("Grade app")
root.geometry("645x260")
root.configure(bg='#C8DACD')

style = ttk.Style()
style.configure('TCheckbutton', background='#C8DACD')
style.map('TCheckbutton',
              background=[('active', '#C8DACD'),  # Фон остается #C8DACD при нажатии
                          ('pressed', '#C8DACD')])  # Фон остается #C8DACD при удерживании

def checkbutton_changed():
    if delete_csv_checkbox.get() == 1:
        gui.delete_csv = True
    else:
        gui.delete_csv = False


delete_csv_checkbox = tk.IntVar()

button_make_grade = PeachButton(
    root, 
    text="Создать выгрузки общих курсов",
    command=gui.on_button_make_grade_click
    )
button_make_grade.grid(row=0, column=0, ipadx=6, ipady=6, padx=15, pady=15, sticky="ew")

button_make_grade_net = PeachButton(root, text="Создать выгрузки курсов из файла", command= lambda: gui.open_file_click("make_order"))
button_make_grade_net.grid(row=1, column=0, ipadx=6, ipady=6, padx=15, pady=15, sticky="ew")

button_download_grade = PeachButton(root, text="Скачать выгрузки общих курсов", command=gui.on_button_download_grade_click)
button_download_grade.grid(row=0, column=1, ipadx=6, ipady=6, padx=15, pady=15, sticky="ew")

button_download_grade_net = PeachButton(root, text="Скачать выгрузки курсов из файла", command=lambda: gui.open_file_click("download_grade"))
button_download_grade_net.grid(row=1, column=1, ipadx=6, ipady=6, padx=15, pady=15, sticky="ew")

button_create_grade = PeachButton(root, text="Объединить файлы выгрузок в один", command=gui.on_button_create_grade_report_click)
button_create_grade.grid(row=2, column=0, columnspan=2, ipadx=5, ipady=5, pady=1)

check_button = ttk.Checkbutton(root, text="Удалить CSV файлы после выполнения", style='TCheckbutton', variable=delete_csv_checkbox, command=checkbutton_changed)
check_button.grid(row=3, column=0, columnspan=2, ipadx=5, ipady=5, pady=1)

root.mainloop()