from typing import List, Optional, Dict, Tuple 
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from database_models import UnitermModel
from database_manager import DatabaseManager

class UnitermRepository:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def get_all_uniterms_for_list(self) -> List[Tuple[int, str]]:
        """Retrieves only ID and display string for list display."""
        results = []
        try:
            with self.db_manager.get_session() as session:
                query_result = session.query(
                        UnitermModel.id,
                        UnitermModel.full_string
                    ).order_by(UnitermModel.id).all()

                results = [(id_val, f"ID: {id_val} - {fs_val}") for id_val, fs_val in query_result]

            return results 
        except SQLAlchemyError as e:
            print(f"Error fetching uniterm list data: {e}")
            return []
        except Exception as e:
             print(f"Unexpected error fetching uniterm list data: {e}")
             return []

    def save_uniterm(self, uniterm_data: Dict) -> Optional[Tuple[int, str]]:
        full_string_to_save = uniterm_data.get('full_string_iii')
        if not full_string_to_save:
            print("Error: 'full_string_iii' missing in data for save.")
            return None
        try:
            with self.db_manager.get_session() as session:
                existing = session.query(UnitermModel).filter(UnitermModel.full_string == full_string_to_save).first()
                if existing:
                    return (existing.id, existing.full_string)
                new_uniterm = UnitermModel(
                    left_part=uniterm_data.get('l_iii'),
                    right_part=uniterm_data.get('r_iii'),
                    separator=uniterm_data.get('s_iii'),
                    full_string=full_string_to_save,
                    stage1_left=uniterm_data.get('s1_l'),
                    stage1_separator=uniterm_data.get('s1_s'),
                    stage1_right=uniterm_data.get('s1_r'),
                    stage2_left=uniterm_data.get('s2_l'),
                    stage2_separator=uniterm_data.get('s2_s'),
                    stage2_right=uniterm_data.get('s2_r'),
                    combination_type=uniterm_data.get('combo_type', 'none')
                )
                session.add(new_uniterm)
                session.flush()
                if new_uniterm.id is None:
                     session.rollback()
                     print("Error: Could not obtain ID for new uniterm after flush.")
                     return None
                saved_id = new_uniterm.id
                saved_fs = new_uniterm.full_string
                return (saved_id, saved_fs) 
        except IntegrityError as e:
            print(f"Error saving uniterm (Integrity Constraint): {e}")
            try:
                with self.db_manager.get_session() as session:
                    existing = session.query(UnitermModel.id, UnitermModel.full_string)\
                                      .filter(UnitermModel.full_string == full_string_to_save).first()
                    return (existing[0], existing[1]) if existing else None
            except Exception as find_e:
                 print(f"Error trying to find existing uniterm after IntegrityError: {find_e}")
                 return None
        except SQLAlchemyError as e:
            print(f"Error saving uniterm '{full_string_to_save}': {e}")
            return None
        except Exception as e:
             print(f"Unexpected error saving uniterm '{full_string_to_save}': {e}")
             return None

    def update_uniterm(self, uniterm_id: int, uniterm_data: Dict) -> bool:
        new_full_string = uniterm_data.get('full_string_iii')
        if not new_full_string:
            print("Error: 'full_string_iii' is required for update.")
            return False
        try:
            with self.db_manager.get_session() as session:
                uniterm_to_update = session.get(UnitermModel, uniterm_id)
                if not uniterm_to_update:
                    print(f"Warning: No uniterm found with ID: {uniterm_id} to update.")
                    return False
                if uniterm_to_update.full_string != new_full_string:
                    conflict = session.query(UnitermModel).filter(
                        UnitermModel.full_string == new_full_string,
                        UnitermModel.id != uniterm_id
                    ).first()
                    if conflict:
                        print(f"Error updating uniterm ID {uniterm_id}: 'full_string' ('{new_full_string}') conflict with ID {conflict.id}.")
                        return False
                uniterm_to_update.left_part = uniterm_data.get('l_iii')
                uniterm_to_update.right_part = uniterm_data.get('r_iii')
                uniterm_to_update.separator = uniterm_data.get('s_iii')
                uniterm_to_update.full_string = new_full_string
                uniterm_to_update.stage1_left = uniterm_data.get('s1_l')
                uniterm_to_update.stage1_separator = uniterm_data.get('s1_s')
                uniterm_to_update.stage1_right = uniterm_data.get('s1_r')
                uniterm_to_update.stage2_left = uniterm_data.get('s2_l')
                uniterm_to_update.stage2_separator = uniterm_data.get('s2_s')
                uniterm_to_update.stage2_right = uniterm_data.get('s2_r')
                uniterm_to_update.combination_type = uniterm_data.get('combo_type', 'none')
                return True
        except IntegrityError as e:
             print(f"Error updating uniterm ID {uniterm_id} (Integrity Constraint): {e}")
             return False
        except SQLAlchemyError as e:
            print(f"Error updating uniterm ID {uniterm_id}: {e}")
            return False
        except Exception as e:
             print(f"Unexpected error updating uniterm ID {uniterm_id}: {e}")
             return False

    def get_uniterm_by_id(self, uniterm_id: int) -> Optional[Dict]:
        try:
            with self.db_manager.get_session() as session:
                uniterm = session.get(UnitermModel, uniterm_id)
                if uniterm:
                    data = {
                        "id": uniterm.id,
                        "left_part": uniterm.left_part,
                        "right_part": uniterm.right_part,
                        "separator": uniterm.separator,
                        "full_string": uniterm.full_string,
                        "stage1_left": uniterm.stage1_left,
                        "stage1_separator": uniterm.stage1_separator,
                        "stage1_right": uniterm.stage1_right,
                        "stage2_left": uniterm.stage2_left,
                        "stage2_separator": uniterm.stage2_separator,
                        "stage2_right": uniterm.stage2_right,
                        "combination_type": uniterm.combination_type,
                    }
                    return data
                else:
                    return None
        except SQLAlchemyError as e:
            print(f"Error fetching uniterm with id {uniterm_id}: {e}")
            return None
        except Exception as e:
             print(f"Unexpected error fetching uniterm ID {uniterm_id}: {e}")
             return None

    def check_uniterm_exists(self, full_string: str) -> Optional[int]:
        if not full_string:
            return None
        try:
            with self.db_manager.get_session() as session:
                result = session.query(UnitermModel.id).filter(UnitermModel.full_string == full_string).first()
                return result.id if result else None
        except SQLAlchemyError as e:
            print(f"Error checking for existing uniterm '{full_string}': {e}")
            return None
        except Exception as e:
             print(f"Unexpected error checking uniterm '{full_string}': {e}")
             return None

    def delete_uniterm(self, uniterm_id: int) -> bool:
        try:
            with self.db_manager.get_session() as session:
                uniterm_to_delete = session.get(UnitermModel, uniterm_id)
                if uniterm_to_delete:
                    session.delete(uniterm_to_delete)
                    return True
                else:
                    print(f"No uniterm found with ID: {uniterm_id} to delete.")
                    return False
        except SQLAlchemyError as e:
            print(f"Error deleting uniterm with ID {uniterm_id}: {e}")
            return False
        except Exception as e:
             print(f"Unexpected error deleting uniterm ID {uniterm_id}: {e}")
             return False