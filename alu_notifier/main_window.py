from datetime import datetime, timedelta

from PyQt6.QtCore import QTimer, QUrl, Qt
from PyQt6.QtGui import QIcon, QAction, QDesktopServices, QFont
from PyQt6.QtWidgets import QMainWindow, QSystemTrayIcon, QMenu, QApplication, QVBoxLayout, \
    QPushButton, QWidget, QLabel, QCheckBox, QDialog, QDateTimeEdit
from win11toast import notify

from alu_notifier.settings import SETTINGS_SERVICE
from alu_notifier.utils import get_resource_path, create_badged_icon, format_time_delta


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
        self.set_time_button = QPushButton("Set Time")
        self.set_time_button.clicked.connect(self.set_time) # type: ignore
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
        layout.addWidget(self.set_time_button)
        layout.addSpacing(10)
        layout.addWidget(self.quit_button)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.main_timer_tick) # type: ignore
        self.refresh_main_timer()

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

    def main_timer_tick(self):
        default_delay = 30 * 60 * 1000 # 30min
        target_time = SETTINGS_SERVICE.get().next_daily_gift_time
        if not target_time:
            self.timer.start(default_delay)
            return

        delay = min(int((target_time - datetime.now()).total_seconds() * 1000), default_delay)
        if delay <= 0:
            self.show_badge()
        else:
            self.clear_badge()

        self.timer.start(delay if delay > 0 else default_delay)

    def refresh_main_timer(self):
        self.timer.stop()
        self.timer.start(100)

    def refresh_time(self):
        settings = SETTINGS_SERVICE.get()
        if not settings.next_daily_gift_time:
            self.timer_label.setText("Timer is not set")
            self.countdown_label.setText("N/A")
            return

        diff = settings.next_daily_gift_time - datetime.now()
        if diff.total_seconds() < 0:
            self.timer_label.setText(f"Next daily gift is available since {settings.next_daily_gift_time:%H:%M:%S}")
            self.countdown_label.setText("Available Now!")
            self.show_badge()
            return

        self.timer_label.setText(f"Next daily gift at {settings.next_daily_gift_time:%H:%M:%S}")
        self.countdown_label.setText(format_time_delta(diff))
        self.clear_badge()

    def set_time(self):
        dialog = QDialog(self)
        dialog.setModal(True)
        dialog.setMinimumSize(180, 120)
        dialog.setWindowTitle("Set Time")

        time = SETTINGS_SERVICE.get().next_daily_gift_time
        time_edit = QDateTimeEdit(time)
        time_edit.setCalendarPopup(True)
        time_edit.setDateTimeRange(datetime.now() - timedelta(days=1), datetime.now() + timedelta(days=2))
        submit_button = QPushButton("Save")
        submit_button.clicked.connect(dialog.accept) # type: ignore

        layout = QVBoxLayout()
        layout.addWidget(time_edit)
        layout.addWidget(submit_button)
        dialog.setLayout(layout)

        if dialog.exec():
            settings = SETTINGS_SERVICE.get()
            settings.next_daily_gift_time = time_edit.dateTime().toPyDateTime()
            SETTINGS_SERVICE.save(settings)
            self.refresh_main_timer()

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
        self.refresh_main_timer()
        self.refresh_time()

    def show_notification_changed(self):
        settings = SETTINGS_SERVICE.get()
        settings.daily_gift_notification = self.show_notification.isChecked()
        SETTINGS_SERVICE.save(settings)