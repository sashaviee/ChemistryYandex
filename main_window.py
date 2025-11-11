import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QLineEdit, QPushButton,
                             QTableWidget, QTableWidgetItem, QMessageBox,
                             QDialog, QFormLayout, QDoubleSpinBox, QSpinBox,
                             QTextEdit, QHeaderView, QGroupBox, QSplitter,
                             QTabWidget, QComboBox, QListWidget, QListWidgetItem,
                             QFileDialog, QProgressBar, QToolBar,
                             QStatusBar, QMenu, QInputDialog)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor, QIcon, QPixmap, QAction
from database_manager import DatabaseManager
from result_window import ResultWindow
from element_dialog import AddElementDialog
from elements_browser import ElementsBrowser
from compound_manager import CompoundManager

class ChemicalCalculator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db_manager = DatabaseManager()
        self.elements_list = []
        self.current_formula_name = ""
        self.init_ui()
        self.load_common_compounds()

    def init_ui(self):
        self.setWindowTitle("Химический калькулятор молярной массы")
        self.setGeometry(100, 100, 1200, 800)
        self.setWindowIcon(self.create_icon())
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)
        self.tab_widget = QTabWidget()
        self.calculator_tab = self.create_calculator_tab()
        self.tab_widget.addTab(self.calculator_tab, "Калькулятор")
        self.elements_tab = ElementsBrowser(self.db_manager, self)
        self.tab_widget.addTab(self.elements_tab, "База элементов")
        self.compounds_tab = CompoundManager(self.db_manager, self)
        self.tab_widget.addTab(self.compounds_tab, "Мои соединения")
        main_layout.addWidget(self.tab_widget)
        self.create_menus()
        self.create_toolbar()
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Готов к работе")
        self.result_window = ResultWindow(self)

    def create_icon(self):
        pixmap = QPixmap(32, 32)
        pixmap.fill(QColor(0, 150, 200))
        return QIcon(pixmap)

    def create_menus(self):
        menubar = self.menuBar()
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
        help_menu = menubar.addMenu('Справка')
        about_action = QAction('О программе', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def create_toolbar(self):
        toolbar = QToolBar("Основные инструменты")
        self.addToolBar(toolbar)
        calculate_action = QAction('Рассчитать', self)
        calculate_action.triggered.connect(self.calculate_molar_mass)
        toolbar.addAction(calculate_action)
        toolbar.addSeparator()
        clear_action = QAction('Очистить', self)
        clear_action.triggered.connect(self.clear_elements_list)
        toolbar.addAction(clear_action)
        add_element_action = QAction('Элемент', self)
        add_element_action.triggered.connect(self.show_add_element_dialog)
        toolbar.addAction(add_element_action)

    def create_calculator_tab(self):
        tab = QWidget()
        layout = QHBoxLayout()
        splitter = QSplitter(Qt.Orientation.Horizontal)
        left_panel = self.create_input_panel()
        right_panel = self.create_elements_panel()
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([400, 800])
        layout.addWidget(splitter)
        tab.setLayout(layout)
        return tab

    def create_input_panel(self):
        panel = QWidget()
        layout = QVBoxLayout()
        input_group = QGroupBox("Добавление элемента")
        input_layout = QFormLayout()
        self.element_input = QLineEdit()
        self.element_input.setPlaceholderText("Введите символ элемента (C, H, O...)")
        self.element_input.textChanged.connect(self.on_element_input_changed)
        self.element_combo = QComboBox()
        self.element_combo.addItem("-- Выберите элемент --")
        elements = self.db_manager.get_all_elements()
        for symbol, name, mass, category in elements:
            self.element_combo.addItem(f"{symbol} - {name} ({mass})", symbol)
        self.element_combo.currentIndexChanged.connect(self.on_element_combo_changed)
        self.quantity_input = QLineEdit()
        self.quantity_input.setPlaceholderText("Введите количество")
        self.quantity_input.setText("1")
        self.add_element_button = QPushButton("Добавить элемент")
        self.add_element_button.clicked.connect(self.add_element_to_list)
        input_layout.addRow("Символ элемента:", self.element_input)
        input_layout.addRow("Быстрый выбор:", self.element_combo)
        input_layout.addRow("Количество:", self.quantity_input)
        input_layout.addRow(self.add_element_button)
        input_group.setLayout(input_layout)
        common_group = QGroupBox("Распространенные соединения")
        common_layout = QVBoxLayout()
        self.common_compounds_list = QListWidget()
        self.common_compounds_list.itemDoubleClicked.connect(self.load_common_compound)
        common_layout.addWidget(self.common_compounds_list)
        common_group.setLayout(common_layout)
        control_group = QGroupBox("Управление")
        control_layout = QVBoxLayout()
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Название соединения:"))
        self.compound_name_input = QLineEdit()
        self.compound_name_input.setPlaceholderText("Введите название соединения")
        name_layout.addWidget(self.compound_name_input)
        control_layout.addLayout(name_layout)
        self.calculate_button = QPushButton("Рассчитать молярную массу")
        self.calculate_button.clicked.connect(self.calculate_molar_mass)
        self.calculate_button.setEnabled(False)
        self.clear_button = QPushButton("Очистить список")
        self.clear_button.clicked.connect(self.clear_elements_list)
        self.add_new_element_button = QPushButton("Добавить новый элемент в базу")
        self.add_new_element_button.clicked.connect(self.show_add_element_dialog)
        control_layout.addWidget(self.calculate_button)
        control_layout.addWidget(self.clear_button)
        control_layout.addWidget(self.add_new_element_button)
        control_layout.addStretch()
        control_group.setLayout(control_layout)
        layout.addWidget(input_group)
        layout.addWidget(common_group)
        layout.addWidget(control_group)
        panel.setLayout(layout)
        return panel

    def create_elements_panel(self):
        panel = QWidget()
        layout = QVBoxLayout()
        title_label = QLabel("Состав вещества")
        title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.elements_table = QTableWidget()
        self.elements_table.setColumnCount(4)
        self.elements_table.setHorizontalHeaderLabels(["Элемент", "Символ", "Количество", "Атомная масса"])
        self.elements_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.elements_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        formula_group = QGroupBox("Текущая формула")
        formula_layout = QVBoxLayout()
        self.formula_display = QTextEdit()
        self.formula_display.setMaximumHeight(100)
        self.formula_display.setReadOnly(True)
        formula_layout.addWidget(self.formula_display)
        formula_group.setLayout(formula_layout)
        info_group = QGroupBox("Информация")
        info_layout = QVBoxLayout()
        self.info_label = QLabel("Добавьте элементы для расчета")
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        info_layout.addWidget(self.info_label)
        info_layout.addWidget(self.progress_bar)
        info_group.setLayout(info_layout)
        self.remove_button = QPushButton("Удалить выбранный элемент")
        self.remove_button.clicked.connect(self.remove_selected_element)
        layout.addWidget(title_label)
        layout.addWidget(self.elements_table)
        layout.addWidget(formula_group)
        layout.addWidget(info_group)
        layout.addWidget(self.remove_button)
        panel.setLayout(layout)
        return panel

    def load_common_compounds(self):
        compounds = self.db_manager.get_common_compounds()
        self.common_compounds_list.clear()
        for name, formula, molar_mass, description in compounds:
            item = QListWidgetItem(f"{name} - {formula} ({molar_mass} г/моль)")
            item.setData(Qt.ItemDataRole.UserRole, (name, formula))
            self.common_compounds_list.addItem(item)

    def load_common_compound(self, item):
        name, formula = item.data(Qt.ItemDataRole.UserRole)
        self.compound_name_input.setText(name)
        QMessageBox.information(self, "Информация", f"Соединение '{name}' загружено.\nФормула: {formula}")

    def on_element_input_changed(self, text):
        if text:
            self.element_input.setText(text.upper())

    def on_element_combo_changed(self, index):
        if index > 0:
            symbol = self.element_combo.itemData(index)
            self.element_input.setText(symbol)

    def add_element_to_list(self):
        symbol = self.element_input.text().strip()
        quantity_text = self.quantity_input.text().strip()
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
        element_data = self.db_manager.get_element_by_symbol(symbol)
        if not element_data:
            QMessageBox.warning(self, "Ошибка", f"Элемент '{symbol}' не найден в базе данных!")
            return
        self.elements_list.append((symbol, quantity))
        self.update_elements_table()
        self.update_formula_display()
        self.element_input.clear()
        self.quantity_input.setText("1")
        self.element_combo.setCurrentIndex(0)
        self.calculate_button.setEnabled(len(self.elements_list) > 0)
        self.status_bar.showMessage(f"Элемент {symbol} добавлен. Всего элементов: {len(self.elements_list)}")

    def remove_selected_element(self):
        current_row = self.elements_table.currentRow()
        if current_row >= 0 and current_row < len(self.elements_list):
            symbol, quantity = self.elements_list[current_row]
            self.elements_list.pop(current_row)
            self.update_elements_table()
            self.update_formula_display()
            self.calculate_button.setEnabled(len(self.elements_list) > 0)
            self.status_bar.showMessage(f"Элемент {symbol} удален")

    def update_elements_table(self):
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
        if self.elements_list:
            self.info_label.setText(f"Всего элементов: {len(self.elements_list)}\nПредварительная масса: {total_mass:.2f} г/моль")
        else:
            self.info_label.setText("Добавьте элементы для расчета")

    def update_formula_display(self):
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
        self.elements_list.clear()
        self.update_elements_table()
        self.update_formula_display()
        self.calculate_button.setEnabled(False)
        self.compound_name_input.clear()
        self.status_bar.showMessage("Список элементов очищен")

    def calculate_molar_mass(self):
        if not self.elements_list:
            QMessageBox.warning(self, "Ошибка", "Список элементов пуст!")
            return
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, len(self.elements_list))
        total_mass = 0.0
        elements_data = []
        for i, (symbol, quantity) in enumerate(self.elements_list):
            element_data = self.db_manager.get_element_by_symbol(symbol)
            if element_data:
                symbol_db, name, atomic_mass, category = element_data
                element_mass = atomic_mass * quantity
                total_mass += element_mass
                elements_data.append((symbol, quantity, element_mass, atomic_mass, name))
            self.progress_bar.setValue(i + 1)
            QApplication.processEvents()
        self.progress_bar.setVisible(False)
        formula_parts = []
        for symbol, quantity in self.elements_list:
            if quantity == 1:
                formula_parts.append(symbol)
            else:
                formula_parts.append(f"{symbol}₍{quantity}₎")
        formula = " + ".join(formula_parts)
        compound_name = self.compound_name_input.text().strip()
        if not compound_name:
            compound_name = "Неизвестное соединение"
        self.result_window.show_results(compound_name, formula, total_mass, elements_data)
        self.status_bar.showMessage(f"Расчет завершен: {total_mass:.2f} г/моль")

    def show_add_element_dialog(self):
        dialog = AddElementDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            element_data = dialog.get_element_data()
            if not all([element_data['symbol'], element_data['name']]):
                QMessageBox.warning(self, "Ошибка", "Символ и название должны быть заполнены!")
                return
            success = self.db_manager.add_element(
                element_data['symbol'],
                element_data['name'],
                element_data['atomic_mass'],
                element_data['atomic_number'],
                element_data['category'],
                element_data['discovered_year']
            )
            if success:
                QMessageBox.information(self, "Успех", f"Элемент {element_data['symbol']} успешно добавлен в базу данных!")
                self.element_combo.clear()
                self.element_combo.addItem("-- Выберите элемент --")
                elements = self.db_manager.get_all_elements()
                for symbol, name, mass, category in elements:
                    self.element_combo.addItem(f"{symbol} - {name} ({mass})", symbol)
                self.status_bar.showMessage(f"Элемент {element_data['symbol']} добавлен в базу")
            else:
                QMessageBox.warning(self, "Ошибка", f"Элемент с символом {element_data['symbol']} уже существует в базе данных!")

    def save_current_compound(self):
        if not self.elements_list:
            QMessageBox.warning(self, "Ошибка", "Нет элементов для сохранения!")
            return
        compound_name = self.compound_name_input.text().strip()
        if not compound_name:
            compound_name, ok = QInputDialog.getText(self, "Сохранение", "Введите название соединения:")
            if not ok or not compound_name:
                return
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
        success = self.db_manager.save_compound(compound_name, formula, total_mass, composition_str)
        if success:
            QMessageBox.information(self, "Успех", "Соединение успешно сохранено!")
            self.status_bar.showMessage(f"Соединение '{compound_name}' сохранено")
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось сохранить соединение!")

    def export_elements(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Экспорт элементов", "chemical_elements.csv", "CSV Files (*.csv)")
        if filename:
            success = self.db_manager.export_to_csv(filename)
            if success:
                QMessageBox.information(self, "Успех", "Элементы успешно экспортированы!")
                self.status_bar.showMessage(f"Элементы экспортированы в {filename}")
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось экспортировать элементы!")

    def import_elements(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Импорт элементов", "", "CSV Files (*.csv)")
        if filename:
            result = self.db_manager.import_from_csv(filename)
            if result > 0:
                QMessageBox.information(self, "Успех", f"Успешно импортировано {result} элементов!")
                self.elements_tab.refresh_elements()
                self.status_bar.showMessage(f"Импортировано {result} элементов")
            elif result == 0:
                QMessageBox.information(self, "Информация", "Нет новых элементов для импорта.")
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось импортировать элементы!")

    def show_about(self):
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
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    calculator = ChemicalCalculator()
    calculator.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()