from sqlalchemy import Column, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class UnitermModel(Base):
    __tablename__ = "uniterms"

    id = Column(Integer, primary_key=True, index=True)
    left_part = Column(Text, nullable=True)
    right_part = Column(Text, nullable=True)
    separator = Column(String(10), nullable=True)
    full_string = Column(String(768), index=True, nullable=False)# Changed from Text to String

    stage1_left = Column(Text, nullable=True)
    stage1_separator = Column(String(10), nullable=True)
    stage1_right = Column(Text, nullable=True)
    stage2_left = Column(Text, nullable=True)
    stage2_separator = Column(String(10), nullable=True)
    stage2_right = Column(Text, nullable=True)
    combination_type = Column(String(20), default='none')

    __table_args__ = (UniqueConstraint('full_string', name='unique_full_string'),)

    def __repr__(self):
        return f"<UnitermModel(id={self.id}, full_string='{self.full_string}')>"

    def get_origin_str(self) -> str:
        origin_s1 = f"S1({self.stage1_left}{self.stage1_separator}{self.stage1_right})" if self.stage1_left or self.stage1_right else ""
        origin_s2 = f"S2({self.stage2_left}{self.stage2_separator}{self.stage2_right})" if self.stage2_left or self.stage2_right else ""
        origin_type = f"Type({self.combination_type})" if self.combination_type != 'none' else ""
        origin_parts = filter(None, [origin_s1, origin_s2, origin_type])
        origin_str = f" Origin[{' '.join(origin_parts)}]" if any(origin_parts) else ""
        return origin_str

    def display_string(self) -> str:
        return f"ID: {self.id} - {self.full_string}"