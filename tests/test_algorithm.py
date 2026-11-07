"""Kern an der Mini-Instanz von Hand und an den Handbeispielen der App (DEMO-PLAYBOOK §1b).

Handrechnung Mini-Instanz (Behälter 10 mal 10; Rechtecke 0: (5, 4), 1: (9, 2), 2: (3, 5), 3: (3, 2); Flächen 20, 18, 15, 6):
  Reihenfolge nach Fläche: 0, 1, 2, 3.
  MaxRects BSSF: frei [(0,0,10,10)]. 0 -> (0, 0); frei [(5,0,5,10), (0,4,10,6)].
      1 (9, 2): (5,0,5,10) ist zu schmal, (0,4,10,6) passt -> (0, 4); frei [(9,0,1,10), (5,0,5,4), (0,6,10,4)] (das Teil (5,6,5,4) liegt in (0,6,10,4), (9,4,1,6) in (9,0,1,10)).
      2 (3, 5): (9,0,1,10) zu schmal, (5,0,5,4) und (0,6,10,4) zu niedrig -> neuer Behälter, (0, 0).
      3 (3, 2): in Behälter 0 passen (5,0,5,4) mit Restkanten (2, 2) und (0,6,10,4) mit (2, 7): (5, 0).             => [[0, 1, 3], [2]], Fläche im leersten Behälter 15
  Reihenfolge 3, 1, 2, 0: 3 (3, 2) -> (0, 0); frei [(3,0,7,10), (0,2,10,8)]. 1 (9, 2): nur (0,2,10,8) -> (0, 2); frei [(9,0,1,10), (3,0,7,2), (0,4,10,6)].
      2 (3, 5): (0,4,10,6) -> (0, 4); frei [(9,0,1,10), (3,0,7,2), (3,4,7,6), (0,9,10,1)]. 0 (5, 4): (3,4,7,6) mit Restkanten (2, 2) -> (3, 4).      => [[3, 1, 2, 0]], Fläche 59
Zufall (Startzahl 1, random() liefert 0,1343...; 0,8474...; 0,7637...):
  unter(10) = int(0,1343 * 10) = 1. mischen([0, 1, 2, 3]): k = 3: j = int(0,1343 * 4) = 0, Tausch von 3 und 0 -> [3, 1, 2, 0]; k = 2: j = int(0,8474 * 3) = 2, kein Tausch; k = 1: j = int(0,7637 * 2) = 1, kein Tausch.
  paar(4): i = int(0,1343 * 4) = 0, j = int(0,8474 * 3) = 2, weil j >= i wird j = 3: (0, 3).
Suche mit der Startzahl 1: die zweite Auswertung ist bei Zufallsstarts die Mischung [3, 1, 2, 0], bei der Tausch-Suche der Tausch (0, 3) der Startreihenfolge 0, 1, 2, 3 -> ebenfalls [3, 1, 2, 0].
"""

import random

import pytest

import rsu_algorithm as A
import rsu_constants as C
from rsu_scenario import beispiel


def test_reihenfolge_nach_flaeche_mit_gleichstaenden_in_lieferreihenfolge(mini):
    assert A.reihenfolge_flaeche(mini.rects) == [0, 1, 2, 3]
    assert A.reihenfolge_flaeche(((2, 3), (3, 2), (1, 7), (6, 1))) == [2, 0, 1, 3]     # Flächen 6, 6, 7, 6: erst die 7, dann die drei Gleichstände in Lieferreihenfolge
    assert A.reihenfolge_flaeche(((2, 3), (3, 2), (6, 1))) == [0, 1, 2]


def test_maxrects_bssf_auf_der_mini_instanz_mit_den_freien_rechtecken(mini):
    bins, platz, zustand = A.pack(mini.rects, [0, 1, 2, 3], 10)
    assert bins == [[0, 1, 3], [2]] and platz == [(0, 0, 0, 0), (1, 0, 0, 4), (2, 1, 0, 0), (3, 0, 5, 0)]
    # Schritt für Schritt: der Zustand nach k Rechtecken ist der Zustand des Anfangs der Reihenfolge
    assert A.pack(mini.rects, [0], 10)[2] == [[(5, 0, 5, 10), (0, 4, 10, 6)]]
    assert A.pack(mini.rects, [0, 1], 10)[2] == [[(9, 0, 1, 10), (5, 0, 5, 4), (0, 6, 10, 4)]]


def test_maxrects_bssf_in_der_tauschreihenfolge(mini):
    bins, platz, zustand = A.pack(mini.rects, [3, 1, 2, 0], 10)
    assert bins == [[3, 1, 2, 0]] and platz == [(3, 0, 0, 0), (1, 0, 0, 2), (2, 0, 0, 4), (0, 0, 3, 4)]
    assert A.pack(mini.rects, [3], 10)[2] == [[(3, 0, 7, 10), (0, 2, 10, 8)]]
    assert A.pack(mini.rects, [3, 1], 10)[2] == [[(9, 0, 1, 10), (3, 0, 7, 2), (0, 4, 10, 6)]]
    assert A.pack(mini.rects, [3, 1, 2], 10)[2] == [[(9, 0, 1, 10), (3, 0, 7, 2), (3, 4, 7, 6), (0, 9, 10, 1)]]


def test_bewerten_zaehlt_behaelter_und_die_flaeche_im_leersten(mini):
    assert A.bewerten(mini.rects, [0, 1, 2, 3], 10) == (2, 15)
    assert A.bewerten(mini.rects, [3, 1, 2, 0], 10) == (1, 59)
    assert A.bewerten(mini.rects, [], 10) == (0, 0)


def test_schranken_der_mini_instanz(mini):
    assert A.schranken(mini.rects, 10) == (1, 0, 1) and A.schranke(mini.rects, 10) == 1
    # drei große Rechtecke (beide Maße über 5) brauchen drei Behälter, obwohl die Fläche (3 mal 36 = 108 von 100 je Behälter) nur zwei fordert
    assert A.schranken(((6, 6), (6, 6), (6, 6)), 10) == (2, 3, 3)
    assert A.schranken(((5, 9), (9, 5)), 10) == (1, 0, 1)      # genau die Hälfte zählt nicht als groß


def test_zufall_stimmt_mit_den_handwerten_der_startzahl_1_ueberein():
    assert random.Random(1).random() == pytest.approx(0.13436424411240122)
    assert A.Zufall(1).unter(10) == 1
    assert A.Zufall(1).mischen(range(4)) == [3, 1, 2, 0]
    assert A.Zufall(1).paar(4) == (0, 3)
    z = A.Zufall(1)
    assert [z.unter(10) for _ in range(3)] == [1, 8, 7]            # 0,134 / 0,847 / 0,763


def test_zufall_nutzt_nur_random_und_ist_reproduzierbar():
    for seed in (0, 1, 7, 999999):
        r = random.Random(seed)
        z = A.Zufall(seed)
        assert [z.unter(37) for _ in range(5)] == [int(r.random() * 37) for _ in range(5)]
        assert A.Zufall(seed).mischen(range(9)) == A.Zufall(seed).mischen(range(9))


def test_mischen_veraendert_die_eingabe_nicht_und_liefert_eine_permutation():
    eingabe = [4, 2, 9, 1]
    for seed in range(30):
        out = A.Zufall(seed).mischen(eingabe)
        assert eingabe == [4, 2, 9, 1] and sorted(out) == [1, 2, 4, 9]


def test_paar_liefert_zwei_verschiedene_positionen_im_bereich():
    z = A.Zufall(3)
    for n in (2, 3, 4, 12):
        for _ in range(200):
            i, j = z.paar(n)
            assert 0 <= i < n and 0 <= j < n and i != j


def test_suche_auf_der_mini_instanz_findet_die_tauschreihenfolge_mit_der_startzahl_1(mini):
    for methode in (1, 2, 3):
        beste, verlauf = A.suche(mini.rects, 10, methode, 2, 1)
        assert beste == [3, 1, 2, 0] and verlauf == [(2, 15), (1, 59)], methode
        beste, verlauf = A.suche(mini.rects, 10, methode, 1, 1)
        assert beste == [0, 1, 2, 3] and verlauf == [(2, 15)], methode


def test_suche_ohne_methode_bleibt_beim_start(mini):
    beste, verlauf = A.suche(mini.rects, 10, 0, 5, 1)
    assert beste == [0, 1, 2, 3] and verlauf == [(2, 15)] * 5


def test_suche_beispiel_1_mit_der_startzahl_1():
    rects = beispiel(0).rects
    assert A.bewerten(rects, A.reihenfolge_flaeche(rects), C.CAP)[0] == 3
    ergebnisse = {m: A.suche(rects, C.CAP, m, 200, 1)[1][-1][0] for m in (2, 3)}
    assert ergebnisse == {2: 3, 3: 2}      # wie im Preset-Text: Tausch mit Zweitziel findet zwei Behälter, Tausch nur auf die Behälterzahl nach 200 Auswertungen noch nicht


def test_suche_ist_deterministisch_und_der_verlauf_ist_ein_praefix_des_laengeren():
    rects = beispiel(0).rects
    for methode in (1, 2, 3):
        kurz = A.suche(rects, C.CAP, methode, 50, 4)[1]
        lang = A.suche(rects, C.CAP, methode, 120, 4)
        assert lang == A.suche(rects, C.CAP, methode, 120, 4) and lang[1][:50] == kurz


def test_verlauf_hat_budget_eintraege_faellt_nie_und_gehoert_zur_besten_reihenfolge():
    for seed in range(8):
        rng = random.Random(seed)
        rects = tuple((rng.randint(10, 60), rng.randint(10, 60)) for _ in range(rng.randint(2, 14)))
        for methode in (1, 2, 3):
            beste, verlauf = A.suche(rects, 100, methode, 60, seed)
            assert len(verlauf) == 60 and sorted(beste) == list(range(len(rects)))
            behaelter = [b for b, _ in verlauf]
            assert behaelter == sorted(behaelter, reverse=True)
            if methode == 3:
                assert verlauf == sorted(verlauf, reverse=True)           # lexikographisch nie schlechter
            assert verlauf[-1] == A.bewerten(rects, beste, 100) and verlauf[0] == A.bewerten(rects, A.reihenfolge_flaeche(rects), 100)
            assert verlauf[-1][0] >= A.schranke(rects, 100)


def test_packung_pruefen_erkennt_fehler(mini):
    gut = [(0, 0, 0, 0), (1, 0, 0, 4), (2, 1, 0, 0), (3, 0, 5, 0)]
    assert A.packung_pruefen(mini.rects, gut, 10)
    assert not A.packung_pruefen(mini.rects, gut[:3], 10) and A.packung_pruefen(mini.rects, gut[:3], 10, vollstaendig=False)
    assert not A.packung_pruefen(mini.rects, gut + [(0, 1, 0, 0)], 10)                       # Rechteck 0 doppelt
    assert not A.packung_pruefen(mini.rects, [(0, 0, 0, 0), (1, 0, 0, 3), (2, 1, 0, 0), (3, 0, 5, 0)], 10)   # (9, 2) bei y = 3 überlappt (5, 4)
    assert not A.packung_pruefen(mini.rects, [(0, 0, 6, 0), (1, 0, 0, 4), (2, 1, 0, 0), (3, 0, 5, 5)], 10)   # (5, 4) bei x = 6 ragt hinaus
    assert A.packung_pruefen(mini.rects, [(0, 0, 0, 0), (1, 0, 0, 4), (2, 1, 0, 0), (3, 0, 5, 2)], 10)        # Berührung ist keine Überlappung
    assert not A.packung_pruefen(mini.rects, [(0, 0, -1, 0), (1, 0, 0, 4), (2, 1, 0, 0), (3, 0, 5, 0)], 10)   # negative Lage
    assert not A.packung_pruefen(mini.rects, [(7, 0, 0, 0)], 10, vollstaendig=False)                           # Nummer außerhalb


def test_pack_lehnt_ungueltige_eingaben_ab(mini):
    with pytest.raises(ValueError):
        A.pack(mini.rects, [0, 0], 10)
    with pytest.raises(ValueError):
        A.pack(mini.rects, [4], 10)
    with pytest.raises(ValueError):
        A.pack(((11, 3),), [0], 10)
    with pytest.raises(ValueError):
        A.pack(((0, 3),), [0], 10)
    with pytest.raises(ValueError):
        A.pack(((3,),), [0], 10)
