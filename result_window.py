from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QTableWidget, QTableWidgetItem, QPushButton,
                             QHeaderView, QGroupBox, QTextEdit, QFileDialog, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import datetime

class ResultWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Результаты расчета молярной массы")
        self.resize(700, 600)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.title_label = QLabel("Результаты расчета")
        self.title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.compound_info = QLabel()
        self.compound_info.setFont(QFont("Arial", 12))
        self.compound_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        formula_group = QGroupBox("Формула соединения")
        formula_layout = QVBoxLayout()
        self.formula_display = QTextEdit()
        self.formula_display.setReadOnly(True)
        self.formula_display.setMaximumHeight(80)
        formula_layout.addWidget(self.formula_display)
        formula_group.setLayout(formula_layout)
        result_group = QGroupBox("Результат расчета")
        result_layout = QVBoxLayout()
        self.mass_label = QLabel()
        self.mass_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        self.mass_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        result_layout.addWidget(self.mass_label)
        result_group.setLayout(result_layout)
        details_group = QGroupBox("Детали расчета")
        details_layout = QVBoxLayout()
        self.details_table = QTableWidget()
        self.details_table.setColumnCount(5)
        self.details_table.setHorizontalHeaderLabels(["Элемент", "Символ", "Количество", "Атомная масса", "Вклад"])
        self.details_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        details_layout.addWidget(self.details_table)
        details_group.setLayout(details_layout)
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Сохранить результат")
        self.save_button.clicked.connect(self.save_results)
        self.close_button = QPushButton("Закрыть")
        self.close_button.clicked.connect(self.close)
        button_layout.addWidget(self.save_button)
        button_layout.addStretch()
        button_layout.addWidget(self.close_button)
        layout.addWidget(self.title_label)
        layout.addWidget(self.compound_info)
        layout.addWidget(formula_group)
        layout.addWidget(result_group)
        layout.addWidget(details_group)
        layout.addLayout(button_layout)
        self.setLayout(layout)

    def show_results(self, compound_name, formula, total_mass, elements_data):
        self.title_label.setText(f"Результаты расчета: {compound_name}")
        self.compound_info.setText(f"Соединение: {compound_name}")
        self.formula_display.setPlainText(formula)
        self.mass_label.setText(f"Молярная масса: {total_mass:.4f} г/моль")
        self.details_table.setRowCount(len(elements_data))
        for row, (symbol, count, mass_contribution, atomic_mass, name) in enumerate(elements_data):
            self.details_table.setItem(row, 0, QTableWidgetItem(name))
            self.details_table.setItem(row, 1, QTableWidgetItem(symbol))
            self.details_table.setItem(row, 2, QTableWidgetItem(str(count)))
            self.details_table.setItem(row, 3, QTableWidgetItem(f"{atomic_mass:.4f}"))
            self.details_table.setItem(row, 4, QTableWidgetItem(f"{mass_contribution:.4f}"))
        self.exec()

    def save_results(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Сохранить результаты", "chemical_results.txt", "Text Files (*.txt)")
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
                QMessageBox.information(self, "Успех", "Результаты успешно сохранены!")
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Не удалось сохранить результаты: {str(e)}")