"""Erzeugt rsu_precomputed.json: das Messraster (vier Verteilungen × Rechteckzahlen 12, 20, 40 × 100 feste Instanzen × drei Suchen × drei Budgets) und die Obergrenze des Dekodierers (alle Reihenfolgen
bei 7 und 8 Rechtecken).

    python generate_precomputed.py                         # rechnet alles neu; die Optima (bei 12 und 20 Rechtecken) kommen aus ../skyline-maxrects-demo/smx_precomputed.json (etwa 20 bis 40 Minuten)
    python generate_precomputed.py --opt-aus PFAD          # dasselbe mit anderer Quelle der Optima
    python generate_precomputed.py --keep-opt              # behält die in der Datei gespeicherten Optima und rechnet das Raster und die Obergrenze neu
    python generate_precomputed.py --nur-stichprobe        # ergänzt in der vorhandenen Datei nur die Stichprobe (die ersten drei Instanzen jeder Zelle einzeln, für die Tests)
    python generate_precomputed.py --check                 # rechnet das Raster (parallel) mit den gespeicherten Optima nach und vergleicht mit der Datei (die Obergrenze nicht)

Die Instanzen des Rasters sind dieselben wie in Stück 7 und 8; das Optimum je Instanz hat dort CP-SAT mit Zeitlimit berechnet (-1 = nicht entschieden). Die Instanzen der Obergrenze haben eigene Seeds;
ihr Optimum rechnet dev/opt.py (CP-SAT, 30 Sekunden Zeitlimit)."""

import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import rsu_constants as C
import rsu_evaluation as ev

STANDARD_QUELLE = Path(__file__).resolve().parent.parent / "skyline-maxrects-demo" / "smx_precomputed.json"


def _zelle(args):
    v, ni, opt = args
    t = time.perf_counter()
    z = ev.messzelle(v, ni, opt)
    if opt is not None:
        z["opt"] = opt
    return ("zelle", v, ni, z, time.perf_counter() - t)


def _obergrenze(args):
    from dev.opt import optimum_cpsat

    v, n = args
    t = time.perf_counter()
    z = ev.obergrenze_zelle(v, n, lambda rects, cap, ober: optimum_cpsat(rects, cap, ober, 30.0, 2))
    return ("ober", v, n, z, time.perf_counter() - t)


def erzeugen(quelle: Path | None, behalten: bool) -> dict:
    if behalten:
        optima = {k: z["opt"] for k, z in ev.vorberechnet()["zellen"].items() if "opt" in z}
    else:
        smx = json.loads(quelle.read_text(encoding="utf-8"))
        assert smx["instanzen"] == C.INSTANZEN and smx["cap"] == C.CAP
        optima = {k: z["opt"] for k, z in smx["zellen"].items() if "opt" in z}
    auftraege = [(_zelle, (v, ni, optima[ev.zelle_schluessel(v, ni)] if n in C.EXAKT_N else None)) for v in range(len(C.VERTEILUNGEN)) for ni, n in enumerate(C.MESS_N)]
    auftraege += [(_obergrenze, (v, n)) for n in C.OBERGRENZE_N for v in range(len(C.VERTEILUNGEN))]
    daten = {"instanzen": C.INSTANZEN, "cap": C.CAP, "opt_herkunft": C.OPT_HERKUNFT, "zellen": {}, "obergrenze": {str(n): {} for n in C.OBERGRENZE_N}}
    with ProcessPoolExecutor(max(1, min(6, (os.cpu_count() or 2) // 2))) as pool:
        futures = [pool.submit(f, a) for f, a in auftraege]
        for fu in futures:
            art, v, x, z, sekunden = fu.result()
            if art == "zelle":
                daten["zellen"][ev.zelle_schluessel(v, x)] = z
                print(f"{ev.zelle_schluessel(v, x)}: {sekunden:.0f} s", flush=True)
            else:
                daten["obergrenze"][str(x)][C.VERTEILUNGEN[v][0]] = z
                print(f"Obergrenze {C.VERTEILUNGEN[v][0]} n = {x}: {sekunden:.0f} s", flush=True)
    reihenfolge = [ev.zelle_schluessel(v, ni) for v in range(len(C.VERTEILUNGEN)) for ni in range(len(C.MESS_N))]
    daten["zellen"] = {k: daten["zellen"][k] for k in reihenfolge}
    return daten


def _stichprobe_zelle(args):
    v, ni, opt = args
    return ev.zelle_schluessel(v, ni), {str(j): ev.messzelle(v, ni, opt, [j]) for j in C.STICHPROBE_J}


def stichprobe_ergaenzen(daten: dict) -> None:
    """Trägt die ersten Instanzen jeder Zelle einzeln ein (`daten["stichprobe"][Zelle][j]`): Die Tests rechnen sie frisch nach, ohne die ganze Zelle zu rechnen."""
    auftraege = []
    for v in range(len(C.VERTEILUNGEN)):
        for ni, n in enumerate(C.MESS_N):
            auftraege.append((v, ni, daten["zellen"][ev.zelle_schluessel(v, ni)].get("opt")))
    with ProcessPoolExecutor(max(1, min(6, (os.cpu_count() or 2) // 2))) as pool:
        daten["stichprobe"] = dict(pool.map(_stichprobe_zelle, auftraege))


def _frisch(args):
    v, ni, opt = args
    z = ev.messzelle(v, ni, opt)
    if opt is not None:
        z["opt"] = opt
    return ev.zelle_schluessel(v, ni), z


def pruefen() -> int:
    gespeichert = ev.vorberechnet()
    auftraege = [(v, ni, gespeichert["zellen"][ev.zelle_schluessel(v, ni)].get("opt")) for v in range(len(C.VERTEILUNGEN)) for ni in range(len(C.MESS_N))]
    schlecht = 0
    with ProcessPoolExecutor(max(1, min(6, (os.cpu_count() or 2) // 2))) as pool:
        for schl, frisch in pool.map(_frisch, auftraege):
            if frisch != gespeichert["zellen"][schl]:
                schlecht += 1
                print("ABWEICHUNG", schl, flush=True)
    print("gleich" if not schlecht else f"{schlecht} Abweichungen")
    return 1 if schlecht else 0


if __name__ == "__main__":
    if "--check" in sys.argv:
        sys.exit(pruefen())
    if "--nur-stichprobe" in sys.argv:
        daten = json.loads(ev.PRECOMPUTED.read_text(encoding="utf-8"))
        stichprobe_ergaenzen(daten)
        ev.PRECOMPUTED.write_text(json.dumps(daten, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        print("Stichprobe ergänzt")
        sys.exit(0)
    quelle = Path(sys.argv[sys.argv.index("--opt-aus") + 1]) if "--opt-aus" in sys.argv else STANDARD_QUELLE
    daten = erzeugen(quelle, "--keep-opt" in sys.argv)
    stichprobe_ergaenzen(daten)
    ev.PRECOMPUTED.write_text(json.dumps(daten, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print("geschrieben:", ev.PRECOMPUTED.name)
