import os
import random
import sys

import constants
from items import (
    AnimationCover,
    Card,
    DealStack,
    DealTrigger,
    DeckStack,
    DropStack,
    WorkStack,
)
from PySide6.QtCore import QPoint, QPointF, QRectF, Qt, QTimer
from PySide6.QtGui import QAction, QActionGroup, QBrush, QIcon, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QGraphicsPixmapItem,
    QGraphicsScene,
    QGraphicsView,
    QMainWindow,
    QMessageBox,
)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # view初始化,设置
        view = QGraphicsView()
        view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        # scene初始化
        self.scene = QGraphicsScene()
        self.scene.setSceneRect(
            QRectF(0, 0, constants.WINDOW_SIZE[0]-10, constants.WINDOW_SIZE[1] - 50)
        )
        # scene背景图片
        felt = QBrush(QPixmap(os.path.join('images','felt.png')))
        self.scene.setBackgroundBrush(felt)
        # scene字样
        name = QGraphicsPixmapItem()
        name.setPixmap(QPixmap(os.path.join('images','name.png')))
        name.setPos(QPointF(170,375))
        self.scene.addItem(name)
        # view -> scene
        view.setScene(self.scene)

        self.timer = QTimer()
        self.timer.setInterval(500) # 间隔0.5秒动一次
        self.timer.timeout.connect(self.win_animation) # 信号写在这里

        self.animation_event_cover = AnimationCover()
        self.scene.addItem(self.animation_event_cover)

        menu = self.menuBar().addMenu('&Game')

        deal_action = QAction(
            QIcon(os.path.join('images','playing-card.png')),
            'Deal...',
            self,
        )
        deal_action.triggered.connect(self.restart_game)
        menu.addAction(deal_action)

        menu.addSeparator()

        deal1_action = QAction('1 card', self)
        deal1_action.setCheckable(True)
        deal1_action.triggered.connect(lambda: self.set_deal_n(1))
        menu.addAction(deal1_action)

        deal3_action = QAction("3 card", self)
        deal3_action.setCheckable(True)
        deal3_action.setChecked(True)
        deal3_action.triggered.connect(lambda: self.set_deal_n(3))

        menu.addAction(deal3_action)

        # 设置组,单选
        dealgroup = QActionGroup(self)
        dealgroup.addAction(deal1_action)
        dealgroup.addAction(deal3_action)
        dealgroup.setExclusive(True)

        menu.addSeparator()

        rounds3_action = QAction('3 rounds',self)
        rounds3_action.setCheckable(True)
        rounds3_action.setChecked(True)
        rounds3_action.triggered.connect(lambda: self.set_rounds_n(3))
        menu.addAction(rounds3_action)

        rounds5_action = QAction("5 rounds", self)
        rounds5_action.setCheckable(True)
        rounds5_action.triggered.connect(lambda: self.set_rounds_n(5))
        menu.addAction(rounds5_action)

        roundsu_action = QAction("Unlimited rounds", self)
        roundsu_action.setCheckable(True)
        roundsu_action.triggered.connect(lambda: self.set_rounds_n(None))
        menu.addAction(roundsu_action)

        roundgroup = QActionGroup(self)
        roundgroup.addAction(rounds3_action)
        roundgroup.addAction(rounds5_action)
        roundgroup.addAction(roundsu_action)
        roundgroup.setExclusive(True)

        menu.addSeparator()

        quit_action = QAction('Quit', self)
        quit_action.triggered.connect(self.quit)
        menu.addAction(quit_action)

        # 牌堆
        self.deck = []
        self.deal_n = 3 # 每轮发牌数
        self.rounds_n = 3 # 回合数

        # 牌堆加牌
        for suit in constants.SUITS:
            for value in range(1,14):
                card = Card(value, suit)
                self.deck.append(card)
                self.scene.addItem(card)
                card.signals.doubleclicked.connect( # 信号写在这里
                    lambda card=card: self.auto_drop_card(card)
                )

        self.setCentralWidget(view)
        self.setFixedSize(*constants.WINDOW_SIZE)

        # 桥牌堆
        self.deckstack = DeckStack()
        self.deckstack.setPos(constants.OFFSET_X, constants.OFFSET_Y)
        self.scene.addItem(self.deckstack)

        # 工作栈
        self.works = []

        for n in range(7):
            stack = WorkStack()
            stack.setPos(
                constants.OFFSET_X + constants.CARD_SPACING_X * n,
                constants.WORK_STACK_Y,
            )
            self.scene.addItem(stack)
            self.works.append(stack)

        # 归栈
        self.drops = []

        for n in range(4):
            stack = DropStack()
            stack.setPos(
                constants.OFFSET_X + constants.CARD_SPACING_X * (3 + n),
                constants.OFFSET_Y,
            )
            stack.signals.comlpete.connect(self.check_win_condition) # 信号写在这里

            self.scene.addItem(stack)
            self.drops.append(stack)

        # 发牌栈
        self.dealstack = DealStack()
        self.dealstack.setPos(
            constants.OFFSET_X + constants.CARD_SPACING_X, constants.OFFSET_Y
        )
        self.scene.addItem(self.dealstack)

        # 发牌器
        dealtrigger = DealTrigger()
        dealtrigger.signals.clicked.connect(self.deal) # 信号写在这里
        self.scene.addItem(dealtrigger)

        self.shuffle_and_stack()
        
        self.setWindowTitle("Saltaire")
        self.show()

    # menu.deal_action ->
    # 弹窗询问
    def restart_game(self):
        reply = QMessageBox.question(
            self,
            'Deal again',
            'Are you sure you want to start a new game?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.shuffle_and_stack()

    # menu.quit_action ->
    def quit(self):
        self.close()

    # menu.deal_action->
    def set_deal_n(self, n):
        self.deal_n = n

    # menu.round_action->
    def set_rounds_n(self, n):
        self.rounds_n = n
        self.deckstack.update_stack_status(self.rounds_n)

    # 洗牌
    def shuffle_and_stack(self):
        # 停止动画
        self.timer.stop()
        self.animation_event_cover.hide()

        # 重置栈
        for stack in [self.deckstack, self.dealstack] + self.drops + self.works:
            stack.reset()

        # 洗牌, random.shuffle()仅打乱顺序
        random.shuffle(self.deck)

        # 为了不改动deck，copy一份卡牌
        cards = self.deck[:] # 浅拷贝

        # 在workstack中添加纸牌
        for n, workstack in enumerate(self.works, 1):
            for a in range(n):
                card = cards.pop() # 不重复
                workstack.add_card(card)
                card.turn_back_up()
                if a == n-1:
                    card.turn_face_up()

        # 剩下的放deckstack
        self.deckstack.stack_cards(cards) # add_card

    # dealtrigger.signals.clicked->
    def deal(self):
        if self.deckstack.cards:
            self.dealstack.spread_from = len(self.dealstack.cards) # dealstack的cards
            for n in range(self.deal_n):
                card = self.deckstack.take_top_card()
                if card:
                    self.dealstack.add_card(card)
                    card.turn_face_up()
        # deck栈空
        elif self.deckstack.can_restack(self.rounds_n):
            self.deckstack.restack(self.dealstack) # 重置回合
            self.deckstack.update_stack_status(self.rounds_n) # color

    # card.signals.doubleclicked->
    def auto_drop_card(self, card):
        for stack in self.drops:
            if stack.is_valid_drop(card):
                card.stack.remove_card(card)
                stack.add_card(card)
                break

    # stack.signals.comlpete->
    def check_win_condition(self):
        # 全部完整 -> True
        complete = all(s.is_complete for s in self.drops)
        if complete:
            self.animation_event_cover.show()
            self.timer.start()

    # self.timer.timeout
    def win_animation(self):
        # 从左到右,每次取一张
        for drop in self.drops:
            if drop.cards:
                card = drop.cards.pop() # 不是remove, card.stack 仍为 dropstack
                # 设置向量,左上
                if card.vector is None:
                    card.vector = QPoint(-random.randint(3, 10), -random.randint(0, 10))
                    break

        # 有向量的卡牌
        for card in self.deck:
            if card.vector is not None:

                # 朝向量方向移动
                card.setPos(card.pos() + card.vector)
                # 对向量施加重力
                card.vector += QPoint(0, 1) # Gravity
                # 卡牌到底
                if (
                    card.pos().y()
                    > constants.WINDOW_SIZE[1] - constants.CARD_DIMENSIONS.height()
                ):
                    # 重置向量
                    card.vector = QPoint(
                        card.vector.x(),
                        # 损失能量，还是会因为重力降下来
                        -max(1,int(card.vector.y() * constants.BOUNCE_ENERGY)),
                    )
                    # 更新一下位置
                    card.setPos(
                        card.pos().x(),
                        constants.WINDOW_SIZE[1] -constants.CARD_DIMENSIONS.height()
                    )
                # 卡牌触边,重置
                if card.pos().x() < -constants.CARD_DIMENSIONS.width():
                    card.vector = None
                    card.stack.add_card(card)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    app.exec()