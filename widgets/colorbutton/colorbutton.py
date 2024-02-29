from PySide6.QtCore import Qt
from PySide6.QtCore import Signal as Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QColorDialog, QPushButton


class ColorButton(QPushButton):
    """
    自定义小组件，展示选择的颜色

    左键点击：展示所选颜色
    右键点击：还原默认颜色
    """
    """
    super(ColorButton, self).__init__()是指首先找到ColorButton的父类
    然后把类ColorButton的对象self转换为类QPushButton的对象，
    然后“被转换”的类QPushButton对象调用自己的init函数，
    其实简单理解就是子类把父类的__init__()放到自己的__init__()当中，
    这样子类就有了父类的__init__()的那些东西。
    """
    colorChanged = Signal(object) # 自定义信号

    def __init__(self, *args, color=None, **kwargs):
        super(ColorButton, self).__init__(*args, **kwargs)
        self.setObjectName('ColorButton')
        self._color = None
        self._default = color # 默认颜色
        self.pressed.connect(self.onColorPicker) # 信号写在这里

        self.setColor(self._default)

    def setColor(self, color):
        # print(None != 'red') -> True
        # # None表示空，但它不等于空字符串、空列表，也不等同于False
        if color != self._color:
            self._color = color
            self.colorChanged.emit(color) # 信号同步

        # 设置button颜色
        if self._color:
            self.setStyleSheet(f"#ColorButton {{background-color: {self._color};}}")
        else:
            self.setStyleSheet("")

    # 调用私有属性
    def color(self):
        return self._color

    def onColorPicker(self):
        dlg = QColorDialog(self)
        if self._color:
            dlg.setCurrentColor(QColor(self._color))

        if dlg.exec():
            self.setColor(dlg.currentColor().name()) # name()->'#ffffff'

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.RightButton:
            self.setColor(self._default)
        else:
            super().mousePressEvent(e)

        # return super().mousePressEvent(e)







