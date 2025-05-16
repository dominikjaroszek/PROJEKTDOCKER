import sys
import traceback
from typing import Optional, Tuple, Dict

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QGroupBox, QListWidget, QSplitter, QMessageBox, QComboBox,
    QListWidgetItem
)
from PyQt6.QtCore import Qt

from config import CONFIG
from database_manager import DatabaseManager
from uniterm_repository import UnitermRepository
from gui_widgets import UnitermWidget

class UnitermGenerator:
    def __init__(self):
        pass

    def generate_uniterm(self, left_part: str, right_part: str, separator: str) -> Tuple[str, str, str]:
        return left_part, right_part, separator

    def combine_replace_left(self, uniterm_i: Tuple[str, str, str], uniterm_ii: Tuple[str, str, str]) -> Tuple[str, str, str, str, str]:
        if not uniterm_i or not uniterm_ii:
            raise ValueError("Unitermy I i II nie zostały wygenerowane")
        _, uniterm_i_right_part, uniterm_i_separator = uniterm_i
        uniterm_ii_left_part, uniterm_ii_right_part, uniterm_ii_separator = uniterm_ii
        new_left_part = f"{uniterm_ii_left_part}{uniterm_ii_separator}{uniterm_ii_right_part}"
        return new_left_part, uniterm_i_right_part, uniterm_i_separator, new_left_part, 'left'

    def combine_replace_right(self, uniterm_i: Tuple[str, str, str], uniterm_ii: Tuple[str, str, str]) -> Tuple[str, str, str, str, str]:
        if not uniterm_i or not uniterm_ii:
            raise ValueError("Unitermy I i II nie zostały wygenerowane")
        uniterm_i_left_part, _, uniterm_i_separator = uniterm_i
        uniterm_ii_left_part, uniterm_ii_right_part, uniterm_ii_separator = uniterm_ii
        new_right_part = f"{uniterm_ii_left_part}{uniterm_ii_separator}{uniterm_ii_right_part}"
        return uniterm_i_left_part, new_right_part, uniterm_i_separator, new_right_part, 'right'

class DatabaseInteraction:
    def __init__(self, db_manager: DatabaseManager, uniterm_repo: UnitermRepository):
        self.db_manager = db_manager
        self.uniterm_repo = uniterm_repo

    def save_uniterm(self, data: Dict):
        if not self.uniterm_repo:
            raise Exception("Repozytorium jest niedostępne.")
        return self.uniterm_repo.save_uniterm(data)

    def get_all_uniterms(self):
        if not self.uniterm_repo:
            raise Exception("Repozytorium jest niedostępne.")
        return self.uniterm_repo.get_all_uniterms_for_list()

    def get_uniterm_by_id(self, uniterm_id: int):
        if not self.uniterm_repo:
            raise Exception("Repozytorium jest niedostępne.")
        return self.uniterm_repo.get_uniterm_by_id(uniterm_id)

    def delete_uniterm(self, uniterm_id: int):
        if not self.uniterm_repo:
            raise Exception("Repozytorium jest niedostępne.")
        return self.uniterm_repo.delete_uniterm(uniterm_id)

class AppState:
    def __init__(self):
        self.uniterm_i: Optional[Tuple[str, str, str]] = None
        self.uniterm_ii: Optional[Tuple[str, str, str]] = None
        self.is_database_available = False

class UnitermApp(QWidget):
    def __init__(self):
        super().__init__()
        self.app_state = AppState()
        self.db_available = False

        try:
            self.database_manager = DatabaseManager(CONFIG["db"])
            self.uniterm_repository = UnitermRepository(self.database_manager)
        except Exception as e:
            QMessageBox.critical(self, "Błąd Krytyczny DB",
                                 f"Nie można zainicjować menedżera bazy danych: {e}\n"
                                 "Aplikacja zostanie zamknięta.")
            self.database_manager = None
            self.uniterm_repository = None
            self.app_state.is_database_available = False

        if self.database_manager and self.uniterm_repository:
            self.init_db_check()
            self.db_interaction = DatabaseInteraction(self.database_manager, self.uniterm_repository)

        self.uniterm_generator = UnitermGenerator()
        self.init_ui()

        if self.app_state.is_database_available:
             self.refresh_uniterm_list()

    def init_db_check(self):
        if not self.database_manager:
             self.app_state.is_database_available = False
             return
        try:
            if self.database_manager.check_mysql_container(CONFIG["docker"]):
                if self.database_manager.setup_database_schema():
                    self.app_state.is_database_available = True
                    print("Database is available and schema checked/created.")
                else:
                    raise RuntimeError("Failed to configure the database schema.")
            else:
                 raise RuntimeError("MySQL container check failed or DB not responsive.")
        except Exception as e:
             if "Nie można zainicjować menedżera bazy danych" not in str(e):
                 QMessageBox.critical(self, "Krytyczny Błąd Inicjalizacji DB",
                                      f"Nie udało się połączyć lub skonfigurować bazy danych: {e}\n"
                                      "Funkcjonalność bazy danych będzie niedostępna.")
             self.app_state.is_database_available = False

    def init_ui(self):
        self.setWindowTitle('Uniterm')
        self.setGeometry(100, 100, 950, 700)

        main_layout = QHBoxLayout(self)
        splitter = QSplitter(Qt.Orientation.Horizontal)

        left_panel = self._create_left_panel()
        splitter.addWidget(left_panel)

        right_panel = self._create_right_panel()
        splitter.addWidget(right_panel)

        splitter.setSizes([580, 370])
        main_layout.addWidget(splitter)
        self.setLayout(main_layout)
    
    def _create_left_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(15)

        group_i = QGroupBox("Etap I")
        layout_i = QVBoxLayout()
        inputs_i = QHBoxLayout()
        self.input_i_left_part = QLineEdit(placeholderText="String 1")
        self.input_i_separator = QComboBox(editable=False)
        self.input_i_separator.setFixedWidth(50)
        self.input_i_separator.addItems([';', ':'])
        self.input_i_separator.setCurrentIndex(0)
        self.input_i_right_part = QLineEdit(placeholderText="String 2")
        inputs_i.addWidget(self.input_i_left_part)
        inputs_i.addWidget(QLabel("Separator:"))
        inputs_i.addWidget(self.input_i_separator)
        inputs_i.addWidget(self.input_i_right_part)
        layout_i.addLayout(inputs_i)
        self.btn_generate_uniterm_i = QPushButton("Generuj Uniterm I", clicked=self.generate_uniterm_i)
        layout_i.addWidget(self.btn_generate_uniterm_i)
        self.display_uniterm_i = UnitermWidget()
        layout_i.addWidget(self.display_uniterm_i)
        group_i.setLayout(layout_i)
        layout.addWidget(group_i)

        group_ii = QGroupBox("Etap II")
        layout_ii = QVBoxLayout()
        inputs_ii = QHBoxLayout()
        self.input_ii_left_part = QLineEdit(placeholderText="String 1")
        self.input_ii_separator = QComboBox(editable=False)
        self.input_ii_separator.setFixedWidth(50)
        self.input_ii_separator.addItems([';', ':'])
        self.input_ii_separator.setCurrentIndex(0)
        self.input_ii_right_part = QLineEdit(placeholderText="String 2")
        inputs_ii.addWidget(self.input_ii_left_part)
        inputs_ii.addWidget(QLabel("Separator:"))
        inputs_ii.addWidget(self.input_ii_separator)
        inputs_ii.addWidget(self.input_ii_right_part)
        layout_ii.addLayout(inputs_ii)
        self.btn_generate_uniterm_ii = QPushButton("Generuj Uniterm II", clicked=self.generate_uniterm_ii)
        layout_ii.addWidget(self.btn_generate_uniterm_ii)
        self.display_uniterm_ii = UnitermWidget()
        layout_ii.addWidget(self.display_uniterm_ii)
        group_ii.setLayout(layout_ii)
        layout.addWidget(group_ii)

        group_iii = QGroupBox("Etap III: Kombinacja / Wynik")
        layout_iii = QVBoxLayout()
        combine_btns = QHBoxLayout()
        self.btn_combine_replace_left = QPushButton("Podmień lewą część I przez II", clicked=self.combine_replace_left)
        self.btn_combine_replace_right = QPushButton("Podmień prawą część I przez II", clicked=self.combine_replace_right)
        combine_btns.addWidget(self.btn_combine_replace_left)
        combine_btns.addWidget(self.btn_combine_replace_right)
        layout_iii.addLayout(combine_btns)
        self.display_uniterm_iii = UnitermWidget()
        layout_iii.addWidget(self.display_uniterm_iii)
        group_iii.setLayout(layout_iii)
        layout.addWidget(group_iii)

        layout.addStretch()
        return panel

    def _create_right_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(5, 5, 5, 5)

        self.database_group = QGroupBox("Baza Danych Unitermów")
        db_layout = QVBoxLayout()

        self.uniterm_list_widget = QListWidget(alternatingRowColors=True)
        self.uniterm_list_widget.itemDoubleClicked.connect(self.load_selected_uniterm)
        db_layout.addWidget(self.uniterm_list_widget)

        db_actions_top_layout = QHBoxLayout()
        self.btn_refresh_database = QPushButton("Odśwież", clicked=self.refresh_uniterm_list)
        self.btn_load_from_database = QPushButton("Załaduj", clicked=self.load_selected_uniterm)
        self.btn_delete_from_database = QPushButton("Usuń", clicked=self.delete_selected_uniterm)
        self.btn_save_to_database = QPushButton("Zapisz Wynik", clicked=self.save_current_state)
        self.btn_save_to_database.setToolTip("Zapisz aktualny wynik z Etapu III do bazy")
        db_actions_top_layout.addWidget(self.btn_save_to_database)
        db_actions_top_layout.addWidget(self.btn_refresh_database)
        db_actions_top_layout.addWidget(self.btn_load_from_database)
        db_actions_top_layout.addWidget(self.btn_delete_from_database)
        db_layout.addLayout(db_actions_top_layout)

        self.database_group.setLayout(db_layout)
        layout.addWidget(self.database_group)

        if not self.app_state.is_database_available:
            self.database_group.setEnabled(False)
            self.database_group.setTitle(f"{self.database_group.title()} (Niedostępna)")
        else:
             self.database_group.setEnabled(True)

        return panel
    
    def _validate_inputs(self, left_input: QLineEdit, right_input: QLineEdit, sep_input: QComboBox) -> Optional[Tuple[str, str, str]]:
        left = left_input.text().strip()
        right = right_input.text().strip()
        sep = sep_input.currentText()

        if not left or not right:
            QMessageBox.warning(self, "Błąd danych", "Pola 'String 1' i 'String 2' muszą być wypełnione.")
            return None

        if not sep:
            QMessageBox.warning(self, "Błąd danych", "Musisz wybrać separator.")
            return None

        return left, right, sep

    def generate_uniterm_i(self):
        validated_data = self._validate_inputs(self.input_i_left_part, self.input_i_right_part, self.input_i_separator)
        if validated_data:
            left, right, sep = validated_data
            self.app_state.uniterm_i = self.uniterm_generator.generate_uniterm(left, right, sep)
            self.display_uniterm_i.setUniterm(left, right, sep)

    def generate_uniterm_ii(self):
        validated_data = self._validate_inputs(self.input_ii_left_part, self.input_ii_right_part, self.input_ii_separator)
        if validated_data:
            left, right, sep = validated_data
            self.app_state.uniterm_ii = self.uniterm_generator.generate_uniterm(left, right, sep)
            self.display_uniterm_ii.setUniterm(left, right, sep)

    def combine_replace_left(self):
        if not self.app_state.uniterm_i or not self.app_state.uniterm_ii:
            QMessageBox.warning(self, "Brak danych", "Najpierw wygeneruj lub załaduj Unitermy I i II.")
            return
        try:
            new_left, u1_right, u1_sep, nested_text, nested_side = self.uniterm_generator.combine_replace_left(self.app_state.uniterm_i, self.app_state.uniterm_ii)
            self.display_uniterm_iii.setUniterm(new_left, u1_right, u1_sep, nested_text, nested_side)
        except ValueError as e:
            QMessageBox.warning(self, "Błąd", str(e))

    def combine_replace_right(self):
        if not self.app_state.uniterm_i or not self.app_state.uniterm_ii:
            QMessageBox.warning(self, "Brak danych", "Najpierw wygeneruj lub załaduj Unitermy I i II.")
            return
        try:
            u1_left, new_right, u1_sep, nested_text, nested_side = self.uniterm_generator.combine_replace_right(self.app_state.uniterm_i, self.app_state.uniterm_ii)
            self.display_uniterm_iii.setUniterm(u1_left, new_right, u1_sep, nested_text, nested_side)
        except ValueError as e:
            QMessageBox.warning(self, "Błąd", str(e))

    def _get_current_state_for_db(self) -> Optional[Dict]:
        uniterm_iii_left_part = self.display_uniterm_iii._left_part
        uniterm_iii_right_part = self.display_uniterm_iii._right_part
        uniterm_iii_separator = self.display_uniterm_iii._separator
        full_string_iii = self.display_uniterm_iii.get_full_string()

        if not full_string_iii:
             return None

        uniterm_i_left_part, uniterm_i_right_part, uniterm_i_separator = self.app_state.uniterm_i if self.app_state.uniterm_i else ('', '', '')
        uniterm_ii_left_part, uniterm_ii_right_part, uniterm_ii_separator = self.app_state.uniterm_ii if self.app_state.uniterm_ii else ('', '', '')

        combination_type = 'none'
        if self.display_uniterm_iii._nested_side == 'left':
            combination_type = 'replace_left'
        elif self.display_uniterm_iii._nested_side == 'right':
            combination_type = 'replace_right'

        return {
            "left_part": uniterm_iii_left_part,
            "right_part": uniterm_iii_right_part,
            "separator": uniterm_iii_separator,
            "full_string": full_string_iii,
            "stage1_left": uniterm_i_left_part,
            "stage1_separator": uniterm_i_separator,
            "stage1_right": uniterm_i_right_part,
            "stage2_left": uniterm_ii_left_part,
            "stage2_separator": uniterm_ii_separator,
            "stage2_right": uniterm_ii_right_part,
            "combination_type": combination_type
        }

    def save_current_state(self):
        if not self.app_state.is_database_available or not self.db_interaction:
            QMessageBox.warning(self, "Baza Niedostępna", "Nie można zapisać, baza danych jest niedostępna lub nie zainicjowano repozytorium.")
            return
        current_state_dict = self._get_current_state_for_db()
        if current_state_dict is None:
            QMessageBox.warning(self, "Brak danych", "Wyświetlacz Etapu III jest pusty. Nic do zapisania.")
            return
        full_string_to_save = current_state_dict["full_string"]
        try:
            save_result = self.db_interaction.save_uniterm(current_state_dict)

            if save_result is not None:
                saved_uniterm_id, saved_full_string = save_result
                is_uniterm_exist = False
                for i in range(self.uniterm_list_widget.count()):
                    list_item = self.uniterm_list_widget.item(i)
                    list_item_data = list_item.data(Qt.ItemDataRole.UserRole)
                    if isinstance(list_item_data, int) and list_item_data == saved_uniterm_id:
                        is_uniterm_exist = True
                        break
                if is_uniterm_exist:
                    QMessageBox.information(self, "Uniterm Istnieje",
                                             f"Uniterm '{saved_full_string}' (ID: {saved_uniterm_id}) już istnieje.")
                else:
                    QMessageBox.information(self, "Zapisano",
                                             f"Zapisano nowy uniterm '{saved_full_string}' (ID: {saved_uniterm_id}).")
                    self.refresh_uniterm_list()
            else:
                QMessageBox.critical(self, "Błąd Zapisu", f"Nie udało się zapisać unitermu '{full_string_to_save}'. Sprawdź logi konsoli.")
        except Exception as e:
            traceback.print_exc()
            QMessageBox.critical(self, "Krytyczny Błąd Zapisu", f"Wystąpił nieoczekiwany błąd podczas zapisu: {e}")

    def refresh_uniterm_list(self):
        if not self.app_state.is_database_available or not self.db_interaction:
            self.uniterm_list_widget.clear()
            self.uniterm_list_widget.addItem("Baza danych niedostępna.")
            self.uniterm_list_widget.setEnabled(False)
            self.btn_load_from_database.setEnabled(False)
            self.btn_delete_from_database.setEnabled(False)
            if hasattr(self, 'database_group') and self.database_group.isEnabled():
                 self.database_group.setEnabled(False)
                 self.database_group.setTitle(f"{self.database_group.title().split('(')[0].strip()} (Niedostępna)")
            return

        if hasattr(self, 'database_group') and not self.database_group.isEnabled():
             self.database_group.setEnabled(True)
             self.database_group.setTitle(f"{self.database_group.title().split('(')[0].strip()} (MySQL + SQLAlchemy)")

        self.uniterm_list_widget.clear()
        try:
            uniterm_list_data = self.db_interaction.get_all_uniterms()

            if not uniterm_list_data:
                self.uniterm_list_widget.addItem("Brak zapisanych unitermów.")
                self.uniterm_list_widget.setEnabled(False)
                self.btn_load_from_database.setEnabled(False)
                self.btn_delete_from_database.setEnabled(False)
            else:
                self.uniterm_list_widget.setEnabled(True)
                self.btn_load_from_database.setEnabled(True)
                self.btn_delete_from_database.setEnabled(True)
                for uniterm_id, full_string in uniterm_list_data:
                    list_item = QListWidgetItem(full_string)
                    list_item.setData(Qt.ItemDataRole.UserRole, uniterm_id)
                    self.uniterm_list_widget.addItem(list_item)

        except Exception as e:
             traceback.print_exc()
             QMessageBox.critical(self, "Błąd Bazy Danych", f"Nie można odświeżyć listy unitermów: {e}")
             self.uniterm_list_widget.setEnabled(False)
             self.btn_load_from_database.setEnabled(False)
             self.btn_delete_from_database.setEnabled(False)

    def load_selected_uniterm(self):
        if not self.app_state.is_database_available or not self.db_interaction:
             QMessageBox.warning(self, "Baza Niedostępna", "Nie można załadować danych.")
             return

        selected_items = self.uniterm_list_widget.selectedItems()
        if not selected_items:
            return

        selected_item = selected_items[0]
        uniterm_id = selected_item.data(Qt.ItemDataRole.UserRole)

        if not isinstance(uniterm_id, int):
             QMessageBox.critical(self, "Błąd Danych", "Zaznaczony element nie zawiera poprawnego ID.")
             return

        try:
            loaded_data = self.db_interaction.get_uniterm_by_id(uniterm_id)

            if loaded_data is None:
                QMessageBox.warning(self, "Błąd Ładowania", f"Nie znaleziono unitermu o ID {uniterm_id} w bazie danych.")
                return

            stage1_left_part = loaded_data.get('stage1_left', '')
            stage1_right_part = loaded_data.get('stage1_right', '')
            stage1_separator = loaded_data.get('stage1_separator') or ';'
            stage1_separator_index = self.input_i_separator.findText(stage1_separator)
            self.input_i_left_part.setText(stage1_left_part)
            self.input_i_right_part.setText(stage1_right_part)
            self.input_i_separator.setCurrentIndex(stage1_separator_index if stage1_separator_index >= 0 else 0)
            self.app_state.uniterm_i = (stage1_left_part, stage1_right_part, stage1_separator) if stage1_left_part or stage1_right_part else None
            self.display_uniterm_i.setUniterm(stage1_left_part, stage1_right_part, stage1_separator)

            stage2_left_part = loaded_data.get('stage2_left', '')
            stage2_right_part = loaded_data.get('stage2_right', '')
            stage2_separator = loaded_data.get('stage2_separator') or ';'
            stage2_separator_index = self.input_ii_separator.findText(stage2_separator)
            self.input_ii_left_part.setText(stage2_left_part)
            self.input_ii_right_part.setText(stage2_right_part)
            self.input_ii_separator.setCurrentIndex(stage2_separator_index if stage2_separator_index >= 0 else 0)
            self.app_state.uniterm_ii = (stage2_left_part, stage2_right_part, stage2_separator) if stage2_left_part or stage2_right_part else None
            self.display_uniterm_ii.setUniterm(stage2_left_part, stage2_right_part, stage2_separator)

            uniterm_iii_left_part = loaded_data.get('left_part', '')
            uniterm_iii_right_part = loaded_data.get('right_part', '')
            uniterm_iii_separator = loaded_data.get('separator') or ';'
            combination_type = loaded_data.get('combination_type', 'none')
            nested_text, nested_side = None, None
            if combination_type == 'replace_left':
                nested_text, nested_side = uniterm_iii_left_part, 'left'
            elif combination_type == 'replace_right':
                nested_text, nested_side = uniterm_iii_right_part, 'right'
            self.display_uniterm_iii.setUniterm(uniterm_iii_left_part, uniterm_iii_right_part, uniterm_iii_separator, nested_text, nested_side)

        except Exception as e:
             traceback.print_exc()
             QMessageBox.critical(self, "Błąd Ładowania", f"Wystąpił nieoczekiwany błąd podczas ładowania danych: {e}")

    def delete_selected_uniterm(self):
        if not self.app_state.is_database_available or not self.db_interaction:
             QMessageBox.warning(self, "Baza Niedostępna", "Nie można usunąć danych.")
             return

        selected_items = self.uniterm_list_widget.selectedItems()
        if not selected_items:
             QMessageBox.warning(self, "Brak zaznaczenia", "Zaznacz uniterm do usunięcia.")
             return

        selected_item = selected_items[0]
        uniterm_id_to_delete = selected_item.data(Qt.ItemDataRole.UserRole)
        uniterm_text = selected_item.text()

        if not isinstance(uniterm_id_to_delete, int):
             QMessageBox.warning(self, "Błąd Danych", "Zaznaczony element nie zawiera poprawnego ID do usunięcia.")
             return

        reply = QMessageBox.question(self, "Potwierdzenie Usunięcia",
                                     f"Czy na pewno chcesz usunąć uniterm:\n{uniterm_text}?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            try:
                deleted = self.db_interaction.delete_uniterm(uniterm_id_to_delete)
                if deleted:
                    QMessageBox.information(self, "Usunięto", f"Uniterm (ID: {uniterm_id_to_delete}) został usunięty.")
                    self.refresh_uniterm_list()
                else:
                    QMessageBox.warning(self, "Błąd Usuwania", f"Nie udało się usunąć unitermu o ID {uniterm_id_to_delete}. Sprawdź logi.")
            except Exception as e:
                 traceback.print_exc()
                 QMessageBox.critical(self, "Krytyczny Błąd Usuwania", f"Nie można usunąć unitermu: {e}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = UnitermApp()
    main_window.show()
    sys.exit(app.exec())