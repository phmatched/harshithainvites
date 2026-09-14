# Wedding Invitation

A single-page online wedding invitation in the Tulunad (coastal Karnataka) tradition,
built to be hosted free on GitHub Pages.

No build step, no npm, no frameworks. What is in this folder is exactly what gets served.
All the artwork — the marigold toran, the cusped arch, the floral corners, the peacock,
the mandala, the watercolour backgrounds — is drawn from scratch and lives in this repo.
Nothing is licensed from anyone, and there is nothing to pay for.

---

## Editing your details

**Everything you need to change is in one file: [`assets/js/data.js`](assets/js/data.js).**

Open it in any text editor. Every placeholder is marked `<<< DUMMY >>>`. Change the text
between the quotes, save, refresh the page. Nothing else needs touching.

Two rules:

1. Keep the quotes — `"Ashwini"` is right, `Ashwini` is wrong.
2. Keep the comma at the end of each line.

If the page ever goes blank after an edit, you've almost certainly dropped a quote or a
comma. Undo the last change and try again.

### The date format matters

`muhurta` drives the countdown and the calendar buttons, so it has a strict format:

```
"2026-12-06T11:15:00+05:30"
 YYYY-MM-DD T HH:MM:SS  +05:30   <- 24-hour clock, IST. Keep the +05:30.
```

11:15 AM is `11:15:00`; 7:00 PM is `19:00:00`.

`dateLine` is the separate, human-readable line shown under the names — write that
however you like, e.g. `"Sunday, 6 December 2026"`.

### The map

`venue.mapsQuery` is literally what gets typed into Google Maps. Venue name plus city
usually works. If the map lands on the wrong place, open Google Maps, right-click the
venue, copy the coordinates, and paste those instead:

```js
mapsQuery: "12.9141,74.8560",
```

`venue.short` is the one-line version shown under the names at the top. Keep it brief —
the full address appears further down.

### Events

The Nishchaya Tambila is deliberately not listed — it has already taken place.

To remove an event, delete its whole `{ ... }` block including the trailing comma.
To add one, copy an existing block and change the values. Keep `highlight: true` on the
Dhare Muhurtha only — it gives that card a heavier gold edge.

Each event card is built from:

- `scene` — the artwork along its foot: `haldi`, `mehendi`, `dhare` or `lamp`
- `accent` / `accentDeep` — the two sky colours behind it
- `icon` — its motif: `turmeric`, `mehendi`, `dhare`, `lamp`, `betel`, `mallige`
- `image` — leave `""` to use the built-in artwork, or point at your own
  painting (see [The event cards](#the-event-cards))

Keep `note` under about 100 characters — longer and it crowds the artwork.

---

## Previewing on your computer

You can't just double-click `index.html` — the map and fonts need a real server.
In Terminal:

```sh
cd /Users/prathik/Documents/InvitationAshu
python3 -m http.server 8000
```

Then open <http://localhost:8000>. Press `Ctrl+C` to stop.

---

## Publishing to GitHub Pages

1. Create a new repository on GitHub (`harshithainvites`). It must be **public** for
   free Pages hosting.

2. From this folder:

   ```sh
   git init
   git add .
   git commit -m "Wedding invitation"
   git branch -M main
   git remote add origin https://github.com/phmatched/harshithainvites.git
   git push -u origin main
   ```

3. On GitHub: **Settings → Pages → Build and deployment**
   - Source: **Deploy from a branch**
   - Branch: **main**, folder: **/ (root)** → Save

4. Wait a minute or two. Your invitation is live at:

   ```
   https://phmatched.github.io/harshithainvites/
   ```

5. **Now go back and fix the share-preview URLs** — see the next section. Then commit and
   push again.

To publish changes later: `git add . && git commit -m "Update details" && git push`.

### A custom domain (optional)

If you own a domain, add a file named `CNAME` at the top level of this folder containing
just the domain (e.g. `ashwini-rakshith.com`), push it, and point the domain's DNS at
GitHub Pages. Then use that domain in the share-preview tags below.

---

## The WhatsApp share preview

This is the one thing **not** in `data.js`. When someone pastes the link into WhatsApp,
the preview card comes from `<meta>` tags near the top of `index.html`. WhatsApp reads
those with a crawler that doesn't run JavaScript, so they have to be written into the
HTML directly.

Open `index.html`, find the block marked `SHARE PREVIEW`, and edit the values there.
`og:image` and `og:url` must be **full absolute URLs**:

```html
<meta property="og:image" content="https://phmatched.github.io/harshithainvites/assets/img/og-image.png">
<meta property="og:url"   content="https://phmatched.github.io/harshithainvites/">
```

The preview picture itself is `assets/img/og-image.png` — a designed card with the names
on it. Once you've put the real names in `data.js`, regenerate it:

```sh
python3 tools/make_share_card.py
```

It reads the names, date and venue from `data.js` so the card can't drift from the site.
(macOS only — it renders via QuickLook. If you're not on a Mac, ask and I'll regenerate it.)

WhatsApp caches previews aggressively. If you change these after sharing the link, the old
card may stick around for a day or so — test with a throwaway chat before sending it out
to everyone.

---

## The artwork

Nothing here is a stock photo or a licensed asset. The artwork is made by two kinds of
generator in `tools/`:

- **Painted rasters** — the event scenes, the section backdrops and the watercolour washes
  are produced by a small painting engine (`tools/paint.py`): soft brush dabs with colour
  jitter, atmospheric haze for depth, one directional light with warm highlights and cool
  shadows, contact shadows, and additive bloom around every flame.
- **Vector ornament** — the toran, arch, mandala, corner sprays and dividers stay SVG, so
  they hold their edge at any size.

| File | What it is |
|---|---|
| `toran.svg` | The marigold-and-mango-leaf garland across the top |
| `arch.svg` | The cusped Mughal arch framing the names |
| `corner-left/right.svg` | Rose, jasmine and marigold corner sprays |
| `mandala.svg` | The faint medallion behind each section |
| `kalasha.svg` | The sacred pot with coconut and mango leaves |
| `peacock.svg` | Peacock pair (shown on wide screens only) |
| `divider.svg` | The lotus rule under each heading |
| `garland-side.svg` | Hanging strand — mallige, rudraksha and a brass bell |
| `scene-haldi.png` | *Painted* — turmeric pots, marigold backdrop, banana clumps |
| `scene-mehendi.png` | *Painted* — lanterns in bloom, a low divan, henna cones |
| `scene-dhare.png` | *Painted* — tiled mandap, gopuram receding into haze |
| `scene-lamp.png` | *Painted* — brass lamp stands, a row of diyas, a lotus pond |
| `bg-*.png` | *Painted* — one backdrop per interior section |
| `wash-*.png` | *Painted* — the hero, body and closing washes |
| `grain.png` | Handmade-paper texture laid over everything |

### The event cards

Each event is a tall 9:16 panel built from layers — a sky tinted with that
event's `accent`, the toran across the top, hanging strands down both edges, and
its `scene` along the bottom — with the text laid over in HTML. Nothing is baked
into a picture, so editing `data.js` is all it takes to change a time or a venue.

The scene itself is a painted PNG with a transparent, faded top edge, so it composites
onto the card's own sky.

**To use your own illustration instead**, drop a tall portrait image (9:16, e.g.
1080×1920) into `assets/img/events/` and point that event at it:

```js
image: "assets/img/events/dhare.jpg",
```

That one line replaces every generated layer for that card. Nothing else changes,
and you can do it for one event or all four.

### Changing the colours

Site colours are CSS variables at the top of [`assets/css/style.css`](assets/css/style.css) —
change `--maroon`, `--gold`, and the rest there.

The colours *inside* the artwork are set at the top of the two generator scripts. To
recolour the flowers or the gold, edit the palette constants and re-run:

```sh
python3 tools/generate_ornament.py      # redraws the SVG ornament
python3 tools/generate_backgrounds.py   # repaints the hero/body/closing washes
python3 tools/generate_backdrops.py     # repaints the per-section backdrops
python3 tools/generate_scenes.py        # repaints the four event scenes
```

The painting engine itself is `tools/paint.py`. The scene layouts and their palettes are
at the top of `generate_scenes.py`.

Both write straight into `assets/img/`. Only needed if you want different colours — the
artwork is already committed.

### Fonts

Cinzel (headings), Cormorant Garamond (body), Great Vibes (the names) and Noto Serif
Kannada, all loaded from Google Fonts. The Kannada font is not optional — system
fallbacks render Kannada conjuncts badly.

---

## The scratch card

In the Counting Down section the timer and the muhurta date sit under a brushed
gold foil. Guests scratch it away with a finger or the mouse; once about half is
cleared the rest fades on its own. There is a **Reveal without scratching** link
underneath for anyone who would rather not drag.

The time shown on it is read from `muhurta` in `data.js` and formatted in IST, so
it can never disagree with the countdown above it. If JavaScript doesn't run, no
foil is drawn and the countdown is simply visible.

---

## Before you share the link

- [ ] Every `<<< DUMMY >>>` in `data.js` replaced with real details
- [ ] **All Kannada text proofread by someone who reads Kannada** — especially names.
      The ritual names and the invocation were written from reference, not dictation.
- [ ] Family names, spellings and honorifics checked by both families
- [ ] `muhurta` date and time confirmed against the actual muhurta
- [ ] Map pin opens to the right venue
- [ ] `python3 tools/make_share_card.py` re-run with the real names
- [ ] Share-preview `<meta>` tags in `index.html` updated with the live URL and real names
- [ ] Opened on an actual phone, and the link pasted into a WhatsApp chat to check the
      preview card

---

## Optional: background music

Off by default. To switch it on:

1. Put an `.mp3` in `assets/audio/`
2. In `data.js`, set `music.enabled` to `true` and `music.file` to the filename

A mute button appears in the bottom-right corner. Music starts only when the envelope is
tapped — every browser requires a tap before playing audio, so this is by design.

---

## What's in here

```
index.html            The invitation. All sections, and the small motif icons.
404.html              Shown if someone mistypes the URL.
.nojekyll             Tells GitHub Pages to serve these files as-is. Don't delete.
assets/css/style.css  All styling. Colours are the variables at the very top.
assets/js/data.js     >>> YOUR DETAILS GO HERE <<<
assets/js/app.js      Builds the page from data.js. You shouldn't need to edit this.
assets/img/           The artwork, the favicon and the share image.
assets/audio/         Optional background music.
tools/                Scripts that generate the artwork and the share card.
```

### A note on file paths

Every link in this site is **relative** (`assets/css/style.css`, never `/assets/...`).
On a GitHub project page the site is served from `/your-repo/`, and absolute paths
starting with `/` will 404. If you add files, keep the paths relative.
