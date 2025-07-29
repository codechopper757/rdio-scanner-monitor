# SDRTrunk Curses Dashboard

A terminal-based dashboard using `curses` to display active talkgroup logs from [SDRTrunk](https://github.com/DSheirer/sdrtrunk) and `rdio-scanner` in real-time. Talkgroups are color-coded for quick, at-a-glance visibility.

---

## 🚀 Features

- Real-time log monitoring from `rdio-scanner`
- Color-coded talkgroups by category (fully customizable)
- Optional talkgroup name mapping via TSV file
- Lightweight and terminal-friendly

---

## 📦 Prerequisites

- Python 3.7+
- `curses` (preinstalled on most Linux/macOS systems)

---

## ⚙️ Setup

### 1. SDRTrunk + `rdio-scanner` Logging

Ensure you're running [`rdio-scanner`](https://github.com/robotastic/rdio-scanner) and logging output to daily files like:

```
~/SDRTrunk/logs/rdio-YYYYMMDD.log
```

#### Example startup script using `tmux`:

```bash
#!/bin/bash

SESSION_NAME="rdio"
LOGFILE="$HOME/SDRTrunk/logs/rdio-$(date +%Y%m%d).log"

# Clean up old logs (older than 7 days)
find "$HOME/SDRTrunk/logs" -name 'rdio-*.log' -mtime +7 -delete

if ! tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
    tmux new-session -d -s "$SESSION_NAME" bash -c "/usr/bin/rdio-scanner >> \"$LOGFILE\" 2>&1"
fi
```

> You can also run `rdio-scanner` directly without `tmux` — just make sure it writes to the expected log location.

You can automate this via a cron job or systemd timer.

---

### 2. Talkgroup Map (Optional but Recommended)

Create a TSV file at:

```
~/SDRTrunk/logs/talkgroups.tsv
```

Use tab-separated lines:

```
247	Police1
245	Police2
330	Fire Dispatch
```

- Lines beginning with `#` or blank lines are ignored.
- This allows the dashboard to show friendly names instead of numeric TGs.

> **Note:** Color coding is handled inside the script itself. You'll need to edit the `TG_COLOR_MAP` dictionary to customize which talkgroups get which colors. It supports both ranges and individual values.

---

### 3. Run the Dashboard

```bash
python3 sdrdash_curses.py
```

- Resize your terminal as needed — wide terminals work best.

---

## 🖍️ Customizing Colors

Open `sdrdash_curses.py` and look for this section near the top:

```python
TG_COLOR_MAP = {
    'red': {str(tg) for tg in range(290, 299)},
    'green': {'383', '384', '376'},
    # etc...
}
```

You can adjust or add ranges/sets to change how talkgroups are color-coded.

---

## 📄 License

MIT — use freely, modify as needed.
