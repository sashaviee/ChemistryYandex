import sqlite3
import os
import csv
from PyQt5.QtWidgets import QMessageBox


class DatabaseManager:
    def __init__(self, db_name="chemical_elements.db"):
        self.db_name = db_name
        self.init_database()

    def init_database(self):
        """Инициализация базы данных и создание таблиц"""
        if not os.path.exists(self.db_name):
            self.create_tables()
            self.populate_elements()
            self.create_compounds_table()

    def create_tables(self):
        """Создание таблиц химических элементов и соединений"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        # Таблица элементов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS elements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                atomic_mass REAL NOT NULL,
                atomic_number INTEGER NOT NULL,
                category TEXT,
                discovered_year INTEGER
            )
        ''')

        # Таблица распространенных соединений
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS common_compounds (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                formula TEXT NOT NULL,
                molar_mass REAL NOT NULL,
                description TEXT
            )
        ''')

        conn.commit()
        conn.close()

    def create_compounds_table(self):
        """Создание таблицы для сохраненных соединений"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS saved_compounds (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                formula TEXT NOT NULL,
                molar_mass REAL NOT NULL,
                composition TEXT NOT NULL,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()

    def populate_elements(self):
        """Заполнение таблицы химическими элементами"""
        elements = [
            ('H', 'Водород', 1.008, 1, 'Неметалл', 1766),
            ('He', 'Гелий', 4.0026, 2, 'Инертный газ', 1868),
            ('Li', 'Литий', 6.94, 3, 'Щелочной металл', 1817),
            ('Be', 'Бериллий', 9.0122, 4, 'Щелочноземельный', 1797),
            ('B', 'Бор', 10.81, 5, 'Металлоид', 1808),
            ('C', 'Углерод', 12.011, 6, 'Неметалл', -2000),
            ('N', 'Азот', 14.007, 7, 'Неметалл', 1772),
            ('O', 'Кислород', 15.999, 8, 'Неметалл', 1774),
            ('F', 'Фтор', 18.998, 9, 'Галоген', 1886),
            ('Ne', 'Неон', 20.180, 10, 'Инертный газ', 1898),
            ('Na', 'Натрий', 22.990, 11, 'Щелочной металл', 1807),
            ('Mg', 'Магний', 24.305, 12, 'Щелочноземельный', 1755),
            ('Al', 'Алюминий', 26.982, 13, 'Постпереходный металл', 1825),
            ('Si', 'Кремний', 28.085, 14, 'Металлоид', 1824),
            ('P', 'Фосфор', 30.974, 15, 'Неметалл', 1669),
            ('S', 'Сера', 32.06, 16, 'Неметалл', -2000),
            ('Cl', 'Хлор', 35.45, 17, 'Галоген', 1774),
            ('Ar', 'Аргон', 39.948, 18, 'Инертный газ', 1894),
            ('K', 'Калий', 39.098, 19, 'Щелочной металл', 1807),
            ('Ca', 'Кальций', 40.078, 20, 'Щелочноземельный', 1808),
            ('Fe', 'Железо', 55.845, 26, 'Переходный металл', -2000),
            ('Cu', 'Медь', 63.546, 29, 'Переходный металл', -8000),
            ('Zn', 'Цинк', 65.38, 30, 'Переходный металл', 1746),
            ('Ag', 'Серебро', 107.87, 47, 'Переходный металл', -3000),
            ('Au', 'Золото', 196.97, 79, 'Переходный металл', -3000),
            ('Hg', 'Ртуть', 200.59, 80, 'Переходный металл', -2000),
            ('Pb', 'Свинец', 207.2, 82, 'Постпереходный металл', -3000)
        ]

        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.executemany('''
            INSERT OR IGNORE INTO elements (symbol, name, atomic_mass, atomic_number, category, discovered_year)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', elements)

        # Добавление распространенных соединений
        compounds = [
            ('Вода', 'H2O', 18.015, 'Основной растворитель'),
            ('Поваренная соль', 'NaCl', 58.44, 'Хлорид натрия'),
            ('Серная кислота', 'H2SO4', 98.079, 'Сильная кислота'),
            ('Глюкоза', 'C6H12O6', 180.156, 'Углевод'),
            ('Метан', 'CH4', 16.04, 'Природный газ'),
            ('Этанол', 'C2H5OH', 46.07, 'Спирт')
        ]

        cursor.executemany('''
            INSERT OR IGNORE INTO common_compounds (name, formula, molar_mass, description)
            VALUES (?, ?, ?, ?)
        ''', compounds)

        conn.commit()
        conn.close()

    def get_all_elements(self):
        """Получение всех элементов из базы данных"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT symbol, name, atomic_mass, category FROM elements 
            ORDER BY atomic_number
        ''')
        elements = cursor.fetchall()

        conn.close()
        return elements

    def get_element_by_symbol(self, symbol):
        """Получение элемента по символу"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT symbol, name, atomic_mass, category FROM elements 
            WHERE symbol = ?
        ''', (symbol,))
        element = cursor.fetchone()

        conn.close()
        return element

    def search_elements(self, query):
        """Поиск элементов по названию или символу"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT symbol, name, atomic_mass, category FROM elements 
            WHERE name LIKE ? OR symbol LIKE ?
            ORDER BY atomic_number
        ''', (f'%{query}%', f'%{query}%'))

        elements = cursor.fetchall()
        conn.close()
        return elements

    def add_element(self, symbol, name, atomic_mass, atomic_number, category="", discovered_year=None):
        """Добавление нового элемента в базу данных"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO elements (symbol, name, atomic_mass, atomic_number, category, discovered_year)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (symbol, name, atomic_mass, atomic_number, category, discovered_year))
            conn.commit()
            success = True
        except sqlite3.IntegrityError as e:
            success = False
        finally:
            conn.close()

        return success

    def update_element(self, old_symbol, symbol, name, atomic_mass, atomic_number, category, discovered_year):
        """Обновление данных элемента"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                UPDATE elements 
                SET symbol=?, name=?, atomic_mass=?, atomic_number=?, category=?, discovered_year=?
                WHERE symbol=?
            ''', (symbol, name, atomic_mass, atomic_number, category, discovered_year, old_symbol))
            conn.commit()
            success = True
        except Exception as e:
            success = False
        finally:
            conn.close()

        return success

    def delete_element(self, symbol):
        """Удаление элемента из базы данных"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        try:
            cursor.execute('DELETE FROM elements WHERE symbol = ?', (symbol,))
            conn.commit()
            success = True
        except Exception as e:
            success = False
        finally:
            conn.close()

        return success

    def get_common_compounds(self):
        """Получение списка распространенных соединений"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute('SELECT name, formula, molar_mass, description FROM common_compounds')
        compounds = cursor.fetchall()

        conn.close()
        return compounds

    def save_compound(self, name, formula, molar_mass, composition):
        """Сохранение соединения в базу данных"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO saved_compounds (name, formula, molar_mass, composition)
                VALUES (?, ?, ?, ?)
            ''', (name, formula, molar_mass, composition))
            conn.commit()
            success = True
        except Exception as e:
            success = False
        finally:
            conn.close()

        return success

    def get_saved_compounds(self):
        """Получение сохраненных соединений"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT name, formula, molar_mass, composition, created_date 
            FROM saved_compounds 
            ORDER BY created_date DESC
        ''')
        compounds = cursor.fetchall()

        conn.close()
        return compounds

    def export_to_csv(self, filename):
        """Экспорт элементов в CSV файл"""
        try:
            elements = self.get_all_elements()
            with open(filename, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['Символ', 'Название', 'Атомная масса', 'Категория'])
                for element in elements:
                    writer.writerow(element)
            return True
        except Exception as e:
            return False

    def import_from_csv(self, filename):
        """Импорт элементов из CSV файла"""
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                next(reader)  # Пропускаем заголовок

                imported_count = 0
                for row in reader:
                    if len(row) >= 3:
                        symbol, name, atomic_mass = row[0], row[1], float(row[2])
                        category = row[3] if len(row) > 3 else ""

                        # Проверяем, существует ли уже элемент
                        existing = self.get_element_by_symbol(symbol)
                        if not existing:
                            self.add_element(symbol, name, atomic_mass, 0, category)
                            imported_count += 1

                return imported_count
        except Exception as e:
            return -1