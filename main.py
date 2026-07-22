"""Legal Freedom — Fluent-style countdown to 18 November 2028.

The set of visible unit cards adapts to how far away the target is:
leading units that have reached zero (years, then months, ...) are hidden,
and the nanoseconds card only appears in the final minute.
"""

import sys
import time
import calendar
from datetime import datetime

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

TARGET = datetime(2028, 11, 18, 0, 0, 0)  # local time
NS_PER_SEC = 1_000_000_000

ACCENT = "#60cdff"

QSS = f"""
QWidget#root {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #15151e, stop:0.5 #1a1c2a, stop:1 #161a26);
}}
QLabel#eyebrow {{
    color: {ACCENT};
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 4px;
}}
QLabel#title {{
    color: #ffffff;
    font-size: 28px;
    font-weight: 600;
}}
QLabel#subtitle {{
    color: rgba(255, 255, 255, 0.55);
    font-size: 13px;
}}
QFrame#card {{
    background: rgba(255, 255, 255, 0.045);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 10px;
}}
QFrame#card[accent="true"] {{
    background: rgba(96, 205, 255, 0.10);
    border: 1px solid rgba(96, 205, 255, 0.45);
}}
QLabel#value {{
    color: #ffffff;
    font-size: 40px;
    font-weight: 600;
}}
QFrame#card[accent="true"] QLabel#value {{
    color: {ACCENT};
}}
QLabel#caption {{
    color: rgba(255, 255, 255, 0.50);
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 2px;
}}
QLabel#footer {{
    color: rgba(255, 255, 255, 0.40);
    font-size: 12px;
}}
QLabel#done {{
    color: {ACCENT};
    font-size: 34px;
    font-weight: 700;
}}
"""


def add_months(dt: datetime, n: int) -> datetime:
    """Add n calendar months, clamping the day to the target month's length."""
    month_index = dt.year * 12 + (dt.month - 1) + n
    year, month = divmod(month_index, 12)
    month += 1
    day = min(dt.day, calendar.monthrange(year, month)[1])
    return dt.replace(year=year, month=month, day=day)


def breakdown(now_ns: int):
    """Split the time remaining until TARGET into calendar-aware fields.

    Returns None once the target has passed.
    """
    target_ns = int(TARGET.timestamp() * NS_PER_SEC)
    rem_ns = target_ns - now_ns
    if rem_ns <= 0:
        return None

    nanoseconds = rem_ns % NS_PER_SEC
    now = datetime.fromtimestamp((now_ns + nanoseconds) / NS_PER_SEC)

    months_total = (TARGET.year - now.year) * 12 + (TARGET.month - now.month)
    while months_total > 0 and add_months(now, months_total) > TARGET:
        months_total -= 1
    anchor = add_months(now, months_total)

    rest = TARGET - anchor
    total_seconds = int(rest.total_seconds())

    return {
        "rem_ns": rem_ns,
        "years": months_total // 12,
        "months": months_total % 12,
        "days": rest.days,
        "hours": (total_seconds // 3600) % 24,
        "minutes": (total_seconds // 60) % 60,
        "seconds": total_seconds % 60,
        "nanoseconds": nanoseconds,
    }


class UnitCard(QFrame):
    def __init__(self, caption: str, wide: bool = False, accent: bool = False):
        super().__init__()
        self.setObjectName("card")
        self.setProperty("accent", "true" if accent else "false")
        self.setMinimumSize(150 if wide else 108, 96)

        self.value_label = QLabel("0")
        self.value_label.setObjectName("value")
        self.value_label.setAlignment(Qt.AlignCenter)

        caption_label = QLabel(caption.upper())
        caption_label.setObjectName("caption")
        caption_label.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(2)
        layout.addWidget(self.value_label)
        layout.addWidget(caption_label)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(24)
        shadow.setOffset(0, 6)
        shadow.setColor(QColor(0, 0, 0, 90))
        self.setGraphicsEffect(shadow)

    def set_value(self, text: str):
        self.value_label.setText(text)


class CountdownWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("root")
        self.setWindowTitle("Legal Freedom — Countdown")
        self.setMinimumWidth(560)

        eyebrow = QLabel("COUNTDOWN")
        eyebrow.setObjectName("eyebrow")
        eyebrow.setAlignment(Qt.AlignCenter)

        title = QLabel("Legal Freedom")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)

        subtitle = QLabel(TARGET.strftime("%A, %d %B %Y · %H:%M"))
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignCenter)

        self.cards = {
            "years": UnitCard("Years"),
            "months": UnitCard("Months"),
            "days": UnitCard("Days"),
            "hours": UnitCard("Hours"),
            "minutes": UnitCard("Minutes"),
            "seconds": UnitCard("Seconds"),
            "nanoseconds": UnitCard("Nanoseconds", wide=True, accent=True),
        }

        self.cards_row = QHBoxLayout()
        self.cards_row.setSpacing(10)
        self.cards_row.addStretch(1)
        for card in self.cards.values():
            self.cards_row.addWidget(card)
        self.cards_row.addStretch(1)

        self.done_label = QLabel("It's time — you're free. 🎉")
        self.done_label.setObjectName("done")
        self.done_label.setAlignment(Qt.AlignCenter)
        self.done_label.hide()

        self.footer = QLabel("")
        self.footer.setObjectName("footer")
        self.footer.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 28, 36, 24)
        layout.setSpacing(6)
        layout.addWidget(eyebrow)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(18)
        layout.addLayout(self.cards_row)
        layout.addWidget(self.done_label)
        layout.addSpacing(14)
        layout.addWidget(self.footer)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)
        self.timer.start(100)
        self.tick()

    def tick(self):
        fields = breakdown(time.time_ns())

        if fields is None:
            self.timer.stop()
            for card in self.cards.values():
                card.hide()
            self.done_label.show()
            self.footer.setText(TARGET.strftime("Reached on %d %B %Y"))
            return

        rem_ns = fields["rem_ns"]

        # Leading units at zero are hidden; nanoseconds only in the final minute.
        visible = {}
        larger_nonzero = False
        for unit in ("years", "months", "days", "hours", "minutes", "seconds"):
            visible[unit] = fields[unit] > 0 or larger_nonzero
            larger_nonzero = larger_nonzero or fields[unit] > 0
        visible["nanoseconds"] = rem_ns < 60 * NS_PER_SEC

        for unit, card in self.cards.items():
            card.setVisible(visible[unit])
            if unit == "nanoseconds":
                card.set_value(f"{fields[unit]:09d}")
            else:
                card.set_value(str(fields[unit]))

        total_days = rem_ns // (86_400 * NS_PER_SEC)
        self.footer.setText(f"≈ {total_days:,} days to go")

        # Tick fast only when the nanoseconds card is on screen.
        interval = 16 if visible["nanoseconds"] else 100
        if self.timer.interval() != interval:
            self.timer.setInterval(interval)


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(QSS)
    app.setFont(QFont("Segoe UI Variable Display"))

    window = CountdownWindow()
    window.show()

    # Hidden flag used for automated visual verification.
    if "--screenshot" in sys.argv:
        out = sys.argv[sys.argv.index("--screenshot") + 1]

        def grab():
            window.grab().save(out)
            app.quit()

        QTimer.singleShot(600, grab)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
