import os
import sys

from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QIcon, QPainter, QColor


def get_resource_path(relative_path: str) -> str:
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, "resources", relative_path)

def format_time_delta(time_delta) -> str:
    minutes, seconds = divmod(int(time_delta.total_seconds()), 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)

    day_str = ""
    if days > 0:
        day_str = f"{days} day, " if days == 1 else f"{days} days, "
    return f"{day_str}{hours:02}:{minutes:02}:{seconds:02}"

def create_badged_icon(base_icon: QIcon, radius = 24, color = QColor(255, 50, 50)) -> QIcon:
    pixmap = base_icon.pixmap(128, 128)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    x = pixmap.width() - radius - 2
    y = 2 + radius

    painter.setBrush(color)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(QPointF(x, y), radius, radius)
    painter.end()

    return QIcon(pixmap)
