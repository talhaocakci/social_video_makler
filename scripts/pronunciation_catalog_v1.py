#!/usr/bin/env python3
"""Author the v1 English, Spanish, and German pronunciation-module sources.

The compact catalog below is the editorial source of truth.  ``gff_pronunciation_bulk.py``
turns it into immutable learner-facing JSON after local dictionary G2P and validation.
Each group is ``(learner-visible pattern, pattern IPA, [(word, focus), ...])``.
"""

from __future__ import annotations

from typing import Any


LANGUAGES: dict[str, dict[str, Any]] = {
    "en": {
        "locale": "en-US",
        "variety": "General American English",
        "language_name": "English",
        "evidence": [
            {
                "publisher": "Standards and Testing Agency, GOV.UK",
                "title": "Assessment framework for the development of the Year 1 phonics screening check",
                "url": "https://www.gov.uk/government/publications/assessment-framework-for-the-development-of-the-year-1-phonics-screening-check/assessment-framework-for-the-development-of-the-year-1-phonics-screening-check",
                "supports": ["grapheme-phoneme correspondences", "common exception words"],
            },
            {
                "publisher": "Department for Education, GOV.UK",
                "title": "National curriculum in England: English programmes of study",
                "url": "https://www.gov.uk/government/publications/national-curriculum-in-england-english-programmes-of-study/national-curriculum-in-england-english-programmes-of-study",
                "supports": ["phonics progression", "spelling alternatives"],
            },
        ],
    },
    "es": {
        "locale": "es-419",
        "variety": "español internacional, seseo y yeísmo",
        "language_name": "Spanish",
        "evidence": [
            {
                "publisher": "Instituto Cervantes",
                "title": "Plan curricular: Pronunciación y prosodia, inventario A1-A2",
                "url": "https://cvc.cervantes.es/ensenanza/biblioteca_Ele/plan_curricular/niveles/03_pronunciacion_inventario_a1-a2.htm",
                "supports": ["Spanish phoneme inventory", "sound-spelling relationships", "connected speech"],
            },
            {
                "publisher": "Real Academia Española and ASALE",
                "title": "Diccionario panhispánico de dudas: u",
                "url": "https://www.rae.es/dpd/u",
                "supports": ["silent u in que/qui and gue/gui", "pronounced ü in güe/güi"],
            },
            {
                "publisher": "Real Academia Española",
                "title": "Ortografía básica de la lengua española",
                "url": "https://www.rae.es/diccionario-estudiante/docs/ortografia.pdf",
                "supports": ["orthographic rules", "written stress"],
            },
        ],
    },
    "de": {
        "locale": "de-DE",
        "variety": "Standarddeutsch",
        "language_name": "German",
        "evidence": [
            {
                "publisher": "Leibniz-Institut für Deutsche Sprache",
                "title": "Amtliches Regelwerk: Vokale",
                "url": "https://grammis.ids-mannheim.de/rechtschreibung/6145",
                "supports": ["German vowel spelling", "vowel combinations"],
            },
            {
                "publisher": "Leibniz-Institut für Deutsche Sprache",
                "title": "Das ie",
                "url": "https://grammis.ids-mannheim.de/progr@mm/6803",
                "supports": ["ie spelling", "long i pronunciation"],
            },
            {
                "publisher": "Goethe-Institut London",
                "title": "Deutsch mit Karla & Kai, Volume 1",
                "url": "https://www.goethe.de/prj/dlp/dlapi/v1/index.cfm?endpoint=%2Ftlm%2Fdownload&file_ID=8752&tlm_ID=2776",
                "supports": ["learner progression", "example-word families"],
            },
        ],
    },
}


def g(pattern: str, sound: str, *examples: tuple[str, str]) -> tuple[Any, ...]:
    return pattern, sound, examples


def m(code: str, *groups: tuple[Any, ...], cefr: str = "A1") -> dict[str, Any]:
    return {"code": code, "cefr": cefr, "groups": groups}


MODULES: dict[str, list[dict[str, Any]]] = {
    "en": [
        m("C01", g("b", "/b/", ("bad", "b")), g("d", "/d/", ("bed", "d")), g("f / ff", "/f/", ("fish", "f"), ("off", "ff")), g("h", "/h/", ("hat", "h"), ("behind", "h"))),
        m("C02", g("c", "/k/", ("cat", "c"), ("cold", "c")), g("k", "/k/", ("key", "k"), ("skin", "k")), g("ck", "/k/", ("back", "ck"), ("clock", "ck"))),
        m("C03", g("g", "/ɡ/", ("gum", "g"), ("go", "g"), ("garden", "g")), g("j", "/dʒ/", ("giant", "g"), ("job", "j"), ("jacket", "j"))),
        m("C04", g("l / ll", "/l/", ("leg", "l"), ("hill", "ll")), g("m", "/m/", ("man", "m"), ("name", "m")), g("n", "/n/", ("net", "n"), ("dinner", "nn"))),
        m("C05", g("p", "/p/", ("pet", "p")), g("t", "/t/", ("top", "t")), g("v", "/v/", ("vet", "v"), ("move", "v")), g("z / zz", "/z/", ("zip", "z"), ("buzz", "zz"))),
        m("C06", g("r", "/ɹ/", ("red", "r"), ("right", "r")), g("w", "/w/", ("wet", "w"), ("away", "w")), g("y", "/j/", ("yes", "y"), ("yellow", "y"))),
        m("C07", g("s", "/s/", ("sit", "s"), ("bus", "s"), ("basic", "s")), g("s", "/z/", ("music", "s"), ("roses", "s"), ("easy", "s"))),
        m("C08", g("x", "/ks/", ("mix", "x"), ("box", "x"), ("next", "x")), g("x", "/ɡz/", ("exam", "x"), ("exist", "x"), ("exact", "x"))),
        m("D01", g("sh", "/ʃ/", ("she", "sh"), ("fish", "sh")), g("ch", "/tʃ/", ("check", "ch"), ("lunch", "ch"))),
        m("D02", g("th", "/θ/", ("thin", "th"), ("three", "th")), g("th", "/ð/", ("this", "th"), ("mother", "th"))),
        m("D03", g("ng", "/ŋ/", ("sing", "ng"), ("long", "ng")), g("nk", "/ŋk/", ("think", "nk"), ("bank", "nk"))),
        m("D04", g("ph", "/f/", ("phone", "ph"), ("dolphin", "ph")), g("wh", "/w/", ("when", "wh"), ("white", "wh"))),
        m("D05", g("c + e, i, y", "/s/", ("city", "c"), ("center", "c"), ("cycle", "c")), g("c + a, o, u", "/k/", ("cat", "c"), ("cold", "c"), ("cup", "c"))),
        m("D06", g("g + e, i, y", "/dʒ/", ("gem", "g"), ("giant", "g"), ("gym", "g")), g("g + a, o, u", "/ɡ/", ("gap", "g"), ("go", "g"), ("gum", "g"))),
        m("D07", g("ch", "/tʃ/", ("chair", "ch"), ("child", "ch")), g("ch", "/k/", ("school", "ch"), ("chorus", "ch")), g("ch", "/ʃ/", ("chef", "ch"), ("machine", "ch"))),
        m("D08", g("kn", "/n/", ("knee", "kn"), ("knife", "kn")), g("wr", "/ɹ/", ("write", "wr"), ("wrong", "wr")), g("mb", "/m/", ("lamb", "mb"), ("climb", "mb"))),
        m("V01", g("a", "/æ/", ("cat", "a")), g("e", "/ɛ/", ("hen", "e")), g("i", "/ɪ/", ("sit", "i")), g("o", "/ɑ/", ("hot", "o")), g("u", "/ʌ/", ("cup", "u"))),
        m("V02", g("a–e", "/eɪ/", ("name", "a"), ("late", "a")), g("i–e", "/aɪ/", ("time", "i"), ("five", "i")), g("o–e", "/oʊ/", ("home", "o"), ("rose", "o"))),
        m("V03", g("e–e", "/iː/", ("these", "e"), ("complete", "e")), g("u–e", "/uː/", ("rule", "u")), g("u–e", "/juː/", ("cube", "u"))),
        m("V04", g("ar", "/ɑɹ/", ("arm", "ar"), ("car", "ar")), g("or", "/ɔɹ/", ("born", "or"), ("short", "or")), g("er / ir / ur", "/ɝ/", ("her", "er"), ("bird", "ir"), ("turn", "ur"))),
        m("V05", g("air / are", "/ɛɹ/", ("air", "air"), ("chair", "air"), ("care", "are"), ("share", "are")), g("ear", "/ɪɹ/", ("ear", "ear"), ("near", "ear"))),
        m("T01", g("ee", "/iː/", ("see", "ee"), ("green", "ee")), g("ea", "/iː/", ("eat", "ea"), ("dream", "ea"))),
        m("T02", g("ea", "/iː/", ("team", "ea"), ("clean", "ea")), g("ea", "/ɛ/", ("head", "ea"), ("bread", "ea")), g("ea", "/eɪ/", ("great", "ea"), ("break", "ea"))),
        m("T03", g("oo", "/uː/", ("moon", "oo"), ("food", "oo")), g("oo", "/ʊ/", ("book", "oo"), ("good", "oo"))),
        m("T04", g("ai", "/eɪ/", ("rain", "ai"), ("train", "ai")), g("ay", "/eɪ/", ("day", "ay"), ("play", "ay"))),
        m("T05", g("oi", "/ɔɪ/", ("coin", "oi"), ("point", "oi")), g("oy", "/ɔɪ/", ("boy", "oy"), ("toy", "oy"))),
        m("T06", g("oa", "/oʊ/", ("boat", "oa"), ("road", "oa")), g("o–e", "/oʊ/", ("home", "o"), ("rose", "o")), g("ow", "/oʊ/", ("snow", "ow"), ("grow", "ow"))),
        m("T07", g("ow", "/oʊ/", ("snow", "ow"), ("grow", "ow")), g("ow", "/aʊ/", ("cow", "ow"), ("town", "ow"))),
        m("T08", g("ou", "/aʊ/", ("out", "ou")), g("ou", "/oʊ/", ("soul", "ou")), g("ou", "/ʌ/", ("young", "ou")), g("ou", "/uː/", ("soup", "ou"))),
        m("T09", g("au", "/ɔ/", ("author", "au"), ("August", "Au")), g("aw", "/ɔ/", ("saw", "aw"), ("draw", "aw"))),
        m("T10", g("igh", "/aɪ/", ("night", "igh"), ("light", "igh")), g("ie", "/aɪ/", ("pie", "ie"), ("tie", "ie")), g("y", "/aɪ/", ("my", "y"), ("fly", "y"))),
        m("T11", g("ew", "/uː/", ("grew", "ew"), ("new", "ew")), g("ue", "/uː/", ("blue", "ue")), g("ue", "/juː/", ("cue", "ue")), g("u–e", "/uː/", ("rule", "u")), g("u–e", "/juː/", ("cube", "u"))),
        m("T12", g("er", "/ɚ/", ("teacher", "er"), ("number", "er"), ("better", "er"), ("summer", "er"))),
        m("E01", g("-s", "/s/", ("cats", "s"), ("works", "s")), g("-s", "/z/", ("dogs", "s"), ("runs", "s")), g("-es", "/ɪz/", ("buses", "es"), ("watches", "es")), cefr="A2"),
        m("E02", g("-ed", "/t/", ("worked", "ed"), ("washed", "ed")), g("-ed", "/d/", ("played", "ed"), ("called", "ed")), g("-ed", "/ɪd/", ("wanted", "ed"), ("needed", "ed")), cefr="A2"),
        m("E03", g("-tion", "/ʃən/", ("nation", "tion"), ("action", "tion")), g("-sion", "/ʒən/", ("vision", "sion")), g("-sion", "/ʃən/", ("tension", "sion")), cefr="A2"),
        m("E04", g("c", "/k/", ("cat", "c")), g("k", "/k/", ("skin", "k")), g("ck", "/k/", ("back", "ck")), g("dge", "/dʒ/", ("bridge", "dge"), ("badge", "dge")), g("tch", "/tʃ/", ("match", "tch"), ("kitchen", "tch")), cefr="A2"),
        m("E05", g("o", "/wʌ/", ("one", "o")), g("tw", "/t/", ("two", "tw")), g("ai", "/ɛ/", ("said", "ai")), g("oe", "/ʌ/", ("does", "oe")), g("eo", "/iː/", ("people", "eo")), g("ou", "/ʊ/", ("could", "ou")), g("o", "/ɪ/", ("women", "o")), g("u", "/ɪ/", ("busy", "u")), cefr="A2"),
    ],
    "es": [
        m("V01", g("a", "/a/", ("casa", "a")), g("e", "/e/", ("mesa", "e")), g("i", "/i/", ("vino", "i")), g("o", "/o/", ("boca", "o")), g("u", "/u/", ("luna", "u"))),
        m("V02", g("ia", "/ja/", ("viaje", "ia")), g("ie", "/je/", ("tierra", "ie")), g("io", "/jo/", ("patio", "io")), g("ua", "/wa/", ("cuatro", "ua")), g("ue", "/we/", ("puerta", "ue")), g("uo", "/wo/", ("cuota", "uo"))),
        m("V03", g("ai / ay", "/ai̯/", ("aire", "ai"), ("hay", "ay")), g("ei / ey", "/ei̯/", ("peine", "ei"), ("rey", "ey")), g("oi / oy", "/oi̯/", ("boina", "oi"), ("hoy", "oy")), g("au", "/au̯/", ("causa", "au")), g("eu", "/eu̯/", ("Europa", "Eu"))),
        m("V04", g("a-í", "/a.i/", ("país", "aí"), ("raíz", "aí")), g("í-o", "/i.o/", ("río", "ío")), g("í-a", "/i.a/", ("día", "ía")), g("a-ú", "/a.u/", ("baúl", "aú")), g("ú-a", "/u.a/", ("actúa", "úa"))),
        m("V05", g("caso / casó", "/ˈkaso/ · /kaˈso/", ("caso", "a"), ("casó", "ó")), g("papa / papá", "/ˈpapa/ · /paˈpa/", ("papa", "a"), ("papá", "á")), g("termino / terminó", "/teɾˈmino/ · /teɾmiˈno/", ("termino", "i"), ("terminó", "ó"))),
        m("C01", g("p", "/p/", ("pan", "p"), ("mapa", "p")), g("t", "/t/", ("té", "t"), ("gato", "t")), g("c / qu", "/k/", ("casa", "c"), ("queso", "qu"))),
        m("C02", g("b / v", "/b/", ("boca", "b"), ("vivir", "v")), g("b / v", "/β/", ("uva", "v"), ("beber", "b"))),
        m("C03", g("d", "/d/", ("día", "d"), ("dedo", "d")), g("d", "/ð/", ("cada", "d"), ("nada", "d"))),
        m("C04", g("f", "/f/", ("foto", "f"), ("café", "f")), g("m", "/m/", ("mano", "m"), ("cama", "m")), g("n", "/n/", ("nube", "n"), ("luna", "n"))),
        m("C05", g("ñ", "/ɲ/", ("niño", "ñ"), ("año", "ñ")), g("ch", "/tʃ/", ("chico", "ch"), ("noche", "ch"))),
        m("C06", g("j", "/x/", ("jefe", "j"), ("rojo", "j")), g("g + e, i", "/x/", ("gente", "g"), ("girar", "g"))),
        m("C07", g("g + a, o, u", "/ɡ/", ("gato", "g"), ("goma", "g"), ("gusano", "g")), g("gu + e, i", "/ɡ/", ("guerra", "gu"), ("guitarra", "gu")), g("gü + e, i", "/ɡw/", ("pingüino", "gü"), ("vergüenza", "gü"))),
        m("C08", g("l", "/l/", ("lado", "l"), ("sol", "l")), g("ll / y", "/ʝ/", ("llave", "ll"), ("pollo", "ll"), ("yo", "y"), ("mayo", "y"))),
        m("A01", g("c + a, o, u", "/k/", ("casa", "c"), ("cosa", "c"), ("cuna", "c")), g("qu + e, i", "/k/", ("queso", "qu"), ("quince", "qu"))),
        m("A02", g("c + e, i", "/s/", ("cero", "c"), ("cine", "c")), g("z", "/s/", ("zapato", "z"), ("luz", "z"))),
        m("A03", g("s", "/s/", ("casa", "s"), ("paso", "s")), g("c / z", "/s/", ("caza", "z"), ("pozo", "z"))),
        m("A04", g("r", "/ɾ/", ("pero", "r"), ("caro", "r")), g("rr / r-", "/r/", ("perro", "rr"), ("carro", "rr"), ("rosa", "r"), ("alrededor", "r"))),
        m("A05", g("x", "/ks/", ("taxi", "x"), ("examen", "x")), g("x", "/x/", ("México", "x")), g("x", "/s/", ("xilófono", "x"))),
        m("A06", g("h", "/∅/", ("hola", "h"), ("ahora", "h"), ("hacer", "h"), ("hotel", "h"))),
        m("A07", g("u", "/∅/", ("queso", "u"), ("quince", "u"), ("guerra", "u"), ("guitarra", "u")), g("ü", "/w/", ("cigüeña", "ü"), ("lingüista", "ü"))),
        m("A08", g("y", "/ʝ/", ("yo", "y"), ("ayuda", "y")), g("y", "/i/", ("y", "y"), ("rey", "y"))),
        m("P01", g("sílaba abierta", "/CV/", ("casa", "ca"), ("alto", "to")), g("sílaba cerrada", "/CVC/", ("cantar", "tar"), ("nombre", "nom")), cefr="A2"),
        m("P02", g("enlace", "/s‿a/", ("dos amigos", "dos amigos")), g("enlace", "/l‿a/", ("el amor", "el amor")), g("enlace", "/o‿e/", ("vivo en Málaga", "vivo en Málaga")), cefr="A2"),
        m("P03", g("sinalefa", "/a‿a/", ("la amiga", "la amiga")), g("sinalefa", "/i‿e/", ("mi hermano", "mi hermano")), g("sinalefa", "/o‿e/", ("vivo en España", "vivo en España")), cefr="A2"),
        m("P04", g("-j", "/x/", ("reloj", "j")), g("-d", "/ð/", ("ciudad", "d"), ("usted", "d")), g("-s", "/s/", ("mismo", "s")), cefr="A2"),
    ],
    "de": [
        m("V01", g("i", "/ɪ/", ("mit", "i"), ("bitte", "i")), g("ie", "/iː/", ("Biene", "ie"), ("Liebe", "ie"))),
        m("V02", g("e", "/ɛ/", ("Bett", "e"), ("Ende", "E")), g("e", "/eː/", ("Weg", "e"), ("leben", "e")), g("-e", "/ə/", ("bitte", "e"), ("Name", "e"))),
        m("V03", g("a", "/a/", ("Mann", "a"), ("Katze", "a")), g("a", "/aː/", ("Name", "a"), ("Tag", "a"))),
        m("V04", g("o", "/ɔ/", ("Sonne", "o"), ("offen", "o")), g("o", "/oː/", ("Ofen", "O"), ("rot", "o"))),
        m("V05", g("u", "/ʊ/", ("Mutter", "u"), ("Hund", "u")), g("u", "/uː/", ("gut", "u"), ("Schule", "u"))),
        m("V06", g("ä", "/ɛ/", ("Männer", "ä")), g("ä", "/ɛː/", ("spät", "ä")), g("ö", "/œ/", ("können", "ö")), g("ö", "/øː/", ("schön", "ö")), g("ü", "/ʏ/", ("fünf", "ü")), g("ü", "/yː/", ("Tür", "ü"))),
        m("V07", g("o + mm", "/ɔ/", ("kommen", "omm")), g("e + tt", "/ɛ/", ("Bett", "ett")), g("o + h", "/oː/", ("wohnen", "oh")), g("e + h", "/eː/", ("nehmen", "eh"))),
        m("D01", g("ei / ai / ay / ey", "/aɪ̯/", ("Eis", "Ei"), ("mein", "ei"), ("Mai", "ai"), ("Bayern", "ay"), ("Meyer", "ey")), g("ie", "/iː/", ("Biene", "ie"), ("Liebe", "ie"))),
        m("D02", g("eu", "/ɔʏ̯/", ("neu", "eu"), ("heute", "eu")), g("äu", "/ɔʏ̯/", ("Häuser", "äu"), ("Bäume", "äu"))),
        m("D03", g("au", "/aʊ̯/", ("Haus", "au"), ("Frau", "au"), ("blau", "au"), ("kaufen", "au"))),
        m("C01", g("sch", "/ʃ/", ("Schule", "Sch"), ("Tisch", "sch")), g("sp-", "/ʃp/", ("Sport", "Sp"), ("Spiel", "Sp")), g("st-", "/ʃt/", ("Stadt", "St"), ("stehen", "st"))),
        m("C02", g("ch", "/x/", ("Bach", "ch"), ("Buch", "ch")), g("ch", "/ç/", ("ich", "ch"), ("Bücher", "ch"))),
        m("C03", g("pf", "/pf/", ("Pferd", "Pf"), ("Kopf", "pf")), g("z / tz", "/ts/", ("Zeit", "Z"), ("Katze", "tz"))),
        m("C04", g("tsch", "/tʃ/", ("Deutsch", "tsch"), ("Tschüss", "Tsch")), g("dsch", "/dʒ/", ("Dschungel", "Dsch"), ("Dschinn", "Dsch"))),
        m("C05", g("ng", "/ŋ/", ("singen", "ng"), ("lang", "ng")), g("nk", "/ŋk/", ("trinken", "nk"), ("Bank", "nk"))),
        m("C06", g("qu", "/kv/", ("Quelle", "Qu"), ("bequem", "qu")), g("x / chs", "/ks/", ("Taxi", "x"), ("sechs", "chs"))),
        m("C07", g("j", "/j/", ("ja", "j"), ("Jahr", "J")), g("w", "/v/", ("Wasser", "W"), ("zwei", "w")), g("v", "/f/", ("Vater", "V")), g("v", "/v/", ("Vase", "V"))),
        m("C08", g("s-", "/z/", ("Sonne", "S"), ("sehen", "s")), g("ss / ß", "/s/", ("Wasser", "ss"), ("Straße", "ß"))),
        m("C09", g("r", "/ʁ/", ("rot", "r"), ("Brot", "r")), g("-er", "/ɐ/", ("Lehrer", "er"), ("besser", "er"))),
        m("C10", g("h-", "/h/", ("Haus", "H"), ("haben", "h")), g("-h-", "/∅/", ("gehen", "h"), ("sehen", "h"))),
        m("A01", g("-b", "/p/", ("ab", "b"), ("lieb", "b")), g("-d", "/t/", ("Rad", "d"), ("Hund", "d")), g("-g", "/k/", ("Tag", "g"), ("Weg", "g")), cefr="A2"),
        m("A02", g("-ig", "/ɪç/", ("richtig", "ig"), ("fertig", "ig"), ("wichtig", "ig"), ("König", "ig")), cefr="A2"),
        m("A03", g("-er", "/ɐ/", ("Lehrer", "er"), ("Kinder", "er")), g("-e", "/ə/", ("bitte", "e"), ("Name", "e")), cefr="A2"),
        m("A04", g("Vokaleinsatz", "/ʔ/", ("arbeiten", "a"), ("erinnern", "e"), ("Verein", "e"), ("beachten", "a")), cefr="A2"),
    ],
}


assert {language: len(modules) for language, modules in MODULES.items()} == {
    "en": 38,
    "es": 25,
    "de": 24,
}
