import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import datetime

# --- Настройки ---
DATA_FILE = "data.json"
DATE_FORMAT = "%Y-%m-%d" # Формат даты: ГГГГ-ММ-ДД

class TrainingPlannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Training Planner")
        self.root.geometry("800x500")

        # Загрузка данных из файла
        self.data = self.load_data()

        # Создание виджетов
        self.create_widgets()
        self.update_treeview()

    def create_widgets(self):
        # --- Рамка для ввода данных ---
        input_frame = ttk.LabelFrame(self.root, text="Добавить новую тренировку", padding="10")
        input_frame.pack(fill="x", padx=10, pady=5)

        # Поле Дата
        ttk.Label(input_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=0, sticky="w", pady=2)
        self.date_entry = ttk.Entry(input_frame)
        self.date_entry.grid(row=0, column=1, sticky="ew", pady=2)

        # Поле Тип тренировки
        ttk.Label(input_frame, text="Тип:").grid(row=1, column=0, sticky="w", pady=2)
        self.type_var = tk.StringVar()
        self.type_entry = ttk.Combobox(input_frame, textvariable=self.type_var, values=["Кардио", "Силовая", "Растяжка", "Йога"])
        self.type_entry.grid(row=1, column=1, sticky="ew", pady=2)
        
        # Поле Длительность
        ttk.Label(input_frame, text="Длительность (мин):").grid(row=2, column=0, sticky="w", pady=2)
        self.duration_entry = ttk.Entry(input_frame)
        self.duration_entry.grid(row=2, column=1, sticky="ew", pady=2)

        # Кнопка Добавить
        ttk.Button(input_frame, text="Добавить тренировку", command=self.add_training).grid(row=3, column=0, columnspan=2, pady=10)

        # --- Рамка для фильтрации ---
        filter_frame = ttk.LabelFrame(self.root, text="Фильтр", padding="10")
        filter_frame.pack(fill="x", padx=10, pady=5)

        # Фильтр по типу
        ttk.Label(filter_frame, text="Тип:").grid(row=0, column=0, sticky="w")
        self.filter_type_var = tk.StringVar()
        filter_type_combo = ttk.Combobox(filter_frame, textvariable=self.filter_type_var, 
                                         values=["Все", "Кардио", "Силовая", "Растяжка", "Йога"])
        filter_type_combo.current(0) # Выбираем "Все" по умолчанию
        filter_type_combo.grid(row=0, column=1, sticky="ew")

        # Фильтр по дате
        ttk.Label(filter_frame, text="Дата:").grid(row=1, column=0, sticky="w")
        self.filter_date_var = tk.StringVar()
        filter_date_entry = ttk.Entry(filter_frame, textvariable=self.filter_date_var)
        filter_date_entry.grid(row=1, column=1, sticky="ew")
        
        # Кнопка Применить фильтр
        ttk.Button(filter_frame, text="Применить фильтр", command=self.apply_filter).grid(row=2, column=0, columnspan=2, pady=5)

        # --- Таблица (Treeview) ---
        columns = ("date", "type", "duration")
        
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings")
        
        self.tree.heading("date", text="Дата")
        self.tree.heading("type", text="Тип")
        self.tree.heading("duration", text="Длительность (мин)")
        
        self.tree.column("date", width=120)
        self.tree.column("type", width=150)
        
        self.tree.pack(fill="both", expand=True, padx=10, pady=5)

    def add_training(self):
        """Метод для добавления новой тренировки после проверки данных."""
        
        date_str = self.date_entry.get()
        tr_type = self.type_var.get()
        
         # Проверка на выбор типа из выпадающего списка
        if tr_type == "":
            messagebox.showerror("Ошибка", "Пожалуйста, выберите тип тренировки из списка.")
            return
            
         # Проверка на ввод длительности (целое число > 0)
         try:
            duration = int(self.duration_entry.get())
            if duration <= 0:
                raise ValueError("Длительность должна быть положительной.")
         except ValueError:
            messagebox.showerror("Ошибка", "Длительность должна быть целым положительным числом.")
            return

         # Проверка формата даты
         try:
            date_obj = datetime.strptime(date_str, DATE_FORMAT)
            formatted_date = date_obj.strftime(DATE_FORMAT) # Приводим к единому формату
         except ValueError:
            messagebox.showerror("Ошибка", f"Неверный формат даты. Используйте {DATE_FORMAT}.")
            return

         # Добавление в список данных и обновление таблицы
         new_record = {"date": formatted_date, "type": tr_type, "duration": duration}
         self.data.append(new_record)
         self.save_data()
         self.update_treeview()
         
         # Очистка полей после добавления
         self.date_entry.delete(0, tk.END)
         self.duration_entry.delete(0, tk.END)
         self.type_var.set("")
         
    def update_treeview(self):
        """Метод для обновления данных в таблице с учетом текущего фильтра."""
        
         # Очистка текущей таблицы
         for item in self.tree.get_children():
             self.tree.delete(item)
             
         filtered_data = self.data.copy()
         
         # Применение фильтра по типу
         filter_type = self.filter_type_var.get()
         if filter_type != "Все":
             filtered_data = [item for item in filtered_data if item["type"] == filter_type]
             
         # Применение фильтра по дате (точное совпадение)
         filter_date = self.filter_date_var.get()
         if filter_date:
             try:
                 datetime.strptime(filter_date, DATE_FORMAT) # Проверка формата
                 filtered_data = [item for item in filtered_data if item["date"] == filter_date]
             except ValueError:
                 messagebox.showwarning("Предупреждение", f"Неверный формат даты в фильтре. Используйте {DATE_FORMAT}.")
                 
         # Вставка данных в таблицу
         for record in filtered_data:
             self.tree.insert("", tk.END, values=(record["date"], record["type"], record["duration"]))

    def apply_filter(self):
         """Обновляет таблицу при нажатии кнопки фильтра."""
         self.update_treeview()

    def load_data(self):
         """Загрузка данных из JSON файла при запуске."""
         
         try:
             with open(DATA_FILE, "r") as f:
                 return json.load(f)
         except (FileNotFoundError, json.JSONDecodeError):
             return []

    def save_data(self):
         """Сохранение данных в JSON файл."""
         
         with open(DATA_FILE, "w") as f:
             json.dump(self.data, f, indent=4)

if __name__ == "__main__":
    root = tk.Tk()
    app = TrainingPlannerApp(root)
    root.mainloop()
