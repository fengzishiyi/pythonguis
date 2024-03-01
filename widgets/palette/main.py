import sys

from PySide6.QtWidgets import QApplication, QMainWindow

from palette import PaletteGrid, PaletteHorizontal, PaletteVertical


class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        palette = PaletteHorizontal('paired12')
        palette.selected.connect(self.show_selected_color) # 信号输出
        self.setCentralWidget(palette)
        self.show()

    def show_selected_color(self, c):
        print("Selected: {}".format(c))


app = QApplication(sys.argv)
w = Window()
w.show()
app.exec()