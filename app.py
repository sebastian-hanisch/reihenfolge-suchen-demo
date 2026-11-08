"""Packen: Reihenfolge suchen, Zufall und Tausch - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Stück 12 der Reihe „Packen: Reihenfolge und Platzierungsregel“. Der Dekodierer (MaxRects BSSF aus Stück 8) macht aus jeder Reihenfolge eine Packung; hier wird die Reihenfolge gesucht:
mit Zufallsstarts und mit einer Tausch-Suche. Das Messraster (vorberechnet in rsu_precomputed.json) zeigt an je 100 Zufallsinstanzen, was die Suche bringt.

Lauffähig mit: streamlit run app.py
"""

import streamlit as st

import rsu_constants as C
from rsu_evaluation import (
    SUCHEN_LISTE,
    Settings,
    analyse,
    obergrenze_zeilen,
    optimum_zeilen,
    referenz,
    verdict_aktuell,
    verdict_messung,
    verdict_obergrenze,
    verdict_optimum,
    zeile,
)
from rsu_layout import dunkles_design, kopf_css
from rsu_presets import (
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    randomize_seed,
    sidebar_presets,
    sync_query_params,
)
from rsu_visualization import build_behaelter, build_messung, build_verlauf

st.set_page_config(page_title="Packen – Sebastian Hanisch", layout="wide")


@st.cache_data(show_spinner=False)
def _analysis(settings):
    return analyse(settings)


# Fester Kopf: nur der Titel bleibt beim Scrollen oben (Stylesheet in rsu_layout.py).
st.html(kopf_css(dunkles_design()))
with st.container(key="kopf"):
    st.title("🔀 Reihenfolge suchen: Zufall und Tausch")
st.markdown(
    """
Der Dekodierer aus Stück 8 (**MaxRects**) macht aus jeder Reihenfolge der Rechtecke eine Packung. Die Reihenfolge nach Fläche ist ein guter Start, aber nicht der beste. Zwei Fragen: **Findet eine Suche eine Reihenfolge mit weniger Behältern**, und **hilft es, auch die Füllung des leersten Behälters zu zählen**, wenn die Behälterzahl allein nichts mehr unterscheidet? Die Demo lässt eine Suche live laufen und zeigt an einem Messraster aus je 100 Zufallsinstanzen, wie viel das bringt.

Weiter unten: der Abschnitt **🔬 Experimente**, **🚧 Wo die Annahmen enden**, der Expander **⚠️ Annahmen, Grenzen und bekannte Probleme** und der Expander **📐 Mathematische Formulierung**.
"""
)

with st.expander("So funktioniert die Suche", expanded=True):
    st.markdown(
        """
1. **Start:** Die erste Auswertung ist die Reihenfolge nach fallender Fläche. Eine *Auswertung* heißt: die Reihenfolge dekodieren und die Behälter zählen.
2. **Zufallsstarts:** Jede weitere Auswertung ist eine ganz neue zufällige Reihenfolge; die mit den wenigsten Behältern bleibt (bei Gleichstand die frühere).
3. **Tausch-Suche:** Jede weitere Auswertung vertauscht zwei zufällige Positionen der bisher besten Reihenfolge. Wird die Behälterzahl nicht größer, wird die neue Reihenfolge die beste (Variante *nur Behälterzahl*). In der Variante *mit Zweitziel* zählt bei gleicher Behälterzahl auch die Fläche im am wenigsten gefüllten Behälter, die kleiner werden soll: Der leerste Behälter soll sich leeren, damit er am Ende vielleicht ganz verschwindet.
4. **Verlauf:** Die Kurve zeigt nach jeder Auswertung die Behälter (Stufenlinie) und die Fläche im leersten Behälter der bisher besten Reihenfolge.
        """
    )

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    sidebar_presets()  # Schnellstart oben, das aktive Preset ist hervorgehoben
    st.header("⚙️ Einstellungen")
    st.markdown("**Rechtecke**")
    quelle = st.selectbox("Instanz", list(C.QUELLEN), format_func=C.QUELLEN.get, key="quelle_select",
                          help="Die beiden Beispiele haben je zwölf feste Rechtecke. Die anderen vier sind Zufallsinstanzen mit verschiedener Verteilung der Maße.")
    n_index = st.selectbox("Zahl der Rechtecke (nur Zufallsinstanzen)", list(range(len(C.N_WERTE))), format_func=lambda i: str(C.N_WERTE[i]), key="n_select",
                           help="Gilt nur für Zufallsinstanzen.")
    seed = st.number_input("Startzahl der Zufallsinstanz", *bounds("seed_input"), key="seed_input", step=1,
                           help="Wirkt nur bei den Zufallsinstanzen.")
    st.button("🎲 Neue Zufallsinstanz würfeln", width="stretch", on_click=randomize_seed)
    st.markdown("**Suche**")
    suche = st.selectbox("Suche", list(C.SUCHEN), format_func=C.SUCHEN.get, key="suche_select",
                         help="Wie die Reihenfolge verändert wird. „Keine Suche“ bleibt bei der Reihenfolge nach Fläche.")
    budget = st.number_input("Auswertungen (Budget)", *bounds("budget_input"), key="budget_input", step=50,
                             help="Wie viele Reihenfolgen höchstens dekodiert werden, die erste (nach Fläche) eingerechnet.")
    suchseed = st.number_input("Startzahl der Suche", *bounds("suchseed_input"), key="suchseed_input", step=1,
                               help="Der Zufall der Suche. Eine andere Startzahl gibt einen anderen Lauf: Ein einzelner Lauf ist ein Zufallsergebnis.")

sync_query_params({"quelle_select": int(quelle), "n_select": int(n_index), "seed_input": int(seed), "suche_select": int(suche), "budget_input": int(budget),
                   "suchseed_input": int(suchseed)})

settings = Settings(int(quelle), int(n_index), int(seed), int(suche), int(budget), int(suchseed))
a = _analysis(settings)

# --- Ergebnis ------------------------------------------------------------------------------------------------------------------------------

st.markdown("## 🎯 Ergebnis")
m1, m2, m3, m4 = st.columns(4)
# Delta immer als „mein Wert minus Referenz“; die Farbe regelt delta_color="inverse" (Vorzeichen-Falle, DEMO-PLAYBOOK §2).
m1.metric("Behälter nach der Suche", a.count, delta=a.count - a.start[0], delta_color="inverse", help="Delta: Behälter der Suche minus Behälter der Reihenfolge nach Fläche.")
m2.metric("Reihenfolge nach Fläche", a.start[0], delta="Start", delta_color="off")
if a.opt is not None:
    m3.metric("Optimum (exakt, über alle Packungen)", a.opt, delta="Referenz", delta_color="off")
else:
    m3.metric("Optimum", "nicht berechnet", delta="nur für die Beispiele", delta_color="off")
m4.metric("Untere Schranke", a.schranke, delta="Fläche oder große Rechtecke", delta_color="off")
flaeche = sum(w * h for w, h in a.inst.rects)
st.caption(f"{a.inst.n} Rechtecke, Gesamtfläche {flaeche} von {a.inst.cap * a.inst.cap} je Behälter. Fläche im leersten Behälter: {a.start[1]} am Start, {a.verlauf[-1][1]} am Ende.")
kind, text = verdict_aktuell(a)
getattr(st, kind)(text)
st.markdown("**Beste gefundene Packung:** jeder gestrichelte Rahmen ist ein Behälter, die Farbe zeigt die Reihenfolge des Setzens, die Zahl die Nummer des Rechtecks in der Lieferreihenfolge.")
st.plotly_chart(build_behaelter(a.inst.rects, a.platz, a.inst.cap), width="stretch", key="main_chart")
st.markdown("**Verlauf der Suche**")
st.plotly_chart(build_verlauf(a.verlauf, a.schranke, a.opt), width="stretch", key="verlauf_chart")
st.caption("Die Stufenlinie ist die Behälterzahl der bisher besten Reihenfolge, die gepunktete Linie die Fläche im leersten Behälter (rechte Achse). Beide können nur fallen. Die Schranke ist grau, das Optimum (nur bei den Beispielen) rot gestrichelt.")

st.markdown("---")

# --- Experimente ---------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experimente: Gilt das für viele Instanzen?")
st.caption(
    f"Gemessen an je {C.INSTANZEN} festen Zufallsinstanzen pro Zelle, Behälter {C.CAP} mal {C.CAP}, ganzzahlige Maße der Rechtecke ohne Drehung; dieselben Instanzen und Optima wie in Stück 7 und 8. "
    "Jede Suche läuft je Instanz einmal mit einer festen Startzahl. Die Zahlen sind vorberechnet (`generate_precomputed.py`)."
)
e1, e2 = st.columns(2)
verteilung = e1.selectbox("Verteilung der Rechtecke", list(range(len(C.VERTEILUNGEN))), index=0, format_func=lambda i: C.VERTEILUNGEN[i][1], key="exp_verteilung")
ni = e2.selectbox("Zahl der Rechtecke n", list(range(len(C.MESS_N))), index=1, format_func=lambda i: str(C.MESS_N[i]), key="exp_n")
z = zeile(int(verteilung), int(ni))

st.markdown("### Experiment 1: Was bringt die Suche über viele Instanzen?")
basis, mittel = referenz(z)
st.plotly_chart(build_messung(mittel, f"Behälter über {basis} (Mittel)"), width="stretch", key="exp_chart")
tab = ["| Suche | " + " | ".join(f"{b} Ausw." for b in C.BUDGETS) + " |", "|---|" + "---|" * len(C.BUDGETS)]
for m in SUCHEN_LISTE:
    tab.append(f"| {C.SUCHE_KURZ[m]} | " + " | ".join(f"{mittel[m][b]:.2f}" for b in C.BUDGETS) + " |")
st.markdown("\n".join(tab))
st.caption(f"Mittlere Behälter über {basis}: Mittel über die Instanzen der Zelle" + (" (nur die entschiedenen)" if z["exakt"] else "") + ". „Fläche“ ist die feste Reihenfolge ohne Suche, „Tausch B“ die Tausch-Suche auf die Behälterzahl, „Tausch B+F“ mit Zweitziel.")
kind, text = verdict_messung(z)
getattr(st, kind)(text)

st.markdown("### Experiment 2: Wie oft trifft die Suche das Optimum?")
oz = optimum_zeilen()
tab2 = ["| Rechtecke | Fläche | Zufall | Tausch B | Tausch B+F |", "|---|---|---|---|---|"]
for r in oz:
    f = lambda x: "-" if x is None else f"{x:.0f} %"  # noqa: E731
    offen = f", {r['offen']} offen" if r["offen"] else ""
    tab2.append(f"| {C.VERTEILUNG_KURZ[r['verteilung']]} {r['n']}{offen} | {f(r['flaeche'])} | {f(r['zufall'])} | {f(r['tausch_b'])} | {f(r['tausch_bf'])} |")
st.markdown("\n".join(tab2))
st.caption(
    f"Anteil der entschiedenen Instanzen, in denen die Reihenfolge nach {C.BUDGETS[-1]} Auswertungen genau das Optimum braucht. "
    "„offen“ hinter dem Namen: Zahl der nicht entschiedenen Instanzen; die entschiedenen sind die für CP-SAT leichteren. Das Optimum gilt über alle Packungen."
)
kind, text = verdict_optimum(oz)
getattr(st, kind)(text)

st.markdown("### Experiment 3: Wie weit kann die Suche überhaupt kommen?")
ob = obergrenze_zeilen()
tab3 = ["| Rechtecke | Instanzen entschieden | Fläche trifft Optimum | beste Reihenfolge trifft Optimum |", "|---|---|---|---|"]
for r in ob:
    tab3.append(f"| {r['n']} | {r['entschieden']} von {r['instanzen']} | {r['flaeche_trifft']} | {r['beste_trifft']} |")
st.markdown("\n".join(tab3))
st.caption("Bei 7 und 8 Rechtecken werden alle Reihenfolgen durchprobiert (7! = 5040, 8! = 40320), je Verteilung mit eigenen Instanzen, die Summe über vier Verteilungen. Die beste Reihenfolge ist die Obergrenze für jede Suche mit diesem Dekodierer.")
kind, text = verdict_obergrenze(ob)
getattr(st, kind)(text)

st.markdown("---")

# --- Grenzen -------------------------------------------------------------------------------------------------------------------------------

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(
    """
| Annahme | Was passiert, wenn sie verletzt ist |
|---|---|
| **Ein fester Dekodierer** | Alles gilt für MaxRects BSSF. Mit einem anderen Dekodierer (Regal, Skyline) sieht dieselbe Suche anders aus; die Demo misst das nicht. |
| **Eine Startzahl je Lauf** | Ein einzelner Lauf ist ein Zufallsergebnis; die Beispiele zeigen es: Andere Startzahlen finden mehr oder weniger. Die Tabellen mitteln über Instanzen, nicht über Läufe. |
| **Das Budget zählt Auswertungen** | Die Zeit einer Auswertung wächst mit der Zahl der Rechtecke. Die Demo macht keine Aussage zur Rechenzeit. |
| **Nur diese Suchen** | Es gibt viele weitere Verfahren (Tabu-Suche, genetische Verfahren). Die Demo vergleicht Zufallsstarts und zwei Varianten einer Tausch-Suche. |
| **Keine Drehung, alle Rechtecke bekannt** | Wie in Stück 7 und 8. |
"""
)

with st.expander("⚠️ Annahmen, Grenzen und bekannte Probleme"):
    st.markdown(C.ASSUMPTIONS_MARKDOWN)

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
**Lesehilfe.** *Gegeben:* Rechtecke mit ganzzahliger Breite und Höhe, Behälter der Größe $C \times C$, ein Dekodierer. *Gesucht:* eine Reihenfolge, deren Dekodierung wenige Behälter braucht.

| Symbol | Bedeutung |
|---|---|
| $n$ | Zahl der Rechtecke |
| $w_i$, $h_i$ | Breite und Höhe von Rechteck $i$ |
| $\pi$ | Reihenfolge, eine Permutation von $\{1, \dots, n\}$ |
| $D(\pi)$ | Packung, die MaxRects BSSF aus $\pi$ macht |
| $B(\pi)$ | Zahl der Behälter von $D(\pi)$ |
| $F(\pi)$ | Fläche im am wenigsten gefüllten Behälter von $D(\pi)$ |
| $\mathrm{OPT}$ | kleinste mögliche Zahl von Behältern über alle Packungen |

**Dekodierer.** $D(\pi)$ setzt die Rechtecke in der Reihenfolge $\pi$; jedes kommt in den ersten Behälter, in dem ein freies Rechteck für es passt, an die linke untere Ecke des freien Rechtecks mit der kleinsten kurzen Restkante $\min(f_w - w, f_h - h)$, sonst in einen neuen Behälter (Stück 8). Der Dekodierer ist deterministisch: gleiche Reihenfolge, gleiche Packung.

**Ziel.** Gesucht ist $\min_\pi B(\pi)$. Dieses Minimum kann über $\mathrm{OPT}$ liegen, weil nicht jede Packung als Dekodierung einer Reihenfolge entsteht; bei 7 und 8 Rechtecken wird es durch Durchprobieren aller $n!$ Reihenfolgen berechnet und lag in allen 340 Instanzen bei $\mathrm{OPT}$.

**Zweitziel.** In der Tausch-Suche mit Zweitziel wird $(B(\pi), F(\pi))$ lexikographisch verglichen, beides soll klein sein: Bei gleicher Behälterzahl ist die Reihenfolge besser, die den leersten Behälter weiter leert.

**Zufallsstarts.** $\pi_1$ ist die Reihenfolge nach fallender Fläche, jedes weitere $\pi_t$ eine gleichverteilte Zufallsreihenfolge (Fisher-Yates); behalten wird das $\pi_t$ mit dem kleinsten $B$, bei Gleichstand das frühere.

**Tausch-Suche.** $\pi_1$ wie oben; aus der bisher besten Reihenfolge $\pi^\ast$ entsteht $\pi_t$ durch Vertauschen zweier gleichverteilt gewählter verschiedener Positionen. Gilt $B(\pi_t) \le B(\pi^\ast)$ (bzw. $(B, F)(\pi_t) \le (B, F)(\pi^\ast)$ lexikographisch beim Zweitziel), wird $\pi^\ast \leftarrow \pi_t$. Nach höchstens $T$ Auswertungen endet die Suche.

**Schranken.** $L_{\mathrm{Fl}} = \left\lceil \tfrac{1}{C^2} \sum_i w_i h_i \right\rceil \le \mathrm{OPT}$; $L_{\mathrm{gr}} = |\{ i : w_i > C/2,\ h_i > C/2 \}| \le \mathrm{OPT}$; $L = \max(L_{\mathrm{Fl}}, L_{\mathrm{gr}})$.

**Exaktes Optimum** (Stück 7, nicht diese App). CP-SAT mit `NoOverlap2D` minimiert die Zahl benutzter Behälter; es wird mit Herkunftsvermerk aus Stück 7 und 8 übernommen.

**Literatur.** Keine Zahl und keine Aussage der Literatur ist in diese Demo übernommen; alle Zahlen sind selbst gemessen.
        """
    )

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html)."
)
