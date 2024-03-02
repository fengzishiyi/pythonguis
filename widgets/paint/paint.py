from PySide6.QtCore import QPoint, QPointF, Qt
from PySide6.QtGui import QBrush, QColor, QPainter, QPen, QPixmap
from PySide6.QtWidgets import QLabel


class PaintWidget(QLabel):
    def __init__(
            self,
            width,
            height,
            background='white',
            *args,
            **kwargs
    ):
        super().__init__(*args, **kwargs)
        pixmap = QPixmap(width,height)

        painter = QPainter(pixmap)
        brush = QBrush()
        brush.setColor(QColor(background))
        brush.setStyle(Qt.BrushStyle.SolidPattern)
        painter.fillRect(0, 0, pixmap.width(), pixmap.height(), brush)
        painter.end()
        self.setPixmap(pixmap)

        self.last_x, self.last_y = None, None
        self._pen_color = QColor('#000000')
        self._pen_width = 4

    def setPenColor(self, c):
        self._pen_color = QColor(c)

    def setPenWidth(self, w):
        self._pen_width = int(w)

    # position()返回相对子控件位置
    def mouseMoveEvent(self, e):
        if self.last_x is None:
            self.last_x = e.position().x()
            self.last_y = e.position().y()
            return # 第一次随便动，不画

        pixmap = self.pixmap()
        painter = QPainter(pixmap)
        p = painter.pen()
        p.setWidth(self._pen_width)
        p.setColor(self._pen_color)
        painter.setPen(p)
        painter.drawLine(
            QPointF(self.last_x, self.last_y),
            QPointF(e.position().x(),e.position().y()),
        )
        painter.end()
        self.setPixmap(pixmap)

        self.last_x = e.position().x()
        self.last_y = e.position().y()

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.RightButton:
            self._flood_fill_from_event(e)

    def mouseReleaseEvent(self, e):
        self.last_x = None
        self.last_y = None

    def _flood_fill_from_event(self, e):
        pass




