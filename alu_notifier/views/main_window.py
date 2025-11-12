from datetime import datetime, timedelta

from PyQt6.QtCore import QTimer, QUrl, Qt
from PyQt6.QtGui import QIcon, QAction, QDesktopServices, QFont
from PyQt6.QtWidgets import QMainWindow, QSystemTrayIcon, QMenu, QApplication, QVBoxLayout, QHBoxLayout, \
    QPushButton, QWidget, QLabel, QCheckBox
from win11toast import notify

from alu_notifier.services.settings import SETTINGS_SERVICE
from alu_notifier.utils.utils import get_resource_path, create_badged_icon, format_time_delta


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.daily_gift_badge_showing = False
        self.setWindowTitle("ALU Daily Gift Notifier")
        self.setWindowIcon(QIcon(get_resource_path("logo.ico")))
        self.setMinimumSize(320, 320)
        self.tray_icon = self.create_tray_icon()


        self.timer_label = QLabel()
        self.countdown_label = QLabel()
        font = QFont()
        font.setPointSize(24)
        self.countdown_label.setFont(font)
        self.countdown_label.setStyleSheet("color: #ff5959;")

        settings = SETTINGS_SERVICE.get()
        self.show_notification = QCheckBox("Show notification")
        self.show_notification.setChecked(settings.daily_gift_notification)
        self.show_notification.checkStateChanged.connect(self.show_notification_changed) # type: ignore

        self.open_shop_button = QPushButton("Visit Gameloft Shop")
        self.open_shop_button.clicked.connect(self.open_shop) # type: ignore
        self.refresh_timer_button = QPushButton("Refresh Timer")
        self.refresh_timer_button.clicked.connect(self.refresh_timer) # type: ignore
        self.quit_button = QPushButton("Quit")
        self.quit_button.clicked.connect(QApplication.quit) # type: ignore

        layout = QVBoxLayout()
        layout.addWidget(self.countdown_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(5)
        layout.addWidget(self.timer_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()
        layout.addWidget(self.show_notification)
        layout.addSpacing(10)
        layout.addWidget(self.open_shop_button)
        layout.addWidget(self.refresh_timer_button)
        layout.addSpacing(10)
        layout.addWidget(self.quit_button)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.label_timer = QTimer(self)
        self.label_timer.timeout.connect(self.refresh_time) # type: ignore
        self.refresh_time()

    def create_tray_icon(self):
        tray_icon = QSystemTrayIcon(QIcon(get_resource_path("logo.ico")), self)
        tray_icon.setVisible(True)

        show_action = QAction("Open", self)
        open_shop_action = QAction("Visit Gameloft Shop", self)
        refresh_timer_action = QAction("Refresh Timer", self)
        quit_action = QAction("Quit", self)

        show_action.triggered.connect(self.show_window) # type: ignore
        open_shop_action.triggered.connect(self.open_shop) # type: ignore
        refresh_timer_action.triggered.connect(self.refresh_timer) # type: ignore
        quit_action.triggered.connect(QApplication.quit) # type: ignore

        tray_menu = QMenu()
        tray_menu.addAction(show_action)
        tray_menu.addAction(open_shop_action)
        tray_menu.addAction(refresh_timer_action)
        tray_menu.addAction(quit_action)
        tray_icon.setContextMenu(tray_menu)
        tray_icon.activated.connect(self.on_tray_icon_activated) # type: ignore
        return tray_icon

    def showEvent(self, event):
        self.refresh_time()
        self.label_timer.start(1000)

    def closeEvent(self, event):
        self.label_timer.stop()
        event.ignore()
        self.hide()

    def show_window(self):
        self.showNormal()
        self.activateWindow()

    def show_badge(self):
        if self.daily_gift_badge_showing:
            return
        self.daily_gift_badge_showing = True

        badged = create_badged_icon(QIcon(get_resource_path("logo.ico")))
        self.setWindowIcon(badged)
        if self.tray_icon:
            self.tray_icon.setIcon(badged)
        if SETTINGS_SERVICE.get().daily_gift_notification:
            notify('Daily Gift Available!', 'Click tray icon to visit the shop')

    def clear_badge(self):
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

    def refresh_time(self):
        settings = SETTINGS_SERVICE.get()
        if not settings.next_daily_gift_time:
            self.timer_label.setText("Timer is not set")
            self.countdown_label.setText("N/A")
            return

        diff = settings.next_daily_gift_time - datetime.now()
        if diff.total_seconds() < 0:
            self.timer_label.setText("Next daily gift is available now!")
            self.countdown_label.setText("Available Now!")
            self.show_badge()
            return

        self.timer_label.setText(f"Next daily gift at {settings.next_daily_gift_time:%H:%M:%S}")
        self.countdown_label.setText(format_time_delta(diff))
        self.clear_badge()

    def open_shop(self):
        settings = SETTINGS_SERVICE.get()
        if settings.daily_gift_link:
            QDesktopServices.openUrl(QUrl(settings.daily_gift_link))
        if not settings.next_daily_gift_time or settings.next_daily_gift_time < datetime.now():
            self.refresh_timer()

    def refresh_timer(self):
        settings = SETTINGS_SERVICE.get()
        settings.next_daily_gift_time = datetime.now() + timedelta(days=1)
        SETTINGS_SERVICE.save(settings)
        self.refresh_time()

    def show_notification_changed(self):
        settings = SETTINGS_SERVICE.get()
        settings.daily_gift_notification = self.show_notification.isChecked()
        SETTINGS_SERVICE.save(settings)