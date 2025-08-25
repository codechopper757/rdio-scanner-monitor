#!/usr/bin/env python3
import curses
import time
import os
import datetime
import sys

#
# Colors groups for Talkgroups #
# Edit this section for your particular area, ranges work as well #
#

TG_COLOR_MAP = {
    'red': {str(tg) for tg in range(290, 299)},
    'green': {'383', '384', '376', '375', '381'},
    'brown': {'360', '361', '362', '363', '345', '346', '347', '352', '340', '341', '343', '342', '348', '349', '350'},
    'orange': {str(tg) for tg in range(201, 206)},
    'white': {'270', '272', '273', '274'},
    'yellow': {'231', '232'},
    'magenta': {str(tg) for tg in range(212, 225)},
}

def get_color_for_tg(tg):
    if tg in TG_COLOR_MAP['red']:
        return 'red'
    if tg in TG_COLOR_MAP['green']:
        return 'green'
    if tg in TG_COLOR_MAP['brown']:
        return 'brown'
    if tg in TG_COLOR_MAP['orange']:
        return 'orange'
    if tg in TG_COLOR_MAP['white']:
        return 'white'
    if tg in TG_COLOR_MAP['yellow']:
        return 'yellow'
    if tg in TG_COLOR_MAP['magenta']:
        return 'magenta'
    return 'default'

def load_talkgroup_map(filepath):
    tg_map = {}
    try:
        with open(filepath, 'r') as f:
            for line in f:
                if line.strip() == '' or line.startswith('#'):
                    continue
                parts = line.strip().split('\t')
                if len(parts) >= 2:
                    tg_map[parts[0]] = parts[1]
    except FileNotFoundError:
        pass
    return tg_map

def follow(file):
    file.seek(0, os.SEEK_END)
    while True:
        line = file.readline()
        if not line:
            time.sleep(0.25)  # refresh rate
            yield None
        else:
            yield line.strip()

def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    curses.start_color()
    curses.use_default_colors()

    # Define color pairs
    curses.init_pair(1, curses.COLOR_RED, -1)
    curses.init_pair(2, curses.COLOR_GREEN, -1)
    curses.init_pair(3, 94, -1)    # Brown-ish
    curses.init_pair(4, 208, -1)   # Orange
    curses.init_pair(5, curses.COLOR_WHITE, -1)
    curses.init_pair(6, curses.COLOR_YELLOW, -1)
    curses.init_pair(7, curses.COLOR_CYAN, -1)
    curses.init_pair(8, curses.COLOR_MAGENTA, -1)

    COLOR_PAIR_MAP = {
        'red': curses.color_pair(1),
        'green': curses.color_pair(2),
        'brown': curses.color_pair(3),
        'orange': curses.color_pair(4),
        'white': curses.color_pair(5),
        'yellow': curses.color_pair(6),
        'cyan': curses.color_pair(7),
        'magenta': curses.color_pair(8),
        'default': curses.A_NORMAL,
    }

    # Automatically pick today's log file
    log_path = os.path.expanduser(f"~/SDRTrunk/logs/rdio-{datetime.datetime.now():%Y%m%d}.log")
    talkgroup_map_path = os.path.expanduser('~/SDRTrunk/logs/talkgroups.tsv')
    talkgroup_map = load_talkgroup_map(talkgroup_map_path)

    stdscr.addstr(0, 0, "📻 SDRTrunk Curses Dashboard", COLOR_PAIR_MAP['magenta'] | curses.A_BOLD)
    stdscr.refresh()

    max_lines = curses.LINES - 2
    lines = []

    # Track idle
    last_activity = time.time()
    idle_timeout = 10  # seconds

    try:
        with open(log_path, "r") as logfile:
            loglines = follow(logfile)
            for line in loglines:
                if stdscr.getch() == ord('q'):
                    break

                if line and "newcall:" in line:
                    parts = line.strip().split()
                    ts = f"{parts[0]} {parts[1]}"
                    tg = next((p.split('=')[1] for p in parts if p.startswith("talkgroup=")), None)
                    file_name = next((p.split('=')[1] for p in parts if p.startswith("file=")), None)
                    tg_name = talkgroup_map.get(tg, "Unknown TG") if tg else "Unknown TG"
                    color_key = get_color_for_tg(tg) if tg else 'default'
                    color = COLOR_PAIR_MAP.get(color_key, curses.A_NORMAL)

                    display_line = f"🕒 {ts}  🔊 TG:{tg} - {tg_name}"
                    lines.append((display_line, color))
                    if len(lines) > max_lines:
                        lines.pop(0)

                    # Update last activity timestamp
                    last_activity = time.time()

                    # Write current line for genmon
                    try:
                        with open("/tmp/sdrtrunk_lastline.txt", "w") as f:
                            f.write(display_line + "\n")
                    except Exception as e:
                        print(f"Error writing lastline file: {e}", file=sys.stderr)

                    # -- Old lines kept for reference --
                    # display_line = f"🕒 {ts}  🔊 TG:{tg} - {tg_name}"
                    # lines.append((display_line, color))
                    # if len(lines) > max_lines:
                    #     lines.pop(0)
                    #
                    # stdscr.clear()
                    # stdscr.addstr(0, 0, "📻 SDRTrunk Curses Dashboard", COLOR_PAIR_MAP['magenta'] | curses.A_BOLD)
                    # for idx, (text, clr) in enumerate(lines, 1):
                    #     stdscr.addstr(idx, 0, text[:curses.COLS-1], clr)
                    # stdscr.refresh()

                # Handle idle
                if time.time() - last_activity > idle_timeout:
                    try:
                        with open("/tmp/sdrtrunk_lastline.txt", "w") as f:
                            f.write("📻 Idle\n")
                    except Exception as e:
                        print(f"Error writing idle lastline: {e}", file=sys.stderr)

                # Update curses display
                stdscr.clear()
                stdscr.addstr(0, 0, "📻 SDRTrunk Curses Dashboard", COLOR_PAIR_MAP['magenta'] | curses.A_BOLD)
                for idx, (text, clr) in enumerate(lines, 1):
                    stdscr.addstr(idx, 0, text[:curses.COLS-1], clr)
                stdscr.refresh()

    except FileNotFoundError:
        stdscr.addstr(2, 0, f"Log file not found: {log_path}", COLOR_PAIR_MAP['red'])
        stdscr.refresh()
        stdscr.getch()


if __name__ == '__main__':
    curses.wrapper(main)

