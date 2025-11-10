import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QLineEdit, QPushButton,
                             QTableWidget, QTableWidgetItem, QMessageBox,
                             QDialog, QFormLayout, QDoubleSpinBox, QSpinBox,
                             QTextEdit, QHeaderView, QGroupBox, QSplitter,
                             QTabWidget, QComboBox, QListWidget, QListWidgetItem,
                             QFileDialog, QProgressBar, QToolBar, QAction,
                             QStatusBar, QMenu, QInputDialog, QCheckBox)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon, QPixmap

from database_manager import DatabaseManager
from result_window import ResultWindow
from element_dialog import AddElementDialog
from elements_browser import ElementsBrowser
from compound_manager import CompoundManager


class ChemicalCalculator(QMainWindow):
    """Главное окно химического калькулятора"""

    def __init__(self):
        super().__init__()
        self.db_manager = DatabaseManager()
        self.elements_list = []
        self.current_formula_name = ""
        self.init_ui()
        self.load_common_compounds()

    def init_ui(self):
        """Инициализация пользовательского интерфейса главного окна"""
        self.setWindowTitle("Химический калькулятор молярной массы")
        self.setGeometry(100, 100, 1200, 800)

        self.setWindowIcon(self.create_icon())

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        # Создание вкладок
        self.tab_widget = QTabWidget()

        # Вкладка калькулятора
        self.calculator_tab = self.create_calculator_tab()
        self.tab_widget.addTab(self.calculator_tab, "Калькулятор")

        # Вкладка базы элементов
        self.elements_tab = ElementsBrowser(self.db_manager, self)
        self.tab_widget.addTab(self.elements_tab, "База элементов")

        # Вкладка управления соединениями
        self.compounds_tab = CompoundManager(self.db_manager, self)
        self.tab_widget.addTab(self.compounds_tab, "Мои соединения")

        main_layout.addWidget(self.tab_widget)

        # Создание меню
        self.create_menus()

        # Создание тулбара
        self.create_toolbar()

        # Создание статусбара
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Готов к работе")

        # Инициализация окна результатов
        self.result_window = ResultWindow(self)

    def create_icon(self):
        """Создание простой иконки для приложения"""
        pixmap = QPixmap(32, 32)
        pixmap.fill(QColor(0, 150, 200))
        return QIcon(pixmap)

    def create_menus(self):
        """Создание меню приложения"""
        menubar = self.menuBar()

        # Меню Файл
        file_menu = menubar.addMenu('Файл')

        new_action = QAction('Новое соединение', self)
        new_action.setShortcut('Ctrl+N')
        new_action.triggered.connect(self.clear_elements_list)
        file_menu.addAction(new_action)

        file_menu.addSeparator()

        save_action = QAction('Сохранить соединение...', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_current_compound)
        file_menu.addAction(save_action)

        export_action = QAction('Экспорт элементов...', self)
        export_action.triggered.connect(self.export_elements)
        file_menu.addAction(export_action)

        import_action = QAction('Импорт элементов...', self)
        import_action.triggered.connect(self.import_elements)
        file_menu.addAction(import_action)

        file_menu.addSeparator()

        exit_action = QAction('Выход', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Меню Справка
        help_menu = menubar.addMenu('Справка')

        about_action = QAction('О программе', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def create_toolbar(self):
        """Создание панели инструментов"""
        toolbar = QToolBar("Основные инструменты")
        self.addToolBar(toolbar)

        # Кнопка расчета
        calculate_action = QAction('Рассчитать', self)
        calculate_action.triggered.connect(self.calculate_molar_mass)
        toolbar.addAction(calculate_action)

        toolbar.addSeparator()

        # Кнопка очистки
        clear_action = QAction('Очистить', self)
        clear_action.triggered.connect(self.clear_elements_list)
        toolbar.addAction(clear_action)

        # Кнопка добавления элемента
        add_element_action = QAction('Элемент', self)
        add_element_action.triggered.connect(self.show_add_element_dialog)
        toolbar.addAction(add_element_action)

    def create_calculator_tab(self):
        """Создание вкладки калькулятора"""
        tab = QWidget()
        layout = QHBoxLayout()

        # Создание сплиттера
        splitter = QSplitter(Qt.Horizontal)

        # Левая панель - ввод данных
        left_panel = self.create_input_panel()

        # Правая панель - список элементов и управление
        right_panel = self.create_elements_panel()

        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([400, 800])

        layout.addWidget(splitter)
        tab.setLayout(layout)

        return tab

    def create_input_panel(self):
        """Создание панели для ввода данных"""
        panel = QWidget()
        layout = QVBoxLayout()

        # Группа для ввода элемента
        input_group = QGroupBox("Добавление элемента")
        input_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        input_layout = QFormLayout()

        # Поле для ввода символа элемента с автодополнением
        self.element_input = QLineEdit()
        self.element_input.setPlaceholderText("Введите символ элемента (C, H, O...)")
        self.element_input.textChanged.connect(self.on_element_input_changed)

        # Выпадающий список для быстрого выбора элементов
        self.element_combo = QComboBox()
        self.element_combo.addItem("-- Выберите элемент --")
        elements = self.db_manager.get_all_elements()
        for symbol, name, mass, category in elements:
            self.element_combo.addItem(f"{symbol} - {name} ({mass})", symbol)
        self.element_combo.currentIndexChanged.connect(self.on_element_combo_changed)

        # Поле для ввода количества
        self.quantity_input = QLineEdit()
        self.quantity_input.setPlaceholderText("Введите количество")
        self.quantity_input.setText("1")

        # Кнопка добавления элемента
        self.add_element_button = QPushButton("Добавить элемент")
        self.add_element_button.clicked.connect(self.add_element_to_list)
        self.add_element_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)

        input_layout.addRow("Символ элемента:", self.element_input)
        input_layout.addRow("Быстрый выбор:", self.element_combo)
        input_layout.addRow("Количество:", self.quantity_input)
        input_layout.addRow(self.add_element_button)

        input_group.setLayout(input_layout)

        # Группа распространенных соединений
        common_group = QGroupBox("Распространенные соединения")
        common_layout = QVBoxLayout()

        self.common_compounds_list = QListWidget()
        self.common_compounds_list.itemDoubleClicked.connect(self.load_common_compound)
        common_layout.addWidget(self.common_compounds_list)

        common_group.setLayout(common_layout)

        # Группа для управления
        control_group = QGroupBox("Управление")
        control_layout = QVBoxLayout()

        # Поле для имени соединения
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Название соединения:"))
        self.compound_name_input = QLineEdit()
        self.compound_name_input.setPlaceholderText("Введите название соединения")
        name_layout.addWidget(self.compound_name_input)
        control_layout.addLayout(name_layout)

        # Кнопка расчета
        self.calculate_button = QPushButton("Рассчитать молярную массу")
        self.calculate_button.clicked.connect(self.calculate_molar_mass)
        self.calculate_button.setEnabled(False)
        self.calculate_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 12px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)

        # Кнопка очистки
        self.clear_button = QPushButton("Очистить список")
        self.clear_button.clicked.connect(self.clear_elements_list)

        # Кнопка добавления нового элемента в БД
        self.add_new_element_button = QPushButton("Добавить новый элемент в базу")
        self.add_new_element_button.clicked.connect(self.show_add_element_dialog)

        control_layout.addWidget(self.calculate_button)
        control_layout.addWidget(self.clear_button)
        control_layout.addWidget(self.add_new_element_button)
        control_layout.addStretch()

        control_group.setLayout(control_layout)

        # Добавление групп в layout
        layout.addWidget(input_group)
        layout.addWidget(common_group)
        layout.addWidget(control_group)

        panel.setLayout(layout)
        return panel

    def create_elements_panel(self):
        """Создание панели для отображения списка элементов"""
        panel = QWidget()
        layout = QVBoxLayout()

        # Заголовок
        title_label = QLabel("Сoстав вещества")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setStyleSheet("color: #2c3e50; padding: 10px;")

        # Таблица элементов
        self.elements_table = QTableWidget()
        self.elements_table.setColumnCount(4)
        self.elements_table.setHorizontalHeaderLabels(["Элемент", "Символ", "Количество", "Атомная масса"])
        self.elements_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.elements_table.setSelectionBehavior(QTableWidget.SelectRows)

        # Поле для отображения текущей формулы
        formula_group = QGroupBox("Текущая формула")
        formula_layout = QVBoxLayout()
        self.formula_display = QTextEdit()
        self.formula_display.setMaximumHeight(100)
        self.formula_display.setReadOnly(True)
        self.formula_display.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 2px solid #dee2e6;
                border-radius: 5px;
                padding: 10px;
                font-family: 'Courier New';
                font-size: 14px;
                font-weight: bold;
            }
        """)
        formula_layout.addWidget(self.formula_display)
        formula_group.setLayout(formula_layout)

        # Информация о соединении
        info_group = QGroupBox("Информация")
        info_layout = QVBoxLayout()

        self.info_label = QLabel("Добавьте элементы для расчета")
        self.info_label.setStyleSheet("color: #666; font-style: italic;")
        info_layout.addWidget(self.info_label)

        # Прогресс-бар для визуализации
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        info_layout.addWidget(self.progress_bar)

        info_group.setLayout(info_layout)

        # Кнопка удаления выбранного элемента
        self.remove_button = QPushButton("Удалить выбранный элемент")
        self.remove_button.clicked.connect(self.remove_selected_element)
        self.remove_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)

        layout.addWidget(title_label)
        layout.addWidget(self.elements_table)
        layout.addWidget(formula_group)
        layout.addWidget(info_group)
        layout.addWidget(self.remove_button)

        panel.setLayout(layout)
        return panel

    def load_common_compounds(self):
        """Загрузка распространенных соединений"""
        compounds = self.db_manager.get_common_compounds()
        self.common_compounds_list.clear()

        for name, formula, molar_mass, description in compounds:
            item = QListWidgetItem(f"{name} - {formula} ({molar_mass} г/моль)")
            item.setData(Qt.UserRole, (name, formula))
            self.common_compounds_list.addItem(item)

    def load_common_compound(self, item):
        """Загрузка распространенного соединения в калькулятор"""
        name, formula = item.data(Qt.UserRole)
        self.compound_name_input.setText(name)

        # Парсинг формулы (простая реализация)
        # В реальном приложении нужен более сложный парсер химических формул
        QMessageBox.information(self, "Информация",
                                f"Соединение '{name}' загружено.\nФормула: {formula}\n\nВ реальном приложении здесь будет автоматическое разложение формулы на элементы.")

    # Далее идут все методы из предыдущей реализации...
    # on_element_input_changed, on_element_combo_changed, add_element_to_list,
    # remove_selected_element, update_elements_table, update_formula_display,
    # clear_elements_list, calculate_molar_mass, show_add_element_dialog,
    # save_current_compound, export_elements, import_elements, show_about

    def on_element_input_changed(self, text):
        """Обработка изменения текста в поле ввода элемента"""
        if text:
            self.element_input.setText(text.upper())

    def on_element_combo_changed(self, index):
        """Обработка выбора элемента из комбобокса"""
        if index > 0:
            symbol = self.element_combo.itemData(index)
            self.element_input.setText(symbol)

    def add_element_to_list(self):
        """Добавление элемента в список для расчета"""
        symbol = self.element_input.text().strip()
        quantity_text = self.quantity_input.text().strip()

        # Проверка введенных данных
        if not symbol:
            QMessageBox.warning(self, "Ошибка", "Введите символ элемента!")
            return

        if not quantity_text:
            QMessageBox.warning(self, "Ошибка", "Введите количество!")
            return

        try:
            quantity = float(quantity_text)
            if quantity <= 0:
                QMessageBox.warning(self, "Ошибка", "Количество должно быть положительным числом!")
                return
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Количество должно быть числом!")
            return

        # Проверка существования элемента в базе данных
        element_data = self.db_manager.get_element_by_symbol(symbol)
        if not element_data:
            QMessageBox.warning(self, "Ошибка",
                                f"Элемент '{symbol}' не найден в базе данных!")
            return

        # Добавление элемента в список
        self.elements_list.append((symbol, quantity))

        # Обновление интерфейса
        self.update_elements_table()
        self.update_formula_display()

        # Очистка полей ввода
        self.element_input.clear()
        self.quantity_input.setText("1")
        self.element_combo.setCurrentIndex(0)

        # Активация кнопки расчета
        self.calculate_button.setEnabled(len(self.elements_list) > 0)
        self.status_bar.showMessage(f"Элемент {symbol} добавлен. Всего элементов: {len(self.elements_list)}")

    def remove_selected_element(self):
        """Удаление выбранного элемента из списка"""
        current_row = self.elements_table.currentRow()
        if current_row >= 0 and current_row < len(self.elements_list):
            symbol, quantity = self.elements_list[current_row]
            self.elements_list.pop(current_row)
            self.update_elements_table()
            self.update_formula_display()
            self.calculate_button.setEnabled(len(self.elements_list) > 0)
            self.status_bar.showMessage(f"Элемент {symbol} удален")

    def update_elements_table(self):
        """Обновление таблицы элементов"""
        self.elements_table.setRowCount(len(self.elements_list))

        total_mass = 0
        for row, (symbol, quantity) in enumerate(self.elements_list):
            element_data = self.db_manager.get_element_by_symbol(symbol)
            if element_data:
                symbol_db, name, atomic_mass, category = element_data
                element_mass = atomic_mass * quantity
                total_mass += element_mass

                self.elements_table.setItem(row, 0, QTableWidgetItem(name))
                self.elements_table.setItem(row, 1, QTableWidgetItem(symbol))
                self.elements_table.setItem(row, 2, QTableWidgetItem(str(quantity)))
                self.elements_table.setItem(row, 3, QTableWidgetItem(f"{atomic_mass:.4f}"))

        # Обновление информации
        if self.elements_list:
            self.info_label.setText(
                f"Всего элементов: {len(self.elements_list)}\nПредварительная масса: {total_mass:.2f} г/моль")
        else:
            self.info_label.setText("Добавьте элементы для расчета")

    def update_formula_display(self):
        """Обновление отображения формулы"""
        if not self.elements_list:
            self.formula_display.clear()
            return

        formula_parts = []
        for symbol, quantity in self.elements_list:
            if quantity == 1:
                formula_parts.append(symbol)
            else:
                formula_parts.append(f"{symbol}₍{quantity}₎")

        formula = " + ".join(formula_parts)
        self.formula_display.setPlainText(formula)

    def clear_elements_list(self):
        """Очистка списка элементов"""
        self.elements_list.clear()
        self.update_elements_table()
        self.update_formula_display()
        self.calculate_button.setEnabled(False)
        self.compound_name_input.clear()
        self.status_bar.showMessage("Список элементов очищен")

    def calculate_molar_mass(self):
        """Расчет молярной массы вещества"""
        if not self.elements_list:
            QMessageBox.warning(self, "Ошибка", "Список элементов пуст!")
            return

        # Показ прогресс-бара
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, len(self.elements_list))

        total_mass = 0.0
        elements_data = []

        # Расчет массы для каждого элемента
        for i, (symbol, quantity) in enumerate(self.elements_list):
            element_data = self.db_manager.get_element_by_symbol(symbol)
            if element_data:
                symbol_db, name, atomic_mass, category = element_data
                element_mass = atomic_mass * quantity
                total_mass += element_mass
                elements_data.append((symbol, quantity, element_mass, atomic_mass, name))

            # Обновление прогресс-бара
            self.progress_bar.setValue(i + 1)
            QApplication.processEvents()

        # Скрытие прогресс-бара
        self.progress_bar.setVisible(False)

        # Формирование красивой формулы
        formula_parts = []
        for symbol, quantity in self.elements_list:
            if quantity == 1:
                formula_parts.append(symbol)
            else:
                formula_parts.append(f"{symbol}₍{quantity}₎")

        formula = " + ".join(formula_parts)

        # Получение имени соединения
        compound_name = self.compound_name_input.text().strip()
        if not compound_name:
            compound_name = "Неизвестное соединение"

        # Показ результатов
        self.result_window.show_results(compound_name, formula, total_mass, elements_data)
        self.status_bar.showMessage(f"Расчет завершен: {total_mass:.2f} г/моль")

    def show_add_element_dialog(self):
        """Показ диалога добавления нового элемента"""
        dialog = AddElementDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            element_data = dialog.get_element_data()

            # Проверка данных
            if not all([element_data['symbol'], element_data['name']]):
                QMessageBox.warning(self, "Ошибка", "Символ и название должны быть заполнены!")
                return

            # Добавление элемента в базу данных
            success = self.db_manager.add_element(
                element_data['symbol'],
                element_data['name'],
                element_data['atomic_mass'],
                element_data['atomic_number'],
                element_data['category'],
                element_data['discovered_year']
            )

            if success:
                QMessageBox.information(self, "Успех",
                                        f"Элемент {element_data['symbol']} успешно добавлен в базу данных!")
                # Обновление комбобокса
                self.element_combo.clear()
                self.element_combo.addItem("-- Выберите элемент --")
                elements = self.db_manager.get_all_elements()
                for symbol, name, mass, category in elements:
                    self.element_combo.addItem(f"{symbol} - {name} ({mass})", symbol)

                self.status_bar.showMessage(f"Элемент {element_data['symbol']} добавлен в базу")
            else:
                QMessageBox.warning(self, "Ошибка",
                                    f"Элемент с символом {element_data['symbol']} уже существует в базе данных!")

    def save_current_compound(self):
        """Сохранение текущего соединения"""
        if not self.elements_list:
            QMessageBox.warning(self, "Ошибка", "Нет элементов для сохранения!")
            return

        compound_name = self.compound_name_input.text().strip()
        if not compound_name:
            compound_name, ok = QInputDialog.getText(self, "Сохранение",
                                                     "Введите название соединения:")
            if not ok or not compound_name:
                return

        # Расчет молярной массы
        total_mass = 0.0
        composition = []
        for symbol, quantity in self.elements_list:
            element_data = self.db_manager.get_element_by_symbol(symbol)
            if element_data:
                symbol_db, name, atomic_mass, category = element_data
                total_mass += atomic_mass * quantity
                composition.append(f"{symbol}:{quantity}")

        formula = self.formula_display.toPlainText()
        composition_str = ";".join(composition)

        # Сохранение в базу данных
        success = self.db_manager.save_compound(compound_name, formula, total_mass, composition_str)

        if success:
            QMessageBox.information(self, "Успех", "Соединение успешно сохранено!")
            self.status_bar.showMessage(f"Соединение '{compound_name}' сохранено")
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось сохранить соединение!")

    def export_elements(self):
        """Экспорт элементов в CSV файл"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Экспорт элементов", "chemical_elements.csv", "CSV Files (*.csv)"
        )

        if filename:
            success = self.db_manager.export_to_csv(filename)
            if success:
                QMessageBox.information(self, "Успех", "Элементы успешно экспортированы!")
                self.status_bar.showMessage(f"Элементы экспортированы в {filename}")
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось экспортировать элементы!")

    def import_elements(self):
        """Импорт элементов из CSV файла"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Импорт элементов", "", "CSV Files (*.csv)"
        )

        if filename:
            result = self.db_manager.import_from_csv(filename)
            if result > 0:
                QMessageBox.information(self, "Успех",
                                        f"Успешно импортировано {result} элементов!")
                # Обновление интерфейса
                self.elements_tab.refresh_elements()
                self.status_bar.showMessage(f"Импортировано {result} элементов")
            elif result == 0:
                QMessageBox.information(self, "Информация",
                                        "Нет новых элементов для импорта.")
            else:
                QMessageBox.warning(self, "Ошибка",
                                    "Не удалось импортировать элементы!")

    def show_about(self):
        """Показ информации о программе"""
        about_text = """
        <h2>Химический калькулятор</h2>
        <p>Версия 1.0</p>
        <p>Программа для расчета молярной массы химических соединений.</p>
        <p>Функции:</p>
        <ul>
            <li>Расчет молярной массы</li>
            <li>База химических элементов</li>
            <li>Сохранение соединений</li>
            <li>Импорт/экспорт данных</li>
        </ul>
        <p>© 2024 Химический калькулятор</p>
        """
        QMessageBox.about(self, "О программе", about_text)


def main():
    """Основная функция запуска приложения"""
    app = QApplication(sys.argv)

    # Установка стиля приложения
    app.setStyle('Fusion')

    # Создание и показ главного окна
    calculator = ChemicalCalculator()
    calculator.show()

    sys.exit(app.exec_())


if __name__ == "__main__":

    main()
