from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QPen, QFontMetrics, QColor, QBrush, QFont
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
        width = fm.horizontalAdvance(text) + 40 if text else self.minimumWidth()
        height = fm.height() * 3 + 35
        return QSize(max(width, self.minimumWidth()), max(height, self.minimumHeight()))

    def minimumSizeHint(self):
         return QSize(150, 70)

    def get_full_string(self):
        if not self._left_part and not self._right_part and not self._separator:
             return ""
        return f"{self._left_part}{self._separator}{self._right_part}"

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
        text_width = fm.horizontalAdvance(full_text)
        text_height = fm.height()
        widget_width = self.width()
        widget_height = self.height()

        text_x = (widget_width - text_width) / 2
        text_y = widget_height - fm.descent() - 10
        painter.setPen(Qt.GlobalColor.black)
        painter.setFont(font)
        painter.drawText(int(text_x), int(text_y), full_text)

        main_arc_pen = QPen(Qt.GlobalColor.black, 2)
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
            left_part_width = fm.horizontalAdvance(self._left_part) if self._left_part else 0
            separator_width = fm.horizontalAdvance(self._separator) if self._separator else 0
            right_part_width = fm.horizontalAdvance(self._right_part) if self._right_part else 0

            left_part_start_x = text_x
            right_part_start_x = text_x + left_part_width + separator_width
            nested_arc_center_x = 0
            if self._nested_side == 'left' and left_part_width > 0:
                 nested_arc_center_x = left_part_start_x + (left_part_width / 2)
            elif self._nested_side == 'right' and right_part_width > 0:
                 nested_arc_center_x = right_part_start_x + (right_part_width / 2)
            else:
                 nested_arc_center_x = text_x + (text_width / 2)


            nested_arc_pen = QPen(Qt.GlobalColor.darkGray, 1.5)
            painter.setPen(nested_arc_pen)
            nested_padding = 3
            nested_arc_width = nested_text_width + 2 * nested_padding
            nested_arc_height = text_height * 1.2
            nested_arc_x = nested_arc_center_x - (nested_arc_width / 2)
            nested_arc_y = main_arc_y + main_arc_height * 0.25
            nested_rect = QRectF(nested_arc_x, nested_arc_y, nested_arc_width, nested_arc_height)
            painter.drawArc(nested_rect, start_angle, span_angle)