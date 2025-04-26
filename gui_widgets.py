# gui_widgets.py

from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QPen, QFontMetrics, QColor, QFont
from PyQt6.QtCore import Qt, QRectF, QSize

class UnitermWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._left_part = ""
        self._right_part = ""
        self._separator = ""
        self._nested_text = None
        self._nested_side = None
        self.setMinimumHeight(70)
        self.setMinimumWidth(150)
        self.setFont(QFont("Arial", 10))

    def setUniterm(self, left, right, separator, nested_text=None, nested_side=None):
        self._left_part = str(left) if left is not None else ""
        self._right_part = str(right) if right is not None else ""
        self._separator = str(separator) if separator is not None else ""
        self._nested_text = nested_text
        self._nested_side = nested_side
        self.updateGeometry()
        self.update()

    def clear(self):
        self.setUniterm("", "", "", None, None)

    def sizeHint(self):
        fm = QFontMetrics(self.font())
        text = self.get_full_string()
        width = fm.horizontalAdvance(text) + 60 if text else self.minimumWidth()
        height = fm.height() * 3 + 35
        return QSize(max(width, self.minimumWidth()), max(height, self.minimumHeight()))

    def minimumSizeHint(self):
         return QSize(150, 70)

    def get_full_string(self):
        if not self._left_part and not self._right_part and not self._separator:
             return ""
        return f"{self._left_part} {self._separator} {self._right_part}" # Dodano spacje przed i po separatorze

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        full_text = self.get_full_string()
        if not full_text:
            painter.setPen(Qt.GlobalColor.gray)
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "")
            return

        font = self.font()
        fm = QFontMetrics(font)
        # Dodano zmienne do wyliczenia położeń
        space_width = fm.horizontalAdvance(" ")
        left_part_width = fm.horizontalAdvance(self._left_part) if self._left_part else 0
        separator_width = fm.horizontalAdvance(self._separator) if self._separator else 0
        right_part_width = fm.horizontalAdvance(self._right_part) if self._right_part else 0
        
        text_width = left_part_width + separator_width + right_part_width + space_width * 2 #Dwie spacje w sumie
        text_height = fm.height()
        widget_width = self.width()
        widget_height = self.height()

        text_x = (widget_width - text_width) / 2
        text_y = widget_height - fm.descent() - 10
        # Zmiana koloru tekstu na niebieski
        painter.setPen(QColor(66, 135, 245))  # RGB: (0, 0, 255) - niebieski
        painter.setFont(font)
        
        current_x_pos = text_x
        painter.drawText(int(current_x_pos), int(text_y), self._left_part)
        current_x_pos += left_part_width + space_width
        painter.drawText(int(current_x_pos), int(text_y), self._separator)
        current_x_pos += separator_width + space_width
        painter.drawText(int(current_x_pos), int(text_y), self._right_part)

        # Zmiana koloru łuku na niebieski
        main_arc_pen = QPen(QColor(66, 135, 245), 2)  # RGB: (0, 0, 255) - niebieski
        painter.setPen(main_arc_pen)
        arc_padding = 5
        main_arc_x = text_x - arc_padding
        main_arc_width = text_width + 2 * arc_padding
        main_arc_height = text_height * 1.8
        main_arc_y = text_y - fm.ascent() - main_arc_height + 5
        main_rect = QRectF(main_arc_x, main_arc_y, main_arc_width, main_arc_height)
        start_angle = 0 * 16
        span_angle = 180 * 16
        painter.drawArc(main_rect, start_angle, span_angle)

        if self._nested_text and self._nested_side:
            nested_text_width = fm.horizontalAdvance(self._nested_text)
            
            # Obliczenie przesunięcia separatora w lewo
            separator_shift = separator_width / 1.5 if separator_width > 0 else 0  # Przesunięcie o 1/2 szerokości separatora
            
            nested_arc_center_x = 0
            if self._nested_side == 'left' and left_part_width > 0:
                 nested_arc_center_x = text_x + (left_part_width / 2) - separator_shift
            elif self._nested_side == 'right' and right_part_width > 0:
                 nested_arc_center_x = text_x + left_part_width + space_width + separator_width + (right_part_width / 2) + separator_shift
            else:
                 nested_arc_center_x = text_x + (text_width / 2)


            nested_arc_pen = QPen(QColor(128, 128, 128), 1.5) # Domyślny szary nested arc
            painter.setPen(nested_arc_pen)
            nested_padding = 3
            nested_arc_width = nested_text_width + 2 * nested_padding
            nested_arc_height = text_height * 1.2
            nested_arc_x = nested_arc_center_x - (nested_arc_width / 2)
            nested_arc_y = main_arc_y + main_arc_height * 0.25
            nested_rect = QRectF(nested_arc_x, nested_arc_y, nested_arc_width, nested_arc_height)
            painter.drawArc(nested_rect, start_angle, span_angle)
