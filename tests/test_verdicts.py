"""Verdikte an von Hand gesetzten Werten (DEMO-PLAYBOOK §12): jede Zahl im Text und jede Schwelle der Art steht hier.

Ein Verdikt ist eine reine Funktion (Art, Text) und bekommt Zeilen, nicht Seeds. Damit prüft der Test die Grenzen (kleiner als nach Rundung auf zwei Stellen, Gleichstand) und jede genannte Zahl direkt."""

import pytest

import rsu_constants as C
import rsu_evaluation as ev
from rsu_scenario import Instance

B = C.BUDGETS


def _analysis(suche, start, verlauf, opt, schranke=2, letzte=1):
    s = ev.Settings(suche=suche, budget=len(verlauf))
    return ev.Analysis(Instance(((5, 5),), 10), start, (0,), tuple(verlauf), ((0,),), (), verlauf[-1][0], schranke, opt, letzte, s)


def test_aktuell_ohne_suche_nennt_nur_den_start():
    kind, text = ev.verdict_aktuell(_analysis(0, (3, 40), [(3, 40)], 2))
    assert kind == "info" and text == "Die feste Reihenfolge nach Fläche braucht **3** Behälter. Das Optimum ist **2**: 1 zu viel (die Schranke ist 2)."


def test_aktuell_weniger_behaelter_ist_ein_erfolg_und_nennt_die_auswertung():
    kind, text = ev.verdict_aktuell(_analysis(3, (3, 40), [(3, 40), (3, 30), (2, 55)], 2, letzte=3))
    assert kind == "success"
    assert text.startswith("Die Reihenfolge nach Fläche braucht 3 Behälter; nach 3 Auswertungen findet die Tausch-Suche mit Zweitziel **2**.")
    assert "Das ist 1 weniger; die beste Reihenfolge kam bei Auswertung 3." in text and "Das ist das Optimum (die Schranke allein ergäbe 2)." in text


def test_aktuell_gleiche_behaelter_aber_weniger_fuellung_ist_info():
    kind, text = ev.verdict_aktuell(_analysis(3, (3, 40), [(3, 40), (3, 25)], 2, letzte=2))
    assert kind == "info"
    assert "Die Behälterzahl bleibt, aber die Fläche im leersten Behälter sinkt von 40 auf 25 (bei Auswertung 2)." in text
    assert "Das Optimum ist **2**: 1 zu viel (die Schranke ist 2)." in text


def test_aktuell_nichts_gefunden():
    kind, text = ev.verdict_aktuell(_analysis(1, (3, 40), [(3, 40)] * 4, 2))
    assert kind == "info" and "nach 4 Auswertungen findet die Suche mit Zufallsstarts **3**" in text and "nichts gefunden" in text


def test_aktuell_gleiche_fuellung_zaehlt_nicht_als_besser():
    kind, text = ev.verdict_aktuell(_analysis(3, (3, 40), [(3, 40), (3, 40)], 3))
    assert "nichts gefunden" in text and "Das ist das Optimum (die Schranke allein ergäbe 2)." in text


def test_aktuell_ohne_optimum_nennt_die_schranke():
    kind, text = ev.verdict_aktuell(_analysis(2, (8, 100), [(8, 100), (7, 100)], None, schranke=7, letzte=2))
    assert kind == "success" and "Das Optimum ist für diese Instanz nicht berechnet; die Schranke ist 7." in text
    assert "findet die Tausch-Suche auf die Behälterzahl **7**" in text


# --- Messraster ----------------------------------------------------------------------------------------------------------------------------


def _mittel(werte):
    """werte[m] = Mittel bei 1000 Auswertungen; bei 50 und 200 etwas höher."""
    return {m: {B[0]: werte[m] + 0.2, B[1]: werte[m] + 0.1, B[2]: werte[m]} for m in range(4)}


def _z(werte, exakt=True, entschieden=100, offen=0, verteilung=0, n=12, instanzen=100):
    m = _mittel(werte)
    return {"verteilung": verteilung, "name": C.VERTEILUNG_LANG[verteilung], "n": n, "instanzen": instanzen, "exakt": exakt, "entschieden": entschieden, "offen": offen,
            "mittel_schranke": m, "mittel_opt": m if exakt and entschieden else None, "anteil_opt": None, "besser": {}, "opt_minus_schranke": None}


def test_messung_zweitziel_besser_ist_ein_erfolg_mit_allen_zahlen():
    kind, text = ev.verdict_messung(_z({0: 0.80, 1: 0.60, 2: 0.50, 3: 0.20}))
    assert kind == "success"
    assert text == ("Für mittlere Rechtecke mit n = 12 liegt die feste Reihenfolge nach Fläche im Mittel 0.80 Behälter über dem Optimum (100 Instanzen); "
                    "nach 1000 Auswertungen sind es 0.60 bei Zufallsstarts, 0.50 bei der Tausch-Suche auf die Behälterzahl und 0.20 bei der Tausch-Suche mit Zweitziel. "
                    "Das **Zweitziel** bringt die Suche weiter als die Behälterzahl allein.")


def test_messung_gleich_nach_rundung_ist_info():
    kind, text = ev.verdict_messung(_z({0: 0.80, 1: 0.60, 2: 0.504, 3: 0.496}))                # beide 0.50 nach Rundung
    assert kind == "info" and "Das Zweitziel bringt hier nicht mehr als die Behälterzahl allein." in text
    kind, text = ev.verdict_messung(_z({0: 0.80, 1: 0.60, 2: 0.40, 3: 0.50}))                  # schlechter
    assert kind == "info"
    kind, text = ev.verdict_messung(_z({0: 0.80, 1: 0.60, 2: 0.506, 3: 0.494}))                # 0.51 gegen 0.49
    assert kind == "success"


def test_messung_offene_instanzen_und_schranke_als_basis():
    kind, text = ev.verdict_messung(_z({0: 0.8, 1: 0.6, 2: 0.5, 3: 0.2}, entschieden=73, offen=27, n=20))
    assert "(73 Instanzen)" in text and "27 von 100 Instanzen sind nicht entschieden und fehlen im Mittel." in text
    kind, text = ev.verdict_messung(_z({0: 1.12, 1: 1.0, 2: 0.9, 3: 0.78}, exakt=False, entschieden=0, n=40, verteilung=3))
    assert "für hohe schmale Rechtecke mit n = 40".lower() in text.lower() and "über der Schranke (100 Instanzen)" in text
    assert "Bei dieser Rechteckzahl fehlt das Optimum und die Schranke ist locker" in text and "nicht entschieden" not in text
    kind, text = ev.verdict_messung(_z({0: 1.0, 1: 0.9, 2: 0.8, 3: 0.7}, exakt=True, entschieden=0, offen=100))     # nichts entschieden: Schranke als Basis
    assert "über der Schranke" in text


def test_referenz_nimmt_das_optimum_nur_mit_entschiedenen_instanzen():
    assert ev.referenz(_z({0: 1, 1: 1, 2: 1, 3: 1}))[0] == "dem Optimum"
    assert ev.referenz(_z({0: 1, 1: 1, 2: 1, 3: 1}, exakt=False, entschieden=0))[0] == "der Schranke"
    assert ev.referenz(_z({0: 1, 1: 1, 2: 1, 3: 1}, entschieden=0, offen=100))[0] == "der Schranke"


def _zeile(v, n, flaeche, zufall, tb, tbf, entschieden=100, offen=0):
    return {"verteilung": v, "n": n, "entschieden": entschieden, "offen": offen, "instanzen": 100, "flaeche": flaeche, "zufall": zufall, "tausch_b": tb, "tausch_bf": tbf}


def test_optimum_verdikt_waehlt_den_groessten_gewinn_und_nennt_alle_zahlen():
    zeilen = [_zeile(0, 12, 72.0, 80.0, 90.0, 96.0, 100), _zeile(0, 20, 60.0, 70.0, 80.0, 92.0, 73, 27), _zeile(1, 12, 90.0, 91.0, 92.0, 93.0)]
    kind, text = ev.verdict_optimum(zeilen)
    assert kind == "info"
    assert text == ("Am meisten bringt die Suche bei mittleren Rechtecken mit n = 20: Die feste Reihenfolge trifft das Optimum in 60 % der 73 entschiedenen Instanzen, "
                    "Zufallsstarts in 70 %, die Tausch-Suche auf die Behälterzahl in 80 % und die Tausch-Suche mit Zweitziel in 92 %.")


def test_optimum_verdikt_gleichstand_im_gewinn_nimmt_das_kleinere_n_dann_die_kleinere_verteilung():
    zeilen = [_zeile(1, 20, 50.0, 60.0, 70.0, 80.0), _zeile(0, 20, 50.0, 60.0, 70.0, 80.0), _zeile(2, 12, 50.0, 60.0, 70.0, 80.0)]
    assert "bei kleinen Rechtecken mit n = 12" in ev.verdict_optimum(zeilen)[1]
    assert "bei mittleren Rechtecken mit n = 20" in ev.verdict_optimum(zeilen[:2])[1]


def test_optimum_verdikt_ohne_zeile_mit_optimum():
    z = _zeile(0, 12, None, None, None, None, 0, 100)
    assert ev.verdict_optimum([z]) == ("info", "Es gibt keine Zelle mit bekanntem Optimum.")
    assert ev.verdict_optimum([]) == ("info", "Es gibt keine Zelle mit bekanntem Optimum.")


def test_obergrenze_verdikt_success_nur_wenn_die_beste_reihenfolge_immer_das_optimum_trifft():
    zeilen = [{"n": 7, "entschieden": 240, "instanzen": 240, "flaeche_trifft": 200, "beste_trifft": 240, "beste_besser_als_flaeche": 40},
              {"n": 8, "entschieden": 100, "instanzen": 100, "flaeche_trifft": 70, "beste_trifft": 100, "beste_besser_als_flaeche": 30}]
    kind, text = ev.verdict_obergrenze(zeilen)
    assert kind == "success"
    assert text == ("Alle Reihenfolgen durchprobiert: bei 7 Rechtecken liefert die beste aller Reihenfolgen in 240 von 240 Instanzen das Optimum, die feste Reihenfolge nach Fläche in 200; "
                    "bei 8 Rechtecken liefert die beste aller Reihenfolgen in 100 von 100 Instanzen das Optimum, die feste Reihenfolge nach Fläche in 70. Der Dekodierer ist hier nicht die Grenze.")
    zeilen[1] = {**zeilen[1], "beste_trifft": 99}
    kind, text = ev.verdict_obergrenze(zeilen)
    assert kind == "info" and "in 99 von 100 Instanzen" in text and "nicht die Grenze" not in text


def test_zeile_rechnet_mittel_und_anteile_aus_den_summen():
    summen = {str(m): {str(b): 4 * (m + 1) for b in B} for m in range(4)}
    zelle = {"ueber_schranke": summen, "besser": {str(m): {str(b): m for b in B} for m in range(4)}, "fuellung_ende": summen,
             "entschieden": 2, "ueber_opt": summen, "trifft_opt": {str(m): {str(b): 1 for b in B} for m in range(4)}, "opt_minus_schranke": 3, "opt_ueber_schranke": 1}
    daten = {"instanzen": 4, "cap": 100, "zellen": {"mittel|12": zelle}}
    z = ev.zeile(0, 0, daten)
    assert z["exakt"] and z["entschieden"] == 2 and z["offen"] == 2
    assert z["mittel_schranke"][2][50] == 3.0 and z["mittel_opt"][2][50] == 6.0 and z["anteil_opt"][3][1000] == 50.0
    assert z["besser"][3][200] == 3 and z["opt_minus_schranke"] == 1.5
    ohne = {"instanzen": 4, "cap": 100, "zellen": {"mittel|40": {k: zelle[k] for k in ("ueber_schranke", "besser", "fuellung_ende")}}}
    z = ev.zeile(0, 2, ohne)
    assert not z["exakt"] and z["offen"] == 0 and z["mittel_opt"] is None and z["anteil_opt"] is None
    with pytest.raises(KeyError):
        ev.zeile(1, 0, daten)
