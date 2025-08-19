import csv
import os
import tkinter as tk

from grade_package.misis_grade import make_grade_report_order, download_grade_report
from tkinter import messagebox
from tkinter import filedialog
from grade_package.join_files import create_grade_report


def open_file_click(action_type):
    # Открываем диалоговое окно выбора файла
    file_path = filedialog.askopenfilename(
        title="Выберите файл",
        filetypes=(("Текстовые файлы", "*.csv"), ("Все файлы", "*.*")),
        initialdir=os.path.join(os.getcwd(), 'list_courses'),
    )
    if file_path:  # Если файл выбран (не нажата "Отмена")
        try: 
            data = read_csv_to_list(file_path)
            if action_type == 'make_order':
                make_grade_report_order(data)
            else:
                download_grade_report(data)
            messagebox.showinfo("Info", "Выгрузки создались!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")
    else:
        messagebox.showinfo("Info", "Пожалуйста, выберете файл")

delete_csv = False
def read_csv_to_list(file_path, delimiter=''):
    data_list = []
    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)           
            for row in csv_reader:
                joined_row = delimiter.join(row)
                data_list.append(joined_row)
                
    except FileNotFoundError:
        print(f"Файл {file_path} не найден.")
        messagebox.showinfo("Info", "Файл с кодами сетевых курсов не нейден!")
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        messagebox.showinfo("Info", f"Произошла ошибка: {e}")
        
    return data_list

def on_button_make_grade_click():
    make_grade_report_order(LIST_COURSES)
    messagebox.showinfo("Info", "Выгрузки создались!")

def on_button_download_grade_click():
    download_grade_report(LIST_COURSES)
    messagebox.showinfo("Info", "Выгрузки скачались!")

def on_button_create_grade_report_click():
    global delete_csv
    try:
        create_grade_report('grade_reports')
        messagebox.showinfo("Info", "Общий файл готов!")
    except:
        messagebox.showinfo("Info", "Нет файлов с выгрузками!")
        return None
    if delete_csv:
        folder_path = os.path.join(os.getcwd(), 'grade_reports')  # Замените на путь к вашей папке
        try:
            for file_name in os.listdir(folder_path):
                if file_name.endswith(".csv"):
                    file_path = os.path.join(folder_path, file_name)
                    os.remove(file_path)
                    print(f"Удален файл: {file_name}")
            messagebox.showinfo("Успех", "CSV файлы успешно удалены.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка при удалении файлов: {e}")

LIST_COURSES = read_csv_to_list(os.path.join(os.getcwd(), 'list_courses/list_courses.csv'))