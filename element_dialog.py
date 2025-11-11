from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLabel,
                             QLineEdit, QPushButton, QDoubleSpinBox,
                             QSpinBox, QHBoxLayout, QMessageBox, QComboBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class AddElementDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить новый элемент")
        self.setModal(True)
        self.resize(400, 350)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        title_label = QLabel("Добавление нового химического элемента")
        title_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        form_layout = QFormLayout()
        self.symbol_input = QLineEdit()
        self.symbol_input.setMaxLength(3)
        self.symbol_input.setPlaceholderText("Например: C, H, O")
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Например: Углерод")
        self.atomic_mass_input = QDoubleSpinBox()
        self.atomic_mass_input.setRange(0.1, 500.0)
        self.atomic_mass_input.setDecimals(4)
        self.atomic_mass_input.setSingleStep(0.1)
        self.atomic_mass_input.setValue(12.011)
        self.atomic_number_input = QSpinBox()
        self.atomic_number_input.setRange(1, 200)
        self.atomic_number_input.setValue(6)
        self.category_combo = QComboBox()
        categories = ["", "Металл", "Неметалл", "Щелочной металл", "Щелочноземельный",
                      "Переходный металл", "Постпереходный металл", "Металлоид",
                      "Галоген", "Инертный газ", "Лантаноид", "Актиноид"]
        self.category_combo.addItems(categories)
        self.discovered_year_input = QSpinBox()
        self.discovered_year_input.setRange(-5000, 2100)
        self.discovered_year_input.setValue(1800)
        self.discovered_year_input.setSpecialValueText("Неизвестно")
        form_layout.addRow("Символ элемента*:", self.symbol_input)
        form_layout.addRow("Название*:", self.name_input)
        form_layout.addRow("Атомная масса*:", self.atomic_mass_input)
        form_layout.addRow("Атомный номер*:", self.atomic_number_input)
        form_layout.addRow("Категория:", self.category_combo)
        form_layout.addRow("Год открытия:", self.discovered_year_input)
        hint_label = QLabel("* - обязательные поля")
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Добавить")
        self.add_button.clicked.connect(self.validate_and_accept)
        self.cancel_button = QPushButton("Отмена")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.cancel_button)
        layout.addWidget(title_label)
        layout.addLayout(form_layout)
        layout.addWidget(hint_label)
        layout.addLayout(button_layout)
        self.setLayout(layout)

    def validate_and_accept(self):
        symbol = self.symbol_input.text().strip()
        name = self.name_input.text().strip()
        if not symbol:
            QMessageBox.warning(self, "Ошибка", "Введите символ элемента!")
            return
        if not name:
            QMessageBox.warning(self, "Ошибка", "Введите название элемента!")
            return
        if len(symbol) > 3:
            QMessageBox.warning(self, "Ошибка", "Символ элемента не может быть длиннее 3 символов!")
            return
        self.accept()

    def get_element_data(self):
        category = self.category_combo.currentText()
        if category == "":
            category = None
        discovered_year = self.discovered_year_input.value()
        if discovered_year == -5000:
            discovered_year = None
        return {
            'symbol': self.symbol_input.text().strip(),
            'name': self.name_input.text().strip(),
            'atomic_mass': self.atomic_mass_input.value(),
            'atomic_number': self.atomic_number_input.value(),
            'category': category,
            'discovered_year': discovered_year
        }