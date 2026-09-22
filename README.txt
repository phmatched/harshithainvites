DROP-IN PHOTOS
==============

The site draws its own artwork, so it is complete and presentable with this
folder completely empty. Every filename below is OPTIONAL. The moment you add
one, the page detects it and cross-fades the photograph over the drawing.
Nothing else needs editing.

  couple.jpg            the couple, portrait crop (tall)      ~1200 x 1600
  story-1.jpg           chapter one                            ~1200 x 1500
  story-2.jpg           chapter two                            ~1200 x 1500
  story-3.jpg           chapter three                          ~1200 x 1500
  venue.jpg             the mantapa, landscape                 ~2000 x 1300
  closing.jpg           the closing quote background           ~2000 x 1300

  gallery-1.jpg  …  gallery-8.jpg     the album                ~1400 wide

  og-image.jpg          the WhatsApp / social share card       1200 x 630
                        IMPORTANT: this one is not auto-detected. It is named
                        in the <meta property="og:image"> tags in index.html.
                        Put the couple's names and the date ON the image —
                        it is what people see before they open the link.

  ambient.mp3           optional background music (nadaswaram, veena, or a
                        soft instrumental). The player button appears only if
                        this file exists, never autoplays, and remembers the
                        guest's choice. Keep it under ~3 MB.

THE FOUR CELEBRATION PANELS
  These are already filled, so nothing is optional here. Each one carries a
  cut-out illustration that stands inside the drawn scene rather than covering
  it, which is why the backgrounds are transparent:

    event-arishina.webp   + .webp is what a guest downloads; the matching
    event-madhrengi.webp     .png is only there for browsers too old for webp.
    event-dhare.webp      + Named in CONFIG.events as  fig:"event-arishina"
    event-reception.webp     — the bare name, no extension.

  To put a real photograph on one of these panels instead, swap that event's
  fig:"event-dhare" for img:"event-dhare.jpg" and drop the JPG in. A photo
  fills the whole panel; a figure stands inside it. Use one or the other.

TIPS
  - Export JPGs at quality ~80. Anything over ~400 KB each will slow the page
    down on hotel wifi, which is where half your guests will open it.
  - Faces should sit in the upper third of portrait crops; the hero frame is a
    temple arch and crops the bottom.
  - To nudge a crop, set data-pos on that frame in index.html, e.g.
        data-pos="50% 22%"
