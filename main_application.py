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
from database_models import UnitermModel
from gui_widgets import UnitermWidget

class UnitermApp(QWidget):
    def __init__(self):
        super().__init__()
        self.uniterm_i: Optional[Tuple[str, str, str]] = None
        self.uniterm_ii: Optional[Tuple[str, str, str]] = None
        self.db_available = False

        try:
            self.db_manager = DatabaseManager(CONFIG["db"])
            self.uniterm_repo = UnitermRepository(self.db_manager)
        except Exception as e:
             QMessageBox.critical(self, "Błąd Krytyczny DB",
                                  f"Nie można zainicjować menedżera bazy danych: {e}\n"
                                  "Aplikacja zostanie zamknięta.")
             self.db_manager = None
             self.uniterm_repo = None
             self.db_available = False 


        if self.db_manager and self.uniterm_repo:
            self.init_db_check()
        else:
             self.db_available = False 

        self.init_ui() 

        if self.db_available:
             self.refresh_uniterm_list()

    def init_db_check(self):
        if not self.db_manager:
             self.db_available = False
             return
        try:
            if self.db_manager.check_mysql_container(CONFIG["docker"]):
                if self.db_manager.setup_database_schema():
                    self.db_available = True
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
             self.db_available = False

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
        self.input_i_left = QLineEdit(placeholderText="String 1")
        self.input_i_sep = QComboBox(editable=False)
        self.input_i_sep.setFixedWidth(50)
        self.input_i_sep.addItems([';', ':'])
        self.input_i_sep.setCurrentIndex(0) 
        self.input_i_right = QLineEdit(placeholderText="String 2")
        inputs_i.addWidget(self.input_i_left)
        inputs_i.addWidget(QLabel("Separator:"))
        inputs_i.addWidget(self.input_i_sep)
        inputs_i.addWidget(self.input_i_right)
        layout_i.addLayout(inputs_i)
        self.btn_gen_i = QPushButton("Generuj Uniterm I", clicked=self.generate_uniterm_i)
        layout_i.addWidget(self.btn_gen_i)
        self.display_i = UnitermWidget()
        layout_i.addWidget(self.display_i)
        group_i.setLayout(layout_i)
        layout.addWidget(group_i)

        group_ii = QGroupBox("Etap II")
        layout_ii = QVBoxLayout()
        inputs_ii = QHBoxLayout()
        self.input_ii_left = QLineEdit(placeholderText="String 1")
        self.input_ii_sep = QComboBox(editable=False)
        self.input_ii_sep.setFixedWidth(50)
        self.input_ii_sep.addItems([';', ':'])
        self.input_ii_sep.setCurrentIndex(0) 
        self.input_ii_right = QLineEdit(placeholderText="String 2")
        inputs_ii.addWidget(self.input_ii_left)
        inputs_ii.addWidget(QLabel("Separator:"))
        inputs_ii.addWidget(self.input_ii_sep)
        inputs_ii.addWidget(self.input_ii_right)
        layout_ii.addLayout(inputs_ii)
        self.btn_gen_ii = QPushButton("Generuj Uniterm II", clicked=self.generate_uniterm_ii)
        layout_ii.addWidget(self.btn_gen_ii)
        self.display_ii = UnitermWidget()
        layout_ii.addWidget(self.display_ii)
        group_ii.setLayout(layout_ii)
        layout.addWidget(group_ii)

        group_iii = QGroupBox("Etap III: Wynik")
        layout_iii = QVBoxLayout()
        combine_btns = QHBoxLayout()
        self.btn_combine_left = QPushButton("Podmień lewą część I przez II", clicked=self.combine_replace_left)
        self.btn_combine_right = QPushButton("Podmień prawą część I przez II", clicked=self.combine_replace_right)
        combine_btns.addWidget(self.btn_combine_left)
        combine_btns.addWidget(self.btn_combine_right)
        layout_iii.addLayout(combine_btns)
        self.display_iii = UnitermWidget()
        layout_iii.addWidget(self.display_iii)
        group_iii.setLayout(layout_iii)
        layout.addWidget(group_iii)

        layout.addStretch()
        return panel

    def _create_right_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(5, 5, 5, 5)

        self.db_group = QGroupBox("Baza Danych Unitermów") 
        db_layout = QVBoxLayout()

        self.uniterm_list = QListWidget(alternatingRowColors=True)
        self.uniterm_list.itemDoubleClicked.connect(self.load_selected_uniterm)
        db_layout.addWidget(self.uniterm_list)

        db_actions_layout = QHBoxLayout()
        self.btn_refresh_db = QPushButton("Odśwież", clicked=self.refresh_uniterm_list)
        self.btn_load_db = QPushButton("Załaduj", clicked=self.load_selected_uniterm)
        self.btn_delete_db = QPushButton("Usuń", clicked=self.delete_selected_uniterm)
        self.btn_save_iii = QPushButton("Zapisz Wynik", clicked=self.save_current_state)
        self.btn_save_iii.setToolTip("Zapisz aktualny wynik z Etapu III do bazy")
        db_actions_layout.addWidget(self.btn_refresh_db)
        db_actions_layout.addWidget(self.btn_load_db)
        db_actions_layout.addWidget(self.btn_delete_db)
        db_actions_layout.addWidget(self.btn_save_iii)
        db_layout.addLayout(db_actions_layout)

        self.db_group.setLayout(db_layout)
        layout.addWidget(self.db_group)

        if not self.db_available:
            self.db_group.setEnabled(False)
            self.db_group.setTitle(f"{self.db_group.title()} (Niedostępna)")
        else:
             self.db_group.setEnabled(True)
             self.db_group.setTitle(f"{self.db_group.title()} ")

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

    def _get_current_state_for_db(self) -> Optional[Dict]:
        l_iii = self.display_iii._left_part
        r_iii = self.display_iii._right_part
        s_iii = self.display_iii._separator
        full_string_iii = self.display_iii.get_full_string()

        if not full_string_iii:
             return None

        s1_l, s1_r, s1_s = self.uniterm_i if self.uniterm_i else ('', '', '')
        s2_l, s2_r, s2_s = self.uniterm_ii if self.uniterm_ii else ('', '', '')

        combo_type = 'none'
        if self.display_iii._nested_side == 'left':
            combo_type = 'replace_left'
        elif self.display_iii._nested_side == 'right':
            combo_type = 'replace_right'

        return {
            "l_iii": l_iii, "r_iii": r_iii, "s_iii": s_iii, "full_string_iii": full_string_iii,
            "s1_l": s1_l, "s1_s": s1_s, "s1_r": s1_r,
            "s2_l": s2_l, "s2_s": s2_s, "s2_r": s2_r,
            "combo_type": combo_type
        }

    def _clear_input_fields(self):
        self.input_i_left.clear()
        self.input_i_right.clear()
        self.input_ii_left.clear()
        self.input_ii_right.clear()
        self.input_i_sep.setCurrentIndex(0)
        self.input_ii_sep.setCurrentIndex(0)
        self.display_i.clear()
        self.display_ii.clear()
        self.display_iii.clear()
        self.uniterm_i = None
        self.uniterm_ii = None

    def generate_uniterm_i(self):
        validated_data = self._validate_inputs(self.input_i_left, self.input_i_right, self.input_i_sep)
        if validated_data:
            left, right, sep = validated_data
            self.uniterm_i = (left, right, sep) 
            self.display_i.setUniterm(left, right, sep)

    def generate_uniterm_ii(self):
        validated_data = self._validate_inputs(self.input_ii_left, self.input_ii_right, self.input_ii_sep)
        if validated_data:
            left, right, sep = validated_data
            self.uniterm_ii = (left, right, sep) 
            self.display_ii.setUniterm(left, right, sep)

    def combine_replace_left(self):
        if not self.uniterm_i or not self.uniterm_ii:
            QMessageBox.warning(self, "Brak danych", "Najpierw wygeneruj lub załaduj Unitermy I i II.")
            return
        _, u1_right, u1_sep = self.uniterm_i
        u2_left, u2_right, u2_sep = self.uniterm_ii

        new_left = f"{u2_left}{u2_sep}{u2_right}"
        self.display_iii.setUniterm(new_left, u1_right, u1_sep, nested_text=new_left, nested_side='left')

    def combine_replace_right(self):
        if not self.uniterm_i or not self.uniterm_ii:
            QMessageBox.warning(self, "Brak danych", "Najpierw wygeneruj lub załaduj Unitermy I i II.")
            return
        u1_left, _, u1_sep = self.uniterm_i
        u2_left, u2_right, u2_sep = self.uniterm_ii

        new_right = f"{u2_left}{u2_sep}{u2_right}"
        self.display_iii.setUniterm(u1_left, new_right, u1_sep, nested_text=new_right, nested_side='right')

    def save_current_state(self):
        if not self.db_available or not self.uniterm_repo:
            QMessageBox.warning(self, "Baza Niedostępna", "Nie można zapisać, baza danych jest niedostępna lub nie zainicjowano repozytorium.")
            return

        current_state_dict = self._get_current_state_for_db()
        if current_state_dict is None:
            QMessageBox.warning(self, "Brak danych", "Wyświetlacz Etapu III jest pusty. Nic do zapisania.")
            return

        full_string_to_save = current_state_dict["full_string_iii"]

        try:
            save_result = self.uniterm_repo.save_uniterm(current_state_dict)

            if save_result is not None:
                saved_id, saved_fs = save_result

                existing_on_list = False
                for i in range(self.uniterm_list.count()):
                    item = self.uniterm_list.item(i)
                    item_data = item.data(Qt.ItemDataRole.UserRole) 
                    if isinstance(item_data, int) and item_data == saved_id:
                        existing_on_list = True
                        break

                if existing_on_list:
                    QMessageBox.information(self, "Uniterm Istnieje",
                                             f"Uniterm '{saved_fs}' (ID: {saved_id}) już istnieje.")
                else:
                    QMessageBox.information(self, "Zapisano",
                                             f"Zapisano nowy uniterm '{saved_fs}' (ID: {saved_id}).")
                    self.refresh_uniterm_list() 
            else:
                QMessageBox.critical(self, "Błąd Zapisu", f"Nie udało się zapisać unitermu '{full_string_to_save}'. Sprawdź logi konsoli.")

        except Exception as e:
            traceback.print_exc()
            QMessageBox.critical(self, "Krytyczny Błąd Zapisu", f"Wystąpił nieoczekiwany błąd podczas zapisu: {e}")

    def refresh_uniterm_list(self):
        if not self.db_available or not self.uniterm_repo: 
            self.uniterm_list.clear()
            self.uniterm_list.addItem("Baza danych niedostępna.")
            self.uniterm_list.setEnabled(False)
            self.btn_load_db.setEnabled(False)
            self.btn_delete_db.setEnabled(False)
            if hasattr(self, 'db_group') and self.db_group.isEnabled():
                 self.db_group.setEnabled(False)
                 self.db_group.setTitle(f"{self.db_group.title().split('(')[0].strip()} (Niedostępna)")
            return

        if hasattr(self, 'db_group') and not self.db_group.isEnabled():
             self.db_group.setEnabled(True)
             self.db_group.setTitle(f"{self.db_group.title().split('(')[0].strip()} (MySQL + SQLAlchemy)")

        self.uniterm_list.clear()
        try:
            uniterm_list_data = self.uniterm_repo.get_all_uniterms_for_list()

            if not uniterm_list_data:
                self.uniterm_list.addItem("Brak zapisanych unitermów.")
                self.uniterm_list.setEnabled(False)
                self.btn_load_db.setEnabled(False)
                self.btn_delete_db.setEnabled(False)
            else:
                self.uniterm_list.setEnabled(True)
                self.btn_load_db.setEnabled(True)
                self.btn_delete_db.setEnabled(True)
                for item_id, display_text in uniterm_list_data:
                    item = QListWidgetItem(display_text)
                    item.setData(Qt.ItemDataRole.UserRole, item_id)
                    self.uniterm_list.addItem(item)

        except Exception as e:
             traceback.print_exc()
             QMessageBox.critical(self, "Błąd Bazy Danych", f"Nie można odświeżyć listy unitermów: {e}")
             self.uniterm_list.setEnabled(False)
             self.btn_load_db.setEnabled(False)
             self.btn_delete_db.setEnabled(False)

    def load_selected_uniterm(self):
        if not self.db_available or not self.uniterm_repo:
             QMessageBox.warning(self, "Baza Niedostępna", "Nie można załadować danych.")
             return

        selected_items = self.uniterm_list.selectedItems()
        if not selected_items:
            return

        selected_item = selected_items[0]
        item_id = selected_item.data(Qt.ItemDataRole.UserRole) 

        if not isinstance(item_id, int):
             QMessageBox.critical(self, "Błąd Danych", "Zaznaczony element nie zawiera poprawnego ID.")
             return

        try:
            loaded_data = self.uniterm_repo.get_uniterm_by_id(item_id)

            if loaded_data is None:
                QMessageBox.warning(self, "Błąd Ładowania", f"Nie znaleziono unitermu o ID {item_id} w bazie danych.")
                return

            s1_l = loaded_data.get('stage1_left', '') 
            s1_r = loaded_data.get('stage1_right', '')
            s1_s = loaded_data.get('stage1_separator') or ';' 
            idx_i = self.input_i_sep.findText(s1_s)
            self.input_i_left.setText(s1_l)
            self.input_i_right.setText(s1_r)
            self.input_i_sep.setCurrentIndex(idx_i if idx_i >= 0 else 0)
            self.uniterm_i = (s1_l, s1_r, s1_s) if s1_l or s1_r else None
            self.display_i.setUniterm(s1_l, s1_r, s1_s)

            s2_l = loaded_data.get('stage2_left', '')
            s2_r = loaded_data.get('stage2_right', '')
            s2_s = loaded_data.get('stage2_separator') or ';'
            idx_ii = self.input_ii_sep.findText(s2_s)
            self.input_ii_left.setText(s2_l)
            self.input_ii_right.setText(s2_r)
            self.input_ii_sep.setCurrentIndex(idx_ii if idx_ii >= 0 else 0)
            self.uniterm_ii = (s2_l, s2_r, s2_s) if s2_l or s2_r else None
            self.display_ii.setUniterm(s2_l, s2_r, s2_s)

            l_iii = loaded_data.get('left_part', '')
            r_iii = loaded_data.get('right_part', '')
            s_iii = loaded_data.get('separator') or ';'
            combo_type = loaded_data.get('combination_type', 'none')
            nested_text, nested_side = None, None
            if combo_type == 'replace_left':
                nested_text, nested_side = l_iii, 'left'
            elif combo_type == 'replace_right':
                nested_text, nested_side = r_iii, 'right'
            self.display_iii.setUniterm(l_iii, r_iii, s_iii, nested_text, nested_side)

        except Exception as e:
             traceback.print_exc()
             QMessageBox.critical(self, "Błąd Ładowania", f"Wystąpił nieoczekiwany błąd podczas ładowania danych: {e}")

    def delete_selected_uniterm(self):
        if not self.db_available or not self.uniterm_repo:
             QMessageBox.warning(self, "Baza Niedostępna", "Nie można usunąć danych.")
             return

        selected_items = self.uniterm_list.selectedItems()
        if not selected_items:
             QMessageBox.warning(self, "Brak zaznaczenia", "Zaznacz uniterm do usunięcia.")
             return

        selected_item = selected_items[0]
        item_id_to_delete = selected_item.data(Qt.ItemDataRole.UserRole)
        uniterm_text = selected_item.text()

        if not isinstance(item_id_to_delete, int):
             QMessageBox.warning(self, "Błąd Danych", "Zaznaczony element nie zawiera poprawnego ID do usunięcia.")
             return

        reply = QMessageBox.question(self, "Potwierdzenie Usunięcia",
                                     f"Czy na pewno chcesz usunąć uniterm:\n{uniterm_text}?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            try:
                deleted = self.uniterm_repo.delete_uniterm(item_id_to_delete)
                if deleted:
                    QMessageBox.information(self, "Usunięto", f"Uniterm (ID: {item_id_to_delete}) został usunięty.")
                    self.refresh_uniterm_list()
                else:
                    QMessageBox.warning(self, "Błąd Usuwania", f"Nie udało się usunąć unitermu o ID {item_id_to_delete}. Sprawdź logi.")
            except Exception as e:
                 traceback.print_exc()
                 QMessageBox.critical(self, "Krytyczny Błąd Usuwania", f"Nie można usunąć unitermu: {e}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = UnitermApp()
    main_window.show()
    sys.exit(app.exec())