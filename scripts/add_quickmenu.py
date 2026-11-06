"""Add a QuickMenu on bottom-right corner tap to KOReader gestures.lua (file manager + reader)."""
import shutil
import sys

path = sys.argv[1]
src = open(path).read()
shutil.copy(path, path + ".bak")

GESTURE = "tap_right_bottom_corner"
FM = ["calibre_start_connection", "toggle_localsend_server", "send_file_localsend",
      "opds_show_catalog", "cloudstorage", "AppStore_open", "toggle_wifi",
      "history", "stats_calendar_view"]
# OPDS is file-manager only; reader gets "send current book" instead
READER = ["calibre_start_connection", "toggle_localsend_server", "send_current_book_localsend",
          "cloudstorage", "toggle_wifi", "history", "stats_calendar_view"]


def entry(actions):
    lines = [f'        ["{GESTURE}"] = {{']
    lines += [f'            ["{a}"] = true,' for a in actions]
    lines += ['            ["settings"] = {',
              '                ["show_as_quickmenu"] = true,',
              '                ["order"] = {']
    lines += [f'                    [{i}] = "{a}",' for i, a in enumerate(actions, 1)]
    lines += ['                },', '            },', '        },']
    return "\n".join(lines) + "\n"


for section, actions in (("gesture_fm", FM), ("gesture_reader", READER)):
    head = f'    ["{section}"] = {{\n'
    start = src.find(head)
    assert start >= 0, f"{section} not found"
    # this section's body ends at the next top-level entry
    end = src.find('\n    ["', start + len(head))
    body = src[start:end if end >= 0 else len(src)]
    assert f'["{GESTURE}"]' not in body, f"{GESTURE} already set in {section}"
    src = src.replace(head, head + entry(actions), 1)

assert src.count(f'["{GESTURE}"]') == 2
open(path, "w").write(src)
print("ok")
