import os

import numpy as np
import manimgx as m

# Fondo blanco (debe fijarse antes de construir la escena)
m.config.background_color = "#FFFFFF"

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
FIGURAS = os.path.join(RAIZ, "figuras")
SALIDA = os.path.join(RAIZ, "videos_salida")
VIDEO = os.path.join(SALIDA, "circuito_rl_primer_orden.mp4")

# ---------------- Paleta (fondo blanco) ----------------
INK = "#1F2933"
GRAY = "#6B7280"
TITLE = "#0B3C5D"
POS = "#D32F2F"        # corriente del inductor
NEG = "#1565C0"        # tensión del inductor
FIELD = "#E65100"      # transitorio
MAG = "#7B1FA2"        # campo magnético
GREEN = "#2E7D32"
LINEC = "#D1D5DB"

# ---------------- Identificación institucional ----------------
UNIVERSIDAD = "Universidad de Antioquia"
DEPARTAMENTO = "Departamento de Ingeniería Electrónica y de Telecomunicaciones"
CURSO = "Circuitos Eléctricos I"

# ---------------- Geometría del circuito ----------------
XS, XC = -6.0, -1.2          # x de la fuente y del inductor
YT, YB, YM = 1.3, -1.5, -0.1  # cable superior, inferior y altura media
PA = np.array([-5.0, YT, 0.0])     # terminal a (fuente)
PB = np.array([-4.75, 0.55, 0.0])  # terminal b (sin fuente)
PP = np.array([-4.2, YT, 0.0])     # pivote del interruptor
XR0, XR1 = -3.7, -2.5        # resistencia
NB, RB = 4, 0.14             # vueltas y radio de la bobina
YL0, YL1 = YM + NB * RB, YM - NB * RB  # extremos de la bobina
V0 = 10.0                    # 10 V, 1 kΩ, 1 H  ->  τ = 1 ms, I0 = V0/R = 10 mA
YPIE = -3.3
YFOOT = -3.78


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


def flecha(p0, p1, color=INK, sw=4, head=0.17):
    p0, p1 = np.array(p0, float), np.array(p1, float)
    d = (p1 - p0) / np.linalg.norm(p1 - p0)
    n = np.array([-d[1], d[0], 0.0])
    return m.VGroup(L(p0, p1, color, sw),
                    L(p1, p1 - head * d + 0.09 * n, color, sw), L(p1, p1 - head * d - 0.09 * n, color, sw))


def resistor(x0, x1, y, picos=6, amp=0.18, color=INK, sw=4):
    dx = (x1 - x0) / picos
    pts = [np.array([x0, y, 0.0])]
    pts += [np.array([x0 + (k + 0.5) * dx, y + amp * (1 if k % 2 == 0 else -1), 0.0]) for k in range(picos)]
    pts.append(np.array([x1, y, 0.0]))
    return m.VMobject(color=color, stroke_width=sw).set_points_as_corners(pts)


def bobina(color=INK, sw=4):
    """Inductor vertical: NB semicírculos hacia la derecha, entre YL0 y YL1."""
    arcos = []
    for k in range(NB):
        yc = YL0 - (2 * k + 1) * RB
        arcos.append(m.ParametricFunction(
            lambda t, yc=yc: np.array([XC + RB * np.cos(t), yc + RB * np.sin(t), 0.0]),
            t_range=[np.pi / 2, -np.pi / 2, -0.05], color=color, stroke_width=sw, fill_opacity=0))
    return m.VGroup(*arcos)


def terminal(p):
    return m.Circle(radius=0.06, stroke_color=INK, stroke_width=3, fill_color="#FFFFFF",
                    fill_opacity=1).move_to(p)


def cuchilla(pos):
    """Hoja del interruptor: hacia a (fuente conectada) o hacia b (fuente retirada)."""
    destino = PA if pos == "a" else PB
    d = destino - PP
    return L(PP, PP + d * (1 - 0.07 / np.linalg.norm(d)), INK, 4)


def fuente(tipo):
    if tipo == "dc":
        return m.VGroup(L([XS, YT, 0], [XS, YM + 0.1, 0]), L([XS, YM - 0.1, 0], [XS, YB, 0]),
                        L([XS - 0.35, YM + 0.1, 0], [XS + 0.35, YM + 0.1, 0], INK, 6),
                        L([XS - 0.2, YM - 0.1, 0], [XS + 0.2, YM - 0.1, 0], INK, 6))
    r = 0.42
    grupo = m.VGroup(L([XS, YT, 0], [XS, YM + r, 0]), L([XS, YM - r, 0], [XS, YB, 0]),
                     m.Circle(radius=r, stroke_color=INK, stroke_width=4).move_to([XS, YM, 0]))
    if tipo == "ac":
        grupo.add(m.ParametricFunction(lambda u: np.array([XS - 0.25 + 0.5 * u, YM + 0.14 * np.sin(2 * np.pi * u), 0.0]),
                                       t_range=[0, 1, 0.02], color=INK, stroke_width=3, fill_opacity=0))
    else:
        grupo.add(MT("+", 24).move_to([XS, YM + 0.2, 0]), MT("-", 24).move_to([XS, YM - 0.2, 0]))
    return grupo


def circuito(tipo="general"):
    """Fuente, interruptor de dos posiciones (a/b), R y L. La hoja del interruptor va aparte."""
    cables = m.VGroup(
        L([XS, YT, 0], PA), L(PB, [PB[0], YB, 0]), L([XS, YB, 0], [XC, YB, 0]),
        L(PP, [XR0, YT, 0]), L([XR1, YT, 0], [XC, YT, 0]),
        L([XC, YT, 0], [XC, YL0, 0]), L([XC, YL1, 0], [XC, YB, 0]),
        bobina(), resistor(XR0, XR1, YT),
        m.Dot([PB[0], YB, 0], radius=0.06, color=INK),
    )
    nom_f = {"general": "v_s", "dc": "V_0", "ac": "v_s"}[tipo]
    nom_r, nom_l = ("R", "L") if tipo != "dc" else (r"R=1\,\mathrm{k\Omega}", r"L=1\,\mathrm{H}")
    etiquetas = m.VGroup(
        MT(nom_f, 30).move_to([XS - 0.75, YM, 0]),
        MT(nom_r, 28).move_to([(XR0 + XR1) / 2, YT + 0.42, 0]),
        MT(nom_l, 28).move_to([XC - 0.95 if tipo == "dc" else XC - 0.5, YM, 0]),
        MT("+", 26, NEG).move_to([XC + 0.45, YL0, 0]), MT("-", 26, NEG).move_to([XC + 0.45, YL1, 0]),
        MT("v_L", 30, NEG).move_to([XC + 0.75, YM, 0]),
        T("a", 24, GRAY).move_to(PA + np.array([0.0, -0.28, 0])),
        T("b", 24, GRAY).move_to(PB + np.array([-0.25, 0.0, 0])),
        MT("t=0", 24, GRAY).move_to([-4.55, YT + 0.45, 0]),
    )
    return m.VGroup(fuente(tipo), cables, m.VGroup(*[terminal(p) for p in (PA, PB, PP)]), etiquetas)


def flecha_i(color=POS):
    return m.VGroup(flecha([-2.3, YT + 0.3, 0], [-1.65, YT + 0.3, 0], color, 3, 0.14),
                    MT("i_L", 28, color).move_to([-1.97, YT + 0.62, 0]))


def mapa(x0, y0, sx, sy):
    return lambda t, v: np.array([x0 + sx * t, y0 + sy * v, 0.0])


def curva(P, f, t0, t1, color, sw=5, n=300):
    ts = np.linspace(t0, max(t1, t0 + 1e-3), n)
    return m.VMobject(color=color, stroke_width=sw).set_points_as_corners([P(t, f(t)) for t in ts])


def ecuacion(tex, color, pos, size=28):
    """Ecuación de una curva, recuadrada en el color de la curva."""
    f = MT(tex, size, color).move_to(pos)
    return m.VGroup(f, m.SurroundingRectangle(f, buff=0.1, color=color, stroke_width=2))


def punto_en_ruta(pts, u):
    seg = [np.linalg.norm(pts[i + 1] - pts[i]) for i in range(len(pts) - 1)]
    d = (u % 1.0) * sum(seg)
    for i, s in enumerate(seg):
        if d <= s:
            return pts[i] + (pts[i + 1] - pts[i]) * (d / s), i
        d -= s
    return pts[-1], len(seg) - 1


# Recorridos de la corriente (sentido real). El salto final de la ruta de energización es la fuente.
RUTA_CARGA = [(XS, YM + 0.12), (XS, YT), tuple(PA), tuple(PP), (XC, YT), (XC, YB), (XS, YB), (XS, YM - 0.12)]
RUTA_DESCARGA = [tuple(PP), (XC, YT), (XC, YB), (PB[0], YB), tuple(PB), tuple(PP)]


def corriente_animada(ruta, intensidad, n=26, rapidez=3.2):
    """Puntos que recorren el circuito: su rapidez y su opacidad siguen a intensidad() (de 0 a 1)."""
    pts = [np.array([p[0], p[1], 0.0], float) for p in ruta]
    total = sum(np.linalg.norm(pts[i + 1] - pts[i]) for i in range(len(pts) - 1))
    grp = m.VGroup(*[m.Dot(radius=0.065, color=POS) for _ in range(n)])
    fase = {"u": 0.0}

    def mover(g, dt):
        k_i = float(intensidad())
        fase["u"] = (fase["u"] + dt * rapidez * k_i / total) % 1.0
        op = float(np.clip(3 * k_i, 0, 1))
        for k, d in enumerate(g):
            p, _ = punto_en_ruta(pts, k / n + fase["u"])
            d.move_to(p)
            d.set_opacity(op)

    grp.add_updater(mover)
    return grp


def bobina_energizada(fraccion):
    """Resalta la bobina en morado según la energía en su campo magnético (∝ i²)."""
    def dibujar():
        a = float(np.clip(fraccion(), 0, 1))
        return bobina(MAG, 7).set_stroke(opacity=a * a)
    return m.always_redraw(dibujar)


def ejes(x0, y0, ancho, arriba, abajo, nombre, color, ticks=(), size=26):
    g = m.VGroup(
        m.Arrow([x0, y0, 0], [x0 + ancho, y0, 0], buff=0, color=GRAY, stroke_width=3),
        m.Arrow([x0, y0 - abajo, 0], [x0, y0 + arriba, 0], buff=0, color=GRAY, stroke_width=3),
        MT(nombre, size + 2, color).next_to([x0, y0 + arriba, 0], m.RIGHT, buff=0.15),
        MT("t", size, GRAY).move_to([x0 + ancho + 0.2, y0 - 0.2, 0]),
    )
    for x, lab in ticks:
        g.add(L([x, y0 - 0.06, 0], [x, y0 + 0.06, 0], GRAY, 2))
        if lab:
            g.add(MT(lab, 28, GRAY).move_to([x, y0 - 0.28, 0]))
    return g


def marcas_tau(x0, sx):
    return [(x0 + sx * k, rf"{k}\tau" if k > 1 else r"\tau") for k in range(1, 6)]


class CircuitoRL(m.Scene):
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

    def panel(self, pares, y=0.3, buff=0.35):
        """Coloca pares (etiqueta, fórmula) en la columna derecha."""
        col = m.VGroup(*pares).arrange(m.DOWN, aligned_edge=m.LEFT, buff=buff)
        col.move_to([3.8, y, 0]).align_to([0.8, 0, 0], m.LEFT)
        return col

    @staticmethod
    def par(titulo, formula, color=INK, size=34, buff=0.12):
        return m.VGroup(T(titulo, 22, GRAY), MT(formula, size, color)).arrange(m.DOWN, aligned_edge=m.LEFT, buff=buff)

    def lectura(self, tT, fi, fv):
        """Lectura en vivo de t (ms), i_L (mA) y v_L (V)."""
        def dibujar():
            t = tT.get_value()
            partes = []
            for sim, val, uni in (("t", t, "ms"), ("i_L", fi(t), "mA"), ("v_L", fv(t), "V")):
                partes.append(m.VGroup(MT(sim + "=", 30, GRAY), T(f"{coma(val, 2)} {uni}", 26, GRAY)).arrange(
                    m.RIGHT, buff=0.1))
            return m.VGroup(*partes).arrange(m.RIGHT, buff=0.5).move_to([-3.6, -2.45, 0])
        return m.always_redraw(dibujar)

    # ---------- escena ----------
    def construct(self):
        self._pie = None
        self._footer = self.crear_footer()
        self.escena_titulo()
        self.play(m.FadeIn(self._footer), run_time=0.6)
        self.escena_circuito()
        self.escena_ecuacion()
        self.escena_solucion_general()
        self.escena_dc_carga()
        self.escena_dc_carga_grafica()
        self.escena_tau()
        self.escena_dc_descarga()
        self.escena_receta_dc()
        self.escena_ac_planteamiento()
        self.escena_ac_particular()
        self.escena_ac_grafica()
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
        t1 = T("Circuitos de primer orden", 62, TITLE).move_to([0, -0.5, 0])
        t2 = T("Parte 2: el circuito RL — energización y desenergización del inductor", 28, GRAY).move_to([0, -1.4, 0])
        P = mapa(-1.6, -3.1, 0.65, 0.8)
        cv = curva(P, lambda t: 1 - np.exp(-t), 0, 5, POS, 5)
        ax = m.VGroup(L(P(0, 0), P(5.1, 0), GRAY, 2), L(P(0, 0), P(0, 1.1), GRAY, 2))
        self.play(*[m.FadeIn(b) for b in bloque], m.FadeIn(uni), m.FadeIn(dep), m.FadeIn(cur), m.Create(sep),
                  run_time=1.4)
        self.play(m.FadeIn(t1, shift=m.UP * 0.3), run_time=1.0)
        self.play(m.FadeIn(t2), m.Create(ax), run_time=1.0)
        self.play(m.Create(cv), run_time=1.2)
        self.wait(2.0)
        self.limpiar()

    # ================= 2. El circuito RL =================
    def escena_circuito(self):
        self.titulo("El circuito RL")
        circ = circuito("general")
        hoja = cuchilla("b")
        self.play(m.Create(circ[1]), m.FadeIn(circ[0]), m.FadeIn(circ[2]), m.Create(hoja), run_time=1.6)
        self.play(m.FadeIn(circ[3]), run_time=0.8)

        p1 = self.par("Un solo elemento que almacena energía (L):", r"\Rightarrow\ \text{ecuación diferencial de primer orden}", size=30)
        p2 = self.par("La incógnita para t ≥ 0:", r"i_L(t)\ \text{(corriente del inductor)}", POS, 30)
        p3 = self.par("La corriente del inductor no cambia de golpe:", r"i_L(0^+)=i_L(0^-)", TITLE, 38, 0.2)
        self.panel([p1, p2, p3], y=0.4, buff=0.5)
        caja = m.SurroundingRectangle(p3[1], buff=0.15, color=TITLE, stroke_width=2)
        self.pie("En t = 0 el interruptor cambia de posición: en a conecta la fuente, en b la retira", 24)
        self.play(m.Transform(hoja, cuchilla("a")), run_time=0.8)
        self.wait(0.6)
        self.play(m.Transform(hoja, cuchilla("b")), run_time=0.8)
        for p in (p1, p2):
            self.play(m.FadeIn(p, shift=m.RIGHT * 0.2), run_time=0.9)
            self.wait(1.4)
        self.play(m.FadeIn(p3, shift=m.RIGHT * 0.2), m.Create(caja), run_time=1.0)
        self.pie("Un salto en la corriente del inductor exigiría una tensión L di/dt infinita", 26)
        self.wait(2.5)
        self.limpiar()

    # ================= 3. Ecuación diferencial =================
    def escena_ecuacion(self):
        self.titulo("Planteamiento: la ecuación diferencial")
        circ = circuito("general")
        hoja = cuchilla("a")
        self.play(m.FadeIn(circ), m.FadeIn(hoja), run_time=1.0)
        self.play(m.FadeIn(flecha_i()), run_time=0.6)
        self.pie("Para t ≥ 0, con el interruptor en a, la malla contiene la fuente, R y L", 24)

        p1 = self.par("Ley de Kirchhoff de tensiones en la malla:", r"v_s(t)=R\,i_L+v_L")
        p2 = self.par("Tensión del inductor:", r"v_L=L\,\frac{di_L}{dt}")
        p3 = self.par("Sustituyendo y dividiendo entre R:", r"\frac{L}{R}\,\frac{di_L}{dt}+i_L=\frac{v_s(t)}{R}")
        p4 = self.par("Con la constante de tiempo τ = L/R:", r"\tau\,\frac{di_L}{dt}+i_L=\frac{v_s(t)}{R}", TITLE, 38, 0.2)
        self.panel([p1, p2, p3, p4], y=0.3, buff=0.28)
        caja = m.SurroundingRectangle(p4[1], buff=0.15, color=TITLE, stroke_width=2)
        for p in (p1, p2, p3):
            self.play(m.FadeIn(p, shift=m.RIGHT * 0.2), run_time=0.9)
            self.wait(1.3)
        self.play(m.FadeIn(p4, shift=m.RIGHT * 0.2), m.Create(caja), run_time=1.0)
        self.pie("La misma ecuación del circuito RC, ahora para la corriente del inductor", 24)
        self.wait(2.0)
        uni = MT(r"[\tau]=\frac{\mathrm{H}}{\Omega}=\frac{\mathrm{V\cdot s/A}}{\mathrm{V/A}}=\mathrm{s}", 30,
                 GREEN).move_to([XC - 2.2, -2.45, 0])
        self.play(m.FadeIn(uni), run_time=0.8)
        self.pie("τ = L/R se mide en segundos: más inductancia o menos resistencia, respuesta más lenta", 24)
        self.wait(2.5)
        self.limpiar()

    # ================= 4. Solución general =================
    def escena_solucion_general(self):
        self.titulo("Solución general: respuesta natural + respuesta forzada")
        f0 = MT(r"i_L(t)=i_h(t)+i_p(t)", 48, TITLE).move_to([0, 2.45, 0])
        self.play(m.FadeIn(f0, shift=m.UP * 0.2), run_time=1.0)
        self.pie("La solución es la suma de la homogénea (natural) y una particular (forzada)", 24)
        self.wait(1.0)

        izq = m.VGroup(
            T("Respuesta natural (homogénea)", 26, GREEN),
            MT(r"\tau\,\frac{di_h}{dt}+i_h=0", 32),
            MT(r"\text{Se propone } i_h=K\,e^{st}:", 28, GRAY),
            MT(r"\tau s+1=0\ \Rightarrow\ s=-\frac{1}{\tau}", 32),
            MT(r"i_h(t)=K\,e^{-t/\tau}", 38, GREEN),
        ).arrange(m.DOWN, aligned_edge=m.LEFT, buff=0.22).move_to([-3.6, 0.0, 0])
        der = m.VGroup(
            T("Respuesta forzada (particular)", 26, FIELD),
            T("Tiene la forma de la fuente:", 22, GRAY),
            MT(r"\text{DC: } v_s=V_0\ \Rightarrow\ i_p=\text{constante}", 30),
            MT(r"\text{AC: } v_s=V_m\cos\omega t\ \Rightarrow\ i_p\ \text{senoidal de la misma }\omega", 30),
        ).arrange(m.DOWN, aligned_edge=m.LEFT, buff=0.3).move_to([3.3, 0.2, 0])
        for g in (izq, der):
            for x in g:
                self.play(m.FadeIn(x, shift=m.RIGHT * 0.15), run_time=0.7)
                self.wait(0.6)
            self.wait(1.0)
        self.pie("La natural depende solo del circuito (τ); la forzada depende de la fuente", 24)
        self.wait(2.5)
        self.play(m.FadeOut(izq), m.FadeOut(der), run_time=0.7)

        k1 = T("La constante K sale de la condición inicial, evaluando en t = 0⁺:", 24, GRAY).move_to([0, 1.45, 0])
        k2 = MT(r"i_L(0^+)=i_p(0^+)+K\ \Rightarrow\ K=i_L(0^+)-i_p(0^+)", 36).move_to([0, 0.75, 0])
        fin = MT(r"i_L(t)=i_p(t)+\big[i_L(0^+)-i_p(0^+)\big]\,e^{-t/\tau},\qquad t\ge 0", 42, TITLE).move_to([0, -0.6, 0])
        caja = m.SurroundingRectangle(fin, buff=0.25, color=TITLE, stroke_width=2)
        notas = m.VGroup(
            T("respuesta forzada (permanente)", 22, FIELD), T("respuesta transitoria", 22, GREEN),
        ).arrange(m.RIGHT, buff=2.2).move_to([0.6, -1.75, 0])
        self.play(m.FadeIn(k1), run_time=0.6)
        self.play(m.FadeIn(k2, shift=m.UP * 0.15), run_time=1.0)
        self.wait(1.5)
        self.play(m.FadeIn(fin), m.Create(caja), run_time=1.2)
        self.play(m.FadeIn(notas), run_time=0.8)
        self.pie("Conocida la corriente, la tensión del inductor sale de L di/dt", 26)
        self.wait(3.0)
        self.limpiar()

    # ================= 5. DC: energización =================
    def escena_dc_carga(self):
        self.titulo("Caso DC: energización del inductor")
        circ = circuito("dc")
        hoja = cuchilla("b")
        self.play(m.FadeIn(circ), m.FadeIn(hoja), run_time=1.0)
        self.pie("Para t < 0 el interruptor está en b y no circula corriente por el inductor", 24)

        p1 = self.par("Condición inicial:", r"i_L(0^-)=0\ \Rightarrow\ i_L(0^+)=0")
        p2 = self.par("Fuente constante: la particular es constante", r"0+i_p=\frac{V_0}{R}\ \Rightarrow\ i_p=I_0=\frac{V_0}{R}")
        p3 = self.par("En la solución general:", r"i_L(t)=I_0+(0-I_0)\,e^{-t/\tau}")
        p4 = m.VGroup(T("Corriente y tensión para t ≥ 0:", 22, GRAY),
                      MT(r"i_L(t)=I_0\big(1-e^{-t/\tau}\big)", 32, TITLE),
                      MT(r"v_L(t)=L\frac{di_L}{dt}=V_0\,e^{-t/\tau}", 32, TITLE)).arrange(
            m.DOWN, aligned_edge=m.LEFT, buff=0.28)
        self.panel([p1, p2, p3, p4], y=0.3, buff=0.28)
        caja = m.SurroundingRectangle(m.VGroup(p4[1], p4[2]), buff=0.12, color=TITLE, stroke_width=2)
        self.play(m.Transform(hoja, cuchilla("a")), run_time=0.8)
        self.play(m.FadeIn(flecha_i()), run_time=0.5)
        for p in (p1, p2, p3):
            self.play(m.FadeIn(p, shift=m.RIGHT * 0.2), run_time=0.9)
            self.wait(1.3)
        self.play(m.FadeIn(p4, shift=m.RIGHT * 0.2), m.Create(caja), run_time=1.0)
        self.pie("Con R = 1 kΩ y L = 1 H:  τ = L/R = 1 ms  e  I₀ = V₀/R = 10 mA", 26)
        self.wait(3.0)
        self.limpiar()

    def escena_dc_carga_grafica(self):
        self.titulo("Energización del inductor: corriente y tensión")
        circ = circuito("dc")
        hoja = cuchilla("b")
        fi_ = flecha_i()
        tT = m.ValueTracker(0)
        self.play(m.FadeIn(circ), m.FadeIn(hoja), run_time=0.8)

        Pi = mapa(1.3, 0.5, 0.95, 2.0 / 10)
        Pv = mapa(1.3, -2.5, 0.95, 1.5 / V0)
        tk = marcas_tau(1.3, 0.95)
        ei = ejes(1.3, 0.5, 5.4, 2.35, 0, "i_L(t)", POS, tk)
        ev = ejes(1.3, -2.5, 5.4, 1.75, 0, "v_L(t)", NEG, tk)
        ref = m.VGroup(m.DashedLine(Pi(0, 10), Pi(5.2, 10), color=LINEC, stroke_width=2),
                       MT("I_0", 26, POS).move_to(Pi(0, 10) + np.array([-0.35, 0, 0])),
                       MT("V_0", 26, NEG).move_to(Pv(0, V0) + np.array([-0.35, 0, 0])))
        self.play(m.FadeIn(ei), m.FadeIn(ev), m.FadeIn(ref), run_time=1.0)

        fi = lambda t: 10 * (1 - np.exp(-t))
        fv = lambda t: V0 * np.exp(-t) if t > 0 else 0.0

        def curvas():
            t = tT.get_value()
            g = m.VGroup(curva(Pi, fi, 0, t, POS), m.Dot(Pi(t, fi(t)), radius=0.07, color=POS))
            if t > 0:
                g.add(curva(Pv, fv, 1e-4, t, NEG), m.Dot(Pv(t, fv(t)), radius=0.07, color=NEG))
            return g

        li = ecuacion(r"i_L(t)=I_0\big(1-e^{-t/\tau}\big)", POS, Pi(3.5, 6.3))
        lv = ecuacion(r"v_L(t)=V_0\,e^{-t/\tau}", NEG, Pv(3.5, 5.5))
        self.pie("Estas son las expresiones que vamos a graficar", 26)
        self.play(m.FadeIn(li, shift=m.UP * 0.15), run_time=0.8)
        self.play(m.FadeIn(lv, shift=m.UP * 0.15), run_time=0.8)
        self.wait(1.2)

        self.add(bobina_energizada(lambda: fi(tT.get_value()) / 10))
        self.add(m.always_redraw(curvas), self.lectura(tT, fi, fv))
        self.pie("En t = 0 el interruptor pasa a a: los puntos rojos muestran la corriente", 24)
        self.play(m.Transform(hoja, cuchilla("a")), m.FadeIn(fi_), run_time=0.6)
        self.add(corriente_animada(RUTA_CARGA, lambda: fi(tT.get_value()) / 10))
        self.play(tT.animate.set_value(5.0), run_time=9.0, rate_func=m.linear)
        self.pie("La corriente arranca en 0 y crece; toda la tensión de la fuente aparece en L en t = 0⁺", 24)
        self.wait(3.0)
        self.pie("En régimen permanente la tensión en L es 0: en DC el inductor se comporta como cortocircuito", 24)
        self.wait(3.0)
        self.limpiar()

    # ================= 6. Constante de tiempo =================
    def escena_tau(self):
        self.titulo("La constante de tiempo τ = L/R")
        P = mapa(-5.6, -2.3, 2.0, 4.6 / 100)
        ex = ejes(-5.6, -2.3, 11.0, 5.2, 0, r"i_L/I_0", POS, marcas_tau(-5.6, 2.0))
        ref = m.VGroup(m.DashedLine(P(0, 100), P(5.3, 100), color=LINEC, stroke_width=2),
                       T("100 %", 22, GRAY).move_to(P(0, 100) + np.array([-0.55, 0, 0])))
        self.play(m.FadeIn(ex), m.FadeIn(ref), run_time=1.0)
        f = lambda t: 100 * (1 - np.exp(-t))
        eq = ecuacion(r"\frac{i_L(t)}{I_0}=1-e^{-t/\tau}", POS, [P(4.3, 0)[0], 2.85, 0], 32)
        self.play(m.FadeIn(eq, shift=m.UP * 0.15), run_time=0.8)
        self.play(m.Create(curva(P, f, 0, 5.3, POS)), run_time=2.5)

        tang = m.DashedLine(P(0, 0), P(1, 100), color=FIELD, stroke_width=3)
        self.pie("La tangente en t = 0 alcanza el valor final justo en t = τ", 26)
        self.play(m.Create(tang), run_time=1.2)
        self.wait(1.5)

        puntos = []
        for k in range(1, 6):
            v = f(k)
            puntos.append(m.VGroup(
                m.DashedLine(P(k, 0), P(k, v), color=LINEC, stroke_width=2),
                m.Dot(P(k, v), radius=0.08, color=POS),
                T(f"{coma(v, 1)} %", 22, POS).move_to(P(k, v) + np.array([0.6, -0.32, 0])),
            ))
        self.pie("En t = τ la corriente alcanza el 63,2 % de su valor final", 26)
        self.play(m.FadeIn(puntos[0]), run_time=0.8)
        self.wait(1.5)
        self.play(*[m.FadeIn(p) for p in puntos[1:]], run_time=1.5, lag_ratio=0.3)
        self.pie("Después de unos 5τ (99,3 %) se considera que el transitorio terminó", 26)
        self.wait(3.0)
        self.limpiar()

    # ================= 7. DC: desenergización =================
    def escena_dc_descarga(self):
        self.titulo("Caso DC: desenergización del inductor")
        circ = circuito("dc")
        hoja = cuchilla("a")
        self.play(m.FadeIn(circ), m.FadeIn(hoja), m.FadeIn(flecha_i()), run_time=1.0)
        self.pie("Corriente establecida I₀; en t = 0 el interruptor pasa a b y retira la fuente", 24)
        self.play(m.Transform(hoja, cuchilla("b")), run_time=0.8)
        self.pie("El contacto b ofrece un camino a la corriente: abrir el circuito sin él produciría una chispa", 22)
        self.wait(2.0)

        p1 = self.par("Condición inicial:", r"i_L(0^-)=I_0\ \Rightarrow\ i_L(0^+)=I_0")
        p2 = self.par("Sin fuente en la malla: la particular es cero", r"\tau\frac{di_L}{dt}+i_L=0\ \Rightarrow\ i_p=0")
        p3 = m.VGroup(T("Corriente y tensión para t ≥ 0:", 22, GRAY),
                      MT(r"i_L(t)=I_0\,e^{-t/\tau}", 32, TITLE),
                      MT(r"v_L(t)=L\frac{di_L}{dt}=-V_0\,e^{-t/\tau}", 32, TITLE)).arrange(
            m.DOWN, aligned_edge=m.LEFT, buff=0.28)
        col = self.panel([p1, p2, p3], y=0.45, buff=0.4)
        caja = m.SurroundingRectangle(m.VGroup(p3[1], p3[2]), buff=0.12, color=TITLE, stroke_width=2)
        for p in (p1, p2):
            self.play(m.FadeIn(p, shift=m.RIGHT * 0.2), run_time=0.9)
            self.wait(1.3)
        self.play(m.FadeIn(p3, shift=m.RIGHT * 0.2), m.Create(caja), run_time=1.0)
        self.pie("La corriente conserva su sentido; la tensión del inductor se invierte", 24)
        self.wait(2.5)
        self.play(m.FadeOut(col), m.FadeOut(caja), run_time=0.6)

        tT = m.ValueTracker(0)
        Pi = mapa(1.3, 0.5, 0.95, 2.0 / 10)
        Pv = mapa(1.3, -0.95, 0.95, 1.5 / V0)
        ei = ejes(1.3, 0.5, 5.4, 2.35, 0, "i_L(t)", POS, marcas_tau(1.3, 0.95))
        ev = ejes(1.3, -0.95, 5.4, 0.35, 1.7, "v_L(t)", NEG)
        ref = m.VGroup(MT("I_0", 26, POS).move_to(Pi(0, 10) + np.array([-0.35, 0, 0])),
                       MT(r"-V_0", 24, NEG).move_to(Pv(0, -V0) + np.array([-0.45, 0, 0])))
        self.play(m.FadeIn(ei), m.FadeIn(ev), m.FadeIn(ref), run_time=1.0)
        fi = lambda t: 10 * np.exp(-t)
        fv = lambda t: -V0 * np.exp(-t)

        def curvas():
            t = tT.get_value()
            return m.VGroup(curva(Pi, fi, 0, t, POS), m.Dot(Pi(t, fi(t)), radius=0.07, color=POS),
                            curva(Pv, fv, 0, t, NEG), m.Dot(Pv(t, fv(t)), radius=0.07, color=NEG))

        li = ecuacion(r"i_L(t)=I_0\,e^{-t/\tau}", POS, Pi(3.5, 5.0))
        lv = ecuacion(r"v_L(t)=-V_0\,e^{-t/\tau}", NEG, Pv(3.5, -6.0))
        self.play(m.FadeIn(li, shift=m.UP * 0.15), run_time=0.8)
        self.play(m.FadeIn(lv, shift=m.UP * 0.15), run_time=0.8)
        self.wait(1.0)

        self.add(bobina_energizada(lambda: fi(tT.get_value()) / 10))
        self.add(m.always_redraw(curvas))
        self.add(corriente_animada(RUTA_DESCARGA, lambda: fi(tT.get_value()) / 10))
        self.pie("El inductor mantiene la corriente por la malla L–R mientras se agota su campo", 24)
        self.play(tT.animate.set_value(5.0), run_time=8.0, rate_func=m.linear)
        self.pie("Toda la energía del campo magnético, ½ L I₀², se disipa como calor en la resistencia", 24)
        self.wait(3.0)
        self.limpiar()

    # ================= 8. Receta DC =================
    def escena_receta_dc(self):
        self.titulo("En DC: la fórmula práctica")
        f = MT(r"i_L(t)=i_L(\infty)+\big[i_L(0^+)-i_L(\infty)\big]\,e^{-t/\tau}", 46, TITLE).move_to([0, 2.3, 0])
        caja = m.SurroundingRectangle(f, buff=0.25, color=TITLE, stroke_width=2)
        self.play(m.FadeIn(f), m.Create(caja), run_time=1.2)
        self.pie("En DC la particular es constante: es el valor final de la corriente del inductor", 24)
        self.wait(1.5)
        pasos = [
            ("1.", r"i_L(0^+):\ \text{con el circuito en } t<0 \text{ y la continuidad } i_L(0^+)=i_L(0^-)"),
            ("2.", r"i_L(\infty):\ \text{régimen permanente, con el inductor como cortocircuito}"),
            ("3.", r"\tau=\frac{L}{R_{eq}}:\ R_{eq}\ \text{es la resistencia que ve el inductor (Thévenin)}"),
        ]
        filas = m.VGroup(*[m.VGroup(T(n, 26, TITLE), MT(s, 30)).arrange(m.RIGHT, buff=0.25) for n, s in pasos])
        filas.arrange(m.DOWN, aligned_edge=m.LEFT, buff=0.25).move_to([0, 0.5, 0])
        for fl in filas:
            self.play(m.FadeIn(fl, shift=m.RIGHT * 0.2), run_time=0.8)
            self.wait(1.2)

        xs = (-3.0, 0.4, 3.4)
        cab = m.VGroup(T("Caso", 22, GRAY).move_to([xs[0], -0.95, 0]), MT(r"i_L(0^+)", 30, GRAY).move_to([xs[1], -0.95, 0]),
                       MT(r"i_L(\infty)", 30, GRAY).move_to([xs[2], -0.95, 0]))
        lin = L([-4.6, -1.25, 0], [4.6, -1.25, 0], LINEC, 2)
        f1 = m.VGroup(T("Energización", 26).move_to([xs[0], -1.6, 0]), MT("0", 32).move_to([xs[1], -1.6, 0]),
                      MT(r"V_0/R", 32).move_to([xs[2], -1.6, 0]))
        f2 = m.VGroup(T("Desenergización", 26).move_to([xs[0], -2.25, 0]), MT(r"V_0/R", 32).move_to([xs[1], -2.25, 0]),
                      MT("0", 32).move_to([xs[2], -2.25, 0]))
        self.play(m.FadeIn(cab), m.Create(lin), run_time=0.7)
        self.play(m.FadeIn(f1, shift=m.UP * 0.1), run_time=0.7)
        self.play(m.FadeIn(f2, shift=m.UP * 0.1), run_time=0.7)
        self.pie("Energización y desenergización son dos casos de la misma fórmula", 26)
        self.wait(3.0)
        self.limpiar()

    # ================= 9. AC: planteamiento =================
    def escena_ac_planteamiento(self):
        self.titulo("Caso AC: fuente senoidal")
        circ = circuito("ac")
        hoja = cuchilla("b")
        self.play(m.FadeIn(circ), m.FadeIn(hoja), run_time=1.0)
        self.play(m.Transform(hoja, cuchilla("a")), m.FadeIn(flecha_i()), run_time=0.8)

        p1 = m.VGroup(MT(r"\text{Fuente para } t\ge 0,\ \text{con } I_m=V_m/R:", 28, GRAY),
                      MT(r"v_s(t)=V_m\cos(\omega t)", 34)).arrange(m.DOWN, aligned_edge=m.LEFT, buff=0.12)
        p2 = self.par("Inductor sin corriente inicial:", r"i_L(0^+)=i_L(0^-)=0")
        p3 = self.par("Ecuación:", r"\tau\,\frac{di_L}{dt}+i_L=I_m\cos(\omega t)")
        p4 = self.par("Particular de la misma frecuencia:",
                      r"i_p(t)=A\cos(\omega t)+B\sin(\omega t)", TITLE, 34, 0.2)
        self.panel([p1, p2, p3, p4], y=0.35, buff=0.32)
        for p in (p1, p2, p3, p4):
            self.play(m.FadeIn(p, shift=m.RIGHT * 0.2), run_time=0.9)
            self.wait(1.3)
        self.pie("Una fuente senoidal fuerza una respuesta senoidal de la misma frecuencia", 24)
        self.wait(2.5)
        self.limpiar()

    # ================= 10. AC: particular =================
    def escena_ac_particular(self):
        self.titulo("Caso AC: cálculo de la respuesta forzada")
        p1 = self.par("Sustituyendo la particular en la ecuación:",
                      r"\big(B-\omega\tau A\big)\sin(\omega t)+\big(A+\omega\tau B\big)\cos(\omega t)=I_m\cos(\omega t)")
        p2 = self.par("Igualando coeficientes de seno y coseno:",
                      r"B-\omega\tau A=0,\qquad A+\omega\tau B=I_m")
        p3 = self.par("Resolviendo:",
                      r"A=\frac{I_m}{1+(\omega\tau)^2},\qquad B=\frac{\omega\tau\,I_m}{1+(\omega\tau)^2}")
        col = m.VGroup(p1, p2, p3).arrange(m.DOWN, aligned_edge=m.LEFT, buff=0.45).move_to([0, 0.4, 0])
        col.align_to([-6.6, 0, 0], m.LEFT)
        for p in (p1, p2, p3):
            self.play(m.FadeIn(p, shift=m.RIGHT * 0.2), run_time=1.0)
            self.wait(1.8)
        self.pie("Dos ecuaciones algebraicas para dos incógnitas, A y B", 26)
        self.wait(1.5)
        self.play(m.FadeOut(col), run_time=0.6)

        q1 = self.par("En forma de amplitud y fase:",
                      r"i_p(t)=\frac{I_m}{\sqrt{1+(\omega\tau)^2}}\cos(\omega t-\varphi),\qquad \varphi=\arctan(\omega\tau)")
        q2 = m.VGroup(
            MT(r"\text{Con } i_L(0^+)=0,\ \text{la constante es } K=-i_p(0)=-\frac{I_m}{1+(\omega\tau)^2}:", 28, GRAY),
            MT(r"i_L(t)=\frac{I_m}{\sqrt{1+(\omega\tau)^2}}\cos(\omega t-\varphi)-\frac{I_m}{1+(\omega\tau)^2}\,e^{-t/\tau}",
               36, TITLE)).arrange(m.DOWN, aligned_edge=m.LEFT, buff=0.3)
        col2 = m.VGroup(q1, q2).arrange(m.DOWN, aligned_edge=m.LEFT, buff=0.6).move_to([0, 0.7, 0])
        col2.align_to([-6.6, 0, 0], m.LEFT)
        caja = m.SurroundingRectangle(q2[1], buff=0.15, color=TITLE, stroke_width=2)
        notas = m.VGroup(
            T("respuesta forzada (permanente)", 22, FIELD), T("respuesta transitoria", 22, GREEN),
        ).arrange(m.RIGHT, buff=1.2).next_to(caja, m.DOWN, buff=0.2)
        self.play(m.FadeIn(q1, shift=m.RIGHT * 0.2), run_time=1.0)
        self.pie("La corriente tiene menor amplitud y va retrasada φ respecto a la fuente", 24)
        self.wait(2.5)
        self.play(m.FadeIn(q2, shift=m.RIGHT * 0.2), m.Create(caja), run_time=1.2)
        self.play(m.FadeIn(notas), run_time=0.6)
        self.pie("Misma estructura que en DC: forzada + transitorio que se extingue en unos 5τ", 24)
        self.wait(3.5)
        self.limpiar()

    # ================= 11. AC: gráfica =================
    def escena_ac_grafica(self):
        self.titulo("Caso AC: conexión y retiro de la fuente")
        t1 = 4 * np.pi                      # se retira tras dos periodos (ωτ = 1  ->  T = 2πτ)
        tf = t1 + 5.0
        P = mapa(-6.4, 0.25, 12.4 / tf, 1.9)
        ex = ejes(-6.4, 0.25, 12.9, 2.25, 2.05, r"v/V_m,\ i/I_m", INK)
        a = 1 / np.sqrt(2)
        i1 = a * np.cos(t1 - np.pi / 4) - 0.5 * np.exp(-t1)

        def fs(t):
            return np.cos(t)

        def ftr(t):
            return -0.5 * np.exp(-t)

        def fc(t):
            return a * np.cos(t - np.pi / 4) + ftr(t) if t < t1 else i1 * np.exp(-(t - t1))

        def fv(t):
            # v_L = L di_L/dt, normalizada con V_m (con ωτ = 1, ωL = R)
            return a * np.cos(t + np.pi / 4) + 0.5 * np.exp(-t) if t < t1 else -i1 * np.exp(-(t - t1))

        marcas = m.VGroup(
            m.DashedLine(P(t1, -1.0), P(t1, 0.98), color=LINEC, stroke_width=2),
            T("b: se retira la fuente", 20, GRAY).move_to(P(t1, -1.15) + np.array([0.2, 0, 0])),
            T("a: se conecta", 20, GRAY).move_to(P(0, -1.15) + np.array([0.95, 0, 0])),
        )
        ley = m.VGroup(
            m.VGroup(L([0, 0, 0], [0.5, 0, 0], GRAY, 3), MT(r"v_s(t)=V_m\cos(\omega t)", 26, GRAY)).arrange(m.RIGHT, buff=0.15),
            m.VGroup(L([0, 0, 0], [0.5, 0, 0], POS, 5), MT("i_L(t)", 26, POS)).arrange(m.RIGHT, buff=0.15),
            m.VGroup(L([0, 0, 0], [0.5, 0, 0], NEG, 4), MT("v_L(t)", 26, NEG)).arrange(m.RIGHT, buff=0.15),
            m.VGroup(L([0, 0, 0], [0.5, 0, 0], FIELD, 3), MT(r"\text{transitorio de } i_L", 26, FIELD)
                     ).arrange(m.RIGHT, buff=0.15),
            MT(r"\omega\tau=1,\ \ I_m=V_m/R", 26, GRAY),
        ).arrange(m.RIGHT, buff=0.45).move_to([0, -2.45, 0])
        eq_i = ecuacion(r"i_L(t)=\frac{I_m}{\sqrt{2}}\cos\big(\omega t-45^\circ\big)-\frac{I_m}{2}\,e^{-t/\tau}",
                        POS, [0, 2.62, 0], 24)
        eq_i.align_to([6.8, 0, 0], m.RIGHT)
        eq_v = ecuacion(r"v_L(t)=\frac{V_m}{\sqrt{2}}\cos\big(\omega t+45^\circ\big)+\frac{V_m}{2}\,e^{-t/\tau}",
                        NEG, [0, 2.62, 0], 24)
        eq_v.next_to(eq_i, m.LEFT, buff=0.25)
        self.play(m.FadeIn(ex), m.FadeIn(marcas), run_time=0.8)
        self.pie("Expresiones que se grafican: corriente y tensión del inductor", 26)
        self.play(m.FadeIn(ley[0]), m.FadeIn(ley[4]), run_time=0.7)
        self.play(m.FadeIn(eq_i, shift=m.DOWN * 0.15), m.FadeIn(ley[1]), m.FadeIn(ley[3]), run_time=0.8)
        self.wait(0.8)
        self.pie("La tensión del inductor sale de derivar su corriente: L di/dt", 26)
        self.play(m.FadeIn(eq_v, shift=m.DOWN * 0.15), m.FadeIn(ley[2]), run_time=0.8)
        self.wait(1.5)
        tT = m.ValueTracker(0)

        def curvas():
            t = tT.get_value()
            g = m.VGroup(curva(P, fs, 0, min(t, t1), GRAY, 3))
            tr = curva(P, ftr, 0, min(t, 6.0), FIELD, 3)
            g.add(m.DashedVMobject(tr, num_dashes=30))
            g.add(curva(P, fv, 0, t, NEG, 4, 500), m.Dot(P(t, fv(t)), radius=0.07, color=NEG))
            g.add(curva(P, fc, 0, t, POS, 5, 500), m.Dot(P(t, fc(t)), radius=0.07, color=POS))
            return g

        self.add(m.always_redraw(curvas))
        self.pie("Al conectar: la tensión en L salta de inmediato, mientras la corriente parte de 0", 24)
        self.play(tT.animate.set_value(6.0), run_time=4.0, rate_func=m.linear)
        self.pie("Régimen permanente: la tensión del inductor va 90° adelantada respecto a su corriente", 24)
        self.play(tT.animate.set_value(t1), run_time=4.0, rate_func=m.linear)
        self.pie("Al retirar la fuente: la corriente decae sin saltos; la tensión se invierte de golpe", 24)
        fd = ecuacion(r"i_L(t)=i_L(t_1)\,e^{-(t-t_1)/\tau}", POS, P(t1 + 2.6, 0.75))
        fdv = ecuacion(r"v_L(t)=-R\,i_L(t_1)\,e^{-(t-t_1)/\tau}", NEG, P(t1 + 2.6, -0.75))
        self.play(m.FadeIn(fd, shift=m.UP * 0.15), m.FadeIn(fdv, shift=m.UP * 0.15), run_time=0.7)
        self.play(tT.animate.set_value(tf), run_time=3.5, rate_func=m.linear)
        self.wait(3.0)
        self.limpiar()

    # ================= 12. Resumen =================
    def escena_resumen(self):
        self.titulo("Resumen")
        pts = [
            r"\text{Planteamiento: LKT y } v_L=L\,\frac{di_L}{dt}\ \Rightarrow\ \tau\,\frac{di_L}{dt}+i_L=\frac{v_s(t)}{R},\ \ \tau=\frac{L}{R}",
            r"\text{Solución: } i_L=i_h+i_p,\ \text{con } i_h=K\,e^{-t/\tau}\ \text{(respuesta natural)}",
            r"K\ \text{sale de la condición inicial, usando } i_L(0^+)=i_L(0^-)",
            r"\text{DC: } i_L(t)=i_L(\infty)+\big[i_L(0^+)-i_L(\infty)\big]\,e^{-t/\tau}",
            r"\text{AC: } i_p\ \text{senoidal de la misma } \omega,\ \text{amplitud } \frac{I_m}{\sqrt{1+(\omega\tau)^2}},"
            r"\ \varphi=\arctan(\omega\tau)",
            r"\text{Dualidad con el RC: } v_C\leftrightarrow i_L,\ \ C\leftrightarrow L,\ \ \tau=RC\leftrightarrow\tau=L/R",
        ]
        items = []
        for i, s in enumerate(pts):
            num = T(str(i + 1), 26, "#FFFFFF")
            circ = m.Circle(radius=0.24, fill_color=TITLE, fill_opacity=1, stroke_width=0)
            marca = m.VGroup(circ, num.move_to(circ.get_center()))
            items.append(m.VGroup(marca, MT(s, 30)).arrange(m.RIGHT, buff=0.3))
        m.VGroup(*items).arrange(m.DOWN, aligned_edge=m.LEFT, buff=0.3).move_to([0, 0.1, 0])
        for row in items:
            self.play(m.FadeIn(row, shift=m.RIGHT * 0.25), run_time=0.9)
            self.wait(1.4)
        self.wait(2.5)
        self.limpiar(1.0)


if __name__ == "__main__":
    os.makedirs(SALIDA, exist_ok=True)
    CircuitoRL().render(VIDEO)
    print("Video guardado en:", VIDEO)
