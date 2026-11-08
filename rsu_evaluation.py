"""Kennzahlen, Verdikt-Logik und das Messraster (vorberechnet in rsu_precomputed.json, erzeugt von generate_precomputed.py)."""

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import rsu_algorithm as A
import rsu_constants as C
from rsu_scenario import Instance, mess_seed, quelle_instanz, zufallsinstanz

PRECOMPUTED = Path(__file__).resolve().parent / "rsu_precomputed.json"
SUCHEN_LISTE = tuple(sorted(C.SUCHEN))
SUCHEN_MIT_LAUF = (1, 2, 3)                # die drei Suchen, die im Raster laufen


@dataclass(frozen=True)
class Settings:
    quelle: int = 0
    n_index: int = 0
    seed: int = C.DEFAULT_SEED
    suche: int = 3
    budget: int = 200
    suchseed: int = C.SUCHSEED_STANDARD


@dataclass(frozen=True)
class Analysis:
    inst: Instance
    start: tuple          # (Behälter, Fläche im leersten Behälter) der Reihenfolge nach Fläche
    beste: tuple          # beste Reihenfolge der Suche (Teilenummern)
    verlauf: tuple        # verlauf[k] = (Behälter, Fläche im leersten Behälter) der besten Reihenfolge nach k + 1 Auswertungen
    bins: tuple
    platz: tuple
    count: int            # Behälter der besten Reihenfolge
    schranke: int
    opt: object           # Optimum (int) bei den Handbeispielen, sonst None
    letzte: int           # Nummer der Auswertung, bei der das Endergebnis zum ersten Mal erreicht wurde (1 = der Start)
    settings: Settings


def analyse(s: Settings) -> Analysis:
    inst = quelle_instanz(s.quelle, C.N_WERTE[s.n_index], s.seed)
    rects = inst.rects
    budget = 1 if s.suche == 0 else max(1, min(s.budget, C.BUDGET_MAX))
    beste, verlauf = A.suche(rects, inst.cap, s.suche, budget, s.suchseed)
    bins, platz, _ = A.pack(rects, beste, inst.cap)
    assert A.packung_pruefen(rects, platz, inst.cap)
    letzte = next(k for k, z in enumerate(verlauf, 1) if z == verlauf[-1])
    return Analysis(inst, verlauf[0], tuple(beste), tuple(verlauf), tuple(tuple(b) for b in bins), tuple(platz), len(bins), A.schranke(rects, inst.cap),
                    C.BEISPIEL_OPTIMUM.get(s.quelle), letzte, s)


# ------------------------------------------------------------------------------------------------------------------------------------------
# Verdikte (reine Funktionen: (Art, Text))


def verdict_aktuell(a: Analysis) -> tuple[str, str]:
    """Verdikt zum Suchlauf: Behälter der Reihenfolge nach Fläche gegen die beste gefundene, Füllung des leersten Behälters und Stand gegen Optimum oder Schranke."""
    s = a.settings
    start_b, start_f = a.start
    if a.opt is None:
        ziel = f" Das Optimum ist für diese Instanz nicht berechnet; die Schranke ist {a.schranke}."
    elif a.count == a.opt:
        ziel = f" Das ist das Optimum (die Schranke allein ergäbe {a.schranke})."
    else:
        ziel = f" Das Optimum ist **{a.opt}**: {a.count - a.opt} zu viel (die Schranke ist {a.schranke})."
    if s.suche == 0:
        return "info", f"Die feste Reihenfolge nach Fläche braucht **{start_b}** Behälter." + ziel
    ende_b, ende_f = a.verlauf[-1]
    kopf = f"Die Reihenfolge nach Fläche braucht {start_b} Behälter; nach {len(a.verlauf)} Auswertungen findet {C.SUCHE_NAME[s.suche]} **{ende_b}**."
    if ende_b < start_b:
        return "success", kopf + f" Das ist {start_b - ende_b} weniger; die beste Reihenfolge kam bei Auswertung {a.letzte}." + ziel
    if ende_f < start_f:
        return "info", kopf + f" Die Behälterzahl bleibt, aber die Fläche im leersten Behälter sinkt von {start_f} auf {ende_f} (bei Auswertung {a.letzte})." + ziel
    return "info", kopf + " Die Suche hat gegenüber der festen Reihenfolge nichts gefunden." + ziel


# ------------------------------------------------------------------------------------------------------------------------------------------
# Messraster


def messzelle(verteilung: int, n_index: int, opt: list | None = None, instanzen=None) -> dict:
    """Rechnet eine Zelle des Messrasters frisch: Summen (ganze Zahlen, damit der Vergleich exakt ist) über INSTANZEN feste Instanzen, je Suche (0 Fläche, 1 Zufall, 2 Tausch B, 3 Tausch B+F)
    und Budget (50, 200, 1000). Jede Suche läuft einmal mit 1000 Auswertungen (Startzahl 10 mal Instanzseed plus Nummer der Suche), die Werte bei 50 und 200 sind der Anfang derselben Suche.

    ueber_schranke[m][b] = Summe über alle Instanzen von (Behälter minus Schranke); besser[m][b] = Zahl der Instanzen, in denen die Suche weniger Behälter findet als die Fläche.
    Mit `opt` (Optimum je Instanz, -1 = nicht entschieden) zusätzlich, nur über die entschiedenen Instanzen: ueber_opt[m][b], trifft_opt[m][b] (Zahl der Instanzen mit Behälter gleich Optimum),
    opt_minus_schranke (Summe), opt_ueber_schranke (Zahl der Instanzen mit Optimum über der Schranke) und entschieden.
    `instanzen` (Nummern j) rechnet nur diese Instanzen der Zelle (die Tests rechnen so Stichproben nach); sonst alle INSTANZEN."""
    n = C.MESS_N[n_index]
    ms = [str(m) for m in SUCHEN_LISTE]
    bs = [str(b) for b in C.BUDGETS]
    out = {"ueber_schranke": {m: dict.fromkeys(bs, 0) for m in ms}, "besser": {m: dict.fromkeys(bs, 0) for m in ms}, "fuellung_ende": {m: dict.fromkeys(bs, 0) for m in ms}}
    if opt is not None:
        out.update({"entschieden": 0, "ueber_opt": {m: dict.fromkeys(bs, 0) for m in ms}, "trifft_opt": {m: dict.fromkeys(bs, 0) for m in ms}, "opt_minus_schranke": 0, "opt_ueber_schranke": 0})
    for j in (range(C.INSTANZEN) if instanzen is None else instanzen):
        inst = zufallsinstanz(verteilung, n, mess_seed(verteilung, n_index, j))
        s = A.schranke(inst.rects, inst.cap)
        ergebnis = {0: [A.bewerten(inst.rects, A.reihenfolge_flaeche(inst.rects), inst.cap)] * C.BUDGET_MAX}
        for m in SUCHEN_MIT_LAUF:
            ergebnis[m] = A.suche(inst.rects, inst.cap, m, C.BUDGET_MAX, 10 * mess_seed(verteilung, n_index, j) + m)[1]
        start = ergebnis[0][0][0]
        entschieden = opt is not None and opt[j] >= 0
        if entschieden:
            out["entschieden"] += 1
            out["opt_minus_schranke"] += opt[j] - s
            out["opt_ueber_schranke"] += opt[j] > s
        for m in SUCHEN_LISTE:
            for b in C.BUDGETS:
                zb, zf = ergebnis[m][b - 1]
                out["ueber_schranke"][str(m)][str(b)] += zb - s
                out["besser"][str(m)][str(b)] += zb < start
                out["fuellung_ende"][str(m)][str(b)] += zf
                if entschieden:
                    out["ueber_opt"][str(m)][str(b)] += zb - opt[j]
                    out["trifft_opt"][str(m)][str(b)] += zb == opt[j]
    return out


def obergrenze_zelle(verteilung: int, n: int, optimum_rechner) -> dict:
    """Bei kleinem n alle Reihenfolgen: Zählungen für eine Verteilung (Instanzen mit eigenen Seeds, nicht aus dem Raster). `optimum_rechner(rects, cap, obergrenze)` liefert das Optimum (-1 = nicht entschieden)."""
    anzahl = C.OBERGRENZE_INSTANZEN[n]
    out = {"instanzen": anzahl, "entschieden": 0, "opt_ueber_schranke": 0, "flaeche_trifft": 0, "beste_trifft": 0, "beste_besser_als_flaeche": 0, "abstand_flaeche": 0, "abstand_beste": 0}
    for j in range(anzahl):
        rects = zufallsinstanz(verteilung, n, obergrenze_seed(verteilung, n, j)).rects
        s = A.schranke(rects, C.CAP)
        flaeche = len(A.pack(rects, A.reihenfolge_flaeche(rects), C.CAP)[0])
        beste = A.bester_aller_reihenfolgen(rects, C.CAP)
        ober = min(beste, flaeche)
        opt = ober if ober == s else optimum_rechner(rects, C.CAP, ober)
        if opt < 0:
            continue
        out["entschieden"] += 1
        out["opt_ueber_schranke"] += opt > s
        out["flaeche_trifft"] += flaeche == opt
        out["beste_trifft"] += beste == opt
        out["beste_besser_als_flaeche"] += beste < flaeche
        out["abstand_flaeche"] += flaeche - opt
        out["abstand_beste"] += beste - opt
    return out


def obergrenze_seed(verteilung: int, n: int, j: int) -> int:
    return 5_000_000 + 1000 * verteilung + 10 * n + j


@lru_cache(maxsize=1)
def vorberechnet() -> dict:
    return json.loads(PRECOMPUTED.read_text(encoding="utf-8"))


def zelle_schluessel(verteilung: int, n_index: int) -> str:
    return f"{C.VERTEILUNGEN[verteilung][0]}|{C.MESS_N[n_index]}"


def zeile(verteilung: int, n_index: int, daten: dict | None = None) -> dict:
    """Mittelwerte und Anteile einer Zelle aus den vorberechneten Summen."""
    daten = daten or vorberechnet()
    z = daten["zellen"][zelle_schluessel(verteilung, n_index)]
    k = daten["instanzen"]
    exakt = "entschieden" in z
    e = z.get("entschieden", 0)

    def tab(summen, nenner):
        return {m: {b: summen[str(m)][str(b)] / nenner for b in C.BUDGETS} for m in SUCHEN_LISTE}

    return {
        "verteilung": verteilung,
        "name": C.VERTEILUNG_LANG[verteilung],
        "n": C.MESS_N[n_index],
        "instanzen": k,
        "exakt": exakt,
        "entschieden": e,
        "offen": (k - e) if exakt else 0,
        "mittel_schranke": tab(z["ueber_schranke"], k),
        "mittel_opt": tab(z["ueber_opt"], e) if exakt and e else None,
        "anteil_opt": {m: {b: 100.0 * z["trifft_opt"][str(m)][str(b)] / e for b in C.BUDGETS} for m in SUCHEN_LISTE} if exakt and e else None,
        "besser": {m: {b: z["besser"][str(m)][str(b)] for b in C.BUDGETS} for m in SUCHEN_LISTE},
        "opt_minus_schranke": z["opt_minus_schranke"] / e if exakt and e else None,
    }


def referenz(z: dict) -> tuple[str, dict]:
    """(Name der Vergleichsbasis, Mittel je Suche und Budget): das Optimum, wo es für mindestens eine Instanz der Zelle bekannt ist, sonst die Schranke."""
    if z["exakt"] and z["entschieden"]:
        return "dem Optimum", z["mittel_opt"]
    return "der Schranke", z["mittel_schranke"]


def gerundet(m: dict) -> dict:
    return {s: {b: round(m[s][b], 2) for b in C.BUDGETS} for s in SUCHEN_LISTE}


def verdict_messung(z: dict) -> tuple[str, str]:
    """Verdikt zur gewählten Zelle: Abstand der Fläche und der drei Suchen bei 1000 Auswertungen; hilft das Zweitziel gegenüber der Behälterzahl allein? Auf zwei Stellen gerundet verglichen."""
    basis, m = referenz(z)
    g = gerundet(m)
    n_inst = z["entschieden"] if basis == "dem Optimum" else z["instanzen"]
    b = C.BUDGETS[-1]
    kopf = (f"Für {C.VERTEILUNG_LANG[z['verteilung']]} mit n = {z['n']} liegt die feste Reihenfolge nach Fläche im Mittel {g[0][b]:.2f} Behälter über {basis} ({n_inst} Instanzen); "
            f"nach {b} Auswertungen sind es {g[1][b]:.2f} bei Zufallsstarts, {g[2][b]:.2f} bei der Tausch-Suche auf die Behälterzahl und {g[3][b]:.2f} bei der Tausch-Suche mit Zweitziel.")
    fuss = ""
    if basis == "dem Optimum" and z["offen"]:
        fuss += f" {z['offen']} von {z['instanzen']} Instanzen sind nicht entschieden und fehlen im Mittel."
    if basis == "der Schranke":
        fuss += " Bei dieser Rechteckzahl fehlt das Optimum und die Schranke ist vermutlich locker: Lesen Sie nur die Unterschiede zwischen den Suchen, nicht den Abstand."
    if g[3][b] < g[2][b]:
        return "success", kopf + " Das **Zweitziel** bringt die Suche weiter als die Behälterzahl allein." + fuss
    return "info", kopf + " Das Zweitziel bringt hier nicht mehr als die Behälterzahl allein." + fuss


def optimum_zeilen(daten: dict | None = None) -> list:
    """Experiment 2: für alle Zellen mit Optimum (n = 12 und 20, vier Verteilungen): Anteil der entschiedenen Instanzen, in denen die feste Reihenfolge und die drei Suchen (1000 Auswertungen) das Optimum treffen."""
    zeilen = []
    for v in range(len(C.VERTEILUNGEN)):
        for ni, n in enumerate(C.MESS_N):
            if n in C.EXAKT_N:
                z = zeile(v, ni, daten)
                t = z["anteil_opt"]
                b = C.BUDGETS[-1]
                zeilen.append({"verteilung": v, "n": n, "entschieden": z["entschieden"], "offen": z["offen"], "instanzen": z["instanzen"],
                               "flaeche": None if t is None else t[0][b], "zufall": None if t is None else t[1][b], "tausch_b": None if t is None else t[2][b], "tausch_bf": None if t is None else t[3][b]})
    return zeilen


def verdict_optimum(zeilen: list) -> tuple[str, str]:
    """Verdikt zu Experiment 2: in welcher Zelle die Tausch-Suche mit Zweitziel gegenüber der festen Reihenfolge am meisten dazugewinnt (auf ganze Prozent gerundet) und wie viel."""
    gueltig = [z for z in zeilen if z["tausch_bf"] is not None]
    if not gueltig:
        return "info", "Es gibt keine Zelle mit bekanntem Optimum."
    gewinn = max(gueltig, key=lambda z: (round(z["tausch_bf"]) - round(z["flaeche"]), -z["n"], -z["verteilung"]))
    return "info", (f"Am meisten bringt die Suche bei {C.VERTEILUNG_DAT[gewinn['verteilung']]} mit n = {gewinn['n']}: Die feste Reihenfolge trifft das Optimum in {gewinn['flaeche']:.0f} % der "
                    f"{gewinn['entschieden']} entschiedenen Instanzen, Zufallsstarts in {gewinn['zufall']:.0f} %, die Tausch-Suche auf die Behälterzahl in {gewinn['tausch_b']:.0f} % und "
                    f"die Tausch-Suche mit Zweitziel in {gewinn['tausch_bf']:.0f} %.")


def obergrenze_zeilen(daten: dict | None = None) -> list:
    """Obergrenze des Dekodierers: je Rechteckzahl (7, 8) die Summe über die vier Verteilungen."""
    daten = daten or vorberechnet()
    zeilen = []
    for n in C.OBERGRENZE_N:
        zellen = daten["obergrenze"][str(n)]
        summe = {k: sum(zellen[name][k] for name, *_ in C.VERTEILUNGEN) for k in ("instanzen", "entschieden", "flaeche_trifft", "beste_trifft", "beste_besser_als_flaeche")}
        zeilen.append({"n": n, **summe})
    return zeilen


def verdict_obergrenze(zeilen: list) -> tuple[str, str]:
    """Verdikt zur Obergrenze: Wie oft liefert die beste aller Reihenfolgen das Optimum, wie oft die feste Reihenfolge?"""
    teile = []
    alle = True
    for z in zeilen:
        teile.append(f"bei {z['n']} Rechtecken liefert die beste aller Reihenfolgen in {z['beste_trifft']} von {z['entschieden']} Instanzen das Optimum, die feste Reihenfolge nach Fläche in {z['flaeche_trifft']}")
        alle = alle and z["beste_trifft"] == z["entschieden"]
    text = "Alle Reihenfolgen durchprobiert: " + "; ".join(teile) + "."
    if alle:
        return "success", text + " Der Dekodierer ist hier nicht die Grenze."
    return "info", text
