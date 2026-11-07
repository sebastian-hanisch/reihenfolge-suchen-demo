"""Randfälle: leere Eingabe, ein und zwei Rechtecke, Rechteck gleich Behälter, Budget 1, ungültige Eingaben, Grenzen der Regler."""

import pytest

import rsu_algorithm as A
import rsu_constants as C
import rsu_evaluation as ev
from rsu_scenario import Instance, mess_seed, quelle_instanz, zufallsinstanz


@pytest.mark.parametrize("methode", range(4))
def test_leere_eingabe_ergibt_keine_behaelter(methode):
    assert A.pack((), [], 10) == ([], [], [])
    assert A.schranken((), 10) == (0, 0, 0)
    beste, verlauf = A.suche((), 10, methode, 3, 1)
    assert beste == [] and verlauf == [(0, 0)] * 3


@pytest.mark.parametrize("methode", range(4))
def test_ein_rechteck_hat_nichts_zu_vertauschen(methode):
    beste, verlauf = A.suche(((7, 3),), 10, methode, 5, 1)
    assert beste == [0] and verlauf == [(1, 21)] * 5


@pytest.mark.parametrize("methode", (1, 2, 3))
def test_zwei_rechtecke_werden_vertauscht_und_keine_position_zweimal(methode):
    # genau zwei Rechtecke: paar(2) liefert immer (0, 1) oder (1, 0); ein Zweig „n < 2“ darf hier nicht greifen
    rects = ((10, 6), (10, 5))
    beste, verlauf = A.suche(rects, 10, methode, 10, 3)
    assert sorted(beste) == [0, 1] and verlauf == [(2, 50)] * 10        # zwei Behälter in jeder Reihenfolge; die Fläche des leersten ist 50
    for seed in range(20):
        assert A.Zufall(seed).paar(2) in ((0, 1), (1, 0))


def test_rechteck_gleich_behaelter_braucht_einen_eigenen_behaelter():
    bins, platz, _ = A.pack(((10, 10), (1, 1)), [1, 0], 10)
    assert bins == [[1], [0]] and platz == [(1, 0, 0, 0), (0, 1, 0, 0)]
    assert A.schranken(((10, 10), (10, 10), (1, 1)), 10) == (3, 2, 3)


def test_budget_1_wertet_nur_den_start_aus():
    rects = quelle_instanz(2, 12, 7).rects
    for methode in range(4):
        beste, verlauf = A.suche(rects, C.CAP, methode, 1, 1)
        assert beste == A.reihenfolge_flaeche(rects) and len(verlauf) == 1


def test_ungueltige_methode_und_budget_werden_abgelehnt():
    with pytest.raises(ValueError):
        A.suche(((3, 3),), 10, 4, 5, 1)
    with pytest.raises(ValueError):
        A.suche(((3, 3),), 10, 1, 0, 1)


def test_instanz_lehnt_ungueltige_rechtecke_ab():
    for rects in (((0, 3),), ((11, 3),), ((3,),), ((3.5, 2),)):
        with pytest.raises(ValueError):
            Instance(rects, 10)
    with pytest.raises(ValueError):
        Instance(((1, 1),), 0)


def test_analyse_an_den_grenzen_der_regler():
    for quelle in C.QUELLEN:
        for n_index in range(len(C.N_WERTE)):
            for seed in (0, C.SEED_MAX):
                a = ev.analyse(ev.Settings(quelle, n_index, seed, 3, 7, 0))
                assert A.packung_pruefen(a.inst.rects, a.platz, a.inst.cap) and len(a.verlauf) == 7
    a = ev.analyse(ev.Settings(2, 2, 5, 3, C.BUDGET_MAX + 500, C.SEED_MAX))              # Budget über dem Höchstwert wird gekappt
    assert len(a.verlauf) == C.BUDGET_MAX
    a = ev.analyse(ev.Settings(2, 0, 5, 0, 900, 1))                                   # keine Suche: eine Auswertung, egal wie groß das Budget
    assert len(a.verlauf) == 1 and a.beste == tuple(A.reihenfolge_flaeche(a.inst.rects))


def test_beispiele_haben_zwoelf_rechtecke_und_das_optimum_der_konstanten():
    for q in C.BEISPIELE:
        inst = quelle_instanz(q, 40, 99)                                              # die Zahl der Rechtecke und die Startzahl gelten nur für Zufallsinstanzen
        assert inst.n == 12 and inst.rects == tuple(C.BEISPIELE[q])


def test_zufallsinstanzen_wachsen_mit_n_und_bleiben_im_bereich():
    for v, (_, _, (wl, wh), (hl, hh)) in enumerate(C.VERTEILUNGEN):
        for n in C.N_WERTE:
            inst = zufallsinstanz(v, n, mess_seed(v, 0, 5))
            assert inst.n == n and all(wl <= w <= wh and hl <= h <= hh for w, h in inst.rects)


def test_mess_seeds_sind_verschieden():
    seeds = {mess_seed(v, ni, j) for v in range(4) for ni in range(3) for j in range(C.INSTANZEN)}
    assert len(seeds) == 4 * 3 * C.INSTANZEN
