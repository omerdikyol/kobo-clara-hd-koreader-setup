"""Add PDF reading profiles (Book / Paper / Slides) to KOReader and list them in the reader QuickMenu.

Usage: python3 add_pdf_profiles.py /Volumes/KOBOeReader/.adds/koreader/settings
Values are the dispatcher "args" from frontend/ui/data/koptoptions.lua (KOReader v2026.07).
Run add_quickmenu.py first if you want the profiles appended to the bottom-right QuickMenu.
"""
import os
import shutil
import sys

settings_dir = sys.argv[1]

PROFILES = {
    "PDF Book": [  # single-column text PDFs: crop margins, fit text width
        ("kopt_page_scroll", "false"),
        ("kopt_trim_page", '"auto"'),
        ("kopt_zoom_mode_genus", '"content"'),
        ("kopt_zoom_mode_type", '"width"'),
        ("kopt_page_margin", "0.1"),
        ("kopt_text_wrap", "0"),
        ("kopt_auto_straighten", "0"),
    ],
    "PDF Paper": [  # two-column academic papers: step through columns
        ("kopt_page_scroll", "false"),
        ("kopt_trim_page", '"auto"'),
        ("kopt_zoom_mode_genus", '"columns"'),
        ("kopt_zoom_range_number", "2"),
        ("kopt_page_margin", "0.05"),
        ("kopt_text_wrap", "0"),
        ("kopt_auto_straighten", "0"),
    ],
    "PDF Slides": [  # whole page visible, no cropping
        ("kopt_page_scroll", "false"),
        ("kopt_trim_page", '"none"'),
        ("kopt_zoom_mode_genus", '"page"'),
        ("kopt_zoom_mode_type", '"full"'),
        ("kopt_page_margin", "0.05"),
        ("kopt_text_wrap", "0"),
    ],
}


def profile_lua(name, actions):
    lines = [f'    ["{name}"] = {{']
    lines += [f'        ["{k}"] = {v},' for k, v in actions]
    # registered = "Show in action list"; without it the profile can't appear in gestures/QuickMenus
    lines += ['        ["settings"] = {', f'            ["name"] = "{name}",', '            ["registered"] = true,',
              '            ["order"] = {']
    lines += [f'                [{i}] = "{k}",' for i, (k, _) in enumerate(actions, 1)]
    lines += ['            },', '        },', '    },']
    return "\n".join(lines) + "\n"


# 1. profiles.lua
path = os.path.join(settings_dir, "profiles.lua")
src = open(path).read() if os.path.exists(path) else "-- ./settings/profiles.lua\nreturn {}\n"
if os.path.exists(path):
    shutil.copy(path, path + ".bak")
new = "".join(profile_lua(n, a) for n, a in PROFILES.items() if f'["{n}"]' not in src)
if "return {}" in src:
    src = src.replace("return {}", "return {\n" + new + "}", 1)
else:
    i = src.rindex("}")  # closing brace of the returned table
    src = src[:i] + new + src[i:]
open(path, "w").write(src)

# 2. reader QuickMenu (bottom-right corner), if present
gpath = os.path.join(settings_dir, "gestures.lua")
g = open(gpath).read()
start = g.find('    ["gesture_reader"] = {\n')
qm = g.find('        ["hold_bottom_right_corner"] = {\n', start)
if start >= 0 and qm >= 0:
    shutil.copy(gpath, gpath + ".bak")
    order_at = g.index('                ["order"] = {\n', qm)
    order_end = g.index("                },\n", order_at)
    n = g[order_at:order_end].count('] = "')  # existing entries; indices must stay contiguous
    adds_bool = adds_order = ""
    for name in PROFILES:
        key = f"profile_exec_{name}"
        if f'["{key}"]' in g[qm:order_end]:
            continue
        n += 1
        adds_bool += f'            ["{key}"] = true,\n'
        adds_order += f'                    [{n}] = "{key}",\n'
    g = g[:order_end] + adds_order + g[order_end:]
    ins = qm + len('        ["hold_bottom_right_corner"] = {\n')
    g = g[:ins] + adds_bool + g[ins:]
    open(gpath, "w").write(g)
print("ok")
