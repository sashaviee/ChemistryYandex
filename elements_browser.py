from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QTableWidget, QTableWidgetItem, QPushButton,
                             QLineEdit, QHeaderView, QMessageBox, QInputDialog,
                             QGroupBox, QComboBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class ElementsBrowser(QWidget):
    """Виджет для просмотра и управления базой элементов"""

    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.parent = parent
        self.init_ui()
        self.refresh_elements()

    def init_ui(self):
        """Инициализация пользовательского интерфейса"""
        layout = QVBoxLayout()

        # Заголовок
        title_label = QLabel("📚 База химических элементов")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setStyleSheet("color: #2c3e50; padding: 10px;")

        # Панель поиска и фильтрации
        search_group = QGroupBox("🔍 Поиск и фильтрация")
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

        # Таблица элементов
        self.elements_table = QTableWidget()
        self.elements_table.setColumnCount(6)
        self.elements_table.setHorizontalHeaderLabels([
            "Символ", "Название", "Атомная масса", "Атомный номер", "Категория", "Год открытия"
        ])
        self.elements_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.elements_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.elements_table.doubleClicked.connect(self.edit_selected_element)

        # Панель управления
        control_layout = QHBoxLayout()

        self.add_button = QPushButton("➕ Добавить элемент")
        self.add_button.clicked.connect(self.add_element)

        self.edit_button = QPushButton("✏️ Редактировать")
        self.edit_button.clicked.connect(self.edit_selected_element)

        self.delete_button = QPushButton("🗑️ Удалить")
        self.delete_button.clicked.connect(self.delete_selected_element)

        self.refresh_button = QPushButton("🔄 Обновить")
        self.refresh_button.clicked.connect(self.refresh_elements)

        control_layout.addWidget(self.add_button)
        control_layout.addWidget(self.edit_button)
        control_layout.addWidget(self.delete_button)
        control_layout.addStretch()
        control_layout.addWidget(self.refresh_button)

        # Статистика
        self.stats_label = QLabel()
        self.stats_label.setStyleSheet("color: #666; font-style: italic;")

        # Добавление виджетов в layout
        layout.addWidget(title_label)
        layout.addWidget(search_group)
        layout.addWidget(self.elements_table)
        layout.addLayout(control_layout)
        layout.addWidget(self.stats_label)

        self.setLayout(layout)

    def refresh_elements(self):
        """Обновление списка элементов"""
        elements = self.db_manager.get_all_elements()
        self.display_elements(elements)

    def display_elements(self, elements):
        """Отображение элементов в таблице"""
        self.elements_table.setRowCount(len(elements))

        for row, (symbol, name, atomic_mass, category) in enumerate(elements):
            # Получаем полные данные элемента для атомного номера и года открытия
            full_data = self.db_manager.get_element_by_symbol(symbol)

            self.elements_table.setItem(row, 0, QTableWidgetItem(symbol))
            self.elements_table.setItem(row, 1, QTableWidgetItem(name))
            self.elements_table.setItem(row, 2, QTableWidgetItem(f"{atomic_mass:.4f}"))

            # Для простоты, в этой демо-версии используем базовые данные
            # В реальном приложении нужно хранить атомный номер в базе
            atomic_number = row + 1  # Заглушка
            self.elements_table.setItem(row, 3, QTableWidgetItem(str(atomic_number)))

            self.elements_table.setItem(row, 4, QTableWidgetItem(category if category else "Не указана"))
            self.elements_table.setItem(row, 5, QTableWidgetItem("Неизвестно"))

        # Обновление статистики
        self.stats_label.setText(f"Всего элементов: {len(elements)}")

    def search_elements(self):
        """Поиск элементов"""
        query = self.search_input.text().strip()
        if query:
            elements = self.db_manager.search_elements(query)
            self.display_elements(elements)
        else:
            self.refresh_elements()

    def filter_by_category(self, category):
        """Фильтрация элементов по категории"""
        if category == "Все категории":
            self.refresh_elements()
        else:
            # В реальном приложении нужно добавить метод фильтрации по категории в DatabaseManager
            all_elements = self.db_manager.get_all_elements()
            filtered = [elem for elem in all_elements if elem[3] == category]
            self.display_elements(filtered)

    def add_element(self):
        """Добавление нового элемента"""
        from element_dialog import AddElementDialog
        dialog = AddElementDialog(self)
        if dialog.exec_() == QDialog.Accepted:
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
        """Редактирование выбранного элемента"""
        current_row = self.elements_table.currentRow()
        if current_row >= 0:
            symbol = self.elements_table.item(current_row, 0).text()
            QMessageBox.information(self, "Редактирование",
                                    f"Редактирование элемента {symbol}\n\nВ реальном приложении здесь будет открыт диалог редактирования.")
        else:
            QMessageBox.warning(self, "Ошибка", "Выберите элемент для редактирования!")

    def delete_selected_element(self):
        """Удаление выбранного элемента"""
        current_row = self.elements_table.currentRow()
        if current_row >= 0:
            symbol = self.elements_table.item(current_row, 0).text()
            name = self.elements_table.item(current_row, 1).text()

            reply = QMessageBox.question(
                self, "Подтверждение",
                f"Вы уверены, что хотите удалить элемент {symbol} ({name})?",
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.Yes:
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