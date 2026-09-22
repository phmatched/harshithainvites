# Sanjana & Rohit — a Mangalorean Hindu wedding invitation

A single-file wedding invitation website. No build step, no dependencies, no
npm. Open `index.html` by double-clicking it, or drag this folder onto Netlify.

---

## Quick start

```bash
# just open it
open index.html

# or serve it (recommended — matches how it behaves when deployed)
python3 -m http.server 8000
# → http://localhost:8000
```

Deploy by dragging this folder onto [netlify.com/drop](https://app.netlify.com/drop),
or push it to GitHub and enable Pages. There is nothing to compile.

---

## Changing the details

**Everything** the site says lives in one `CONFIG` object at the top of the
`<script>` block near the bottom of `index.html`. Search for `const CONFIG`.

| What | Where in CONFIG |
|---|---|
| Names, city, hashtag, monogram | `bride`, `groom`, `city`, `hashtag`, `monogram` |
| The muhurta (drives the countdown) | `muhurta` — ISO 8601 **with the +05:30 offset** |
| Date shown before/after the scratch reveal | `dateTease`, `dateLabel`, `muhurtaShort` |
| The five celebrations | `events[]` |
| Our Story chapters | `story[]` |
| Travel & stay cards | `travel[]` |
| Album captions | `gallery[]` |
| FAQ | `faq[]` |
| Seed blessings on the wishes wall | `seedWishes[]` |
| WhatsApp number + prefilled message | `whatsapp`, `waMessage` |

Add or remove events, FAQs, travel cards or gallery tiles freely — the page
renders whatever is in the arrays, and the roman numerals ("III of V")
renumber themselves.

### Photographs
See `assets/README.txt`. The site is designed to look finished with **no
photos at all** — it draws its own coastal artwork — and upgrades itself as
soon as you add files.

---

## Collecting real RSVPs

Out of the box `CONFIG.rsvpEndpoint` is `""`, which means **demo mode**:
responses are saved in that visitor's own browser and never leave the device.
Good for showing the site off; useless for actually collecting replies.

Visit `index.html?admin=1` to reveal a **Download responses (CSV)** button for
whatever this browser has stored.

To collect replies for real, pick one:

### Option A — Formspree (fastest)
1. Sign up at [formspree.io](https://formspree.io), create a form, copy the
   endpoint (`https://formspree.io/f/xxxxxxx`).
2. Set `rsvpEndpoint: "https://formspree.io/f/xxxxxxx"`.

Replies arrive by email and appear in the Formspree dashboard.

### Option B — Google Sheets (free, unlimited)
1. New Google Sheet → **Extensions → Apps Script**, paste:

```js
function doPost(e) {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheets()[0];
  var d = JSON.parse(e.postData.contents);
  if (sheet.getLastRow() === 0) sheet.appendRow(Object.keys(d));
  sheet.appendRow(Object.keys(d).map(function (k) { return d[k]; }));
  return ContentService.createTextOutput(JSON.stringify({ ok: true }))
    .setMimeType(ContentService.MimeType.JSON);
}
```

2. **Deploy → New deployment → Web app**, execute as *Me*, access
   *Anyone*. Copy the `/exec` URL into `rsvpEndpoint`.

Either way, if the network call fails the reply is still saved locally and the
guest is pointed at the WhatsApp button, so nothing is ever silently lost.
The wishes wall posts to the same endpoint with `type: "wish"`.

---

## Personalised links

Append `?to=` to send someone their own copy:

```
https://your-site.example/?to=Sudha%20Aunty
```

The hero greets them by name and their name is pre-filled in the RSVP form.

---

## Devices

Built and hardened for phones, tablets, laptops and desktops, portrait and
landscape:

- **Safe areas** — the page declares `viewport-fit=cover`, and every fixed
  edge (nav, menu, music button, lightbox close, footer) insets itself with
  `env(safe-area-inset-*)`, so nothing hides under an iPhone notch or home
  indicator.
- **Viewport units** — every `svh` has a `vh` fallback for iOS < 15.4 and
  Android Chrome < 108.
- **iOS form zoom** — all inputs are 16px, so focusing a field never zooms.
- **Touch** — no information is hidden behind `:hover` (gallery captions are
  always visible on touch), buttons do not stick in their hover fill after a
  tap, and every target is at least 44–48px.
- **Scroll** — the scratch panel uses `touch-action: pan-y`, so you can scratch
  it sideways *and* still scroll the page through it. There is also a
  "Reveal it for me" button.
- **In-app browsers** (WhatsApp, Instagram) — these often block file
  downloads, so every event offers a **Google Calendar** link beside the
  `.ics` download, and `localStorage` access is wrapped so a blocked store
  never throws.
- **Rotation** — rotating the phone mid-gate re-centres the invitation card.
- **Reduced motion** — the whole animation layer, gate included, is bypassed.
- **No JavaScript** — content still renders rather than sitting behind a
  curtain it cannot lift.

### Testing on a real device

Serve the folder and open it on your phone over the same wifi:

```bash
python3 -m http.server 8000
ipconfig getifaddr en0        # macOS: your laptop's LAN address
# → open http://<that-address>:8000 on the phone
```

Then add `?devicecheck=1` to the URL:

```
http://192.168.1.20:8000/?devicecheck=1
```

A small panel reports that device's viewport, orientation, horizontal
overflow (and *which element* causes it, if any), safe-area insets, CSS
feature support, how many artwork frames drew, and how many tap targets fall
under 40px. It updates live as you rotate. Anything wrong shows in red.

---

## Structure

One file, in this order: `<head>` (meta, Open Graph, fonts) → `<style>`
(tokens, components, device layer, reduced-motion, print) → markup →
`<script>` (CONFIG, art engine, motion kernel, section renderers,
interactions).

- **Art engine** — `ART` draws every scene as inline SVG from a small library
  of coastal primitives (palms, gopuram, tile roofs, jasmine, betel leaves,
  the dhaare chembu, oil lamps).
- **Motion kernel** — `Motion` replaces GSAP/ScrollTrigger/Lenis with the Web
  Animations API, one `IntersectionObserver`, and a single `requestAnimationFrame`
  loop for parallax. Nothing is loaded from a CDN, so the page works offline
  and will not rot when a library version disappears.

---

## Printing

`Cmd/Ctrl+P` produces a clean single-page invitation card — the animation,
photography, forms and gallery are all stripped out.
