from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QTableWidget, QTableWidgetItem, QPushButton,
                             QLineEdit, QHeaderView, QMessageBox, QDialog,
                             QGroupBox, QComboBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from element_dialog import AddElementDialog

class ElementsBrowser(QWidget):
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.parent = parent
        self.init_ui()
        self.refresh_elements()

    def init_ui(self):
        layout = QVBoxLayout()
        title_label = QLabel("База химических элементов")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        search_group = QGroupBox("Поиск и фильтрация")
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск по названию или символу...")
        self.search_input.textChanged.connect(self.search_elements)
        self.category_combo = QComboBox()
        self.category_combo.addItem("Все категории")
        self.category_combo.addItems(["Металл", "Неметалл", "Щелочной металл",
                                      "Щелочноземельный", "Переходный металл",
                                      "Металлоид", "Галоген", "Инертный газ"])
        self.category_combo.currentTextChanged.connect(self.filter_by_category)
        search_layout.addWidget(QLabel("Поиск:"))
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(QLabel("Категория:"))
        search_layout.addWidget(self.category_combo)
        search_layout.addStretch()
        search_group.setLayout(search_layout)
        self.elements_table = QTableWidget()
        self.elements_table.setColumnCount(6)
        self.elements_table.setHorizontalHeaderLabels([
            "Символ", "Название", "Атомная масса", "Атомный номер", "Категория", "Год открытия"
        ])
        self.elements_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.elements_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.elements_table.doubleClicked.connect(self.edit_selected_element)
        control_layout = QHBoxLayout()
        self.add_button = QPushButton("Добавить элемент")
        self.add_button.clicked.connect(self.add_element)
        self.edit_button = QPushButton("Редактировать")
        self.edit_button.clicked.connect(self.edit_selected_element)
        self.delete_button = QPushButton("Удалить")
        self.delete_button.clicked.connect(self.delete_selected_element)
        self.refresh_button = QPushButton("Обновить")
        self.refresh_button.clicked.connect(self.refresh_elements)
        control_layout.addWidget(self.add_button)
        control_layout.addWidget(self.edit_button)
        control_layout.addWidget(self.delete_button)
        control_layout.addStretch()
        control_layout.addWidget(self.refresh_button)
        self.stats_label = QLabel()
        layout.addWidget(title_label)
        layout.addWidget(search_group)
        layout.addWidget(self.elements_table)
        layout.addLayout(control_layout)
        layout.addWidget(self.stats_label)
        self.setLayout(layout)

    def refresh_elements(self):
        elements = self.db_manager.get_all_elements()
        self.display_elements(elements)

    def display_elements(self, elements):
        self.elements_table.setRowCount(len(elements))
        for row, (symbol, name, atomic_mass, category) in enumerate(elements):
            full_data = self.db_manager.get_element_by_symbol(symbol)
            self.elements_table.setItem(row, 0, QTableWidgetItem(symbol))
            self.elements_table.setItem(row, 1, QTableWidgetItem(name))
            self.elements_table.setItem(row, 2, QTableWidgetItem(f"{atomic_mass:.4f}"))
            atomic_number = row + 1
            self.elements_table.setItem(row, 3, QTableWidgetItem(str(atomic_number)))
            self.elements_table.setItem(row, 4, QTableWidgetItem(category if category else "Не указана"))
            self.elements_table.setItem(row, 5, QTableWidgetItem("Неизвестно"))
        self.stats_label.setText(f"Всего элементов: {len(elements)}")

    def search_elements(self):
        query = self.search_input.text().strip()
        if query:
            elements = self.db_manager.search_elements(query)
            self.display_elements(elements)
        else:
            self.refresh_elements()

    def filter_by_category(self, category):
        if category == "Все категории":
            self.refresh_elements()
        else:
            all_elements = self.db_manager.get_all_elements()
            filtered = [elem for elem in all_elements if elem[3] == category]
            self.display_elements(filtered)

    def add_element(self):
        dialog = AddElementDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            element_data = dialog.get_element_data()
            success = self.db_manager.add_element(
                element_data['symbol'],
                element_data['name'],
                element_data['atomic_mass'],
                element_data['atomic_number'],
                element_data['category'],
                element_data['discovered_year']
            )
            if success:
                QMessageBox.information(self, "Успех", "Элемент успешно добавлен!")
                self.refresh_elements()
                if self.parent:
                    self.parent.status_bar.showMessage("Элемент добавлен в базу")
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось добавить элемент!")

    def edit_selected_element(self):
        current_row = self.elements_table.currentRow()
        if current_row >= 0:
            symbol = self.elements_table.item(current_row, 0).text()
            QMessageBox.information(self, "Редактирование", f"Редактирование элемента {symbol}")
        else:
            QMessageBox.warning(self, "Ошибка", "Выберите элемент для редактирования!")

    def delete_selected_element(self):
        current_row = self.elements_table.currentRow()
        if current_row >= 0:
            symbol = self.elements_table.item(current_row, 0).text()
            name = self.elements_table.item(current_row, 1).text()
            reply = QMessageBox.question(
                self, "Подтверждение",
                f"Вы уверены, что хотите удалить элемент {symbol} ({name})?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                success = self.db_manager.delete_element(symbol)
                if success:
                    QMessageBox.information(self, "Успех", "Элемент успешно удален!")
                    self.refresh_elements()
                    if self.parent:
                        self.parent.status_bar.showMessage("Элемент удален из базы")
                else:
                    QMessageBox.warning(self, "Ошибка", "Не удалось удалить элемент!")
        else:
            QMessageBox.warning(self, "Ошибка", "Выберите элемент для удаления!")