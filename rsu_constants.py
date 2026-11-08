"""Konstanten: Regler-Grenzen, feste Beispiele, Suchen, Messraster, Farben und Presets."""

CAP = 100                 # Behälter 100 x 100 (Breite und Höhe)

# --- Beispiele (Rechtecke als (Breite, Höhe) in Lieferreihenfolge; zwölf Rechtecke aus dem Messraster von Stück 7 und 8, mittlere Rechtecke) -------
# Beispiel 1 (Instanz 0 von 100): Schranke 2, Optimum 2; MaxRects BSSF nach Fläche 3, mit jedem festen Schlüssel 3.
# Beispiel 2 (Instanz 2 von 100): Schranke 2, Optimum 2 (CP-SAT); MaxRects BSSF mit jedem festen Schlüssel 3.
BEISPIELE = {
    0: ((43, 55), (23, 25), (50, 45), (24, 46), (40, 41), (43, 37), (39, 49), (27, 38), (20, 36), (30, 57), (21, 38), (47, 40)),
    1: ((20, 49), (26, 25), (34, 30), (54, 49), (44, 39), (33, 31), (55, 55), (38, 48), (28, 30), (48, 23), (46, 32), (31, 36)),
}
BEISPIEL_OPTIMUM = {0: 2, 1: 2}

# Quellen der Instanz: 0 und 1 = Handbeispiele, 2 bis 5 = Zufallsinstanzen mit der jeweiligen Verteilung
QUELLEN = {0: "Beispiel 1 (zwölf Rechtecke)", 1: "Beispiel 2 (zwölf andere Rechtecke)", 2: "zufällig, mittlere Rechtecke", 3: "zufällig, breit gestreute Rechtecke",
           4: "zufällig, kleine Rechtecke", 5: "zufällig, hohe schmale Rechtecke"}
ZUFALL_QUELLEN = (2, 3, 4, 5)
N_WERTE = (12, 20, 40)                    # Zahl der Rechtecke der Zufallsinstanzen in der App

# Verteilungen (dieselben wie in Stück 7 und 8): (Schlüssel, Name, Bereich der Breite, Bereich der Höhe)
VERTEILUNGEN = (
    ("mittel", "mittlere Rechtecke (20 bis 60)", (20, 60), (20, 60)),
    ("breit", "breit gestreute Rechtecke (5 bis 70)", (5, 70), (5, 70)),
    ("klein", "kleine Rechtecke (10 bis 40)", (10, 40), (10, 40)),
    ("hochschmal", "hohe schmale Rechtecke (Breite 5 bis 30, Höhe 30 bis 80)", (5, 30), (30, 80)),
)
VERTEILUNG_KURZ = ("mittel", "breit", "klein", "hoch schmal")
VERTEILUNG_LANG = ("mittlere Rechtecke", "breit gestreute Rechtecke", "kleine Rechtecke", "hohe schmale Rechtecke")
VERTEILUNG_DAT = ("mittleren Rechtecken", "breit gestreuten Rechtecken", "kleinen Rechtecken", "hohen schmalen Rechtecken")   # nach „bei“

# Suchen: 0 keine (die feste Reihenfolge nach Fläche), 1 Zufallsstarts, 2 Tausch nur auf die Behälterzahl, 3 Tausch auf Behälterzahl und dann Füllung
SUCHEN = {0: "Keine Suche (feste Reihenfolge nach Fläche)", 1: "Zufallsstarts", 2: "Tausch, nur Behälterzahl", 3: "Tausch, Behälterzahl und Füllung"}
SUCHE_KURZ = {0: "Fläche", 1: "Zufall", 2: "Tausch B", 3: "Tausch B+F"}
SUCHE_NAME = {0: "die feste Reihenfolge", 1: "die Suche mit Zufallsstarts", 2: "die Tausch-Suche auf die Behälterzahl", 3: "die Tausch-Suche mit Zweitziel"}
BUDGET_MAX = 1000
BUDGETS = (50, 200, 1000)

SEED_MAX, DEFAULT_SEED = 999999, 7
SUCHSEED_STANDARD = 1

# --- Messraster ---------------------------------------------------------------------------------------------------------------------------
INSTANZEN = 100                           # Instanzen je Zelle; der Wert steht neben jeder Zahl
STICHPROBE_J = (0, 1, 2)                  # Instanzen jeder Zelle, die einzeln gespeichert und in den Tests frisch nachgerechnet werden
MESS_N = (12, 20, 40)
EXAKT_N = (12, 20)                        # in diesen Zellen gibt es das Optimum (aus Stück 7 und 8 übernommen, CP-SAT mit Zeitlimit, ggf. nicht entschieden)
OPT_HERKUNFT = "skyline-maxrects-demo/smx_precomputed.json (Stück 8, dort aus Stück 7): gleiche Verteilungen und Seeds, Optimum je Instanz mit CP-SAT (60 Sekunden Zeitlimit), -1 = nicht entschieden"
OBERGRENZE_N = (7, 8)                     # bei diesen Rechteckzahlen werden alle Reihenfolgen durchprobiert (7! = 5040, 8! = 40320)
OBERGRENZE_INSTANZEN = {7: 60, 8: 25}     # Instanzen je Verteilung

COLOR_LINE = "#c0392b"
REGAL_FARBEN = ("#4c78a8", "#f58518", "#54a24b", "#b279a2", "#e45756", "#72b7b2", "#9d755d", "#bab0ac", "#eeca3b", "#ff9da6")
COLOR_BEHAELTER = "#2F6B65"
COLOR_FUELLUNG = "#c0392b"
SUCHE_FARBEN = {0: "#9d755d", 1: "#4c78a8", 2: "#f58518", 3: "#2F6B65"}

PRESETS = {
    "Beispiel 1, Tausch mit Füllung, 200 Auswertungen": {"quelle": 0, "n_index": 0, "seed": DEFAULT_SEED, "suche": 3, "budget": 200, "suchseed": SUCHSEED_STANDARD},
    "Beispiel 1, Tausch nur Behälterzahl, 200": {"quelle": 0, "n_index": 0, "seed": DEFAULT_SEED, "suche": 2, "budget": 200, "suchseed": SUCHSEED_STANDARD},
    "Beispiel 2, Tausch mit Füllung, 1000": {"quelle": 1, "n_index": 0, "seed": DEFAULT_SEED, "suche": 3, "budget": 1000, "suchseed": SUCHSEED_STANDARD},
    "Mittlere Rechtecke, 40 Stück, Tausch mit Füllung": {"quelle": 2, "n_index": 2, "seed": DEFAULT_SEED, "suche": 3, "budget": 1000, "suchseed": SUCHSEED_STANDARD},
}
PRESET_HELP = {
    "Beispiel 1, Tausch mit Füllung, 200 Auswertungen": "Zwölf Rechtecke: Die Reihenfolge nach Fläche braucht drei Behälter. Die Suche, die auch die Füllung des leersten Behälters zählt, findet mit der Startzahl 1 zwei Behälter.",
    "Beispiel 1, Tausch nur Behälterzahl, 200": "Dieselben zwölf Rechtecke, aber die Suche zählt nur die Behälterzahl: Mit der Startzahl 1 sieht sie nach 200 Auswertungen keinen Unterschied und steht noch bei drei Behältern (andere Startzahlen finden zwei, aber seltener).",
    "Beispiel 2, Tausch mit Füllung, 1000": "Ein zweites Beispiel: Es gibt zwei Behälter (CP-SAT), die Suche findet sie mit der Startzahl 1 in 1000 Auswertungen nicht.",
    "Mittlere Rechtecke, 40 Stück, Tausch mit Füllung": "Vierzig mittlere Rechtecke, 1000 Auswertungen (etwa eine Sekunde): Die Suche bleibt bei acht Behältern (Schranke 7), aber die Füllung des leersten Behälters sinkt von 6609 auf 2925: Er ist näher am Leerwerden.",
}

# Text des Expanders „Annahmen, Grenzen und bekannte Probleme“; derselbe Wortlaut steht in der README (tests/test_claims.py vergleicht beide).
ASSUMPTIONS_MARKDOWN = f"""**Annahmen.** Rechtecke mit ganzzahliger Breite und Höhe, ohne Drehung; Behälter {CAP} mal {CAP}; alle Rechtecke sind vor dem Packen bekannt; der Dekodierer ist MaxRects mit kleinster kurzer Restkante (BSSF) aus Stück 8; eine Auswertung ist eine Dekodierung einer Reihenfolge.

**Grenzen.** Das Messraster deckt vier Verteilungen der Rechteckmaße und drei Rechteckzahlen (12, 20, 40) ab, jeweils mit {INSTANZEN} Instanzen je Zelle; es sind dieselben Instanzen wie in Stück 7 und 8. Die Suchen sind Zufallsstarts und eine Tausch-Suche mit zwei Zielen; weitere Suchverfahren, Dekodierer, Drehung und Praxisdaten kommen nicht vor. 80 Rechtecke fehlen wegen der Rechenzeit des Generators. Das exakte Optimum (über alle Packungen) gibt es bei 12 und 20 Rechtecken, bei 20 nur für die Instanzen, die CP-SAT in der Zeit entschieden hat; bei 40 Rechtecken fehlt es.

**Bekannte Probleme und Unsicherheiten.** Das Ergebnis jeder Suche hängt an ihrer Startzahl: Eine einzelne Suche ist ein Zufallsergebnis, die Tabellen zeigen Mittel über 100 Instanzen mit je einer Startzahl. Bei 40 Rechtecken ist der Maßstab die Schranke, die in 2D locker ist (bei 12 und 20 Rechtecken gemessen, bei 40 vermutlich ebenso). Die entschiedenen Instanzen bei 20 Rechtecken sind die für CP-SAT leichteren, die Mittel dort dürften nach unten verzerrt sein. Die Optima stammen aus Stück 7 und werden nur stichprobenweise nachgerechnet. Das Zweitziel (Füllung des leersten Behälters) ist eine eigene Wahl dieser Demo. Zur Laufzeit macht die Demo keine Aussage: Eine Auswertung ist hier eine Dekodierung, keine Zeit. Die App wurde im Browser bedient (Presets, Würfel-Button, Suchlauf und Ausklapper auf Desktopbreite; auf Telefonbreite wurde nur das Layout geprüft), nicht auf einem echten Touch-Gerät."""
