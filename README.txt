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

  event-madarengi.jpg   one per celebration                    ~1400 x 1600
  event-arishina.jpg
  event-dhare.jpg
  event-reception.jpg

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

TIPS
  - Export JPGs at quality ~80. Anything over ~400 KB each will slow the page
    down on hotel wifi, which is where half your guests will open it.
  - Faces should sit in the upper third of portrait crops; the hero frame is a
    temple arch and crops the bottom.
  - To nudge a crop, set data-pos on that frame in index.html, e.g.
        data-pos="50% 22%"
