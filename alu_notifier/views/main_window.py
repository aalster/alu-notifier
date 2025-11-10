from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtWidgets import QTabWidget, QMainWindow, QSystemTrayIcon, QMenu, QApplication, QVBoxLayout, QHBoxLayout, \
    QPushButton, QWidget
from win11toast import notify

from alu_notifier.services.settings import SETTINGS_SERVICE
from alu_notifier.utils.utils import get_resource_path, create_badged_icon
from alu_notifier.views.daily_gift_tab import DailyGiftTab


class MainWindow(QMainWindow):
    tray_icon: QSystemTrayIcon | None = None

    def __init__(self):
        super().__init__()
        self.daily_gift_badge_showing = False
        self.setWindowTitle("ALU Daily Gift Notifier")
        self.setWindowIcon(QIcon(get_resource_path("logo.ico")))
        self.setMinimumSize(500, 600)
        self.init_tray_icon()

        self.daily_gift_tab = DailyGiftTab(self.show_daily_gift_badge, self.clear_daily_gift_badge)

        self.tabs = QTabWidget()
        self.tabs.currentChanged.connect(self.tab_selected) # type: ignore
        self.tabs.addTab(self.daily_gift_tab, "Daily Gift")


        self.quit_button = QPushButton("Quit")
        self.quit_button.clicked.connect(QApplication.quit) # type: ignore

        self.bottom_layout = QHBoxLayout()
        self.bottom_layout.addStretch()
        self.bottom_layout.addWidget(self.quit_button)

        layout = QVBoxLayout()
        layout.addWidget(self.tabs)
        layout.addLayout(self.bottom_layout)
        layout.addStretch()

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def init_tray_icon(self):
        self.tray_icon = QSystemTrayIcon(QIcon(get_resource_path("logo.ico")), self)
        self.tray_icon.setVisible(True)

        show_action = QAction("Open", self)
        open_shop_action = QAction("Visit Gameloft Shop", self)
        quit_action = QAction("Quit", self)

        show_action.triggered.connect(self.show_window) # type: ignore
        open_shop_action.triggered.connect(self.open_shop) # type: ignore
        quit_action.triggered.connect(QApplication.quit) # type: ignore

        tray_menu = QMenu()
        tray_menu.addAction(show_action)
        tray_menu.addAction(open_shop_action)
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.on_tray_icon_activated) # type: ignore
        return

    def tab_selected(self, idx):
        tab = self.tabs.widget(idx)
        if hasattr(tab, 'refresh'):
            tab.refresh()

    def closeEvent(self, event):
        event.ignore()
        self.hide()

    def show_window(self):
        self.showNormal()
        self.activateWindow()

    def open_shop(self):
        self.daily_gift_tab.on_shop_open()

    def show_daily_gift_badge(self):
        if self.daily_gift_badge_showing:
            return
        self.daily_gift_badge_showing = True

        badged = create_badged_icon(QIcon(get_resource_path("logo.ico")))
        self.setWindowIcon(badged)
        if self.tray_icon:
            self.tray_icon.setIcon(badged)
        if SETTINGS_SERVICE.get().daily_gift_notification:
            notify('Daily Gift Available!', 'Click tray icon to visit the shop')

    def clear_daily_gift_badge(self):
        if not self.daily_gift_badge_showing:
            return
        self.daily_gift_badge_showing = False

        icon = QIcon(get_resource_path("logo.ico"))
        self.setWindowIcon(icon)
        if self.tray_icon:
            self.tray_icon.setIcon(icon)

    def on_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            if self.daily_gift_badge_showing:
                self.open_shop()
                return
            self.show_window()
