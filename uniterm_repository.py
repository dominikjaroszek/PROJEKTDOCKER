from typing import Dict, Optional, Tuple
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base
from database_manager import DatabaseManager

Base = declarative_base()

class UnitermModel(Base):
    __tablename__ = 'uniterms'

    id = Column(Integer, primary_key=True, autoincrement=True)
    left_part = Column(String(255), nullable=False)
    right_part = Column(String(255), nullable=False)
    separator = Column(String(10), nullable=False)
    full_string = Column(String(512), unique=True, nullable=False)
    stage1_left = Column(String(255), nullable=True)
    stage1_right = Column(String(255), nullable=True)
    stage1_separator = Column(String(10), nullable=True)
    stage2_left = Column(String(255), nullable=True)
    stage2_right = Column(String(255), nullable=True)
    stage2_separator = Column(String(10), nullable=True)
    combination_type = Column(String(50), nullable=True)

class UnitermRepository:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def save_new_uniterm(self, uniterm_data: Dict) -> Optional[Tuple[int, str]]:
        full_string_to_save = uniterm_data.get('full_string')
        if not full_string_to_save:
            print("Error: 'full_string' missing in data for save.")
            return None
        try:
            with self.db_manager.get_session() as session:
                uniterm_exists = session.query(UnitermModel).filter(UnitermModel.full_string == full_string_to_save).first()
                if uniterm_exists:
                    return (uniterm_exists.id, uniterm_exists.full_string)
                uniterm_to_save = UnitermModel(
                    left_part=uniterm_data.get('left_part'),
                    right_part=uniterm_data.get('right_part'),
                    separator=uniterm_data.get('separator'),
                    full_string=full_string_to_save,
                    stage1_left=uniterm_data.get('stage1_left'),
                    stage1_right=uniterm_data.get('stage1_right'),
                    stage1_separator=uniterm_data.get('stage1_separator'),
                    stage2_left=uniterm_data.get('stage2_left'),
                    stage2_right=uniterm_data.get('stage2_right'),
                    stage2_separator=uniterm_data.get('stage2_separator'),
                    combination_type=uniterm_data.get('combination_type')
                )
                session.add(uniterm_to_save)
                session.commit()
                return (uniterm_to_save.id, uniterm_to_save.full_string)
        except Exception as e:
            print(f"Error: save_new_uniterm: {e}")
            return None

    def save_uniterm(self, uniterm_data: Dict) -> Optional[Tuple[int, str]]:
        return self.save_new_uniterm(uniterm_data)

    def get_all_uniterms_for_list(self) -> Optional[list[Tuple[int, str]]]:
        try:
            with self.db_manager.get_session() as session:
                uniterms = session.query(UnitermModel).all()
                return [(uniterm.id, uniterm.full_string) for uniterm in uniterms] if uniterms else []
        except Exception as e:
            print(f"Error: get_all_uniterms: {e}")
            return None

    def get_uniterm_by_id(self, uniterm_id: int) -> Optional[Dict]:
        try:
            with self.db_manager.get_session() as session:
                uniterm = session.query(UnitermModel).filter_by(id=uniterm_id).first()
                if uniterm:
                     return {
                        'left_part': uniterm.left_part,
                        'right_part': uniterm.right_part,
                        'separator': uniterm.separator,
                        'full_string': uniterm.full_string,
                        'stage1_left': uniterm.stage1_left,
                        'stage1_right': uniterm.stage1_right,
                        'stage1_separator': uniterm.stage1_separator,
                        'stage2_left': uniterm.stage2_left,
                        'stage2_right': uniterm.stage2_right,
                        'stage2_separator': uniterm.stage2_separator,
                        'combination_type': uniterm.combination_type
                    }
                else:
                     return None
        except Exception as e:
             print(f"Error: get_uniterm_by_id: {e}")
             return None

    def delete_uniterm(self, uniterm_id: int) -> bool:
        try:
            with self.db_manager.get_session() as session:
                uniterm_to_delete = session.query(UnitermModel).filter_by(id=uniterm_id).first()
                if uniterm_to_delete:
                    session.delete(uniterm_to_delete)
                    session.commit()
                    return True
                else:
                    return False
        except Exception as e:
             print(f"Error: delete_uniterm: {e}")
             return False
