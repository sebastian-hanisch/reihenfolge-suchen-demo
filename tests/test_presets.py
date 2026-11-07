"""Presets: Vollständigkeit, gültige Werte, erstes Preset = Standardeinstellungen, jeder Hilfetext stimmt mit der Rechnung überein."""

import rsu_algorithm as A
import rsu_constants as C
import rsu_evaluation as ev
import rsu_presets as P
from rsu_scenario import beispiel


def test_every_preset_has_help_and_all_keys():
    assert set(C.PRESETS) == set(C.PRESET_HELP)
    for name, preset in C.PRESETS.items():
        assert set(preset) == set(P.PRESET_KEYS), name
        assert C.PRESET_HELP[name]


def test_preset_values_are_inside_the_widget_bounds():
    for name, preset in C.PRESETS.items():
        for key, state_key in P.PRESET_KEYS.items():
            spec = P.SETTING_SPECS[state_key]
            assert spec.lo <= preset[key] <= spec.hi, (name, key)


def test_first_preset_equals_the_default_settings():
    assert ev.Settings(**next(iter(C.PRESETS.values()))) == ev.Settings()


def test_setting_specs_cover_every_preset_key():
    assert set(P.PRESET_KEYS.values()) == set(P.SETTING_SPECS)


def test_defaults_of_the_widgets_equal_the_default_settings():
    s = ev.Settings()
    schluessel = ("quelle_select", "n_select", "seed_input", "suche_select", "budget_input", "suchseed_input")
    assert [P.SETTING_SPECS[k].default for k in schluessel] == [s.quelle, s.n_index, s.seed, s.suche, s.budget, s.suchseed]


def _a(name):
    return ev.analyse(ev.Settings(**C.PRESETS[name]))


def _gefunden(quelle, methode, budget, startzahlen=range(1, 21)):
    """In wie vielen der Startzahlen die Suche die zwei Behälter des Optimums findet."""
    rects = beispiel(quelle).rects
    return sum(A.suche(rects, C.CAP, methode, budget, s)[1][-1][0] == 2 for s in startzahlen)


def test_presets_behaupten_nur_was_stimmt():
    eins = _a("Beispiel 1, Tausch mit Füllung, 200 Auswertungen")
    assert eins.start[0] == 3 and eins.count == 2 == eins.opt
    assert "braucht drei Behälter" in C.PRESET_HELP["Beispiel 1, Tausch mit Füllung, 200 Auswertungen"] and "findet mit der Startzahl 1 zwei Behälter" in C.PRESET_HELP["Beispiel 1, Tausch mit Füllung, 200 Auswertungen"]
    zwei = _a("Beispiel 1, Tausch nur Behälterzahl, 200")
    assert zwei.count == 3 == zwei.start[0] and zwei.opt == 2
    hilfe2 = C.PRESET_HELP["Beispiel 1, Tausch nur Behälterzahl, 200"]
    assert "steht noch bei drei Behältern" in hilfe2 and "andere Startzahlen finden zwei, aber seltener" in hilfe2
    assert (_gefunden(0, 2, 200), _gefunden(0, 3, 200)) == (4, 11)              # von 20 Startzahlen: seltener, aber nicht nie
    drei = _a("Beispiel 2, Tausch mit Füllung, 1000")
    assert drei.count == 3 and drei.opt == 2 and "findet sie mit der Startzahl 1 in 1000 Auswertungen nicht" in C.PRESET_HELP["Beispiel 2, Tausch mit Füllung, 1000"]
    vier = _a("Mittlere Rechtecke, 40 Stück, Tausch mit Füllung")
    assert (vier.start, vier.verlauf[-1], vier.schranke) == ((8, 6609), (8, 2925), 7)
    assert "bleibt bei acht Behältern (Schranke 7)" in C.PRESET_HELP["Mittlere Rechtecke, 40 Stück, Tausch mit Füllung"] and "von 6609 auf 2925" in C.PRESET_HELP["Mittlere Rechtecke, 40 Stück, Tausch mit Füllung"]
    assert all(A.packung_pruefen(x.inst.rects, x.platz, x.inst.cap) for x in (eins, zwei, drei, vier))


def test_zweites_beispiel_ist_mit_zwei_behaeltern_loesbar_und_die_suche_findet_sie_selten():
    # die Behauptung „Es gibt zwei Behälter“ steht auf CP-SAT (test_claims.py); hier: von 20 Startzahlen findet höchstens eine sie
    assert [_gefunden(1, m, b) for m in (1, 2, 3) for b in (50, 200, 1000)] == [0, 0, 0, 0, 0, 0, 0, 1, 1]
