from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QTableWidget, QTableWidgetItem, QPushButton,
                             QHeaderView, QGroupBox, QTextEdit, QFileDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import datetime


class ResultWindow(QDialog):
    """Окно для отображения результатов расчета"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Результаты расчета молярной массы")
        self.resize(700, 600)
        self.init_ui()

    def init_ui(self):
        """Инициализация пользовательского интерфейса"""
        layout = QVBoxLayout()

        # Заголовок
        self.title_label = QLabel("Результаты расчета")
        self.title_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("color: #2c3e50; padding: 15px;")

        # Информация о соединении
        self.compound_info = QLabel()
        self.compound_info.setFont(QFont("Arial", 12))
        self.compound_info.setAlignment(Qt.AlignCenter)

        # Формула
        formula_group = QGroupBox("Формула соединения")
        formula_layout = QVBoxLayout()
        self.formula_display = QTextEdit()
        self.formula_display.setReadOnly(True)
        self.formula_display.setMaximumHeight(80)
        self.formula_display.setStyleSheet("""
            QTextEdit {
                background-color: #e8f5e8;
                border: 2px solid #4CAF50;
                border-radius: 5px;
                padding: 10px;
                font-family: 'Courier New';
                font-size: 16px;
                font-weight: bold;
                color: #2E7D32;
            }
        """)
        formula_layout.addWidget(self.formula_display)
        formula_group.setLayout(formula_layout)

        # Результат
        result_group = QGroupBox("Результат расчета")
        result_layout = QVBoxLayout()
        self.mass_label = QLabel()
        self.mass_label.setFont(QFont("Arial", 18, QFont.Bold))
        self.mass_label.setAlignment(Qt.AlignCenter)
        self.mass_label.setStyleSheet("""
            QLabel {
                color: #D32F2F;
                padding: 20px;
                background-color: #ffebee;
                border-radius: 10px;
                border: 2px solid #f44336;
            }
        """)
        result_layout.addWidget(self.mass_label)
        result_group.setLayout(result_layout)

        # Детали расчета
        details_group = QGroupBox("🔍 Детали расчета")
        details_layout = QVBoxLayout()
        self.details_table = QTableWidget()
        self.details_table.setColumnCount(5)
        self.details_table.setHorizontalHeaderLabels(["Элемент", "Символ", "Количество", "Атомная масса", "Вклад"])
        self.details_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.details_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #cccccc;
                border-radius: 5px;
            }
            QHeaderView::section {
                background-color: #3498db;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
        """)
        details_layout.addWidget(self.details_table)
        details_group.setLayout(details_layout)

        # Кнопки
        button_layout = QHBoxLayout()

        self.save_button = QPushButton("Сохранить результат")
        self.save_button.clicked.connect(self.save_results)
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #9C27B0;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7B1FA2;
            }
        """)

        self.close_button = QPushButton("Закрыть")
        self.close_button.clicked.connect(self.close)
        self.close_button.setStyleSheet("""
            QPushButton {
                background-color: #757575;
                color: white;
                border: none;
                padding: 10px 30px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #616161;
            }
        """)

        button_layout.addWidget(self.save_button)
        button_layout.addStretch()
        button_layout.addWidget(self.close_button)

        # Добавление виджетов в layout
        layout.addWidget(self.title_label)
        layout.addWidget(self.compound_info)
        layout.addWidget(formula_group)
        layout.addWidget(result_group)
        layout.addWidget(details_group)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def show_results(self, compound_name, formula, total_mass, elements_data):
        """Отображение результатов расчета"""
        self.title_label.setText(f"Результаты расчета: {compound_name}")
        self.compound_info.setText(f"Соединение: {compound_name}")
        self.formula_display.setPlainText(formula)
        self.mass_label.setText(f"Молярная масса: {total_mass:.4f} г/моль")

        # Заполнение таблицы деталями
        self.details_table.setRowCount(len(elements_data))
        for row, (symbol, count, mass_contribution, atomic_mass, name) in enumerate(elements_data):
            self.details_table.setItem(row, 0, QTableWidgetItem(name))
            self.details_table.setItem(row, 1, QTableWidgetItem(symbol))
            self.details_table.setItem(row, 2, QTableWidgetItem(str(count)))
            self.details_table.setItem(row, 3, QTableWidgetItem(f"{atomic_mass:.4f}"))
            self.details_table.setItem(row, 4, QTableWidgetItem(f"{mass_contribution:.4f}"))

        self.exec_()

    def save_results(self):
        """Сохранение результатов в файл"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Сохранить результаты", "chemical_results.txt", "Text Files (*.txt)"
        )

        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as file:
                    file.write("РЕЗУЛЬТАТЫ РАСЧЕТА МОЛЯРНОЙ МАССЫ\n")
                    file.write("=" * 50 + "\n")
                    file.write(f"Дата расчета: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    file.write(f"Соединение: {self.compound_info.text().replace('Соединение: ', '')}\n")
                    file.write(f"Формула: {self.formula_display.toPlainText()}\n")
                    file.write(f"Молярная масса: {self.mass_label.text().replace('Молярная масса: ', '')}\n\n")

                    file.write("ДЕТАЛИ РАСЧЕТА:\n")
                    file.write("-" * 50 + "\n")
                    file.write(f"{'Элемент':<15} {'Символ':<10} {'Кол-во':<10} {'Ат. масса':<12} {'Вклад':<12}\n")
                    file.write("-" * 50 + "\n")

                    for row in range(self.details_table.rowCount()):
                        element = self.details_table.item(row, 0).text()
                        symbol = self.details_table.item(row, 1).text()
                        count = self.details_table.item(row, 2).text()
                        atomic_mass = self.details_table.item(row, 3).text()
                        contribution = self.details_table.item(row, 4).text()

                        file.write(f"{element:<15} {symbol:<10} {count:<10} {atomic_mass:<12} {contribution:<12}\n")

                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.information(self, "Успех", "Результаты успешно сохранены!")
            except Exception as e:

                QMessageBox.warning(self, "Ошибка", f"Не удалось сохранить результаты: {str(e)}")
