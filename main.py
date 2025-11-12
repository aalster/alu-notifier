import sys

from PyQt6.QtWidgets import QApplication

from alu_notifier.utils.single_instance_lock import single_instance_lock
from alu_notifier.views.main_window import MainWindow


def main():
    window: MainWindow | None = None

    def show_window():
        if window:
            window.show_window()

    lock = single_instance_lock(show_window)
    if not lock:
        print("Application already running.")
        sys.exit(0)

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    font = app.font()
    font.setPointSize(10)
    app.setFont(font)

    window = MainWindow()
    window.hide()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()