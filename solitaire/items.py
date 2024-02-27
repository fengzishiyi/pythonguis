import os

import constants
from PySide6.QtCore import QObject, QPointF, QRectF, Qt, Signal
from PySide6.QtGui import QBrush, QColor, QPen, QPixmap
from PySide6.QtWidgets import (
    QGraphicsItem,
    QGraphicsPixmapItem,
    QGraphicsRectItem,
)


class Signals(QObject):
    comlpete = Signal()
    clicked = Signal()
    doubleclicked = Signal()


class Card(QGraphicsPixmapItem):
    def __init__(self, value, suit):
        super().__init__()

        self.signals = Signals()

        self.stack = None
        self.child = None

        self.value = value
        self.suit = suit
        self.side = None  # face | back

        self.vector = None
        # 边界,可动,限制移动
        self.setShapeMode(QGraphicsPixmapItem.ShapeMode.BoundingRectShape)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)


        self.load_images()

    # 加载正反面
    def load_images(self):
        self.face = QPixmap(os.path.join('cards', '%s%s.png' % (self.value, self.suit)))

        self.back = QPixmap(os.path.join('images', 'back.png'))

    # 显示正面
    def turn_face_up(self):
        self.side = constants.SIDE_FACE  # 0
        self.setPixmap(self.face)

    # 显示反面
    def turn_back_up(self):
        self.side = constants.SIDE_BACK
        self.setPixmap(self.back)

    # 正面 -> True
    @property
    def is_face_up(self):
        return self.side == constants.SIDE_FACE
    # 颜色 -> red | black
    @property
    def color(self):
        return 'r' if self.suit in ('H', 'D') else 'b'

    def mousePressEvent(self, event):
        # back & first -> turn face
        if not self.is_face_up and self.stack.cards[-1] == self:
            self.turn_face_up()
            event.accept()
            return
        # stack & not first, 第一张下面的牌
        # workStack -> face_up & stack & not first
        if self.stack and not self.stack.is_free_card(self):
            # 让父类继续接受事件,isMovable
            event.ignore()
            return

        self.stack.activate()

        event.accept()

        super().mouseReleaseEvent(event)

    def mouseReleaseEvent(self, event):
        self.stack.deactivate()

        items = self.collidingItems() # 获取与当前项碰撞的图形项列表。
        if items:
            for item in items:
                if(isinstance(item, Card) and item.stack != self.stack) or (
                    isinstance(item, StackBase) and item != self.stack
                ):
                    if item.stack.is_valid_drop(self):
                        cards = self.stack.remove_card(self) # children for workstack
                        item.stack.add_cards(cards)
                        break

        self.stack.update()

        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        if self.stack.is_free_card(self):
            self.signals.doubleclicked.emit()
            event.accept()

        super().mouseDoubleClickEvent(event)

# 父类
class StackBase(QGraphicsRectItem):
    def __init__(self):
        super().__init__()

        self.setRect(QRectF(constants.CARD_RECT)) #卡牌大小
        self.setZValue(-1) # 栈位

        self.cards = [] # 卡牌表

        self.stack = self
        self.setup()
        self.reset()

    def setup(self):
        pass

    def reset(self):
        self.remove_all_cards()

    def update(self):
        for n, card in enumerate(self.cards):
            card.setPos(self.pos() + QPointF(n * self.offset_x, n * self.offset_y))
            card.setZValue(n)

    def activate(self):
        pass

    def deactivate(self):
        pass

    def add_card(self, card, update=True):
        card.stack = self # 更新卡牌的所属栈
        self.cards.append(card) #更新该栈的卡牌
        if update:
            self.update()

    def add_cards(self, cards):
        for card in cards:
            self.add_card(card, update=False)
        self.update() # 结束更新视图

    def remove_card(self, card):
        card.stack = None
        self.cards.remove(card)
        self.update()
        return [card] # 返回孩子列表

    # 清空
    def remove_all_cards(self):
        for card in self.cards[:]:
            card.stack = None
        self.cards = []

    def is_valid_drop(self, card):
        return True

    def is_free_card(self, card):
        return False

# 桥牌
class DeckStack(StackBase):
    offset_x = -0.2  # 偏移
    offset_y = -0.3

    restack_counter = 0

    # 重置
    def reset(self):
        super().reset() # remove_all_cards
        self.restack_counter = 0
        self.set_color(Qt.GlobalColor.green)

    # 在栈中放置桥牌
    def stack_cards(self, cards):
        for card in cards:
            self.add_card(card)
            card.turn_back_up()

    # 能否刷新回合
    def can_restack(self, n_rounds=3) -> bool:
        # 无限 | 仍在回合内
        return n_rounds is None or self.restack_counter < n_rounds - 1

    # 当一轮结束后显示回合状态 绿 | 红
    def update_stack_status(self, n_rounds):
        # 轮数用尽,5->3
        if not self.can_restack(n_rounds):
            self.set_color(Qt.GlobalColor.red)
        else:
            self.set_color(Qt.GlobalColor.green)

    # 下一回合
    def restack(self, fromstack):
        self.restack_counter += 1

        for card in fromstack.cards[::-1]:
            fromstack.remove_card(card)
            self.add_card(card)
            card.turn_back_up()

    # 取牌
    def take_top_card(self):
        try:
            card = self.cards[-1]
            self.remove_card(card)
            return card
        except IndexError:
            pass


    # 设置颜色
    def set_color(self, color):
        color = QColor(color)
        color.setAlpha(50)  # 不透明度(0,255)
        brush = QBrush(color)
        self.setBrush(brush)
        self.setPen(QPen(Qt.PenStyle.NoPen))  # 没有线,无边框填充

    # 禁止落牌
    def is_valid_drop(self, card):
        return False

# 展示桥牌
class DealStack(StackBase):
    offset_x = 20
    offset_y = 0

    spread_from = 0

    def setup(self):
        self.setPen(QPen(Qt.PenStyle.NoPen))
        color = QColor(Qt.GlobalColor.black)
        color.setAlpha(50)
        brush = QBrush(color)
        self.setBrush(brush)

    def reset(self):
        super().reset() # remove_all_cards
        self.spread_from = 0

    # 禁止落牌
    def is_valid_drop(self, card):
        return False

    # 自由牌: 第一张
    def is_free_card(self, card):
        return card == self.cards[-1]

    # 更新视图
    def update(self):
        offset_x = 0
        for n, card in enumerate(self.cards):
            card.setPos(self.pos() + QPointF(offset_x, 0))
            card.setZValue(n)

            if n >= self.spread_from:
                offset_x = offset_x + self.offset_x


class WorkStack(StackBase):
    offset_x = 0
    offset_y = 15
    offset_y_back = 8

    def setup(self):
        self.setPen(QPen(Qt.PenStyle.NoPen))
        color = QColor(Qt.GlobalColor.black)
        color.setAlpha(50)
        brush = QBrush(color)
        self.setBrush(brush)

    def activate(self):
        self.setZValue(1000)

    def deactivate(self):
        self.setZValue(-1)

    def is_valid_drop(self, card):
        # 该栈空
        if not self.cards:
            return True

        if card.color != self.cards[-1].color and card.value == self.cards[-1].value - 1:
            return True

        return False

    # 自由牌: 正面必第一张
    def is_free_card(self, card):
        return card.is_face_up

    def add_card(self, card, update=True):
        if self.cards:
            card.setParentItem(self.cards[-1])
        else:
            card.setParentItem(self)

        super().add_card(card, update=update)

    def remove_card(self, card):
        index = self.cards.index(card)
        self.cards, cards = self.cards[:index], self.cards[index:]

        for card in cards:
            card.setParentItem(None)
            card.stack = None

        self.update()
        return cards

    def remove_all_cards(self):
        for card in self.cards[:]:
            card.setParentItem(None)
            card.stack = None
        self.cards = []

    def update(self):
        self.stack.setZValue(-1)
        offset_y = 0
        for n, card in enumerate(self.cards):
            card.setPos(QPointF(0, offset_y))

            if card.is_face_up:
                offset_y = self.offset_y
            else:
                offset_y = self.offset_y_back


class DropStack(StackBase):
    offset_x = -0.2
    offset_y = -0.3

    suit = None
    value = 0

    def setup(self):
        self.signals = Signals()
        color = QColor(Qt.GlobalColor.blue)
        color.setAlpha(50)
        pen = QPen(color)
        pen.setWidth(5)
        self.setPen(pen)

    def reset(self):
        super().reset()
        self.suit = None
        self.value = 0

    def is_valid_drop(self, card):
        if (self.suit is None or card.suit == self.suit) and \
                (card.value == self.value + 1):
            return True

        return False

    def add_card(self, card, update=True):
        super().add_card(card, update=update)
        self.suit = card.suit # 栈花色更新
        self.value = self.cards[-1].value #栈顶值更新

        if self.is_complete:
            self.signals.comlpete.emit()

    # 好像没用
    def remove_card(self, card):
        super().remove_card(card)
        self.value = self.cards[-1].value if self.cards else 0

    @property
    def is_complete(self):
        return self.value == 13

# 发牌器
class DealTrigger(QGraphicsRectItem):
    def __init__(self):
        super().__init__()
        self.setRect(QRectF(constants.DEAL_RECT))
        self.setZValue(1000)

        pen = QPen(Qt.PenStyle.NoPen)
        self.setPen(pen)

        self.signals = Signals()

    def mousePressEvent(self, event):
        self.signals.clicked.emit()


class AnimationCover(QGraphicsRectItem):
    def __init__(self):
        super().__init__()
        self.setRect(QRectF(0, 0, *constants.WINDOW_SIZE))
        self.setZValue(5000)
        pen = QPen(Qt.PenStyle.NoPen)
        self.setPen(pen)

    def mousePressEvent(self, event):
        event.accept()  #
