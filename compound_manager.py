from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QTableWidget, QTableWidgetItem, QPushButton,
                             QHeaderView, QMessageBox, QGroupBox, QTextEdit)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class CompoundManager(QWidget):
    """Виджет для управления сохраненными соединениями"""

    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.parent = parent
        self.init_ui()
        self.load_saved_compounds()

    def init_ui(self):
        """Инициализация пользовательского интерфейса"""
        layout = QVBoxLayout()

        # Заголовок
        title_label = QLabel("💾 Мои сохраненные соединения")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setStyleSheet("color: #2c3e50; padding: 10px;")

        # Таблица соединений
        self.compounds_table = QTableWidget()
        self.compounds_table.setColumnCount(4)
        self.compounds_table.setHorizontalHeaderLabels([
            "Название", "Формула", "Молярная масса", "Дата создания"
        ])
        self.compounds_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.compounds_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.compounds_table.doubleClicked.connect(self.view_compound_details)

        # Детали соединения
        details_group = QGroupBox("🔍 Детали соединения")
        details_layout = QVBoxLayout()
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setMaximumHeight(150)
        details_layout.addWidget(self.details_text)
        details_group.setLayout(details_layout)

        # Панель управления
        control_layout = QHBoxLayout()

        self.view_button = QPushButton("👁️ Просмотреть")
        self.view_button.clicked.connect(self.view_compound_details)

        self.delete_button = QPushButton("🗑️ Удалить")
        self.delete_button.clicked.connect(self.delete_selected_compound)

        self.refresh_button = QPushButton("🔄 Обновить")
        self.refresh_button.clicked.connect(self.load_saved_compounds)

        control_layout.addWidget(self.view_button)
        control_layout.addWidget(self.delete_button)
        control_layout.addStretch()
        control_layout.addWidget(self.refresh_button)

        # Статистика
        self.stats_label = QLabel()
        self.stats_label.setStyleSheet("color: #666; font-style: italic;")

        # Добавление виджетов в layout
        layout.addWidget(title_label)
        layout.addWidget(self.compounds_table)
        layout.addWidget(details_group)
        layout.addLayout(control_layout)
        layout.addWidget(self.stats_label)

        self.setLayout(layout)

    def load_saved_compounds(self):
        """Загрузка сохраненных соединений"""
        compounds = self.db_manager.get_saved_compounds()
        self.display_compounds(compounds)

    def display_compounds(self, compounds):
        """Отображение соединений в таблице"""
        self.compounds_table.setRowCount(len(compounds))

        for row, (name, formula, molar_mass, composition, created_date) in enumerate(compounds):
            self.compounds_table.setItem(row, 0, QTableWidgetItem(name))
            self.compounds_table.setItem(row, 1, QTableWidgetItem(formula))
            self.compounds_table.setItem(row, 2, QTableWidgetItem(f"{molar_mass:.4f} г/моль"))
            self.compounds_table.setItem(row, 3, QTableWidgetItem(created_date))

        # Обновление статистики
        self.stats_label.setText(f"Всего сохраненных соединений: {len(compounds)}")
        self.details_text.clear()

    def view_compound_details(self):
        """Просмотр деталей выбранного соединения"""
        current_row = self.compounds_table.currentRow()
        if current_row >= 0:
            name = self.compounds_table.item(current_row, 0).text()
            formula = self.compounds_table.item(current_row, 1).text()
            molar_mass = self.compounds_table.item(current_row, 2).text()
            created_date = self.compounds_table.item(current_row, 3).text()

            # Получаем полные данные соединения
            compounds = self.db_manager.get_saved_compounds()
            if current_row < len(compounds):
                full_name, full_formula, full_molar_mass, composition, full_date = compounds[current_row]

                details_text = f"""
                <h3>{full_name}</h3>
                <b>Формула:</b> {full_formula}<br>
                <b>Молярная масса:</b> {full_molar_mass:.4f} г/моль<br>
                <b>Дата создания:</b> {full_date}<br>
                <b>Состав:</b> {composition}
                """
                self.details_text.setHtml(details_text)
        else:
            QMessageBox.warning(self, "Ошибка", "Выберите соединение для просмотра!")

    def delete_selected_compound(self):
        """Удаление выбранного соединения"""
        current_row = self.compounds_table.currentRow()
        if current_row >= 0:
            name = self.compounds_table.item(current_row, 0).text()

            reply = QMessageBox.question(
                self, "Подтверждение",
                f"Вы уверены, что хотите удалить соединение '{name}'?",
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                # В реальном приложении нужно добавить метод удаления в DatabaseManager
                QMessageBox.information(self, "Информация",
                                        "В реальном приложении здесь будет удаление соединения из базы данных.")
                # self.load_saved_compounds()  # Обновить список после удаления
        else:
            QMessageBox.warning(self, "Ошибка", "Выберите соединение для удаления!")