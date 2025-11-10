from datetime import datetime, timedelta

from PyQt6.QtCore import QTimer, QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QCheckBox, QFormLayout, QLabel

from alu_notifier.services.settings import SETTINGS_SERVICE
from alu_notifier.utils.utils import format_time_delta


class DailyGiftTab(QWidget):
    def __init__(self, show_badge, clear_badge):
        super().__init__()
        self.show_badge = show_badge
        self.clear_badge = clear_badge

        self.timer_label = QLabel()

        self.show_notification = QCheckBox("Show notification")
        self.show_notification.checkStateChanged.connect(self.show_notification_changed) # type: ignore

        self.form = QFormLayout()
        self.form.addWidget(self.show_notification)
        self.form.addWidget(self.timer_label)

        layout = QVBoxLayout()
        layout.addLayout(self.form)
        layout.addStretch()
        self.setLayout(layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_time) # type: ignore
        self.timer.start(60 * 1000 - 100)

        self.refresh()
        self.refresh_time()

    def refresh(self):
        settings = SETTINGS_SERVICE.get()
        self.show_notification.setChecked(settings.daily_gift_notification)
        self.refresh_time()

    def refresh_time(self):
        settings = SETTINGS_SERVICE.get()
        if not settings.next_daily_gift_time:
            self.timer_label.setText("Next daily gift at N/A")
            return

        diff = settings.next_daily_gift_time - datetime.now()
        if diff.total_seconds() < 0:
            self.timer_label.setText("Next daily gift is available now!")
            self.show_badge()
            return

        self.timer_label.setText(f"Next daily gift in {format_time_delta(diff)}")
        self.clear_badge()

    def on_shop_open(self):
        settings = SETTINGS_SERVICE.get()
        if settings.daily_gift_link:
            QDesktopServices.openUrl(QUrl(settings.daily_gift_link))
        if settings.next_daily_gift_time < datetime.now():
            settings.next_daily_gift_time = datetime.now() + timedelta(days=1)
            SETTINGS_SERVICE.save(settings)
            self.refresh()

    def show_notification_changed(self):
        settings = SETTINGS_SERVICE.get()
        settings.daily_gift_notification = self.show_notification.isChecked()
        SETTINGS_SERVICE.save(settings)