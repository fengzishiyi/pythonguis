from PySide6.QtCore import QRect, QRectF, QSize, Qt, QTimer
from PySide6.QtGui import QBrush, QColor, QPainter
from PySide6.QtWidgets import QSizePolicy, QWidget


class EqualizerBar(QWidget):
    def __init__(self, bars, steps):
        super().__init__()

        self.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)

        if isinstance(steps, list):
            self.n_steps = len(steps) # 几层
            self.steps = steps

        elif isinstance(steps, int):
            self.n_steps = steps
            self.steps = ['red'] * steps

        else:
            raise TypeError('steps must be a list or int')


        self.n_bars = bars # 列数
        self._x_solid_percent = 0.8
        self._y_solid_percent = 0.8
        self._background_color = QColor('black') # 背景颜色
        self._padding = 25

        self._timer = None # 计时器
        self.setDecayFrequencyMs(100) # 衰弱频率
        self._decay = 10 # 衰弱频率

        self._vmin = 0
        self._vmax = 100

        self._values = [0.0] * bars # 列值 list

    def paintEvent(self, event):
        painter = QPainter(self) # 关联的设备device

        brush = QBrush()
        brush.setColor(self._background_color)
        brush.setStyle(Qt.BrushStyle.SolidPattern)
        rect = QRect(0, 0, painter.device().width(), painter.device().height())
        painter.fillRect(rect, brush)


        d_height = painter.device().height() - (self._padding * 2)
        d_width = painter.device().width() - (self._padding * 2)

        step_y = d_height / self.n_steps # 层高
        bar_height = step_y * self._y_solid_percent
        bar_height_space = step_y * (1 - self._x_solid_percent) / 2

        step_x = d_width / self.n_bars
        bar_width = step_x * self._x_solid_percent
        bar_width_space = step_x * (1 - self._y_solid_percent) / 2

        for b in range(self.n_bars):
            pc = (self._values[b] - self._vmin) / (self._vmax - self._vmin)
            n_steps_to_draw = int(pc * self.n_steps) # 画几层

            for n in range(n_steps_to_draw):
                brush.setColor(QColor(self.steps[n]))
                rect = QRectF(
                    self._padding + (step_x * b) + bar_width_space,
                    self._padding + d_height - ((1 + n) * step_y) + bar_height_space,
                    bar_width,
                    bar_height,
                )

                painter.fillRect(rect, brush)

        painter.end()

    # 组件尺寸
    def sizeHint(self):
        return QSize(20, 120) # 组件推荐尺寸

    # ?
    def _trigger_refresh(self):
        self.update()

    # 修改衰弱值
    def setDecay(self, f):
        self._decay = float(f)

    # 修改衰弱频率
    def setDecayFrequencyMs(self, ms):
        if self._timer:
            self._timer.stop()

        if ms:
            self._timer = QTimer()
            self._timer.setInterval(ms)
            self._timer.timeout.connect(self._decay_beat)
            self._timer.start()

    # 槽函数,衰弱,按照DecayFrequencyMs的频率
    def _decay_beat(self):
        self._values = [max(0, v - self._decay) for v in self._values]
        self.update()

    # 修改值
    def setValues(self, v):
        self._values = v
        self.update()

    # 返回值
    def values(self):
        return self._values

    # 修改范围
    def setRange(self, vmin, vmax):
        assert float(vmin) < float(vmax) # 错误就崩溃
        self._vmin, self._vmax = float(vmin), float(vmax)

    # 修改单色
    def setColor(self, color):
        self.steps = [color] * self.n_steps
        self.update()

    # 修改花色
    def setColors(self, colors):
        self.n_steps = len(colors)
        self.steps = colors
        self.update()

    # 修改边距
    def setBarPadding(self, i):
        self._padding = int(i)
        self.update()

    # 修改X比例
    def setBarSolidXPercent(self, f):
        self._x_solid_percent = float(f)
        self.update()

    # 修改Y比例
    def setBarSolidYPercent(self, f):
        self._y_solid_percent = float(f)
        self.update()

    # 修改背景颜色
    def setBackgroundColor(self, color):
        self._background_color = QColor(color)
        self.update()


