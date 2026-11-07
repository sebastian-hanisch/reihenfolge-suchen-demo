"""Kern der Demo (nur Standardbibliothek): der Dekodierer MaxRects BSSF, die Schranken, der unabhängige Prüfer und die Suche nach einer guten Reihenfolge.

Eine Reihenfolge der Rechtecke wird vom Dekodierer (MaxRects mit kleinster kurzer Restkante, wie in Stück 8) zu einer Packung. Eine Suche verändert die Reihenfolge und behält die bessere.
Alle Zufallszahlen kommen aus `random.Random(seed).random()` und werden hier selbst zu Ganzzahlen, Mischungen und Paaren gemacht: `random()` liefert auf jeder Python-Version dieselben Zahlen
(`shuffle` und `sample` sind das nicht versprochen), damit die vorberechneten Zahlen auf jeder Plattform gleich bleiben."""

import itertools
import random


# --- Reihenfolge nach Fläche (der feste Start) ------------------------------------------------------------------------------------------------------


def reihenfolge_flaeche(rects) -> list:
    """Teilenummern nach fallender Fläche; Gleichstände bleiben in der Lieferreihenfolge."""
    return sorted(range(len(rects)), key=lambda i: (-rects[i][0] * rects[i][1], i))


# --- Dekodierer: MaxRects BSSF ----------------------------------------------------------------------------------------------------------------------


def _maximal(frei):
    """Entfernt freie Rechtecke, die in einem anderen enthalten sind (bei Gleichheit bleibt das erste)."""
    behalten = []
    for i, a in enumerate(frei):
        if any(j != i and b[0] <= a[0] and b[1] <= a[1] and a[0] + a[2] <= b[0] + b[2] and a[1] + a[3] <= b[1] + b[3] and (b != a or j < i) for j, b in enumerate(frei)):
            continue
        behalten.append(a)
    return behalten


def pack(rects, order, cap: int):
    """MaxRects BSSF: Rechtecke in der Reihenfolge `order` (jedes höchstens einmal) setzen. Jedes kommt in den ersten Behälter, der ein freies Rechteck für es hat, in die linke untere Ecke des freien
    Rechtecks mit der kleinsten kurzen Restkante (dann kleinsten langen, dann tiefsten und linkesten Lage); sonst in einen neuen Behälter. Danach wird jedes überlappte freie Rechteck in bis zu vier
    Teile zerlegt und die Liste auf die maximalen Rechtecke gekürzt. Gibt (bins, platz, zustand) zurück: bins[b] = Teilenummern, platz = (Teil, Behälter, x, y), zustand[b] = freie Rechtecke (x, y, w, h)."""
    order = list(order)
    if len(set(order)) != len(order) or any(not 0 <= i < len(rects) for i in order):
        raise ValueError("die Reihenfolge darf jedes Rechteck höchstens einmal enthalten")
    for t in rects:
        if len(t) != 2 or any(x <= 0 or x > cap for x in t):
            raise ValueError(f"Rechteck {t!r} ungültig (zwei Maße, je 1 bis {cap})")
    behaelter, bins, platz = [], [], []
    for i in order:
        w, h = rects[i]
        wahl = None
        for b, frei in enumerate(behaelter):
            for (fx, fy, fw, fh) in frei:
                if w <= fw and h <= fh:
                    score = (min(fw - w, fh - h), max(fw - w, fh - h), fy, fx)
                    if wahl is None or score < wahl[0]:
                        wahl = (score, b, fx, fy)
            if wahl is not None:
                break
        if wahl is None:
            behaelter.append([(0, 0, cap, cap)])
            bins.append([])
            wahl = (None, len(behaelter) - 1, 0, 0)
        _, b, px, py = wahl
        platz.append((i, b, px, py))
        bins[b].append(i)
        neu = []
        for (fx, fy, fw, fh) in behaelter[b]:
            if px >= fx + fw or px + w <= fx or py >= fy + fh or py + h <= fy:
                neu.append((fx, fy, fw, fh))
                continue
            if px > fx:
                neu.append((fx, fy, px - fx, fh))
            if px + w < fx + fw:
                neu.append((px + w, fy, fx + fw - px - w, fh))
            if py > fy:
                neu.append((fx, fy, fw, py - fy))
            if py + h < fy + fh:
                neu.append((fx, py + h, fw, fy + fh - py - h))
        behaelter[b] = _maximal(neu)
    return bins, platz, behaelter


def packung_pruefen(rects, platz, cap: int, vollstaendig: bool = True) -> bool:
    """Unabhängiger Prüfer: jedes Rechteck höchstens einmal (bei `vollstaendig` genau einmal), ganz im Behälter, keine zwei Rechtecke eines Behälters überlappen."""
    nummern = sorted(p[0] for p in platz)
    if vollstaendig and nummern != list(range(len(rects))):
        return False
    if len(set(nummern)) != len(nummern) or any(not 0 <= i < len(rects) for i in nummern):
        return False
    je = {}
    for i, b, x, y in platz:
        w, h = rects[i]
        if x < 0 or y < 0 or x + w > cap or y + h > cap:
            return False
        je.setdefault(b, []).append((x, y, x + w, y + h))
    for lst in je.values():
        for a in range(len(lst)):
            for c in range(a + 1, len(lst)):
                p, q = lst[a], lst[c]
                if p[0] < q[2] and q[0] < p[2] and p[1] < q[3] and q[1] < p[3]:
                    return False
    return True


def schranken(rects, cap: int):
    """(Flächenschranke, Zahl der großen Rechtecke, Schranke): die Fläche aller Rechtecke durch die Behälterfläche aufgerundet; die Zahl der Rechtecke, die in beiden Maßen
    über die Hälfte reichen (zwei solche überlappen in jedem Behälter über dem Mittelpunkt, jedes braucht also einen eigenen Behälter); das Größere von beiden."""
    flaeche = -(-sum(w * h for w, h in rects) // (cap * cap))
    gross = sum(1 for w, h in rects if 2 * w > cap and 2 * h > cap)
    return flaeche, gross, max(flaeche, gross)


def schranke(rects, cap: int) -> int:
    return schranken(rects, cap)[2]


# --- Zufall ohne Versionsabhängigkeit ---------------------------------------------------------------------------------------------------------------


class Zufall:
    """Zufallsquelle, die nur `random.Random(seed).random()` benutzt (53-Bit-Gleitkommazahlen im Intervall [0, 1))."""

    def __init__(self, seed: int):
        self._r = random.Random(seed)

    def unter(self, n: int) -> int:
        """Ganze Zahl von 0 bis n - 1."""
        return int(self._r.random() * n)

    def mischen(self, liste: list) -> list:
        """Fisher-Yates-Mischung einer Kopie: von hinten nach vorn tauscht Position k mit einer Position von 0 bis k."""
        liste = list(liste)
        for k in range(len(liste) - 1, 0, -1):
            j = self.unter(k + 1)
            liste[k], liste[j] = liste[j], liste[k]
        return liste

    def paar(self, n: int) -> tuple:
        """Zwei verschiedene Positionen (i, j) von 0 bis n - 1; n >= 2."""
        i = self.unter(n)
        j = self.unter(n - 1)
        if j >= i:
            j += 1
        return i, j


# --- Auswertung und Suche -------------------------------------------------------------------------------------------------------------------------


def bewerten(rects, order, cap: int) -> tuple:
    """(Zahl der Behälter, Fläche im am wenigsten gefüllten Behälter) einer Reihenfolge; beides ist besser, wenn es kleiner ist (der leerste Behälter soll sich leeren)."""
    bins = pack(rects, order, cap)[0]
    return len(bins), min(sum(rects[i][0] * rects[i][1] for i in b) for b in bins) if bins else 0


def suche(rects, cap: int, methode: int, budget: int, seed: int):
    """Sucht eine gute Reihenfolge mit höchstens `budget` Auswertungen (die erste ist die Reihenfolge nach Fläche, der Start). Methode 0: keine Suche (alle Auswertungen gleich dem Start);
    1: Zufallsstarts (jede weitere Auswertung ist eine zufällige Reihenfolge, die beste nach Behälterzahl bleibt, bei Gleichstand die frühere); 2: Tausch-Suche auf die Behälterzahl allein (zwei zufällige
    Positionen tauschen, die neue Reihenfolge behalten, wenn die Behälterzahl nicht größer wird); 3: Tausch-Suche auf (Behälterzahl, Fläche im leersten Behälter) lexikographisch.
    Gibt (beste_reihenfolge, verlauf) zurück, verlauf[k] = (Behälter, Fläche im leersten Behälter) der besten Reihenfolge nach k + 1 Auswertungen."""
    if methode not in (0, 1, 2, 3):
        raise ValueError(f"Methode {methode!r} unbekannt")
    if budget < 1:
        raise ValueError("das Budget muss mindestens 1 sein (die erste Auswertung ist der Start)")
    n = len(rects)
    start = reihenfolge_flaeche(rects)
    beste = list(start)
    zb = bewerten(rects, beste, cap)
    verlauf = [zb]
    zufall = Zufall(seed)
    for _ in range(1, budget):
        if methode == 0 or n < 2:
            verlauf.append(zb)
            continue
        if methode == 1:
            order = zufall.mischen(range(n))
            z = bewerten(rects, order, cap)
            if z[0] < zb[0]:
                beste, zb = order, z
        else:
            i, j = zufall.paar(n)
            order = list(beste)
            order[i], order[j] = order[j], order[i]
            z = bewerten(rects, order, cap)
            if (z[0] <= zb[0]) if methode == 2 else (z <= zb):
                beste, zb = order, z
        verlauf.append(zb)
    return beste, verlauf


def bester_aller_reihenfolgen(rects, cap: int) -> int:
    """Kleinste Behälterzahl des Dekodierers über alle n! Reihenfolgen (nur für kleine n)."""
    return min(len(pack(rects, p, cap)[0]) for p in itertools.permutations(range(len(rects))))
