# Reihenfolge suchen: Zufall und Tausch – Streamlit-Demo

<!-- TODO nach dem Deploy: direkt hierher den Live-Link setzen (Leerzeile davor und danach):
**[→ Demo live ausprobieren](https://sebastianhanisch-reihenfolge-suchen-demo.streamlit.app/)** -->

Stück 12 der Konzepte-Reihe **„Packen: Reihenfolge und Platzierungsregel“** für die Website „Sebastian Hanisch – Operations Research und Machine Learning“ (ein Verfahren mit wachsendem Beispiel: eine Packung entsteht aus einer Reihenfolge der Teile und einer Regel, wohin das nächste kommt). Stück 8 hat die Regel (MaxRects) festgelegt und die Reihenfolge nach Fläche genommen; diese Demo **sucht die Reihenfolge**: mit Zufallsstarts und mit einer Tausch-Suche, die zwei Teile der besten Reihenfolge vertauscht. Die Fall-Demos zu Zuschnitt und Paletten zeigen die Anwendung samt Kostenmodell; diese Demo erklärt den Mechanismus davor.

## Warum dieses Problem

Der Dekodierer macht aus jeder Reihenfolge eine Packung, und die Reihenfolge nach Fläche ist ein guter, aber kein bester Start. Eine Suche kann ihn verbessern, doch wonach sucht sie, wenn die Behälterzahl über Tausende von Reihenfolgen gleich bleibt? Die Demo zeigt an zwölf Rechtecken, dass die Reihenfolge nach Fläche drei Behälter braucht, zwei aber genügen, und lässt die Suche live laufen. Sie misst an je 100 Zufallsinstanzen, was drei Suchen nach 50, 200 und 1000 Auswertungen bringen, und ob es hilft, bei gleicher Behälterzahl auch die Füllung des leersten Behälters zu zählen.

## Modell

Rechtecke mit ganzzahliger Breite und Höhe, ohne Drehung, in Behältern der Größe 100 mal 100, alle vorab bekannt. **Dekodierer:** MaxRects mit der Regel BSSF aus Stück 8 (jedes Rechteck in die linke untere Ecke des freien Rechtecks mit der kleinsten kurzen Restkante, im ersten Behälter, in dem eines passt, sonst in einen neuen). **Auswertung:** eine Reihenfolge dekodieren und (Zahl der Behälter, Fläche im am wenigsten gefüllten Behälter) lesen. **Budget:** höchstens so viele Auswertungen, die erste ist immer die Reihenfolge nach Fläche. **Zufallsstarts:** jede weitere Auswertung ist eine zufällige Reihenfolge, behalten wird die mit den wenigsten Behältern (bei Gleichstand die frühere). **Tausch-Suche:** jede weitere Auswertung vertauscht zwei zufällige Positionen der bisher besten Reihenfolge und behält die neue, wenn sie nicht schlechter ist; *Tausch B* vergleicht nur die Behälterzahl, *Tausch B+F* bei gleicher Behälterzahl auch die Fläche im leersten Behälter (kleiner ist besser: Der leerste Behälter soll sich leeren). **Schranken:** die Fläche aller Rechtecke durch die Behälterfläche, aufgerundet, und die Zahl der Rechtecke, die in beiden Maßen über die Hälfte reichen; das Größere von beiden. **Optimum** über alle Packungen mit CP-SAT (in Stück 7 berechnet, über Stück 8 mit Herkunftsvermerk übernommen). **Vier Verteilungen:** *mittel* (Breite und Höhe 20 bis 60), *breit* (5 bis 70), *klein* (10 bis 40), *hoch schmal* (Breite 5 bis 30, Höhe 30 bis 80). Formeln im Expander 📐 der App.

## Methodik

- **Kern** (`rsu_algorithm.py`): `reihenfolge_flaeche`, `pack` (MaxRects BSSF, liefert Behälter, Platzierungen und die freien Rechtecke; ein Anfang der Reihenfolge liefert den Zustand nach so vielen Schritten), `bewerten`, `suche` (Zufallsstarts und beide Tausch-Suchen, liefert die beste Reihenfolge und den Verlauf), `bester_aller_reihenfolgen` (nur für kleine n), `schranken`, `packung_pruefen` (unabhängiger Prüfer). Alle Zufallszahlen kommen aus `random.Random(seed).random()` (Klasse `Zufall`), das auf jeder Python-Version dieselben Zahlen liefert; `shuffle` und `sample` werden nicht benutzt.
- **Handbeispiele:** zwei feste Mengen von je zwölf Rechtecken aus dem Raster von Stück 7 und 8. Die App zeichnet die beste gefundene Packung maßstäblich und den Verlauf der Suche (Behälter und Fläche im leersten Behälter über die Auswertungen).
- **Messraster:** vier Verteilungen × drei Rechteckzahlen (12, 20, 40) × **100 feste Instanzen** je Zelle, dieselben Instanzen wie in Stück 7 und 8. Jede Suche läuft je Instanz einmal mit 1000 Auswertungen (feste Startzahl aus dem Instanzseed); die Werte bei 50 und 200 Auswertungen sind der Anfang desselben Laufs. Maßstab ist bei 12 und 20 Rechtecken das Optimum (nur die entschiedenen Instanzen), bei 40 die Schranke. Die Summen stehen als ganze Zahlen in `rsu_precomputed.json` (erzeugt von `generate_precomputed.py`, Optima aus `skyline-maxrects-demo/smx_precomputed.json`).
- **Obergrenze:** bei 7 und 8 Rechtecken werden alle 5040 beziehungsweise 40320 Reihenfolgen dekodiert; die beste ist die Grenze für jede Suche mit diesem Dekodierer (240 Instanzen mit 7, 100 mit 8 Rechtecken, eigene Seeds, Optimum mit CP-SAT).

## Befunde (gemessen, keine Behauptungen)

Alle Zahlen sind Messungen an den Instanzen dieser Demo (feste Seeds), nachgerechnet in `tests/test_claims.py`, `tests/test_algorithm.py`, `tests/test_presets.py` und `tests/test_oracle_reihenfolge_suchen.py`. Tabellenwerte sind Mittel über die Instanzen einer Zelle von (Behälter minus Vergleichsbasis); eine Suche läuft je Instanz mit einer Startzahl.

| Frage | Befund |
|---|---|
| Beispiel 1 (zwölf Rechtecke, Schranke 2, Optimum 2) | Die Reihenfolge nach Fläche braucht **3** Behälter. Mit der Startzahl 1 findet die Tausch-Suche mit Zweitziel nach 200 Auswertungen **2**, die auf die Behälterzahl allein nicht. Über die Startzahlen 1 bis 20 findet nach 1000 Auswertungen Zufall 6, Tausch B 14 und Tausch B+F 17 von 20 die zwei Behälter (Tabelle unten) |
| Beispiel 2 (zwölf andere Rechtecke, Schranke 2, Optimum 2) | Die Reihenfolge nach Fläche braucht **3** Behälter. Von 20 Startzahlen findet höchstens eine die zwei Behälter, und nur die Tausch-Suche mit Zweitziel (Tabelle unten) |
| Hilft die Suche? | Bei mittleren Rechtecken sinkt der mittlere Abstand zum Optimum nach 1000 Auswertungen mit Tausch B+F bei n = 12 von **0,28** (Fläche) auf **0,02** und bei n = 20 von **0,40** auf **0,10**; bei n = 40 sinkt der Abstand zur Schranke von **1,12** auf **0,73** |
| Hilft das Zweitziel? | In allen **12** Zellen liegt Tausch B+F nach 1000 Auswertungen höchstens so weit über der Bezugsgröße wie Tausch B, in **8** Zellen darunter (in 4 gleich) |
| Ist die Tausch-Suche besser als Zufallsstarts? | Tausch B ist es nicht klar: nach 1000 Auswertungen in **4** Zellen besser als Zufall, in 6 gleich und in **2** schlechter (mittlere Rechtecke n = 12: 0,09 gegen 0,05; hoch schmal n = 20: 0,03 gegen 0,02) |
| Instanz für Instanz | Von 1200 Instanzen findet nach 1000 Auswertungen eine Reihenfolge mit weniger Behältern als die nach Fläche: Zufallsstarts bei **114**, Tausch B bei **127**, Tausch B+F bei **203**; mit mehr Behältern nie (der Start zählt als erste Auswertung) |
| Wie nah am Optimum? | Die Reihenfolge nach Fläche trifft das Optimum bei 12 Rechtecken in 72 bis 95 %, bei 20 in 60 bis 99 % der entschiedenen Instanzen; Tausch B+F nach 1000 Auswertungen bei 12 in **97 bis 100 %**, bei 20 in **90 bis 99 %** |
| Wie weit kann eine Suche kommen? | Bei 7 und 8 Rechtecken liefert die beste aller Reihenfolgen in **340 von 340** Instanzen das Optimum, die Reihenfolge nach Fläche in **323**; der Dekodierer ist dort nicht die Grenze |
| Wie viele Instanzen sind nicht entschieden? | **3** von 400 bei 12 und **39** von 400 bei 20 Rechtecken (**27** bei mittleren, 1 bei breit gestreuten, 0 bei kleinen und 11 bei hohen schmalen); die Zahl hängt von der Rechenzeit in Stück 7 ab |

**Beispiel 1:** Zahl der Startzahlen 1 bis 20, bei denen die Suche das Optimum (2 Behälter) findet:

| Suche | 50 Auswertungen | 200 Auswertungen | 1000 Auswertungen |
|---|---|---|---|
| Zufall | 1 von 20 | 1 von 20 | 6 von 20 |
| Tausch B | 1 von 20 | 4 von 20 | 14 von 20 |
| Tausch B+F | 1 von 20 | 11 von 20 | 17 von 20 |

**Beispiel 2:**

| Suche | 50 Auswertungen | 200 Auswertungen | 1000 Auswertungen |
|---|---|---|---|
| Zufall | 0 von 20 | 0 von 20 | 0 von 20 |
| Tausch B | 0 von 20 | 0 von 20 | 0 von 20 |
| Tausch B+F | 0 von 20 | 1 von 20 | 1 von 20 |

**Behälter über der Vergleichsbasis** (Mittel; Basis: Optimum bei 12 und 20 Rechtecken, nur über die entschiedenen Instanzen, sonst die Schranke; Zahl hinter dem Namen = Auswertungen; bei 40 Rechtecken ist die Schranke locker, dort zählt nur der Vergleich der Suchen):

| Verteilung | n | Basis | Fläche | Zufall 200 | Zufall 1000 | Tausch B 200 | Tausch B 1000 | Tausch B+F 200 | Tausch B+F 1000 |
|---|---|---|---|---|---|---|---|---|---|
| mittel | 12 | Optimum | 0,28 | 0,11 | 0,05 | 0,11 | 0,09 | 0,06 | 0,02 |
| mittel | 20 | Optimum | 0,40 | 0,22 | 0,16 | 0,22 | 0,16 | 0,12 | 0,10 |
| mittel | 40 | Schranke | 1,12 | 1,05 | 1,00 | 0,98 | 0,97 | 0,82 | 0,73 |
| breit | 12 | Optimum | 0,06 | 0,00 | 0,00 | 0,00 | 0,00 | 0,00 | 0,00 |
| breit | 20 | Optimum | 0,29 | 0,15 | 0,11 | 0,11 | 0,05 | 0,05 | 0,03 |
| breit | 40 | Schranke | 0,92 | 0,90 | 0,86 | 0,81 | 0,80 | 0,64 | 0,59 |
| klein | 12 | Optimum | 0,16 | 0,06 | 0,03 | 0,06 | 0,03 | 0,03 | 0,03 |
| klein | 20 | Optimum | 0,01 | 0,01 | 0,01 | 0,01 | 0,01 | 0,01 | 0,01 |
| klein | 40 | Schranke | 0,15 | 0,13 | 0,13 | 0,12 | 0,10 | 0,05 | 0,03 |
| hoch schmal | 12 | Optimum | 0,05 | 0,00 | 0,00 | 0,00 | 0,00 | 0,00 | 0,00 |
| hoch schmal | 20 | Optimum | 0,12 | 0,06 | 0,02 | 0,03 | 0,03 | 0,04 | 0,01 |
| hoch schmal | 40 | Schranke | 0,91 | 0,89 | 0,89 | 0,89 | 0,89 | 0,86 | 0,81 |

**Optimum getroffen** (Anteil der entschiedenen Instanzen, in denen die Reihenfolge nach 1000 Auswertungen genau das Optimum braucht):

| Verteilung | n | Fläche | Zufall | Tausch B | Tausch B+F |
|---|---|---|---|---|---|
| mittel | 12 | 72 % | 95 % | 91 % | 98 % |
| mittel | 20 | 60 % | 84 % | 84 % | 90 % |
| breit | 12 | 94 % | 100 % | 100 % | 100 % |
| breit | 20 | 71 % | 89 % | 95 % | 97 % |
| klein | 12 | 84 % | 97 % | 97 % | 97 % |
| klein | 20 | 99 % | 99 % | 99 % | 99 % |
| hoch schmal | 12 | 95 % | 100 % | 100 % | 100 % |
| hoch schmal | 20 | 88 % | 98 % | 97 % | 99 % |

**Obergrenze** (alle Reihenfolgen durchprobiert, Summe über die vier Verteilungen):

| Rechtecke | entschiedene Instanzen | Fläche trifft das Optimum | beste Reihenfolge trifft das Optimum |
|---|---|---|---|
| 7 | 240 von 240 | 229 | 240 |
| 8 | 100 von 100 | 94 | 100 |

## Ehrliche Grenzen

- Alle Aussagen gelten für Rechtecke ohne Drehung, vier Verteilungen mit festen Bereichen, drei Rechteckzahlen, eine Behältergröße, **einen** Dekodierer (MaxRects BSSF) und genau diese drei Suchen. Andere Dekodierer, andere Suchverfahren und Praxisdaten sind nicht gemessen.
- Jede Suche läuft je Instanz **einmal**; das Ergebnis hängt an ihrer Startzahl (Beispiele: 6 bis 17 von 20 Startzahlen finden das Optimum, je nach Suche). Die Tabellen mitteln über Instanzen, nicht über Läufe.
- Das Optimum gilt über **alle** Packungen. Es stammt aus Stück 7 (CP-SAT mit Zeitlimit): Bei 20 Rechtecken sind die nicht entschiedenen Instanzen die schweren und fehlen im Mittel; bei mittleren Rechtecken sind 27 von 100 offen, der Mittelwert dort ist nach unten verzerrt. Die Optima werden hier nur stichprobenweise nachgerechnet.
- Bei 40 Rechtecken fehlt das Optimum; die Schranke ist in 2D locker, also ist dort nur der Vergleich der Suchen belastbar, nicht der Abstand zur Schranke.
- Das Zweitziel (Fläche im leersten Behälter) ist eine eigene Wahl dieser Demo; andere Zweitziele sind nicht gemessen.
- Zur **Laufzeit** macht die Demo keine Aussage: Eine Auswertung ist hier eine Dekodierung, deren Zeit mit der Zahl der Rechtecke wächst; Budgets sind in Auswertungen angegeben, nicht in Sekunden.
- Die Obergrenze gilt nur für 7 und 8 Rechtecke; ob die beste Reihenfolge auch bei 12 oder mehr Rechtecken das Optimum erreicht, ist nicht gemessen.
- Es wird keine Zahl und keine Aussage aus der Literatur übernommen.

### Annahmen, Grenzen und bekannte Probleme (Text wie in der App)

**Annahmen.** Rechtecke mit ganzzahliger Breite und Höhe, ohne Drehung; Behälter 100 mal 100; alle Rechtecke sind vor dem Packen bekannt; der Dekodierer ist MaxRects mit kleinster kurzer Restkante (BSSF) aus Stück 8; eine Auswertung ist eine Dekodierung einer Reihenfolge.

**Grenzen.** Das Messraster deckt vier Verteilungen der Rechteckmaße und drei Rechteckzahlen (12, 20, 40) ab, jeweils mit 100 Instanzen je Zelle; es sind dieselben Instanzen wie in Stück 7 und 8. Die Suchen sind Zufallsstarts und eine Tausch-Suche mit zwei Zielen; weitere Suchverfahren, Dekodierer, Drehung und Praxisdaten kommen nicht vor. 80 Rechtecke fehlen wegen der Rechenzeit des Generators. Das exakte Optimum (über alle Packungen) gibt es bei 12 und 20 Rechtecken, bei 20 nur für die Instanzen, die CP-SAT in der Zeit entschieden hat; bei 40 Rechtecken fehlt es.

**Bekannte Probleme und Unsicherheiten.** Das Ergebnis jeder Suche hängt an ihrer Startzahl: Eine einzelne Suche ist ein Zufallsergebnis, die Tabellen zeigen Mittel über 100 Instanzen mit je einer Startzahl. Bei 40 Rechtecken ist der Maßstab die Schranke, die in 2D locker ist. Die entschiedenen Instanzen bei 20 Rechtecken sind die leichteren, die Mittel dort sind nach unten verzerrt. Die Optima stammen aus Stück 7 und werden nur stichprobenweise nachgerechnet. Das Zweitziel (Füllung des leersten Behälters) ist eine eigene Wahl dieser Demo. Zur Laufzeit macht die Demo keine Aussage: Eine Auswertung ist hier eine Dekodierung, keine Zeit. Die App wurde im Browser bedient (Presets, Würfel-Button, Suchlauf und Ausklapper auf Desktopbreite; auf Telefonbreite wurde nur das Layout geprüft), nicht auf einem echten Touch-Gerät.

## Verifikation

- **Kern:** der Dekodierer an einer von Hand gerechneten Mini-Instanz (vier Rechtecke, Behälter 10 mal 10, mit Platzierungen und freien Rechtecken nach jedem Schritt, in zwei Reihenfolgen: nach Fläche 2 Behälter, vertauscht 1); die Zufallszahlen der Startzahl 1 von Hand (`unter`, `mischen`, `paar`) und die Suche mit dieser Startzahl auf der Mini-Instanz; unabhängiger Packungsprüfer; Randfälle (leere Eingabe, ein und zwei Rechtecke, Rechteck gleich Behälter, Budget 1, ungültige Eingaben, Grenzen der Regler); Eigenschaften der Suche (deterministisch, Verlauf ein Präfix des längeren, nie schlechter als der Start, Behälter nie unter der Schranke).
- **Orakel** (`tests/test_oracle_reihenfolge_suchen.py`): der Dekodierer gegen eine Umsetzung, die in jedem Schritt alle maximalen leeren Rechtecke nach Definition aus einem Belegungsraster aufzählt (Behälter 10 bis 14); die freien Rechtecke sind nach jedem Schritt genau diese und ihre Vereinigung ist genau die leere Fläche; die beste aller Reihenfolgen gegen die naive Dekodierung aller Permutationen und nie unter dem Optimum von CP-SAT; die Mischungen sind gleichverteilt (6000 Startzahlen); gemeinsames Skalieren; der Anfang der Reihenfolge ist der Anfang der Packung.
- **Messraster:** die ersten drei Instanzen jeder Zelle werden frisch gerechnet und exakt mit der Stichprobe in `rsu_precomputed.json` verglichen, eine ganze Zelle (mittlere Rechtecke, n = 12) frisch gerechnet; alle Zellen zusammen prüft `python generate_precomputed.py --check` (parallel, rund 15 Minuten). Die Optima werden stichprobenweise mit CP-SAT nachgerechnet; die Zählung der Obergrenze wird an drei Instanzen (klein, n = 7) einzeln mit CP-SAT nachgerechnet; jede Zahl dieser README als Textsuche (`tests/test_claims.py`).
- **Verdikte:** alle Zweige und Schwellen an von Hand gesetzten Werten (`tests/test_verdicts.py`).
- **Presets und Layout:** vollständig, Werte innerhalb der Reglergrenzen, erstes Preset gleich Standardeinstellung, jeder Hilfetext stimmt mit der Rechnung überein; Schnellstart oben in der Seitenleiste, fester Kopf, genau das passende Preset hervorgehoben (`tests/test_layout.py`).
- **Oberfläche:** AppTest-Rauchtest (jeder Button, jede Auswahl in jedem Wert, Startzahlen und Budget an den Grenzen) und Footer-Test.
- **Tests gesamt:** 141 (Stand 2026-11-07, alle grün; ohne `ortools` werden die CP-SAT-Proben übersprungen).

## Dateistruktur

| Datei | Zweck |
|---|---|
| `.github/workflows/tests.yml` | CI: Push, Pull Request, wöchentlicher Canary |
| `.gitignore` | venv, Caches, Streamlit-Secrets |
| `.streamlit/config.toml` | Streamlit-Einstellungen (keine Nutzungsstatistik) |
| `app.py` | Streamlit-App |
| `dev/opt.py` | exaktes Optimum mit CP-SAT (nur für Generator und Tests) |
| `dev/readme_bauen.py`, `dev/readme_vorlage.md` | setzen die README aus der Vorlage, den Tabellen der Messzellen und dem Text der Annahmen zusammen |
| `generate_precomputed.py` | erzeugt `rsu_precomputed.json` (Messraster, Obergrenze, Stichprobe; Optima aus Stück 8); `--check` vergleicht, `--keep-opt` behält die gespeicherten Optima, `--nur-stichprobe` ergänzt die Stichprobe |
| `requirements-dev.txt` | Laufzeit plus pytest und ortools |
| `requirements.txt` | Laufzeit-Bibliotheken (ungepinnt) |
| `rsu_algorithm.py` | Kern: Dekodierer, Zufall, Auswertung, Suchen, Schranken, Packungsprüfer |
| `rsu_constants.py` | Beispiele, Reglerwerte, Messraster, Farben, Presets, Text der Annahmen |
| `rsu_evaluation.py` | Analyse, Verdikte, Messzellen, Obergrenze |
| `rsu_layout.py` | Fester Kopf (Stylesheet) und Tabellen auf dem Telefon |
| `rsu_precomputed.json` | vorberechnete Summen, Optima, Obergrenze und Stichprobe |
| `rsu_presets.py` | Permalink (Begrenzen), Presets (Schnellstart, aktives Preset hervorgehoben), Würfel-Button |
| `rsu_scenario.py` | Instanzen: Handbeispiele und Zufallsinstanzen mit festen Seeds (wie in Stück 7 und 8) |
| `rsu_visualization.py` | Plotly-Abbildungen (Achsen gesperrt) |
| `tests/` | Mini-Instanz und Handrechnung, Orakel, Randfälle, Verdikte, Presets, Layout, Messraster und Zahlen der README, AppTest-Rauchtest, Footer, Laufzeit-Importe |

## Bewusst nicht umgesetzt

- **Weitere Suchverfahren (Tabu-Suche, genetische Verfahren, simuliertes Abkühlen) und andere Dekodierer:** nicht Gegenstand dieses Stücks.
- **Laufzeitvergleich:** hängt an der Umsetzung, keine Aussage.
- **80 Rechtecke:** wegen der Rechenzeit des Generators nicht im Raster.
- **Neu berechnetes Optimum:** die Optima kommen aus Stück 7 und 8; ein eigener CP-SAT-Lauf wäre derselbe, nur länger.
- **Zahlen aus der Literatur:** keine übernommen.

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

Gebaut mit Streamlit und Plotly.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html).
