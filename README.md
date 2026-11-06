# Kobo Clara HD + KOReader setup

My from-scratch setup for a Kobo Clara HD (N249) running KOReader alongside the stock Kobo software (Nickel). Everything was installed over USB from a Mac after a factory reset. Written down so I can redo it, and in case it helps someone else.

Tested November 2026 with:

| Component | Version |
|---|---|
| Kobo firmware | 4.38.23852 |
| KOReader | v2026.07.1 (`koreader-kobo` package) |
| NickelMenu | v0.6.0 |

> **Warning:** Nothing here is official. Back up your device first. Some Clara HD owners report bricked devices after firmware updates, so I avoid connecting Nickel to Wi-Fi during setup.

## 1. Factory reset and skip the Kobo account

1. Settings → Device information → Factory reset. Keep the battery above 50% and don't power off while it restores.
2. On the setup screen, pick a language, then choose to set up **with a computer** (not Wi-Fi), and tap Connect.
3. With the device mounted, add a placeholder user so Nickel skips the account sign-in:

   ```sh
   sqlite3 /Volumes/KOBOeReader/.kobo/KoboReader.sqlite \
     "INSERT INTO user(UserID,UserKey,UserDisplayName,UserEmail) VALUES('00000000-0000-0000-0000-000000000001','','Reader','');"
   ```

Adobe Digital Editions still works without a Kobo account: authorize the device with your Adobe ID in ADE. DRM-protected books open only in Nickel, not KOReader.

## 2. Install KOReader and NickelMenu

Pick the right KOReader package: `koreader-kobo-*.zip` is for firmware 4.x; `koreader-kobov5-*.zip` is only for firmware 5.x.

```sh
K=/Volumes/KOBOeReader
# KOReader
unzip koreader-kobo-v2026.07.1.zip 'koreader/*' -d $K/.adds/
# NickelMenu (installs itself on the next reboot)
cp -X KoboRoot.tgz $K/.kobo/KoboRoot.tgz
# NickelMenu entries
mkdir -p $K/.adds/nm && cp nickelmenu/koreader $K/.adds/nm/koreader
# Keep Nickel from indexing KOReader's hidden folders (firmware 4.17+)
tail -n 2 kobo/Kobo-eReader.conf.snippet >> "$K/.kobo/Kobo/Kobo eReader.conf"
# Remove macOS ._ files before ejecting
dot_clean -m $K
```

NickelMenu is used instead of KFMon because KFMon has to be reinstalled after every firmware update and NickelMenu doesn't. Kobo Start Menu is unmaintained and broken on firmware 4.25+.

[`nickelmenu/koreader`](nickelmenu/koreader) adds four items to the NickelMenu button on Nickel's home screen:

- **KOReader**: launch KOReader
- **Toggle Wi-Fi** and **Reboot**
- **Send Books**: opens [bookdrop.cc](https://bookdrop.cc/) (formerly send.djazz.se) as a pop-up. The `modal:` prefix matters: on firmware 4.23+ you can't leave the browser otherwise.

## 3. Plugins

Built-in KOReader plugins worth turning on: Calibre wireless, Progress sync, Statistics, Vocabulary builder, Exporter, Wallabag, News downloader, OPDS, Cloud storage, Profiles.

Third-party plugins go in `.adds/koreader/plugins/`:

| Plugin | Version | Notes |
|---|---|---|
| [Project: Title](https://github.com/joshuacant/ProjectTitle) | 3.8.3 | Replaces the library view. Disable CoverBrowser when using it. |
| [appstore.koplugin](https://github.com/omer-faruq/appstore.koplugin) | 1.14.0 | Install and update plugins and patches on the device |
| [localsend.koplugin](https://github.com/kaikozlov/localsend.koplugin) | 1.4.6 | Receive files from the [LocalSend](https://localsend.org/) app. Use the `armv7` build on Kobo. |
| [hardcoverapp.koplugin](https://github.com/Billiam/hardcoverapp.koplugin) | 0.4.0 | Hardcover.app sync. Needs an API token. |
| [backlog.koplugin](https://github.com/cdrso/backlog.koplugin) | 1.3.0 | Read tracking for anthology EPUBs |
| [rakuyomi](https://github.com/hanatsumi/rakuyomi) | 1.22.2 | Manga reader. Use the `kindle` build on Kobo, and put [`rakuyomi/settings.json`](rakuyomi/settings.json) in `.adds/koreader/rakuyomi/`. The original project is no longer maintained. |

Skipped on purpose:

- **kobo.koplugin**: syncs Nickel's library and reading position into KOReader and handles Bluetooth. That's pointless without a Kobo account, and the Clara HD has no Bluetooth. It also writes to Nickel's database.
- **koreader-calibre-plugin**: a Calibre-side add-on, only useful if Calibre is your main library manager.

## 4. User patches

Patches go in `.adds/koreader/patches/` and icons in `.adds/koreader/icons/`.

From [sebdelsol/KOReader.patches](https://github.com/sebdelsol/KOReader.patches), the reader-side ones only (Project: Title already covers the file-browser ones):

`guard.lua`, `2-update-patches`, `2-statusbar-thin-chapter`, `2-statusbar-better-compact`, `2-screensaver-cover`, `2-screensaver-chapter`, `2-reference-page-count`, `2-menu-size`

From [SeriousHornet/KOReader.patches](https://github.com/SeriousHornet/KOReader.patches), using the black-and-white icons from `icons (bw)`:

`2--disable-all-PT-widgets` (required first when using Project: Title), `2--rounded-covers`, `2-rounded-folder-covers`, `2-new-status-icons`, `2-percent-badge`, `2-series-badge-numbered`, `2-new-progress-bar`, `2-new-collections-star`, `20-faded-finished-books`

Not used: the stretched-cover and colored variants (the Clara HD screen is black and white), and `2-pages-badge` (too cluttered next to the percent badge).

## 5. KOReader settings

Edited in `.adds/koreader/settings.reader.lua` while KOReader was in USB mode:

```lua
["plugins_disabled"] = { ["coverbrowser"] = true, ["hello"] = true },
["screensaver_type"] = "cover",              -- current book cover as sleep screen
["vocabulary_builder"] = { ["enabled"] = true, ... },
["home_dir"] = "/mnt/onboard/Books",
["inbox_dir"] = "/mnt/onboard/Books",        -- Calibre wireless destination
["LocalSend_save_dir"] = "/mnt/onboard/Books",
```

Keep `Books` at the root of the storage. If it ends up somewhere inside `.adds/koreader/`, it's hidden from Nickel and easy to lose.

Literata (static TTFs from [googlefonts/literata](https://github.com/googlefonts/literata/tree/main/fonts/ttf)) goes in `/fonts`, so both KOReader and Nickel can use it.

### QuickMenu on the bottom-right corner

[`scripts/add_quickmenu.py`](scripts/add_quickmenu.py) adds a QuickMenu to `settings/gestures.lua`, opened by tapping the bottom-right corner, in both the library and the reader. It holds Calibre connect, LocalSend (start/stop server, send file or current book), OPDS, Cloud storage, App Store, Wi-Fi, History and the stats calendar. It saves a `.bak` copy of the original file and refuses to run if that corner already has an action.

```sh
python3 scripts/add_quickmenu.py /Volumes/KOBOeReader/.adds/koreader/settings/gestures.lua
```

The default gestures already handle brightness and warmth: swipe on the left edge for brightness, on the right edge for warmth.

### Done on the device

These are easier in the UI than by editing files:

- Font set to Literata. Long-press a setting to make it the default for all books; otherwise it applies to the current book only.
- Style tweaks: ignore publisher margins and font families.
- Gamma and font weight raised slightly. Highlight style set to underline, which flashes less.
- A "Night" profile (night mode, warm light, larger font) bound to a gesture.

## Getting books onto the device

- **LocalSend** (phone or PC): QuickMenu → Toggle LocalSend server, then send from the app. Files land in `/Books`.
- **Calibre** (PC): Connect/share → Start wireless device connection; on the Kobo, QuickMenu → Calibre wireless connect.
- **Bookdrop** (any browser): NickelMenu → Send Books. These files are handled by Nickel.
- **ADE**: for Adobe DRM books, which are read in Nickel.

## Moving between Nickel and KOReader

- From KOReader to Nickel: top menu → ☰ → Exit.
- From Nickel to KOReader: NickelMenu (bottom right of the home screen) → KOReader.
