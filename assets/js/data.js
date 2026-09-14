/* ============================================================================
 *  WEDDING INVITATION — ALL YOUR DETAILS LIVE IN THIS FILE
 * ============================================================================
 *
 *  This is the ONLY file you need to edit to change names, dates, times,
 *  venues and wording. Nothing else in the project needs touching.
 *
 *  Everything below marked  <<< DUMMY >>>  is placeholder content.
 *
 *  Two rules worth knowing:
 *    1. Keep the quotes. "Ashwini" is right, Ashwini is wrong.
 *    2. Keep the commas at the end of each line.
 *
 *  After editing, just refresh the page in your browser.
 * ========================================================================= */

const INVITE = {

  /* --------------------------------------------------------------------
   *  ONE THING THAT IS *NOT* IN THIS FILE
   *
   *  The WhatsApp / Facebook share preview (the little card that appears
   *  when someone pastes the link) is set by the <meta> tags near the top
   *  of index.html. Those have to be plain HTML, because the crawlers that
   *  read them don't run JavaScript. Edit that block too before sharing.
   * ------------------------------------------------------------------ */


  /* --------------------------------------------------------------------
   *  THE COUPLE
   *
   *  `initial` is the single letter shown on the envelope's wax seal.
   * ------------------------------------------------------------------ */

  bride: {                                                       // <<< DUMMY >>>
    name: "Ashwini",
    kannadaName: "ಅಶ್ವಿನಿ",
    initial: "A",
    parents: "D/o Sri Harish Shetty & Smt Sunitha Shetty",
    grandparents: "Granddaughter of Late Sri Monappa Shetty & Smt Kamala Shetty",
    place: "Mangaluru",
  },

  groom: {                                                       // <<< DUMMY >>>
    name: "Rakshith",
    kannadaName: "ರಕ್ಷಿತ್",
    initial: "R",
    parents: "S/o Sri Ganesh Rai & Smt Vidya Rai",
    grandparents: "Grandson of Late Sri Sanjeeva Rai & Smt Yashoda Rai",
    place: "Puttur",
  },


  /* --------------------------------------------------------------------
   *  THE MUHURTA  — drives the countdown timer and the calendar buttons
   *
   *  Format:  "YYYY-MM-DDTHH:MM:00+05:30"
   *           (24-hour clock; the +05:30 is Indian Standard Time — keep it)
   *
   *  Example: 11:15 AM on 6 Dec 2026  ->  "2026-12-06T11:15:00+05:30"
   *           7:00 PM  on 6 Dec 2026  ->  "2026-12-06T19:00:00+05:30"
   * ------------------------------------------------------------------ */

  muhurta: "2026-12-06T11:15:00+05:30",                          // <<< DUMMY >>>

  // How long the wedding ceremony runs, for the calendar entry.
  muhurtaDurationHours: 3,

  // The human-readable date line shown under the couple's names.
  dateLine: "Sunday, 6 December 2026",                           // <<< DUMMY >>>


  /* --------------------------------------------------------------------
   *  VENUE
   *
   *  mapsQuery: what gets typed into Google Maps. The venue name plus the
   *  city usually works. If the map shows the wrong place, open Google Maps,
   *  find the venue, and paste its coordinates here instead — for example
   *  "12.9141,74.8560".
   * ------------------------------------------------------------------ */

  venue: {                                                       // <<< DUMMY >>>
    name: "Sri Devi Convention Hall",
    addressLines: [
      "Kulur Ferry Road, Kottara",
      "Mangaluru, Dakshina Kannada 575006",
    ],
    mapsQuery: "Sri Devi Convention Hall, Kulur, Mangaluru",

    // The short one-line version shown under the names on the opening screen.
    // Keep it brief — the full address appears in the venue section.
    short: "Sri Devi Convention Hall, Mangaluru",
  },


  /* --------------------------------------------------------------------
   *  EVENTS
   *
   *  Note: the Nishchaya Tambila (betrothal) has already taken place and is
   *  deliberately NOT listed here.
   *
   *  `highlight: true` gives the card the gold treatment — keep it on the
   *  Dhare Muhurtha only.
   *
   *  Each event is a tall illustrated card. Its picture is built from:
   *
   *    scene   which painted scene sits along the bottom of the card —
   *            "haldi", "mehendi", "dhare" or "lamp"
   *    accent  the two sky colours behind it
   *    accentDeep
   *
   *  image   Leave as "" to use the built-in artwork above.
   *          Put a file path here (e.g. "assets/img/events/dhare.jpg") and
   *          that picture replaces the whole scene — this is how you swap in
   *          a commissioned or AI-generated painting later, with no other
   *          change anywhere. Use a tall portrait image, 9:16 (e.g. 1080x1920).
   *
   *  icon    the small motif above the title: turmeric, mehendi, dhare,
   *          lamp, betel or mallige.
   *
   *  Keep `note` under about 100 characters — longer and it crowds the
   *  artwork at the foot of the card.
   *
   *  To remove an event, delete its whole { ... } block including the comma.
   *  To add one, copy an existing block and change the values.
   * ------------------------------------------------------------------ */

  events: [                                                      // <<< DUMMY >>>
    {
      key: "mangala-snana",
      scene: "haldi",
      image: "",
      accent: "#D9931B",
      accentDeep: "#A9670A",
      name: "Mangala Snana",
      kannadaName: "ಮಂಗಳ ಸ್ನಾನ",
      date: "Friday, 4 December 2026",
      time: "10:00 AM onwards",
      venue: "Residence of the Bride, Mangaluru",
      note: "The turmeric bath — family and friends anoint the bride before the wedding days begin.",
      attire: "Traditional yellow",
      icon: "turmeric",
      highlight: false,
    },
    {
      key: "mehendi",
      scene: "mehendi",
      image: "",
      accent: "#3F7340",
      accentDeep: "#24422A",
      name: "Mehendi",
      kannadaName: "ಮೆಹಂದಿ",
      date: "Friday, 4 December 2026",
      time: "05:00 PM to 09:00 PM",
      venue: "Residence of the Bride, Mangaluru",
      note: "An evening of henna, music and mallige, with the women of both families.",
      attire: "Festive ethnic wear",
      icon: "mehendi",
      highlight: false,
    },
    {
      key: "dhare",
      scene: "dhare",
      image: "",
      accent: "#7C1F1A",
      accentDeep: "#4E1010",
      name: "Dhare Muhurtha",
      kannadaName: "ಧಾರೆ ಮುಹೂರ್ತ",
      date: "Sunday, 6 December 2026",
      time: "11:15 AM (Muhurta)",
      venue: "Sri Devi Convention Hall, Mangaluru",
      note: "Our hands joined, and the sacred water poured from the dhare shell.",
      attire: "Traditional South Indian",
      icon: "dhare",
      highlight: true,
    },
    {
      key: "aratakshate",
      scene: "lamp",
      image: "",
      accent: "#0B5C60",
      accentDeep: "#06383C",
      name: "Aratakshate",
      kannadaName: "ಆರತಕ್ಷತೆ",
      date: "Sunday, 6 December 2026",
      time: "07:00 PM onwards",
      venue: "Sri Devi Convention Hall, Mangaluru",
      note: "Rice, blessings and a feast — the evening we hope to spend with every one of you.",
      attire: "Formal or ethnic wear",
      icon: "lamp",
      highlight: false,
    },
  ],


  /* --------------------------------------------------------------------
   *  WORDING
   *
   *  {bride} and {groom} get replaced with the names above automatically.
   * ------------------------------------------------------------------ */

  words: {
    invocation: "ಶ್ರೀ ಗಣೇಶಾಯ ನಮಃ",
    shubhaVivaha: "ಶುಭ ವಿವಾಹ",
    aamantrana: "ಆಮಂತ್ರಣ",
    envelopeCue: "Tap the envelope to open your invitation",

    // The line inside the arch, just above the names.
    heroIntro: "Together with their families, we seek your gracious presence and blessings on the auspicious occasion of the wedding of",

    // The formal invitation paragraph, from the bride's family.
    invitationHeading: "You Are Invited",
    invitationBody:
      "With hearts full of joy, and with the blessings of our elders, " +      // <<< DUMMY >>>
      "Sri Harish Shetty & Smt Sunitha Shetty request the honour of your " +
      "presence at the wedding of their beloved daughter {bride} to {groom}, " +
      "as our two families become one.",

    blessingLine: "Seek the blessings of family and friends as we begin our journey together.",

    closingHeading: "With Love & Gratitude",
    closingBody: "Your presence and blessings will make this occasion truly memorable.",

    // Names in the footer — usually both families.
    closingFamilies: "The Shetty & Rai Families",                 // <<< DUMMY >>>
  },


  /* --------------------------------------------------------------------
   *  OPTIONAL BACKGROUND MUSIC  (currently off)
   *
   *  To switch on: drop an .mp3 into assets/audio/, set enabled to true,
   *  and put the filename below. A mute button appears automatically.
   *  Music starts only when the envelope is tapped — browsers require that.
   * ------------------------------------------------------------------ */

  music: {
    enabled: false,
    file: "assets/audio/background.mp3",
  },

};
