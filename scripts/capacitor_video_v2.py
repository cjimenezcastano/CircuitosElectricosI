import os

import numpy as np
import manimgx as m

# Fondo blanco (debe fijarse antes de construir la escena)
m.config.background_color = "#FFFFFF"

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
FIGURAS = os.path.join(RAIZ, "figuras")
SALIDA = os.path.join(RAIZ, "videos_salida")
VIDEO = os.path.join(SALIDA, "capacitor_dielectrico_v2.mp4")

# ---------------- Paleta (fondo blanco) ----------------
INK = "#1F2933"
GRAY = "#6B7280"
TITLE = "#0B3C5D"
PLATE = "#37474F"
POS = "#D32F2F"
NEG = "#1565C0"
FIELD = "#E65100"
DIEL = "#F9A825"
DIEL_T = "#9A6200"
GREEN = "#2E7D32"
CARD = "#F3F4F6"
LINEC = "#D1D5DB"
IND_POS = "#E57373"
IND_NEG = "#5B9BD5"

# ---------------- Identificación institucional ----------------
UNIVERSIDAD = "Universidad de Antioquia"
DEPARTAMENTO = "Departamento de Ingeniería Electrónica y de Telecomunicaciones"
CURSO = "Circuitos Eléctricos I"

# ---------------- Geometría del capacitor ----------------
CX, CY = -2.3, 0.2     # centro
W0, D0, TH = 4.4, 2.4, 0.2   # ancho de placa, separación (centro a centro), grosor
XBAT = -6.0            # x de la batería
V0 = 9.0               # V (fuente)
KAPPA = 3.0
YPIE = -3.3            # altura de las leyendas
YFOOT = -3.78          # altura del pie institucional


def T(s, size=28, color=INK, **kw):
    return m.Text(s, font_size=size, color=color, **kw)


def MT(s, size=36, color=INK, **kw):
    return m.MathTex(s, font_size=size, color=color, **kw)


def coma(v, n=1):
    return f"{v:.{n}f}".replace(".", ",")


def cargar_logo(alto):
    """Carga el logo si existe (UDEA_LOGO o logo_udea.png/.jpg/.svg en figuras/ o junto a este archivo)."""
    candidatos = []
    if os.environ.get("UDEA_LOGO"):
        candidatos.append(os.environ["UDEA_LOGO"])
    nombres = ("logo_udea.png", "logo_udea.jpg", "logo_udea.jpeg", "logo_udea.svg")
    candidatos += [os.path.join(d, n) for d in (FIGURAS, AQUI) for n in nombres]
    for ruta in candidatos:
        if os.path.exists(ruta):
            try:
                img = m.SVGMobject(ruta) if ruta.lower().endswith(".svg") else m.ImageMobject(ruta)
                img.scale_to_fit_height(alto)
                return img
            except Exception as e:  # noqa: BLE001
                print("No se pudo cargar el logo:", ruta, e)
    return None


def L(p, q, color=INK, sw=4):
    return m.Line(np.array(p, float), np.array(q, float), color=color, stroke_width=sw)


def mas(x, y, s=0.09, color=POS, sw=3):
    return m.VGroup(L([x - s, y, 0], [x + s, y, 0], color, sw), L([x, y - s, 0], [x, y + s, 0], color, sw))


def menos(x, y, s=0.09, color=NEG, sw=3):
    return m.VGroup(L([x - s, y, 0], [x + s, y, 0], color, sw))


def flecha_abajo(x, y0, y1, color=FIELD, sw=4, head=0.17):
    return m.VGroup(
        L([x, y0, 0], [x, y1, 0], color, sw),
        L([x, y1, 0], [x - 0.09, y1 + head, 0], color, sw),
        L([x, y1, 0], [x + 0.09, y1 + head, 0], color, sw),
    )


def doble(p0, p1, color=GRAY, sw=3, head=0.16):
    p0, p1 = np.array(p0, float), np.array(p1, float)
    d = (p1 - p0) / np.linalg.norm(p1 - p0)
    n = np.array([-d[1], d[0], 0.0])
    return m.VGroup(
        L(p0, p1, color, sw),
        L(p0, p0 + head * d + 0.08 * n, color, sw), L(p0, p0 + head * d - 0.08 * n, color, sw),
        L(p1, p1 - head * d + 0.08 * n, color, sw), L(p1, p1 - head * d - 0.08 * n, color, sw),
    )


def placa(cx, y, w):
    return m.Rectangle(width=w, height=TH, fill_color=PLATE, fill_opacity=1, stroke_width=0).move_to([cx, y, 0])


def point_on_path(pts, u):
    seg = [np.linalg.norm(pts[i + 1] - pts[i]) for i in range(len(pts) - 1)]
    d = (u % 1.0) * sum(seg)
    for i, s in enumerate(seg):
        if d <= s:
            return pts[i] + (pts[i + 1] - pts[i]) * (d / s)
        d -= s
    return pts[-1]


def path_length(pts):
    return sum(np.linalg.norm(pts[i + 1] - pts[i]) for i in range(len(pts) - 1))


def fringe(cx, cy, w, d, color=FIELD, sw=2.5):
    """Líneas de campo de borde (curvas) a ambos lados."""
    yTi = cy + d / 2 - TH / 2 - 0.05
    yBi = cy - d / 2 + TH / 2 + 0.05
    out = []
    for s in (-1, 1):
        for x_off, bulge in ((0.12, 0.55), (0.02, 1.05)):
            x0 = cx + s * (w / 2 - x_off)
            curve = m.ParametricFunction(
                lambda u, x0=x0, s=s, b=bulge: np.array(
                    [x0 + s * b * np.sin(np.pi * u) ** 2, yTi + (yBi - yTi) * u, 0.0]),
                t_range=[0, 1, 0.02], color=color, stroke_width=sw, fill_opacity=0)
            xm = x0 + s * bulge
            ym = (yTi + yBi) / 2
            head = m.VGroup(L([xm, ym, 0], [xm - 0.08, ym + 0.14, 0], color, sw),
                            L([xm, ym, 0], [xm + 0.08, ym + 0.14, 0], color, sw))
            out += [curve, head]
    return out


def construir_cap(cx=CX, cy=CY, w=W0, d=D0, n=9):
    """Capacitor estático: placas, cargas, flechas de campo y campo de borde."""
    yT, yB = cy + d / 2, cy - d / 2
    yTi, yBi = yT - TH / 2, yB + TH / 2
    xs = [cx - w / 2 + (i + 0.5) * w / n for i in range(n)]
    xa = [cx - w / 2 + (i + 1) * w / n for i in range(n - 1)]
    return {
        "top": placa(cx, yT, w), "bot": placa(cx, yB, w),
        "plus": [mas(x, yTi - 0.15) for x in xs],
        "minus": [menos(x, yBi + 0.15) for x in xs],
        "arrows": [flecha_abajo(x, yTi - 0.55, yBi + 0.55) for x in xa],
        "fringe": fringe(cx, cy, w, d),
        "yTi": yTi, "yBi": yBi, "yT": yT, "yB": yB,
    }


def cap_dyn(w, d):
    """Capacitor con batería, dibujado para valores dinámicos de ancho w y separación d."""
    yT, yB = CY + d / 2, CY - d / 2
    yTi, yBi = yT - TH / 2, yB + TH / 2
    n = int(np.clip(round(9 * (w / W0) * (D0 / d)), 4, 28))
    items = [placa(CX, yT, w), placa(CX, yB, w)]
    for i in range(n):
        x = CX - w / 2 + (i + 0.5) * w / n
        items += [mas(x, yTi - 0.15), menos(x, yBi + 0.15)]
    na = int(round(8 * w / W0))
    sw = 3.0 * (D0 / d) ** 0.7
    for i in range(na):
        x = CX - w / 2 + (i + 1) * w / (na + 1)
        items.append(flecha_abajo(x, yTi - 0.35, yBi + 0.35, FIELD, sw))
    xe = CX - w / 2
    items += [
        L([xe, yT, 0], [XBAT, yT, 0]), L([XBAT, yT, 0], [XBAT, 0.4, 0]),
        L([XBAT, 0.0, 0], [XBAT, yB, 0]), L([XBAT, yB, 0], [xe, yB, 0]),
        L([XBAT - 0.4, 0.4, 0], [XBAT + 0.4, 0.4, 0], INK, 6),
        L([XBAT - 0.22, 0.0, 0], [XBAT + 0.22, 0.0, 0], INK, 6),
    ]
    return m.VGroup(*items)


class CapacitorVideo(m.Scene):
    # ---------- utilidades de escena ----------
    def titulo(self, texto):
        t = T(texto, 36, TITLE).move_to([-6.8, 3.45, 0], aligned_edge=m.LEFT)
        self.play(m.FadeIn(t, shift=m.DOWN * 0.2), run_time=0.6)
        return t

    def pie(self, texto, size=26, color=INK, rt=0.6):
        nuevo = T(texto, size, color).move_to([0, YPIE, 0])
        if self._pie is not None:
            self.play(m.FadeOut(self._pie), m.FadeIn(nuevo), run_time=rt)
        else:
            self.play(m.FadeIn(nuevo), run_time=rt)
        self._pie = nuevo

    def limpiar(self, t=0.7):
        objs = [o for o in self.mobjects if o is not self._footer]
        for o in objs:
            o.clear_updaters()
        if objs:
            self.play(*[m.FadeOut(o) for o in objs], run_time=t)
        self.remove(*objs)
        self._pie = None

    def crear_footer(self):
        logo = cargar_logo(0.38)
        texto = T(f"{UNIVERSIDAD}  ·  Dpto. de Ingeniería Electrónica y de Telecomunicaciones  ·  {CURSO}",
                  18, GRAY)
        if logo is not None:
            logo.move_to([-6.75, YFOOT, 0])
            texto.move_to([-6.4, YFOOT, 0], aligned_edge=m.LEFT)
            return m.Group(logo, texto)
        texto.move_to([-6.8, YFOOT, 0], aligned_edge=m.LEFT)
        return m.Group(texto)

    # ---------- escena ----------
    def construct(self):
        self._pie = None
        self._footer = self.crear_footer()
        self.escena_titulo()
        self.play(m.FadeIn(self._footer), run_time=0.6)
        self.escena_que_es()
        self.escena_definicion()
        self.escena_carga()
        self.escena_glosario()
        self.escena_geometria()
        self.escena_dielectrico()
        self.escena_casos()
        self.escena_propiedades()
        self.escena_tension_corriente()
        self.escena_energia()
        self.escena_resumen()

    # ================= 1. Portada =================
    def escena_titulo(self):
        logo = cargar_logo(1.3)
        bloque = []
        if logo is not None:
            logo.move_to([0, 3.0, 0])
            bloque.append(logo)
        uni = T(UNIVERSIDAD, 34, TITLE).move_to([0, 1.85, 0])
        dep = T(DEPARTAMENTO, 22, GRAY).move_to([0, 1.35, 0])
        cur = T(f"Curso: {CURSO}", 28, INK).move_to([0, 0.8, 0])
        sep = L([-3.0, 0.4, 0], [3.0, 0.4, 0], LINEC, 2)
        t1 = T("El capacitor", 70, TITLE).move_to([0, -0.5, 0])
        t2 = T("Campo eléctrico, carga y dieléctrico", 32, GRAY).move_to([0, -1.4, 0])
        p1 = L([-1.5, -2.35, 0], [1.5, -2.35, 0], PLATE, 9)
        p2 = L([-1.5, -3.15, 0], [1.5, -3.15, 0], PLATE, 9)
        fl = m.VGroup(*[flecha_abajo(x, -2.47, -3.03, FIELD, 3, 0.13) for x in (-0.95, -0.31, 0.31, 0.95)])
        self.play(*[m.FadeIn(b) for b in bloque], m.FadeIn(uni), m.FadeIn(dep), m.FadeIn(cur), m.Create(sep),
                  run_time=1.4)
        self.play(m.FadeIn(t1, shift=m.UP * 0.3), run_time=1.0)
        self.play(m.FadeIn(t2), m.Create(p1), m.Create(p2), run_time=1.0)
        self.play(m.FadeIn(fl), run_time=0.8)
        self.wait(2.0)
        self.limpiar()

    # ================= 2. Qué es =================
    def escena_que_es(self):
        self.titulo("¿Qué es un capacitor?")
        top, bot = placa(CX, CY + D0 / 2, W0), placa(CX, CY - D0 / 2, W0)
        lab1 = T("Placa conductora", 22, PLATE).move_to([-5.75, CY + D0 / 2, 0])
        lab2 = T("Placa conductora", 22, PLATE).move_to([-5.75, CY - D0 / 2, 0])
        gap = m.VGroup(T("Aislante", 28, DIEL_T), T("(vacío, aire o dieléctrico)", 22, DIEL_T)).arrange(
            m.DOWN, buff=0.1).move_to([CX, CY, 0])
        relleno = m.Rectangle(width=W0, height=D0 - TH, fill_color=DIEL, fill_opacity=0.15,
                              stroke_width=0).move_to([CX, CY, 0])
        yA = CY + D0 / 2 + 0.55
        dimA = doble([CX - W0 / 2, yA, 0], [CX + W0 / 2, yA, 0])
        txtA = T("Área A", 24, GRAY).move_to([CX, yA + 0.4, 0])
        xd = CX + W0 / 2 + 0.5
        dimD = doble([xd, CY + D0 / 2 - TH / 2, 0], [xd, CY - D0 / 2 + TH / 2, 0])
        txtD = T("d", 28, GRAY).move_to([xd + 0.35, CY, 0])

        self.play(m.FadeIn(top, shift=m.DOWN * 0.3), m.FadeIn(bot, shift=m.UP * 0.3), run_time=1.2)
        self.play(m.FadeIn(lab1), m.FadeIn(lab2), m.FadeIn(relleno), m.FadeIn(gap), run_time=1.2)
        self.play(m.Create(dimA), m.FadeIn(txtA), m.Create(dimD), m.FadeIn(txtD), run_time=1.2)

        def punto(color):
            return m.Dot(radius=0.09, color=color)

        b1 = m.VGroup(T("Dos conductores (placas)", 28), T("separados por un aislante", 28)).arrange(
            m.DOWN, aligned_edge=m.LEFT, buff=0.08)
        b2 = m.VGroup(T("Almacena energía en el", 28), T("campo eléctrico entre ellas", 28)).arrange(
            m.DOWN, aligned_edge=m.LEFT, buff=0.08)
        b3 = m.VGroup(T("Capacitancia (en faradios, F):", 28), MT(r"C=\frac{q}{v}", 44, TITLE)).arrange(
            m.DOWN, aligned_edge=m.LEFT, buff=0.15)
        panel = m.VGroup(b1, b2, b3).arrange(m.DOWN, aligned_edge=m.LEFT, buff=0.55)
        panel.move_to([4.35, 0.2, 0]).align_to([1.7, 0, 0], m.LEFT)
        marcas = [punto(c).next_to(b, m.LEFT, buff=0.2).align_to(b[0], m.UP).shift(m.DOWN * 0.1)
                  for b, c in ((b1, POS), (b2, FIELD), (b3, NEG))]
        for b, mk in zip((b1, b2, b3), marcas):
            self.play(m.FadeIn(b, shift=m.RIGHT * 0.2), m.FadeIn(mk), run_time=1.0)
            self.wait(1.6)
        self.wait(1.0)
        self.limpiar()

    # ================= 2b. Definición y análisis dimensional =================
    def escena_definicion(self):
        self.titulo("Capacitancia: definición y análisis dimensional")
        f = MT(r"C=\frac{q}{v}", 84, tex_to_color_map={"C": GREEN, "q": POS, "v": NEG}).move_to([-4.6, 2.1, 0])
        self.play(m.FadeIn(f, shift=m.UP * 0.2), run_time=1.2)

        filas = [
            ("C", GREEN, "Capacitancia (parámetro concentrado), en F"),
            ("q", POS, "Carga almacenada en la placa, en C"),
            ("v", NEG, "Tensión entre las placas, en V"),
        ]
        grupo = []
        for i, (sim, col, txt) in enumerate(filas):
            fila = m.VGroup(MT(sim, 40, col), T(txt, 24)).arrange(m.RIGHT, buff=0.3)
            fila[1].align_to(fila[0], m.DOWN).shift(m.DOWN * 0.0)
            fila.move_to([0, 2.75 - i * 0.6, 0]).align_to([-2.3, 0, 0], m.LEFT)
            grupo.append(fila)
        for fila in grupo:
            self.play(m.FadeIn(fila, shift=m.RIGHT * 0.2), run_time=0.9)
            self.wait(0.7)
        self.pie("q y v son variables (minúsculas); C es un parámetro concentrado (mayúscula)", 24)
        self.wait(1.5)

        cab = T("Análisis dimensional", 24, GRAY).move_to([-6.8, 0.8, 0], aligned_edge=m.LEFT)
        l1 = MT(r"[C]=\frac{[q]}{[v]}=\frac{\mathrm{C}}{\mathrm{V}}=\mathrm{F}", 34).move_to([-6.8, 0.15, 0], aligned_edge=m.LEFT)
        n1 = T("(1 faradio = 1 culombio por voltio)", 22, GREEN).move_to([0.4, 0.15, 0], aligned_edge=m.LEFT)
        l2 = MT(r"[q]=\mathrm{A\cdot s},\qquad [v]=\mathrm{kg\cdot m^{2}\cdot s^{-3}\cdot A^{-1}}", 30).move_to(
            [-6.8, -0.8, 0], aligned_edge=m.LEFT)
        l3 = MT(r"[C]=\frac{\mathrm{A\cdot s}}{\mathrm{kg\cdot m^{2}\cdot s^{-3}\cdot A^{-1}}}"
                r"=\mathrm{A^{2}\cdot s^{4}\cdot kg^{-1}\cdot m^{-2}}", 30).move_to([-6.8, -1.85, 0], aligned_edge=m.LEFT)
        l4 = m.VGroup(T("Dimensiones:", 24, GRAY), MT(r"[C]=\mathrm{M^{-1}\,L^{-2}\,T^{4}\,I^{2}}", 30)).arrange(
            m.RIGHT, buff=0.3).move_to([-6.8, -2.7, 0], aligned_edge=m.LEFT)

        self.play(m.FadeIn(cab), m.FadeIn(l1, shift=m.RIGHT * 0.2), run_time=1.2)
        self.play(m.FadeIn(n1), run_time=0.8)
        self.pie("En un capacitor, [C] = [q] / [v]: culombios por voltio", 26)
        self.wait(1.5)
        self.play(m.FadeIn(l2, shift=m.RIGHT * 0.2), run_time=1.2)
        self.pie("El voltio es J/C: en unidades base, kg·m²·s⁻³·A⁻¹; la carga es A·s", 24)
        self.wait(2.0)
        self.play(m.FadeIn(l3, shift=m.RIGHT * 0.2), run_time=1.2)
        self.wait(1.2)
        self.play(m.FadeIn(l4), run_time=0.8)
        self.pie("Resultado: el faradio es una unidad derivada, 1 F = A²·s⁴·kg⁻¹·m⁻²", 24)
        self.wait(3.0)
        self.limpiar()

    # ================= 3. Carga y campo =================
    def escena_carga(self):
        self.titulo("Cómo se carga: de la batería al campo eléctrico")
        cap = construir_cap()
        n = 9
        qT = m.ValueTracker(0)

        bat = m.VGroup(L([XBAT - 0.4, 0.4, 0], [XBAT + 0.4, 0.4, 0], INK, 6),
                       L([XBAT - 0.22, 0.0, 0], [XBAT + 0.22, 0.0, 0], INK, 6))
        yT, yB = cap["yT"], cap["yB"]
        xe = CX - W0 / 2
        wires = m.VGroup(L([xe, yT, 0], [XBAT, yT, 0]), L([XBAT, yT, 0], [XBAT, 0.4, 0]),
                         L([XBAT, 0.0, 0], [XBAT, yB, 0]), L([XBAT, yB, 0], [xe, yB, 0]))
        lbl_v = m.VGroup(MT(r"V_0", 30), T("9 V", 24)).arrange(m.DOWN, buff=0.06).move_to([XBAT - 0.65, 0.2, 0])

        self.play(m.Create(wires), m.FadeIn(cap["top"]), m.FadeIn(cap["bot"]), m.FadeIn(bat), m.FadeIn(lbl_v),
                  run_time=1.8)
        self.pie("Al cerrar el circuito, la batería mueve electrones de la placa superior a la inferior")

        for i, g in enumerate(cap["plus"]):
            g.add_updater(lambda g, i=i: g.set_opacity(float(np.clip(qT.get_value() * n - i, 0, 1))))
        for i, g in enumerate(cap["minus"]):
            g.add_updater(lambda g, i=i: g.set_opacity(float(np.clip(qT.get_value() * n - i, 0, 1))))
        arrows = m.VGroup(*cap["arrows"])
        arrows.add_updater(lambda g: g.set_opacity(float(qT.get_value())))
        frg = m.VGroup(*cap["fringe"])
        frg.add_updater(lambda g: g.set_stroke(opacity=0.65 * float(qT.get_value())))
        self.add(*cap["plus"], *cap["minus"], arrows, frg)

        ruta = [np.array(p, float) for p in [
            (xe, yT, 0), (XBAT, yT, 0), (XBAT, 0.4, 0), (XBAT, 0.0, 0), (XBAT, yB, 0), (xe, yB, 0)]]
        N = 9
        dots = m.VGroup(*[m.Dot(radius=0.075, color=NEG) for _ in range(N)])
        fase = {"u": 0.0}

        def mover(grp, dt):
            q = float(qT.get_value())
            op = 0.0 if q > 0.985 else 1.0
            largo = path_length(ruta)
            fase["u"] = (fase["u"] + dt * 2.6 * (1 - q) / largo) % 1.0
            for k, dd in enumerate(grp):
                dd.move_to(point_on_path(ruta, k / N + fase["u"]))
                dd.set_opacity(op)

        dots.add_updater(mover)

        def lectura():
            return T(f"Tensión del capacitor:  v = {coma(qT.get_value() * V0)} V", 26, GRAY).move_to([CX, -2.2, 0])

        self.add(dots, m.always_redraw(lectura))
        carga = lambda t: (1 - np.exp(-4 * t)) / (1 - np.exp(-4))
        self.play(qT.animate.set_value(1), run_time=8, rate_func=carga)

        qm = T("+q", 30, POS).move_to([CX, yT + 0.5, 0])
        qn = T("−q", 30, NEG).move_to([CX, yB - 0.5, 0])
        e_lbl = MT(r"\vec{E}", 34, FIELD).move_to([cap["arrows"][3].get_center()[0] + 0.3, CY, 0])
        self.play(m.FadeIn(qm), m.FadeIn(qn), m.FadeIn(e_lbl), run_time=0.8)
        self.pie("Resultado: +q en una placa y −q en la otra. Entre ellas aparece un campo eléctrico E")

        def par(titulo, formula):
            return m.VGroup(T(titulo, 24, GRAY), MT(formula, 36)).arrange(m.DOWN, aligned_edge=m.LEFT, buff=0.12)

        p1 = par("Campo entre las placas (ideal)", r"E=\frac{\sigma}{\varepsilon_0}=\frac{q}{\varepsilon_0 A}")
        p2 = par("Tensión entre las placas", r"v=E\,d")
        p3 = par("Capacitancia", r"C=\frac{q}{v}=\frac{\varepsilon_0 A}{d}")
        panel = m.VGroup(p1, p2, p3).arrange(m.DOWN, aligned_edge=m.LEFT, buff=0.4)
        panel.move_to([4.4, 0.4, 0]).align_to([1.7, 0, 0], m.LEFT)
        for p in (p1, p2, p3):
            self.play(m.FadeIn(p, shift=m.RIGHT * 0.2), run_time=1.0)
            self.wait(1.4)
        self.pie("Con v = V₀ cesa la corriente: capacitor cargado, con energía guardada en E")
        self.wait(2.5)
        self.limpiar()

    # ================= 3b. Glosario de variables =================
    def escena_glosario(self):
        self.titulo("Variables y unidades")
        xs, xm, xu = -6.3, -5.5, 3.7
        cab = m.VGroup(
            T("Variable", 20, GRAY).move_to([xs, 2.85, 0]),
            T("Significado", 20, GRAY).move_to([xm, 2.85, 0], aligned_edge=m.LEFT),
            T("Unidad (SI)", 20, GRAY).move_to([xu, 2.85, 0], aligned_edge=m.LEFT),
        )
        filas = [
            ("q", "Carga almacenada en una placa (+q / −q)", "C  (culombio)", POS),
            ("v", "Tensión (diferencia de potencial) entre las placas", "V  (voltio)", NEG),
            ("C", "Capacitancia (parámetro concentrado)", "F  (faradio)", GREEN),
            ("E", "Campo eléctrico entre las placas", "V/m", FIELD),
            (r"\sigma", "Densidad superficial de carga, σ = q / A", "C/m²", INK),
            (r"\varepsilon_0", "Permitividad del vacío (8,85 × 10⁻¹² F/m)", "F/m", INK),
            ("A", "Área de una placa", "m²", INK),
            ("d", "Separación entre las placas", "m", INK),
            (r"\kappa", "Constante dieléctrica relativa (ε / ε₀)", "adimensional", DIEL_T),
        ]
        items = []
        for i, (sim, sig, uni, col) in enumerate(filas):
            y = 2.4 - i * 0.44
            g = m.VGroup(
                MT(sim, 34, col).move_to([xs, y, 0]),
                T(sig, 22).move_to([xm, y, 0], aligned_edge=m.LEFT),
                T(uni, 24, col if col != INK else TITLE).move_to([xu, y, 0], aligned_edge=m.LEFT),
            )
            items.append(g)
        self.play(m.FadeIn(cab), run_time=0.6)
        self.play(m.FadeIn(m.VGroup(*items), lag_ratio=0.18), run_time=4.5)

        nota = m.VGroup(
            T("Minúsculas: variables que cambian en el tiempo (q, v).", 20, GRAY),
            T("Mayúsculas: parámetros concentrados y valores constantes (C, V₀, Q₀).", 20, GRAY),
        ).arrange(m.DOWN, aligned_edge=m.LEFT, buff=0.08).move_to([-6.8, -1.65, 0], aligned_edge=m.LEFT)
        self.play(m.FadeIn(nota), run_time=0.8)
        self.wait(2.0)

        ch = T("Comprobación dimensional de las ecuaciones", 22, TITLE).move_to([-6.8, -2.3, 0], aligned_edge=m.LEFT)
        c1 = MT(r"E=\frac{\sigma}{\varepsilon_0}:\ \frac{\mathrm{C/m^{2}}}{\mathrm{F/m}}=\frac{\mathrm{V}}{\mathrm{m}}", 24)
        c2 = MT(r"v=E\,d:\ \frac{\mathrm{V}}{\mathrm{m}}\,\mathrm{m}=\mathrm{V}", 24)
        c3 = MT(r"C=\frac{\varepsilon_0 A}{d}:\ \frac{\mathrm{F}}{\mathrm{m}}\frac{\mathrm{m^{2}}}{\mathrm{m}}=\mathrm{F}", 24)
        fila = m.VGroup(c1, c2, c3).arrange(m.RIGHT, buff=0.55).move_to([0.2, -2.95, 0])
        self.play(m.FadeIn(ch), run_time=0.6)
        for c in (c1, c2, c3):
            self.play(m.FadeIn(c, shift=m.UP * 0.15), run_time=0.9)
            self.wait(0.9)
        self.wait(2.0)
        self.limpiar()

    # ================= 4. Geometría =================
    def escena_geometria(self):
        self.titulo("De qué depende la capacitancia")
        wT = m.ValueTracker(W0)
        dT = m.ValueTracker(D0)
        dyn = m.always_redraw(lambda: cap_dyn(wT.get_value(), dT.get_value()))
        self.play(m.FadeIn(dyn), run_time=1.0)

        f = MT(r"C=\varepsilon_0\,\frac{A}{d}", 52, TITLE).move_to([4.4, 2.0, 0]).align_to([1.7, 0, 0], m.LEFT)
        k = T("ε₀ = 8,85 × 10⁻¹² F/m", 24, GRAY).next_to(f, m.DOWN, buff=0.25, aligned_edge=m.LEFT)
        self.play(m.FadeIn(f), m.FadeIn(k), run_time=1.0)

        def lect():
            a = wT.get_value() / W0
            dd = dT.get_value() / D0
            c = a / dd
            return m.VGroup(
                T(f"A = {coma(a, 2)} A₀", 28),
                T(f"d = {coma(dd, 2)} d₀", 28),
                T(f"C = {coma(c, 2)} C₀", 30, TITLE),
            ).arrange(m.DOWN, aligned_edge=m.LEFT, buff=0.22).move_to([4.4, -0.7, 0]).align_to([1.7, 0, 0], m.LEFT)

        self.add(m.always_redraw(lect))
        self.pie("Con la batería conectada la tensión es fija y la carga almacenada es q = C · v")
        self.wait(1.0)
        self.pie("Placas más cercanas (d menor): C aumenta y entra más carga")
        self.play(dT.animate.set_value(1.4), run_time=3, rate_func=m.smooth)
        self.wait(1.2)
        self.pie("Placas más grandes (A mayor): C también aumenta")
        self.play(wT.animate.set_value(5.6), run_time=3, rate_func=m.smooth)
        self.wait(2.0)
        self.limpiar()

    # ================= 5. Dieléctrico =================
    def escena_dielectrico(self):
        self.titulo("El dieléctrico entre las placas")
        cap = construir_cap()
        yTi, yBi = cap["yTi"], cap["yBi"]
        arrows = m.VGroup(*cap["arrows"])
        frg = m.VGroup(*cap["fringe"])
        frg.set_stroke(opacity=0.65)
        xl0 = CX + W0 / 2 + 0.3
        xl1 = CX - W0 / 2
        xlT = m.ValueTracker(xl0)

        def frac():
            return float(np.clip((CX + W0 / 2 - xlT.get_value()) / W0, 0, 1))

        def vfrac():
            return 1.0 / (1.0 + (KAPPA - 1.0) * frac())

        arrows.add_updater(lambda g: g.set_stroke(width=4.0 * vfrac()))

        self.play(m.FadeIn(cap["top"]), m.FadeIn(cap["bot"]), run_time=0.8)
        self.add(*cap["plus"], *cap["minus"], arrows, frg)
        self.play(*[m.FadeIn(g) for g in cap["plus"] + cap["minus"]], m.FadeIn(arrows), m.FadeIn(frg), run_time=1.0)
        qm = T("+Q", 30, POS).move_to([CX, cap["yT"] + 0.5, 0])
        qn = T("−Q", 30, NEG).move_to([CX, cap["yB"] - 0.5, 0])
        self.play(m.FadeIn(qm), m.FadeIn(qn), run_time=0.6)
        self.pie("Capacitor cargado y desconectado de la batería: la carga Q queda constante")

        def lectura():
            vf = vfrac()
            return T(f"v = {coma(V0 * vf)} V     E = {coma(vf, 2)} E₀     C = {coma(1 / vf, 2)} C₀",
                     26, GRAY).move_to([CX, -2.2, 0])

        self.add(m.always_redraw(lectura))
        self.wait(1.5)

        rng = np.random.default_rng(7)
        th0 = rng.uniform(-np.pi, np.pi, (3, 9))
        thf = -np.pi / 2 + rng.normal(0, 0.12, (3, 9))
        delta = ((thf - th0 + np.pi) % (2 * np.pi)) - np.pi

        def losa():
            return m.Rectangle(width=W0, height=D0 - TH, fill_color=DIEL, fill_opacity=0.28,
                               stroke_color=DIEL, stroke_width=2).move_to([xlT.get_value() + W0 / 2, CY, 0])

        def dipolos():
            xl = xlT.get_value()
            fr = frac()
            a = fr * fr * (3 - 2 * fr)
            it = []
            for j in range(3):
                for i in range(9):
                    x = xl + (i + 0.5) * W0 / 9
                    y = CY + (j - 1) * 0.42
                    th = th0[j, i] + a * delta[j, i]
                    u = np.array([np.cos(th), np.sin(th), 0.0])
                    c = np.array([x, y, 0.0])
                    pm, pp = c - 0.15 * u, c + 0.15 * u
                    it += [L(pm, pp, GRAY, 3), m.Dot(pp, radius=0.055, color=POS), m.Dot(pm, radius=0.055, color=NEG)]
            return m.VGroup(*it)

        slab = m.always_redraw(losa)
        dip = m.always_redraw(dipolos)
        self.play(m.FadeIn(slab), m.FadeIn(dip), run_time=1.0)
        etq = T("Dieléctrico (κ = 3): moléculas polares orientadas al azar", 24, DIEL_T).move_to([CX + 2.0, CY + 2.15, 0])
        self.pie("Un dieléctrico está formado por moléculas polares: dipolos con extremos + y −")
        self.play(m.FadeIn(etq), run_time=0.6)
        self.wait(2.0)
        self.pie("Al entrar al campo, los dipolos se orientan en su dirección")
        self.play(m.FadeOut(etq), run_time=0.3)
        self.play(xlT.animate.set_value(xl1), run_time=5.5, rate_func=m.smooth)
        self.wait(0.5)

        ind_neg = m.VGroup(*[menos(CX - W0 / 2 + (i + 0.5) * W0 / 6, yTi - 0.4, 0.075, IND_NEG, 4) for i in range(6)])
        ind_pos = m.VGroup(*[mas(CX - W0 / 2 + (i + 0.5) * W0 / 6, yBi + 0.4, 0.075, IND_POS, 4) for i in range(6)])
        self.pie("Aparecen cargas inducidas en el dieléctrico, de signo opuesto al de las placas")
        self.play(m.FadeIn(ind_neg), m.FadeIn(ind_pos), run_time=1.5)
        self.wait(1.0)

        leg1 = m.VGroup(mas(0, 0, 0.1, POS, 4), T("Carga libre (placas)", 22)).arrange(m.RIGHT, buff=0.25)
        leg2 = m.VGroup(mas(0, 0, 0.1, IND_POS, 4), T("Carga inducida (dieléctrico)", 22)).arrange(m.RIGHT, buff=0.25)
        leg = m.VGroup(leg1, leg2).arrange(m.DOWN, aligned_edge=m.LEFT, buff=0.25).move_to([4.4, -1.55, 0]).align_to(
            [1.7, 0, 0], m.LEFT)

        h1 = T("Dieléctrico con κ = 3", 28, DIEL_T)
        h2 = T("(Q constante)", 22, GRAY)
        fE = MT(r"E=\dfrac{E_0}{\kappa}", 36)
        fV = MT(r"v=\dfrac{V_0}{\kappa}", 36)
        fC = MT(r"C=\kappa\,C_0=\kappa\,\dfrac{\varepsilon_0 A}{d}", 36, TITLE)
        panel = m.VGroup(h1, h2, fE, fV, fC).arrange(m.DOWN, aligned_edge=m.LEFT, buff=0.22)
        panel.move_to([4.4, 1.0, 0]).align_to([1.7, 0, 0], m.LEFT)
        self.play(m.FadeIn(h1), m.FadeIn(h2), m.FadeIn(leg), run_time=0.8)
        for fm in (fE, fV, fC):
            self.play(m.FadeIn(fm, shift=m.RIGHT * 0.2), run_time=0.9)
            self.wait(1.2)
        self.pie("E₀, V₀ y C₀: valores sin dieléctrico.  κ: constante dieléctrica relativa (sin unidades)")
        self.wait(3.5)
        self.pie("Las cargas inducidas debilitan el campo: E y v bajan a 1/κ y C sube a κ·C₀")
        self.wait(3.0)
        self.limpiar()

    # ================= 5b. Dos casos =================
    def escena_casos(self):
        self.titulo("Al insertar el dieléctrico: dos casos")
        ejes_x = [-5.0, -0.7, 4.4]
        h_a = m.VGroup(T("Batería desconectada", 26, TITLE), T("(Q constante)", 22, GRAY)).arrange(m.DOWN, buff=0.08).move_to(
            [ejes_x[1], 2.35, 0])
        h_b = m.VGroup(T("Batería conectada", 26, TITLE), T("(v constante)", 22, GRAY)).arrange(m.DOWN, buff=0.08).move_to(
            [ejes_x[2], 2.35, 0])
        filas = [
            ("Capacitancia", r"C=\kappa C_0", r"C=\kappa C_0", GREEN, GREEN),
            ("Tensión", r"v=V_0/\kappa", r"v=V_0", NEG, GRAY),
            ("Carga", r"q=Q_0", r"q=\kappa Q_0", GRAY, POS),
            ("Campo", r"E=E_0/\kappa", r"E=E_0", NEG, GRAY),
            ("Energía", r"w=W_0/\kappa", r"w=\kappa W_0", NEG, POS),
        ]
        lineas = []
        grupos = []
        for i, (nom, fa, fb, ca, cb) in enumerate(filas):
            y = 1.35 - i * 0.82
            g = m.VGroup(
                T(nom, 26).move_to([-6.6, y, 0], aligned_edge=m.LEFT),
                MT(fa, 36, ca).move_to([ejes_x[1], y, 0]),
                MT(fb, 36, cb).move_to([ejes_x[2], y, 0]),
            )
            grupos.append(g)
            lineas.append(L([-6.7, y - 0.41, 0], [6.7, y - 0.41, 0], LINEC, 2))
        self.play(m.FadeIn(h_a), m.FadeIn(h_b), m.Create(lineas[0]), run_time=1.0)
        for g, ln in zip(grupos, lineas):
            self.play(m.FadeIn(g, shift=m.UP * 0.15), m.Create(ln), run_time=0.9)
            self.wait(0.8)
        self.pie("Con la batería conectada, v se mantiene y entra más carga: q = κ Q₀")
        self.wait(3.0)
        self.limpiar()

    # ================= 6. Propiedades del dieléctrico =================
    def escena_propiedades(self):
        self.titulo("Qué aporta el dieléctrico")
        cab = T("Constante dieléctrica κ (valores típicos)", 24, GRAY).move_to([-6.8, 2.5, 0], aligned_edge=m.LEFT)
        filas = [("Vacío", "1"), ("Aire", "1,0006"), ("Teflón", "2,1"), ("Papel", "≈ 3,7"),
                 ("Vidrio", "≈ 5 a 10"), ("Agua", "≈ 80"), ("Cerámicos (BaTiO₃)", "≈ 10³ a 10⁴")]
        tabla = m.VGroup()
        for i, (nom, val) in enumerate(filas):
            y = 1.7 - i * 0.58
            tabla.add(T(nom, 26).move_to([-6.6, y, 0], aligned_edge=m.LEFT))
            tabla.add(T(val, 26, TITLE).move_to([-1.35, y, 0], aligned_edge=m.RIGHT))
        nota = T("Aproximados, a unos 20 °C", 20, GRAY).move_to([-6.6, -2.7, 0], aligned_edge=m.LEFT)
        self.play(m.FadeIn(cab), run_time=0.6)
        self.play(m.FadeIn(tabla, lag_ratio=0.12), run_time=2.5)
        self.play(m.FadeIn(nota), run_time=0.4)

        datos = [
            ("1. Mayor capacitancia", ["C = κ C₀: mismo tamaño,", "más carga almacenada"], GREEN),
            ("2. Soporte mecánico", ["Mantiene separadas las placas,", "permite una distancia d muy pequeña"], FIELD),
            ("3. Mayor tensión máxima", ["Rigidez dieléctrica: el aire resiste unos 3 MV/m;",
                                          "muchos dieléctricos resisten varias veces más"], NEG),
        ]
        tarjetas = []
        for i, (h, lineas, c) in enumerate(datos):
            y = 1.9 - i * 1.7
            caja = m.Rectangle(width=7.0, height=1.45, fill_color=CARD, fill_opacity=1, stroke_color=c,
                               stroke_width=3).move_to([3.4, y, 0])
            txt = m.VGroup(T(h, 26, c), *[T(l, 20) for l in lineas]).arrange(m.DOWN, aligned_edge=m.LEFT, buff=0.07)
            txt.move_to(caja.get_center()).align_to(caja, m.LEFT).shift(m.RIGHT * 0.25)
            tarjetas.append(m.VGroup(caja, txt))
        for tj in tarjetas:
            self.play(m.FadeIn(tj, shift=m.LEFT * 0.3), run_time=1.0)
            self.wait(1.5)
        self.pie("Si el campo supera la rigidez dieléctrica, el aislante se rompe y salta una chispa", 24)
        self.wait(3.0)
        self.limpiar()

    # ================= 6b. Relación tensión–corriente =================
    def escena_tension_corriente(self):
        self.titulo("Relación tensión–corriente en el capacitor")

        def par(titulo, formula, color=INK, buff=0.12):
            return m.VGroup(T(titulo, 22, GRAY), MT(formula, 36, color)).arrange(m.DOWN, aligned_edge=m.LEFT, buff=buff)

        p1 = par("De q = C v, derivando en el tiempo (C constante):",
                 r"i(t)=\frac{dq}{dt}=C\,\frac{dv}{dt}")
        p2 = par("Integrando (la primitiva):", r"v(t)=\frac{1}{C}\int_{-\infty}^{t} i(\tau)\,d\tau")
        p3 = par("Desde un instante inicial t₀:",
                 r"v(t)=v(t_0)+\frac{1}{C}\int_{t_0}^{t} i(\tau)\,d\tau", TITLE, buff=0.3)
        nota = m.VGroup(
            T("v(t₀): tensión inicial (la «memoria» del capacitor)", 20, GRAY),
            T("τ: variable de integración", 20, GRAY),
        ).arrange(m.DOWN, aligned_edge=m.LEFT, buff=0.08)
        col = m.VGroup(p1, p2, p3, nota).arrange(m.DOWN, aligned_edge=m.LEFT, buff=0.35)
        col.move_to([-3.0, 0.1, 0]).align_to([-6.8, 0, 0], m.LEFT)
        caja = m.SurroundingRectangle(p3[1], buff=0.15, color=TITLE, stroke_width=2)

        self.play(m.FadeIn(p1, shift=m.RIGHT * 0.2), run_time=1.0)
        self.pie("La corriente es la rapidez con que cambia la carga en las placas", 24)
        self.wait(1.5)
        self.play(m.FadeIn(p2, shift=m.RIGHT * 0.2), run_time=1.0)
        self.pie("La tensión acumula toda la historia de la corriente que ha entrado al capacitor", 24)
        self.wait(1.5)
        self.play(m.FadeIn(p3, shift=m.RIGHT * 0.2), m.Create(caja), run_time=1.2)
        self.play(m.FadeIn(nota), run_time=0.6)
        self.pie("Lo ocurrido antes de t₀ queda resumido en la tensión inicial v(t₀)", 24)
        self.wait(2.0)

        # ---- ejemplo: pulso de corriente constante ----
        x0, x1, xa, xb = 2.0, 6.6, 2.9, 5.0     # eje t: origen, fin, t₀, t₁
        yi, yv = 0.9, -1.9                      # origen de cada gráfica
        hI, v0, hV = 0.9, 0.3, 1.1              # altura de I₀, v(t₀) y del aumento de v

        def ejes(y, nombre, color):
            return m.VGroup(
                m.Arrow([x0, y, 0], [x1, y, 0], buff=0, color=GRAY, stroke_width=3),
                m.Arrow([x0, y, 0], [x0, y + 1.45, 0], buff=0, color=GRAY, stroke_width=3),
                MT(nombre, 28, color).move_to([x0 + 0.45, y + 1.45, 0]),
                MT("t", 26, GRAY).move_to([x1 + 0.2, y - 0.2, 0]),
            )

        marcas = m.VGroup(
            m.DashedLine([xa, yv, 0], [xa, yi + 1.2, 0], color=LINEC, stroke_width=2),
            m.DashedLine([xb, yv, 0], [xb, yi + 1.2, 0], color=LINEC, stroke_width=2),
            MT("t_0", 26, GRAY).move_to([xa, yv - 0.3, 0]),
            MT("t_1", 26, GRAY).move_to([xb, yv - 0.3, 0]),
        )
        etq = m.VGroup(
            MT("I_0", 26, POS).move_to([x0 - 0.3, yi + hI, 0]),
            MT("v(t_0)", 24, NEG).move_to([x0 - 0.5, yv + v0, 0]),
        )
        tT = m.ValueTracker(x0)

        def curvas():
            x = tT.get_value()

            def corriente(s):
                return hI if xa <= s < xb else 0.0

            def tension(s):
                return v0 + hV * float(np.clip((s - xa) / (xb - xa), 0, 1))

            ss = np.linspace(x0, max(x, x0 + 1e-3), 200)
            pi = [np.array([s, yi + corriente(s), 0.0]) for s in ss]
            pv = [np.array([s, yv + tension(s), 0.0]) for s in ss]
            return m.VGroup(
                m.VMobject(color=POS, stroke_width=5).set_points_as_corners(pi),
                m.VMobject(color=NEG, stroke_width=5).set_points_as_corners(pv),
            )

        self.pie("Ejemplo: entre t₀ y t₁ entra una corriente constante I₀", 24)
        self.play(m.FadeIn(ejes(yi, "i(t)", POS)), m.FadeIn(ejes(yv, "v(t)", NEG)), m.FadeIn(marcas), m.FadeIn(etq),
                  run_time=1.0)
        self.add(m.always_redraw(curvas))
        self.play(tT.animate.set_value(x1 - 0.1), run_time=4.0, rate_func=m.linear)
        pend = MT(r"\text{pendiente}=\frac{I_0}{C}", 24, NEG).next_to([xb, yv + 0.7, 0], m.RIGHT, buff=0.12)
        self.play(m.FadeIn(pend), run_time=0.6)
        self.pie("Con corriente constante, v crece linealmente; si i = 0, v se mantiene", 24)
        self.wait(2.5)
        self.pie("v no puede cambiar de forma instantánea: exigiría una corriente infinita", 24)
        self.wait(2.5)
        self.pie("En DC (v constante), i = C dv/dt = 0: el capacitor actúa como circuito abierto", 24)
        self.wait(3.0)
        self.limpiar()

    # ================= 7. Energía =================
    def escena_energia(self):
        self.titulo("¿Dónde se guarda la energía?")
        cap = construir_cap()
        vol = m.Rectangle(width=W0, height=D0 - TH, fill_color=FIELD, fill_opacity=0.10,
                          stroke_color=FIELD, stroke_width=2).move_to([CX, CY, 0])
        self.play(m.FadeIn(cap["top"]), m.FadeIn(cap["bot"]), m.FadeIn(vol), run_time=1.0)
        self.play(*[m.FadeIn(g) for g in cap["plus"] + cap["minus"] + cap["arrows"]], m.FadeIn(m.VGroup(*cap["fringe"])),
                  run_time=1.0)
        lbl = T("Energía almacenada en el campo E", 24, FIELD).move_to([CX, -1.9, 0])
        self.play(m.FadeIn(lbl), run_time=0.6)
        self.pie("El trabajo para separar las cargas queda almacenado en el campo entre las placas")

        a = T("Energía almacenada (w, en julios)", 24, GRAY)
        f1 = MT(r"w=\tfrac{1}{2}\,C\,v^{2}=\tfrac{1}{2}\,q\,v=\dfrac{q^{2}}{2C}", 30)
        b = T("Densidad de energía (u, en J/m³)", 24, GRAY)
        f2 = MT(r"u=\tfrac{1}{2}\,\varepsilon\,E^{2}", 36, TITLE)
        c = T("con ε = κ ε₀ (en el vacío, κ = 1)", 22, GRAY)
        chk = MT(r"\frac{\mathrm{F}}{\mathrm{m}}\left(\frac{\mathrm{V}}{\mathrm{m}}\right)^{2}=\frac{\mathrm{J}}{\mathrm{m^{3}}}", 28)
        panel = m.VGroup(a, f1, b, f2, c, chk).arrange(m.DOWN, aligned_edge=m.LEFT, buff=0.2)
        panel.move_to([4.4, 0.2, 0]).align_to([1.7, 0, 0], m.LEFT)
        for grp in ((a, f1), (b, f2, c), (chk,)):
            self.play(*[m.FadeIn(x, shift=m.RIGHT * 0.2) for x in grp], run_time=1.0)
            self.wait(2.0)
        self.wait(2.0)
        self.limpiar()

    # ================= 8. Resumen =================
    def escena_resumen(self):
        self.titulo("Resumen")
        pts = [
            ("Capacitor: dos conductores separados por un aislante.", TITLE),
            ("Cargas +q y −q crean un campo uniforme entre las placas: E = σ / ε.", TITLE),
            ("Capacitancia: C = q / v = κ ε₀ A / d, medida en faradios (F = C/V).", TITLE),
            ("El dieléctrico se polariza, debilita el campo (E₀/κ) y aumenta C.", TITLE),
            ("Relación v–i: i = C dv/dt,  v(t) = v(t₀) + (1/C) ∫ i dτ desde t₀.", TITLE),
            ("Energía: w = ½ C v², guardada en el campo eléctrico.", TITLE),
        ]
        items = []
        for i, (s, c) in enumerate(pts):
            num = T(str(i + 1), 28, "#FFFFFF")
            circ = m.Circle(radius=0.26, fill_color=c, fill_opacity=1, stroke_width=0)
            marca = m.VGroup(circ, num.move_to(circ.get_center()))
            txt = T(s, 28)
            row = m.VGroup(marca, txt).arrange(m.RIGHT, buff=0.35)
            items.append(row)
        col = m.VGroup(*items).arrange(m.DOWN, aligned_edge=m.LEFT, buff=0.4).move_to([0, 0.1, 0])
        for row in items:
            self.play(m.FadeIn(row, shift=m.RIGHT * 0.25), run_time=0.9)
            self.wait(1.3)
        self.wait(2.5)
        self.limpiar(1.0)


if __name__ == "__main__":
    os.makedirs(SALIDA, exist_ok=True)
    CapacitorVideo().render(VIDEO)
    print("Video guardado en:", VIDEO)
