# Time Debt Clock — PWA

The single-file duel timer (`Duel_Timer_v1.html`) packaged as an installable, offline-capable
Progressive Web App.

## Run it

Service workers and install prompts require `http://` (they will not work from `file://`):

```
cd duel-timer-pwa
python serve.py            # http://127.0.0.1:8080
python serve.py 9000       # custom port
```

Then open the printed URL in Chrome/Edge. **Install** appears as a `⬇` button in the top
toolbar (when the browser fires `beforeinstallprompt`), and as the browser's own install button
in the address bar. On iPhone: Share → **Add to Home Screen** (uses the apple-touch-icon).

## Files

| File | Purpose |
| --- | --- |
| `index.html` | The app (original app + PWA wiring) |
| `manifest.webmanifest` | Name, icons, standalone display, shortcuts, screenshots |
| `sw.js` | Service worker: offline cache + update detection |
| `icons/` | Generated icons (standard, maskable, apple-touch, favicon, screenshot) |
| `make_icons.py` | Regenerates every icon: `python make_icons.py` (needs Pillow) |
| `serve.py` | Dev server with manifest MIME type + no-cache headers |
| `check_js.py` | Extracts the inline script so `node --check` can validate it |

## Caching strategy (`sw.js`)

- **Navigations** → network-first, so updates land; falls back to the cached shell when offline.
- **Same-origin assets** → cache-first with runtime caching.
- **Activate** → deletes every cache not prefixed with the current `VERSION`.

## Shipping an update

Bump `VERSION` in `sw.js` (e.g. `tdc-v2`) after changing the app. The next visit installs the
new worker and the app shows an **"Update available" → Reload** toast.

## Notes / limitations

- `beforeinstallprompt` is Chromium-only; Firefox has no install prompt, and iOS Safari uses
  "Add to Home Screen" (no manifest shortcuts, no maskable icons).
- The app is fully self-contained (no CDN, fonts, or analytics), so the offline cache is complete.
- Manifest shortcut **New duel** opens `./index.html?action=reset`, which starts a fresh duel.
- Game state is not persisted across reloads — that is the original app's behavior, unchanged.
