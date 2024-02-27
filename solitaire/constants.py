import os

from PySide6.QtCore import QRect, QSize
from PySide6.QtGui import QImage

WINDOW_SIZE = 840, 600 # tuple

CARD_DIMENSIONS = QSize(80, 116)  # 二维对象
CARD_RECT = QRect(0, 0, 80, 116) #矩形
CARD_SPACING_X = 110 # 卡槽间隔
CARD_BACK = QImage(os.path.join('images','back.png'))

# DealTrigger->
DEAL_RECT = QRect(30, 30, 110, 140)

OFFSET_X = 50
OFFSET_Y = 50
WORK_STACK_Y = 200

SIDE_FACE = 0
SIDE_BACK = 1

BOUNCE_ENERGY = 0.8

# We store cards as numbers 1-13, since we only need
# to know their order for solitaire.
SUITS = ["C", "S", "H", "D"]