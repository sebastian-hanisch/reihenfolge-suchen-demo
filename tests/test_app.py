"""End-to-end Smoke-Test via Streamlits offiziellem AppTest-Framework: lädt app.py mit den Standardeinstellungen, klickt jeden Button, stellt jede Auswahl
auf jeden ihrer Werte und die Zahlenfelder an ihre Grenzen und prüft, dass kein Python-Fehler auftritt (insbesondere `StreamlitDuplicateElementId`
bei mehreren Diagrammen ohne key= und `StreamlitAPIException` bei Auswahlen mit ungültigem Wert)."""

import os

from streamlit.testing.v1 import AppTest

import rsu_constants as C

APP_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app.py")
TIMEOUT = int(os.environ.get("APPTEST_TIMEOUT", "300"))  # unter Last (parallele Läufe) reichen 180 s nicht immer; Umgebungsvariable zum Anpassen
WUERFEL = "🎲 Neue Zufallsinstanz würfeln"


def _fresh_app() -> AppTest:
    at = AppTest.from_file(APP_PATH)
    at.run(timeout=TIMEOUT)
    assert not at.exception, [str(e) for e in at.exception]
    return at


def test_app_loads_without_exception():
    _fresh_app()


def test_every_button_click_does_not_raise():
    labels = [b.label for b in _fresh_app().button]
    assert labels, "keine Buttons gefunden"
    for index, label in enumerate(labels):
        at = _fresh_app()
        at.button[index].click().run(timeout=TIMEOUT)
        assert not at.exception, (label, [str(e) for e in at.exception])


def test_every_selectbox_value_does_not_raise():
    keys = [s.key for s in _fresh_app().selectbox]
    assert {"quelle_select", "n_select", "suche_select", "exp_verteilung", "exp_n"} <= set(keys)
    werte = {"quelle_select": list(C.QUELLEN), "n_select": list(range(len(C.N_WERTE))), "suche_select": list(C.SUCHEN),
             "exp_verteilung": list(range(len(C.VERTEILUNGEN))), "exp_n": list(range(len(C.MESS_N)))}
    for key in keys:
        for wert in werte[key]:
            at = _fresh_app()
            at.selectbox(key=key).set_value(wert).run(timeout=TIMEOUT)
            assert not at.exception, (key, wert, [str(e) for e in at.exception])


def test_zahlenfelder_an_ihren_grenzen_loesen_keinen_fehler_aus():
    for quelle in (0, 5):
        for wert in (0, C.SEED_MAX):
            at = _fresh_app()
            at.selectbox(key="quelle_select").set_value(quelle).run(timeout=TIMEOUT)
            at.number_input(key="seed_input").set_value(wert).run(timeout=TIMEOUT)
            at.number_input(key="suchseed_input").set_value(wert).run(timeout=TIMEOUT)
            assert not at.exception, (quelle, wert, [str(e) for e in at.exception])
    for budget in (1, 2, C.BUDGET_MAX):
        at = _fresh_app()
        at.number_input(key="budget_input").set_value(budget).run(timeout=TIMEOUT)
        assert not at.exception, (budget, [str(e) for e in at.exception])


def test_wuerfeln_wechselt_vom_beispiel_zu_einer_zufallsinstanz():
    at = _fresh_app()
    assert at.selectbox(key="quelle_select").value == 0
    at.button[[b.label for b in at.button].index(WUERFEL)].click().run(timeout=TIMEOUT)
    assert at.selectbox(key="quelle_select").value == 2 and not at.exception
    at.selectbox(key="quelle_select").set_value(5).run(timeout=TIMEOUT)
    seed_vorher = at.number_input(key="seed_input").value
    at.button[[b.label for b in at.button].index(WUERFEL)].click().run(timeout=TIMEOUT)
    assert at.selectbox(key="quelle_select").value == 5 and at.number_input(key="seed_input").value != seed_vorher


def test_standardansicht_zeigt_das_erwartete_verdikt():
    at = _fresh_app()
    erfolge = [e.value for e in at.success]
    assert any("Die Reihenfolge nach Fläche braucht 3 Behälter; nach 200 Auswertungen findet die Tausch-Suche mit Zweitziel **2**." in e and "Das ist das Optimum (die Schranke allein ergäbe 2)." in e
               for e in erfolge)                     # Beispiel 1, Tausch mit Zweitziel, 200 Auswertungen, Startzahl 1


def test_ohne_suche_zeigt_die_app_den_start():
    at = _fresh_app()
    at.selectbox(key="suche_select").set_value(0).run(timeout=TIMEOUT)
    assert not at.exception and any("Die feste Reihenfolge nach Fläche braucht **3** Behälter." in i.value for i in at.info)


def test_expander_stehen_unter_ihren_namen():
    labels = [e.label for e in _fresh_app().expander]
    assert "📐 Mathematische Formulierung" in labels and "⚠️ Annahmen, Grenzen und bekannte Probleme" in labels
