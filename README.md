# Legal Freedom Countdown

A Fluent-design desktop countdown to **18 November 2028**, built with Python and PySide6 (Qt).

The visible unit cards adapt to how far away the date is:

- Leading units that have counted down to zero (years, then months, then days, ...) are hidden automatically.
- The **nanoseconds** card (accent-highlighted, driven by `time.time_ns()`) only appears during the final minute, when the app also switches to a ~60 fps refresh.
- When the moment arrives, the cards are replaced by a completion message.

## Run

```bash
.venv/bin/python main.py
```

(From WSL with WSLg, the window opens on the Windows desktop.)

## Setup from scratch

```bash
python3 -m virtualenv .venv        # or python3 -m venv if python3-venv is installed
.venv/bin/pip install -r requirements.txt
```

## Notes

- The target is local time midnight, `datetime(2028, 11, 18)` in `main.py`.
- Years/months are calendar-aware (month lengths are respected, day-of-month clamped).
- `main.py --screenshot out.png` renders one frame and saves it — used for automated visual checks.
