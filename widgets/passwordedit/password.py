import os

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QLineEdit

folder = os.path.dirname(__file__)


class PasswordEdit(QLineEdit):
    """
        Password LineEdit with icons to show/hide password entries.
        Based on this example https://kushaldas.in/posts/creating-password-input-widget-in-pyqt.html by Kushal Das.
    """

    def __init__(
            self,
            # show_visibility=True,
            visible_icon=None,
            hidden_icon=None,
            icons_from_theme=False,  # 从系统1主题获取图标
            *args,
            **kwargs,
    ):
        super().__init__(*args, **kwargs)

        # icon
        if icons_from_theme:
            self.visibleIcon = QIcon.fromTheme("view_visible")
            self.hiddenIcon = QIcon.fromTheme("view_hidden")
        else:
            if visible_icon:
                self.visibleIcon = visible_icon
            else:
                self.visibleIcon = QIcon(os.path.join(folder, "eye.svg"))
            if hidden_icon:
                self.hiddenIcon = hidden_icon
            else:
                self.hiddenIcon = QIcon(os.path.join(folder, "hidden.svg"))

        # 模式
        self.setEchoMode(QLineEdit.EchoMode.Password)  # 输入模式

        # if show_visibility:
        # 部件显示在文本右侧
        self.togglepasswordAction = self.addAction(self.hiddenIcon, QLineEdit.ActionPosition.TrailingPosition)
        # 信号控制
        self.togglepasswordAction.triggered.connect(self.on_toggle_password_Action)

        self.password_shown = False

    def on_toggle_password_Action(self):
        # 隐藏
        if not self.password_shown:
            self.setEchoMode(QLineEdit.EchoMode.Normal)  # 模式
            self.password_shown = True  # 属性
            self.togglepasswordAction.setIcon(self.visibleIcon)  # 图标
        # 显示
        else:
            self.setEchoMode(QLineEdit.EchoMode.Password)
            self.password_shown = False
            self.togglepasswordAction.setIcon(self.hiddenIcon)
