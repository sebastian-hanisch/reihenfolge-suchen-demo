"""Plotly-Abbildungen. Alle Achsen sind gesperrt (fixedrange), damit Touch-Geräte beim Scrollen nicht am Diagramm hängen bleiben."""

import plotly.graph_objects as go

import rsu_constants as C

ABSTAND = 8     # Platz zwischen zwei Behältern in der Zeichnung


def lock_axes(fig):
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def _base(fig, height=340):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", y=-0.25), plot_bgcolor="rgba(0,0,0,0)")
    return lock_axes(fig)


def build_behaelter(rects, platz, cap):
    """Alle Behälter nebeneinander, jedes Rechteck an seiner Stelle; die Farbe zeigt die Reihenfolge des Setzens (die der Suche), die Beschriftung die Teilenummer (Lieferreihenfolge).

    Die Behälterrahmen sind rot gestrichelt. Das Achsenverhältnis ist 1 : 1, damit die Rechtecke maßstäblich sind."""
    anzahl = max(1 + max((b for _, b, _, _ in platz), default=0), 1)
    shapes = []
    for b in range(anzahl):
        x0 = b * (cap + ABSTAND)
        shapes.append(dict(type="rect", x0=x0, y0=0, x1=x0 + cap, y1=cap, line=dict(color=C.COLOR_LINE, width=2, dash="dash"), fillcolor="rgba(0,0,0,0)"))
    for s, (i, b, x, y) in enumerate(platz):
        w, h = rects[i]
        x0 = b * (cap + ABSTAND) + x
        shapes.append(dict(type="rect", x0=x0, y0=y, x1=x0 + w, y1=y + h, line=dict(color="white", width=1.5), fillcolor=C.REGAL_FARBEN[s % len(C.REGAL_FARBEN)], opacity=0.85))
    fig = go.Figure(go.Scatter(x=[b * (cap + ABSTAND) + x + rects[i][0] / 2 for i, b, x, y in platz], y=[y + rects[i][1] / 2 for i, b, x, y in platz], mode="text",
                               text=[str(i + 1) for i, *_ in platz], textfont=dict(color="white", size=11),
                               hovertext=[f"Schritt {s + 1}: Teil {i + 1}, {rects[i][0]} × {rects[i][1]}, Behälter {b + 1}, links unten ({x}, {y})" for s, (i, b, x, y) in enumerate(platz)],
                               hoverinfo="text", showlegend=False))
    fig.update_layout(shapes=shapes)
    breite = anzahl * (cap + ABSTAND) - ABSTAND
    fig.update_xaxes(range=[-2, breite + 2], constrain="domain", showgrid=False, zeroline=False, tickmode="array", tickvals=[b * (cap + ABSTAND) + cap / 2 for b in range(anzahl)],
                     ticktext=[f"B{b + 1}" for b in range(anzahl)])
    fig.update_yaxes(range=[-2, cap + 2], constrain="domain", showgrid=False, zeroline=False, scaleanchor="x", scaleratio=1, title_text="Höhe")
    return _base(fig, 340)


def build_verlauf(verlauf, schranke, optimum):
    """Verlauf der besten Reihenfolge über die Auswertungen: Behälter (Stufenlinie, linke Achse) und Fläche im leersten Behälter (rechte Achse); Schranke und Optimum als waagerechte Linien."""
    xs = list(range(1, len(verlauf) + 1))
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=xs, y=[b for b, _ in verlauf], mode="lines", line=dict(color=C.COLOR_BEHAELTER, width=3, shape="hv"), name="Behälter",
                             hovertemplate="Auswertung %{x}: %{y} Behälter<extra></extra>"))
    fig.add_trace(go.Scatter(x=xs, y=[f for _, f in verlauf], mode="lines", line=dict(color=C.COLOR_FUELLUNG, width=2, dash="dot", shape="hv"), name="Fläche im leersten Behälter", yaxis="y2",
                             hovertemplate="Auswertung %{x}: leerster Behälter %{y}<extra></extra>"))
    fig.add_hline(y=schranke, line=dict(color="gray", width=1, dash="dash"), annotation_text="Schranke", annotation_position="bottom right")
    if optimum is not None:
        fig.add_hline(y=optimum, line=dict(color=C.COLOR_LINE, width=1, dash="dash"), annotation_text="Optimum", annotation_position="top right")
    hoechst = max(b for b, _ in verlauf)
    fig.update_layout(yaxis=dict(title_text="Behälter", range=[max(0, min(schranke, optimum or schranke) - 1), hoechst + 1], dtick=1),
                      yaxis2=dict(overlaying="y", side="right", showgrid=False, title_text="Fläche im leersten Behälter", rangemode="tozero"))
    fig.update_xaxes(title_text="Auswertungen")
    return _base(fig, 300)


def build_messung(mittel, titel):
    """Gruppierte Balken: je Auswertungsbudget (50, 200, 1000) die mittleren Behälter über der Bezugsgröße für die feste Reihenfolge und die drei Suchen."""
    fig = go.Figure()
    for m in sorted(C.SUCHEN):
        fig.add_trace(go.Bar(name=C.SUCHE_KURZ[m], x=[f"{b} Auswertungen" for b in C.BUDGETS], y=[mittel[m][b] for b in C.BUDGETS], marker_color=C.SUCHE_FARBEN[m],
                             hovertemplate="%{x}: %{y:.2f}<extra>" + C.SUCHE_KURZ[m] + "</extra>"))
    fig.update_layout(barmode="group")
    fig.update_yaxes(title_text=titel)
    return _base(fig, 320)
