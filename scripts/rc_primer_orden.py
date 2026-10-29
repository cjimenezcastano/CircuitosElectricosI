import os

import numpy as np
import manimgx as m

# Fondo blanco (debe fijarse antes de construir la escena)
m.config.background_color = "#FFFFFF"

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
FIGURAS = os.path.join(RAIZ, "figuras")
SALIDA = os.path.join(RAIZ, "videos_salida")
VIDEO = os.path.join(SALIDA, "circuito_rc_primer_orden.mp4")

# ---------------- Paleta (fondo blanco) ----------------
INK = "#1F2933"
GRAY = "#6B7280"
TITLE = "#0B3C5D"
POS = "#D32F2F"        # corriente
NEG = "#1565C0"        # tensión del capacitor
FIELD = "#E65100"      # transitorio
GREEN = "#2E7D32"
CARD = "#F3F4F6"
LINEC = "#D1D5DB"

# ---------------- Identificación institucional ----------------
UNIVERSIDAD = "Universidad de Antioquia"
DEPARTAMENTO = "Departamento de Ingeniería Electrónica y de Telecomunicaciones"
CURSO = "Circuitos Eléctricos I"

# ---------------- Geometría del circuito ----------------
XS, XC = -6.0, -1.2          # x de la fuente y del capacitor
YT, YB, YM = 1.3, -1.5, -0.1  # cable superior, inferior y altura media
PA = np.array([-5.0, YT, 0.0])     # terminal a (fuente)
PB = np.array([-4.75, 0.55, 0.0])  # terminal b (descarga)
PP = np.array([-4.2, YT, 0.0])     # pivote del interruptor
XR0, XR1 = -3.7, -2.5        # resistencia
V0, RK, CM = 10.0, 1.0, 1.0  # 10 V, 1 kΩ, 1 mF  ->  τ = 1 s, V0/R = 10 mA
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


def terminal(p):
    return m.Circle(radius=0.06, stroke_color=INK, stroke_width=3, fill_color="#FFFFFF",
                    fill_opacity=1).move_to(p)


def cuchilla(pos):
    """Hoja del interruptor: hacia a (fuente conectada) o hacia b (fuente desconectada)."""
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
    """Fuente, interruptor de dos posiciones (a/b), R y C. La hoja del interruptor va aparte."""
    cables = m.VGroup(
        L([XS, YT, 0], PA), L(PB, [PB[0], YB, 0]), L([XS, YB, 0], [XC, YB, 0]),
        L(PP, [XR0, YT, 0]), L([XR1, YT, 0], [XC, YT, 0]),
        L([XC, YT, 0], [XC, YM + 0.1, 0]), L([XC, YM - 0.1, 0], [XC, YB, 0]),
        L([XC - 0.4, YM + 0.1, 0], [XC + 0.4, YM + 0.1, 0], INK, 6),
        L([XC - 0.4, YM - 0.1, 0], [XC + 0.4, YM - 0.1, 0], INK, 6),
        resistor(XR0, XR1, YT),
        m.Dot([PB[0], YB, 0], radius=0.06, color=INK),
    )
    nom_f = {"general": "v_s", "dc": "V_0", "ac": "v_s"}[tipo]
    nom_r, nom_c = ("R", "C") if tipo != "dc" else (r"R=1\,\mathrm{k\Omega}", r"C=1\,\mathrm{mF}")
    etiquetas = m.VGroup(
        MT(nom_f, 30).move_to([XS - 0.75, YM, 0]),
        MT(nom_r, 28).move_to([(XR0 + XR1) / 2, YT + 0.42, 0]),
        MT(nom_c, 28).move_to([XC - 1.15 if tipo == "dc" else XC - 0.7, YM, 0]),
        MT("+", 26, NEG).move_to([XC + 0.3, YM + 0.35, 0]), MT("-", 26, NEG).move_to([XC + 0.3, YM - 0.35, 0]),
        MT("v_C", 30, NEG).move_to([XC + 0.75, YM, 0]),
        T("a", 24, GRAY).move_to(PA + np.array([0.0, -0.28, 0])),
        T("b", 24, GRAY).move_to(PB + np.array([-0.25, 0.0, 0])),
        MT("t=0", 24, GRAY).move_to([-4.55, YT + 0.45, 0]),
    )
    return m.VGroup(fuente(tipo), cables, m.VGroup(*[terminal(p) for p in (PA, PB, PP)]), etiquetas)


def flecha_i(color=POS):
    return m.VGroup(flecha([-2.3, YT + 0.3, 0], [-1.65, YT + 0.3, 0], color, 3, 0.14),
                    MT("i", 28, color).move_to([-1.97, YT + 0.6, 0]))


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


# Recorridos de la corriente (sentido real). Los tramos ocultos no son cable: la fuente o el capacitor.
RUTA_CARGA = [(XC, YM - 0.12), (XC, YB), (XS, YB), (XS, YM - 0.12), (XS, YM + 0.12), (XS, YT),
              tuple(PA), tuple(PP), (XC, YT), (XC, YM + 0.12)]
RUTA_DESCARGA = [(XC, YM + 0.12), (XC, YT), tuple(PP), tuple(PB), (PB[0], YB), (XC, YB), (XC, YM - 0.12)]


def corriente_animada(ruta, ocultos, intensidad, n=26, rapidez=3.2):
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
            p, i = punto_en_ruta(pts, k / n + fase["u"])
            d.move_to(p)
            d.set_opacity(0.0 if i in ocultos else op)

    grp.add_updater(mover)
    return grp


def placas_cargadas(fraccion):
    """Tiñe las placas: roja la superior (+q) y azul la inferior (−q), según la carga almacenada."""
    def dibujar():
        a = float(np.clip(fraccion(), 0, 1))
        sup = L([XC - 0.4, YM + 0.1, 0], [XC + 0.4, YM + 0.1, 0], POS, 6).set_stroke(opacity=a)
        inf = L([XC - 0.4, YM - 0.1, 0], [XC + 0.4, YM - 0.1, 0], NEG, 6).set_stroke(opacity=a)
        return m.VGroup(sup, inf)
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


class CircuitoRC(m.Scene):
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
        """Coloca pares (etiqueta, fórmula) en la columna derecha y los muestra uno a uno."""
        col = m.VGroup(*pares).arrange(m.DOWN, aligned_edge=m.LEFT, buff=buff)
        col.move_to([3.8, y, 0]).align_to([0.8, 0, 0], m.LEFT)
        return col

    @staticmethod
    def par(titulo, formula, color=INK, size=34, buff=0.12):
        return m.VGroup(T(titulo, 22, GRAY), MT(formula, size, color)).arrange(m.DOWN, aligned_edge=m.LEFT, buff=buff)

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
        t2 = T("Parte 1: el circuito RC — carga y descarga del capacitor", 30, GRAY).move_to([0, -1.4, 0])
        P = mapa(-1.6, -3.1, 0.65, 0.8)
        cv = curva(P, lambda t: 1 - np.exp(-t), 0, 5, NEG, 5)
        ax = m.VGroup(L(P(0, 0), P(5.1, 0), GRAY, 2), L(P(0, 0), P(0, 1.1), GRAY, 2))
        self.play(*[m.FadeIn(b) for b in bloque], m.FadeIn(uni), m.FadeIn(dep), m.FadeIn(cur), m.Create(sep),
                  run_time=1.4)
        self.play(m.FadeIn(t1, shift=m.UP * 0.3), run_time=1.0)
        self.play(m.FadeIn(t2), m.Create(ax), run_time=1.0)
        self.play(m.Create(cv), run_time=1.2)
        self.wait(2.0)
        self.limpiar()

    # ================= 2. El circuito RC =================
    def escena_circuito(self):
        self.titulo("El circuito RC")
        circ = circuito("general")
        hoja = cuchilla("b")
        self.play(m.Create(circ[1]), m.FadeIn(circ[0]), m.FadeIn(circ[2]), m.Create(hoja), run_time=1.6)
        self.play(m.FadeIn(circ[3]), run_time=0.8)

        p1 = self.par("Un solo elemento que almacena energía (C):", r"\Rightarrow\ \text{ecuación diferencial de primer orden}", size=30)
        p2 = self.par("La incógnita para t ≥ 0:", r"v_C(t)\ \text{(tensión del capacitor)}", NEG, 30)
        p3 = self.par("La tensión del capacitor no cambia de golpe:", r"v_C(0^+)=v_C(0^-)", TITLE, 38, 0.2)
        col = self.panel([p1, p2, p3], y=0.4, buff=0.5)
        caja = m.SurroundingRectangle(p3[1], buff=0.15, color=TITLE, stroke_width=2)
        self.pie("En t = 0 el interruptor cambia de posición: en a conecta la fuente, en b la retira", 24)
        self.play(m.Transform(hoja, cuchilla("a")), run_time=0.8)
        self.wait(0.6)
        self.play(m.Transform(hoja, cuchilla("b")), run_time=0.8)
        for p in (p1, p2):
            self.play(m.FadeIn(p, shift=m.RIGHT * 0.2), run_time=0.9)
            self.wait(1.4)
        self.play(m.FadeIn(p3, shift=m.RIGHT * 0.2), m.Create(caja), run_time=1.0)
        self.pie("0⁻: justo antes de la conmutación;  0⁺: justo después", 26)
        self.wait(2.5)
        self.limpiar()

    # ================= 3. Ecuación diferencial =================
    def escena_ecuacion(self):
        self.titulo("Planteamiento: la ecuación diferencial")
        circ = circuito("general")
        hoja = cuchilla("a")
        fi = flecha_i()
        self.play(m.FadeIn(circ), m.FadeIn(hoja), run_time=1.0)
        self.play(m.FadeIn(fi), run_time=0.6)
        self.pie("Para t ≥ 0, con el interruptor en a, la malla contiene la fuente, R y C", 24)

        p1 = self.par("Ley de Kirchhoff de tensiones en la malla:", r"v_s(t)=R\,i+v_C")
        p2 = self.par("Corriente del capacitor:", r"i=C\,\frac{dv_C}{dt}")
        p3 = self.par("Sustituyendo:", r"RC\,\frac{dv_C}{dt}+v_C=v_s(t)")
        p4 = self.par("Con la constante de tiempo τ = RC:", r"\tau\,\frac{dv_C}{dt}+v_C=v_s(t)", TITLE, 38, 0.2)
        col = self.panel([p1, p2, p3, p4], y=0.35, buff=0.3)
        caja = m.SurroundingRectangle(p4[1], buff=0.15, color=TITLE, stroke_width=2)
        for p in (p1, p2, p3):
            self.play(m.FadeIn(p, shift=m.RIGHT * 0.2), run_time=0.9)
            self.wait(1.3)
        self.play(m.FadeIn(p4, shift=m.RIGHT * 0.2), m.Create(caja), run_time=1.0)
        self.pie("Ecuación diferencial lineal de primer orden con coeficientes constantes", 24)
        self.wait(2.0)
        uni = MT(r"[\tau]=\Omega\cdot\mathrm{F}=\frac{\mathrm{V}}{\mathrm{A}}\cdot\frac{\mathrm{C}}{\mathrm{V}}"
                 r"=\frac{\mathrm{C}}{\mathrm{A}}=\mathrm{s}", 30, GREEN).move_to([XC - 2.2, -2.45, 0])
        self.play(m.FadeIn(uni), run_time=0.8)
        self.pie("τ se mide en segundos: fija la escala de tiempo del circuito", 26)
        self.wait(2.5)
        self.limpiar()

    # ================= 4. Solución general =================
    def escena_solucion_general(self):
        self.titulo("Solución general: respuesta natural + respuesta forzada")
        f0 = MT(r"v_C(t)=v_h(t)+v_p(t)", 48, TITLE).move_to([0, 2.45, 0])
        self.play(m.FadeIn(f0, shift=m.UP * 0.2), run_time=1.0)
        self.pie("La solución es la suma de la homogénea (natural) y una particular (forzada)", 24)
        self.wait(1.0)

        izq = m.VGroup(
            T("Respuesta natural (homogénea)", 26, GREEN),
            MT(r"\tau\,\frac{dv_h}{dt}+v_h=0", 32),
            MT(r"\text{Se propone } v_h=K\,e^{st}:", 28, GRAY),
            MT(r"\tau s+1=0\ \Rightarrow\ s=-\frac{1}{\tau}", 32),
            MT(r"v_h(t)=K\,e^{-t/\tau}", 38, GREEN),
        ).arrange(m.DOWN, aligned_edge=m.LEFT, buff=0.22).move_to([-3.6, 0.0, 0])
        der = m.VGroup(
            T("Respuesta forzada (particular)", 26, FIELD),
            T("Tiene la forma de la fuente:", 22, GRAY),
            MT(r"\text{DC: } v_s=V_0\ \Rightarrow\ v_p=\text{constante}", 30),
            MT(r"\text{AC: } v_s=V_m\cos\omega t\ \Rightarrow\ v_p\ \text{senoidal de la misma }\omega", 30),
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
        k2 = MT(r"v_C(0^+)=v_p(0^+)+K\ \Rightarrow\ K=v_C(0^+)-v_p(0^+)", 36).move_to([0, 0.75, 0])
        fin = MT(r"v_C(t)=v_p(t)+\big[v_C(0^+)-v_p(0^+)\big]\,e^{-t/\tau},\qquad t\ge 0", 42, TITLE).move_to([0, -0.6, 0])
        caja = m.SurroundingRectangle(fin, buff=0.25, color=TITLE, stroke_width=2)
        notas = m.VGroup(
            T("respuesta forzada (permanente)", 22, FIELD), T("respuesta transitoria", 22, GREEN),
        ).arrange(m.RIGHT, buff=2.2).move_to([0.6, -1.75, 0])
        self.play(m.FadeIn(k1), run_time=0.6)
        self.play(m.FadeIn(k2, shift=m.UP * 0.15), run_time=1.0)
        self.wait(1.5)
        self.play(m.FadeIn(fin), m.Create(caja), run_time=1.2)
        self.play(m.FadeIn(notas), run_time=0.8)
        self.pie("El término exponencial es transitorio: prácticamente desaparece después de unos 5τ", 24)
        self.wait(3.0)
        self.limpiar()

    # ================= 5. DC: carga =================
    def escena_dc_carga(self):
        self.titulo("Caso DC: carga del capacitor")
        circ = circuito("dc")
        hoja = cuchilla("b")
        self.play(m.FadeIn(circ), m.FadeIn(hoja), run_time=1.0)
        self.pie("Para t < 0 el interruptor está en b y el capacitor está descargado", 26)

        p1 = self.par("Condición inicial:", r"v_C(0^-)=0\ \Rightarrow\ v_C(0^+)=0")
        p2 = self.par("Fuente constante: la particular es constante", r"0+v_p=V_0\ \Rightarrow\ v_p=V_0")
        p3 = self.par("En la solución general:", r"v_C(t)=V_0+(0-V_0)\,e^{-t/\tau}")
        p4 = m.VGroup(T("Tensión y corriente para t ≥ 0:", 22, GRAY),
                      MT(r"v_C(t)=V_0\big(1-e^{-t/\tau}\big)", 32, TITLE),
                      MT(r"i(t)=C\frac{dv_C}{dt}=\frac{V_0}{R}\,e^{-t/\tau}", 32, TITLE)).arrange(
            m.DOWN, aligned_edge=m.LEFT, buff=0.28)
        col = self.panel([p1, p2, p3, p4], y=0.3, buff=0.3)
        caja = m.SurroundingRectangle(m.VGroup(p4[1], p4[2]), buff=0.12, color=TITLE, stroke_width=2)
        self.play(m.Transform(hoja, cuchilla("a")), run_time=0.8)
        self.play(m.FadeIn(flecha_i()), run_time=0.5)
        for p in (p1, p2, p3):
            self.play(m.FadeIn(p, shift=m.RIGHT * 0.2), run_time=0.9)
            self.wait(1.3)
        self.play(m.FadeIn(p4, shift=m.RIGHT * 0.2), m.Create(caja), run_time=1.0)
        self.pie("Con R = 1 kΩ y C = 1 mF:  τ = RC = 1 s  y  V₀ / R = 10 mA", 26)
        self.wait(3.0)
        self.limpiar()

    def escena_dc_carga_grafica(self):
        self.titulo("Carga del capacitor: tensión y corriente")
        circ = circuito("dc")
        hoja = cuchilla("b")
        fi = flecha_i()
        tT = m.ValueTracker(0)
        self.play(m.FadeIn(circ), m.FadeIn(hoja), run_time=0.8)

        Pv = mapa(1.3, 0.5, 0.95, 2.0 / V0)
        Pi = mapa(1.3, -2.5, 0.95, 1.5 / 10)
        tk = [(1.3 + 0.95 * k, rf"{k}\tau" if k > 1 else r"\tau") for k in range(1, 6)]
        ev = ejes(1.3, 0.5, 5.4, 2.35, 0, "v_C(t)", NEG, tk)
        ei = ejes(1.3, -2.5, 5.4, 1.75, 0, "i(t)", POS, tk)
        ref = m.VGroup(m.DashedLine(Pv(0, V0), Pv(5.2, V0), color=LINEC, stroke_width=2),
                       MT("V_0", 26, NEG).move_to(Pv(0, V0) + np.array([-0.35, 0, 0])),
                       MT(r"\frac{V_0}{R}", 24, POS).move_to(Pi(0, 10) + np.array([-0.4, 0, 0])))
        self.play(m.FadeIn(ev), m.FadeIn(ei), m.FadeIn(ref), run_time=1.0)

        fv = lambda t: V0 * (1 - np.exp(-t))
        fc = lambda t: 10 * np.exp(-t)

        def curvas():
            t = tT.get_value()
            g = m.VGroup(curva(Pv, fv, 0, t, NEG), m.Dot(Pv(t, fv(t)), radius=0.07, color=NEG))
            if t > 0:
                g.add(curva(Pi, fc, 0, t, POS), m.Dot(Pi(t, fc(t)), radius=0.07, color=POS))
            return g

        def lectura():
            t = tT.get_value()
            i = fc(t) if t > 0 else 0.0
            partes = []
            for sim, val, uni in (("t", t, "s"), ("v_C", fv(t), "V"), ("i", i, "mA")):
                partes.append(m.VGroup(MT(sim + "=", 30, GRAY), T(f"{coma(val, 2)} {uni}", 26, GRAY)).arrange(
                    m.RIGHT, buff=0.1))
            return m.VGroup(*partes).arrange(m.RIGHT, buff=0.6).move_to([-3.6, -2.45, 0])

        lv = ecuacion(r"v_C(t)=V_0\big(1-e^{-t/\tau}\big)", NEG, Pv(3.5, 6.3))
        li = ecuacion(r"i(t)=\frac{V_0}{R}\,e^{-t/\tau}", POS, Pi(3.5, 5.5))
        self.pie("Estas son las expresiones que vamos a graficar", 26)
        self.play(m.FadeIn(lv, shift=m.UP * 0.15), run_time=0.8)
        self.play(m.FadeIn(li, shift=m.UP * 0.15), run_time=0.8)
        self.wait(1.2)

        self.add(placas_cargadas(lambda: fv(tT.get_value()) / V0))
        self.add(m.always_redraw(curvas), m.always_redraw(lectura))
        self.pie("En t = 0 el interruptor pasa a a: los puntos rojos muestran la corriente", 24)
        self.play(m.Transform(hoja, cuchilla("a")), m.FadeIn(fi), run_time=0.6)
        self.add(corriente_animada(RUTA_CARGA, {3}, lambda: np.exp(-tT.get_value())))
        self.play(tT.animate.set_value(5.0), run_time=9.0, rate_func=m.linear)
        self.pie("La corriente salta a V₀ / R en t = 0⁺, pero la tensión del capacitor parte de 0", 24)
        self.wait(3.0)
        self.pie("En régimen permanente i = 0: en DC el capacitor se comporta como circuito abierto", 24)
        self.wait(3.0)
        self.limpiar()

    # ================= 6. Constante de tiempo =================
    def escena_tau(self):
        self.titulo("La constante de tiempo τ")
        P = mapa(-5.6, -2.3, 2.0, 4.6 / 100)
        tk = [(-5.6 + 2 * k, rf"{k}\tau" if k > 1 else r"\tau") for k in range(1, 6)]
        ex = ejes(-5.6, -2.3, 11.0, 5.2, 0, r"v_C/V_0", NEG, tk)
        ref = m.VGroup(m.DashedLine(P(0, 100), P(5.3, 100), color=LINEC, stroke_width=2),
                       T("100 %", 22, GRAY).move_to(P(0, 100) + np.array([-0.55, 0, 0])))
        self.play(m.FadeIn(ex), m.FadeIn(ref), run_time=1.0)
        f = lambda t: 100 * (1 - np.exp(-t))
        eq = ecuacion(r"\frac{v_C(t)}{V_0}=1-e^{-t/\tau}", NEG, [P(3.5, 0)[0], 2.85, 0], 32)
        self.play(m.FadeIn(eq, shift=m.UP * 0.15), run_time=0.8)
        self.play(m.Create(curva(P, f, 0, 5.3, NEG)), run_time=2.5)

        tang = m.DashedLine(P(0, 0), P(1, 100), color=FIELD, stroke_width=3)
        self.pie("La tangente en t = 0 alcanza el valor final justo en t = τ", 26)
        self.play(m.Create(tang), run_time=1.2)
        self.wait(1.5)

        puntos = []
        for k in range(1, 6):
            v = f(k)
            puntos.append(m.VGroup(
                m.DashedLine(P(k, 0), P(k, v), color=LINEC, stroke_width=2),
                m.Dot(P(k, v), radius=0.08, color=NEG),
                T(f"{coma(v, 1)} %", 22, NEG).move_to(P(k, v) + np.array([0.6, -0.32, 0])),
            ))
        self.pie("En t = τ el capacitor alcanza el 63,2 % de su valor final", 26)
        self.play(m.FadeIn(puntos[0]), run_time=0.8)
        self.wait(1.5)
        self.play(*[m.FadeIn(p) for p in puntos[1:]], run_time=1.5, lag_ratio=0.3)
        self.pie("Después de unos 5τ (99,3 %) se considera que el transitorio terminó", 26)
        self.wait(3.0)
        self.limpiar()

    # ================= 7. DC: descarga =================
    def escena_dc_descarga(self):
        self.titulo("Caso DC: descarga del capacitor")
        circ = circuito("dc")
        hoja = cuchilla("a")
        self.play(m.FadeIn(circ), m.FadeIn(hoja), m.FadeIn(flecha_i()), run_time=1.0)
        self.pie("Capacitor cargado a V₀; en t = 0 el interruptor pasa a b y retira la fuente", 24)
        self.play(m.Transform(hoja, cuchilla("b")), run_time=0.8)

        p1 = self.par("Condición inicial:", r"v_C(0^-)=V_0\ \Rightarrow\ v_C(0^+)=V_0")
        p2 = self.par("Sin fuente en la malla: la particular es cero", r"\tau\frac{dv_C}{dt}+v_C=0\ \Rightarrow\ v_p=0")
        p3 = self.par("Tensión y corriente para t ≥ 0:",
                      r"v_C(t)=V_0\,e^{-t/\tau},\quad i(t)=C\frac{dv_C}{dt}=-\frac{V_0}{R}\,e^{-t/\tau}", TITLE, 30, 0.2)
        col = self.panel([p1, p2, p3], y=0.5, buff=0.4)
        caja = m.SurroundingRectangle(p3[1], buff=0.12, color=TITLE, stroke_width=2)
        for p in (p1, p2):
            self.play(m.FadeIn(p, shift=m.RIGHT * 0.2), run_time=0.9)
            self.wait(1.3)
        self.play(m.FadeIn(p3, shift=m.RIGHT * 0.2), m.Create(caja), run_time=1.0)
        self.pie("El signo − indica que la corriente circula en sentido contrario a la referencia", 24)
        self.wait(2.5)
        self.play(m.FadeOut(col), m.FadeOut(caja), run_time=0.6)

        tT = m.ValueTracker(0)
        Pv = mapa(1.3, 0.5, 0.95, 2.0 / V0)
        Pi = mapa(1.3, -0.95, 0.95, 1.5 / 10)
        tk = [(1.3 + 0.95 * k, rf"{k}\tau" if k > 1 else r"\tau") for k in range(1, 6)]
        ev = ejes(1.3, 0.5, 5.4, 2.35, 0, "v_C(t)", NEG, tk)
        ei = ejes(1.3, -0.95, 5.4, 0.35, 1.7, "i(t)", POS)
        ref = m.VGroup(MT("V_0", 26, NEG).move_to(Pv(0, V0) + np.array([-0.35, 0, 0])),
                       MT(r"-\frac{V_0}{R}", 24, POS).move_to(Pi(0, -10) + np.array([-0.5, 0, 0])))
        self.play(m.FadeIn(ev), m.FadeIn(ei), m.FadeIn(ref), run_time=1.0)
        fv = lambda t: V0 * np.exp(-t)
        fc = lambda t: -10 * np.exp(-t)

        def curvas():
            t = tT.get_value()
            return m.VGroup(curva(Pv, fv, 0, t, NEG), m.Dot(Pv(t, fv(t)), radius=0.07, color=NEG),
                            curva(Pi, fc, 0, t, POS), m.Dot(Pi(t, fc(t)), radius=0.07, color=POS))

        lv = ecuacion(r"v_C(t)=V_0\,e^{-t/\tau}", NEG, Pv(3.5, 5.0))
        li = ecuacion(r"i(t)=-\frac{V_0}{R}\,e^{-t/\tau}", POS, Pi(3.5, -6.0))
        self.play(m.FadeIn(lv, shift=m.UP * 0.15), run_time=0.8)
        self.play(m.FadeIn(li, shift=m.UP * 0.15), run_time=0.8)
        self.wait(1.0)

        self.add(placas_cargadas(lambda: fv(tT.get_value()) / V0))
        self.add(m.always_redraw(curvas))
        self.add(corriente_animada(RUTA_DESCARGA, set(), lambda: np.exp(-tT.get_value())))
        self.pie("La corriente sale de la placa positiva y recorre R en sentido contrario a la referencia", 24)
        self.play(tT.animate.set_value(5.0), run_time=8.0, rate_func=m.linear)
        self.pie("Toda la energía almacenada, ½ C V₀², se disipa como calor en la resistencia", 24)
        self.wait(3.0)
        self.limpiar()

    # ================= 8. Receta DC =================
    def escena_receta_dc(self):
        self.titulo("En DC: la fórmula práctica")
        f = MT(r"v_C(t)=v_C(\infty)+\big[v_C(0^+)-v_C(\infty)\big]\,e^{-t/\tau}", 46, TITLE).move_to([0, 2.3, 0])
        caja = m.SurroundingRectangle(f, buff=0.25, color=TITLE, stroke_width=2)
        self.play(m.FadeIn(f), m.Create(caja), run_time=1.2)
        self.pie("En DC la particular es constante: es el valor final de la tensión del capacitor", 24)
        self.wait(1.5)
        pasos = [
            ("1.", r"v_C(0^+):\ \text{con el circuito en } t<0 \text{ y la continuidad } v_C(0^+)=v_C(0^-)"),
            ("2.", r"v_C(\infty):\ \text{régimen permanente, con el capacitor como circuito abierto}"),
            ("3.", r"\tau=R_{eq}\,C:\ R_{eq}\ \text{es la resistencia que ve el capacitor (Thévenin)}"),
        ]
        filas = m.VGroup(*[m.VGroup(T(n, 26, TITLE), MT(s, 30)).arrange(m.RIGHT, buff=0.25) for n, s in pasos])
        filas.arrange(m.DOWN, aligned_edge=m.LEFT, buff=0.3).move_to([0, 0.55, 0])
        for fl in filas:
            self.play(m.FadeIn(fl, shift=m.RIGHT * 0.2), run_time=0.8)
            self.wait(1.2)

        xs = (-3.0, 0.4, 3.4)
        cab = m.VGroup(T("Caso", 22, GRAY).move_to([xs[0], -0.85, 0]), MT(r"v_C(0^+)", 30, GRAY).move_to([xs[1], -0.85, 0]),
                       MT(r"v_C(\infty)", 30, GRAY).move_to([xs[2], -0.85, 0]))
        lin = L([-4.4, -1.15, 0], [4.6, -1.15, 0], LINEC, 2)
        f1 = m.VGroup(T("Carga", 26).move_to([xs[0], -1.5, 0]), MT("0", 32).move_to([xs[1], -1.5, 0]),
                      MT("V_0", 32).move_to([xs[2], -1.5, 0]))
        f2 = m.VGroup(T("Descarga", 26).move_to([xs[0], -2.15, 0]), MT("V_0", 32).move_to([xs[1], -2.15, 0]),
                      MT("0", 32).move_to([xs[2], -2.15, 0]))
        self.play(m.FadeIn(cab), m.Create(lin), run_time=0.7)
        self.play(m.FadeIn(f1, shift=m.UP * 0.1), run_time=0.7)
        self.play(m.FadeIn(f2, shift=m.UP * 0.1), run_time=0.7)
        self.pie("Carga y descarga son dos casos de la misma fórmula", 26)
        self.wait(3.0)
        self.limpiar()

    # ================= 9. AC: planteamiento =================
    def escena_ac_planteamiento(self):
        self.titulo("Caso AC: fuente senoidal")
        circ = circuito("ac")
        hoja = cuchilla("b")
        self.play(m.FadeIn(circ), m.FadeIn(hoja), run_time=1.0)
        self.play(m.Transform(hoja, cuchilla("a")), m.FadeIn(flecha_i()), run_time=0.8)

        p1 = self.par("Fuente para t ≥ 0:", r"v_s(t)=V_m\cos(\omega t)")
        p2 = self.par("Capacitor inicialmente descargado:", r"v_C(0^+)=v_C(0^-)=0")
        p3 = self.par("Ecuación:", r"\tau\,\frac{dv_C}{dt}+v_C=V_m\cos(\omega t)")
        p4 = self.par("Particular de la misma frecuencia:",
                      r"v_p(t)=A\cos(\omega t)+B\sin(\omega t)", TITLE, 34, 0.2)
        col = self.panel([p1, p2, p3, p4], y=0.35, buff=0.32)
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
                      r"\big(B-\omega\tau A\big)\sin(\omega t)+\big(A+\omega\tau B\big)\cos(\omega t)=V_m\cos(\omega t)")
        p2 = self.par("Igualando coeficientes de seno y coseno:",
                      r"B-\omega\tau A=0,\qquad A+\omega\tau B=V_m")
        p3 = self.par("Resolviendo:",
                      r"A=\frac{V_m}{1+(\omega\tau)^2},\qquad B=\frac{\omega\tau\,V_m}{1+(\omega\tau)^2}")
        col = m.VGroup(p1, p2, p3).arrange(m.DOWN, aligned_edge=m.LEFT, buff=0.45).move_to([0, 0.4, 0])
        col.align_to([-6.6, 0, 0], m.LEFT)
        for p in (p1, p2, p3):
            self.play(m.FadeIn(p, shift=m.RIGHT * 0.2), run_time=1.0)
            self.wait(1.8)
        self.pie("Dos ecuaciones algebraicas para dos incógnitas, A y B", 26)
        self.wait(1.5)
        self.play(m.FadeOut(col), run_time=0.6)

        q1 = self.par("En forma de amplitud y fase:",
                      r"v_p(t)=\frac{V_m}{\sqrt{1+(\omega\tau)^2}}\cos(\omega t-\varphi),\qquad \varphi=\arctan(\omega\tau)")
        q2 = m.VGroup(
            MT(r"\text{Con } v_C(0^+)=0,\ \text{la constante es } K=-v_p(0)=-\frac{V_m}{1+(\omega\tau)^2}:", 28, GRAY),
            MT(r"v_C(t)=\frac{V_m}{\sqrt{1+(\omega\tau)^2}}\cos(\omega t-\varphi)-\frac{V_m}{1+(\omega\tau)^2}\,e^{-t/\tau}",
               36, TITLE)).arrange(m.DOWN, aligned_edge=m.LEFT, buff=0.3)
        col2 = m.VGroup(q1, q2).arrange(m.DOWN, aligned_edge=m.LEFT, buff=0.6).move_to([0, 0.7, 0])
        col2.align_to([-6.6, 0, 0], m.LEFT)
        caja = m.SurroundingRectangle(q2[1], buff=0.15, color=TITLE, stroke_width=2)
        notas = m.VGroup(
            T("respuesta forzada (permanente)", 22, FIELD), T("respuesta transitoria", 22, GREEN),
        ).arrange(m.RIGHT, buff=1.2).next_to(caja, m.DOWN, buff=0.2)
        self.play(m.FadeIn(q1, shift=m.RIGHT * 0.2), run_time=1.0)
        self.pie("La tensión del capacitor tiene menor amplitud y va retrasada φ respecto a la fuente", 24)
        self.wait(2.5)
        self.play(m.FadeIn(q2, shift=m.RIGHT * 0.2), m.Create(caja), run_time=1.2)
        self.play(m.FadeIn(notas), run_time=0.6)
        self.pie("Misma estructura que en DC: forzada + transitorio que se extingue en unos 5τ", 24)
        self.wait(3.5)
        self.limpiar()

    # ================= 11. AC: gráfica =================
    def escena_ac_grafica(self):
        self.titulo("Caso AC: conexión y desconexión de la fuente")
        t1 = 4 * np.pi                      # se desconecta tras dos periodos (ωτ = 1  ->  T = 2πτ)
        tf = t1 + 5.0
        P = mapa(-6.4, 0.25, 12.4 / tf, 1.9)
        ex = ejes(-6.4, 0.25, 12.9, 2.25, 2.05, r"v/V_m,\ i/I_m", INK)
        a = 1 / np.sqrt(2)
        v1 = a * np.cos(t1 - np.pi / 4) - 0.5 * np.exp(-t1)

        def fs(t):
            return np.cos(t)

        def ftr(t):
            return -0.5 * np.exp(-t)

        def fc(t):
            return a * np.cos(t - np.pi / 4) + ftr(t) if t < t1 else v1 * np.exp(-(t - t1))

        def fi(t):
            # i_C = C dv_C/dt, normalizada con I_m = V_m/R (con ωτ = 1, ωC = 1/R)
            return a * np.cos(t + np.pi / 4) + 0.5 * np.exp(-t) if t < t1 else -v1 * np.exp(-(t - t1))

        marcas = m.VGroup(
            m.DashedLine(P(t1, -1.0), P(t1, 0.98), color=LINEC, stroke_width=2),
            T("b: se retira la fuente", 20, GRAY).move_to(P(t1, -1.15) + np.array([0.2, 0, 0])),
            T("a: se conecta", 20, GRAY).move_to(P(0, -1.15) + np.array([0.95, 0, 0])),
        )
        ley = m.VGroup(
            m.VGroup(L([0, 0, 0], [0.5, 0, 0], GRAY, 3), MT(r"v_s(t)=V_m\cos(\omega t)", 26, GRAY)).arrange(m.RIGHT, buff=0.15),
            m.VGroup(L([0, 0, 0], [0.5, 0, 0], NEG, 5), MT("v_C(t)", 26, NEG)).arrange(m.RIGHT, buff=0.15),
            m.VGroup(L([0, 0, 0], [0.5, 0, 0], POS, 4), MT("i_C(t)", 26, POS)).arrange(m.RIGHT, buff=0.15),
            m.VGroup(L([0, 0, 0], [0.5, 0, 0], FIELD, 3), MT(r"\text{transitorio de } v_C", 26, FIELD)
                     ).arrange(m.RIGHT, buff=0.15),
            MT(r"\omega\tau=1,\ \ I_m=V_m/R", 26, GRAY),
        ).arrange(m.RIGHT, buff=0.45).move_to([0, -2.45, 0])
        eq_c = ecuacion(r"v_C(t)=\frac{V_m}{\sqrt{2}}\cos\big(\omega t-45^\circ\big)-\frac{V_m}{2}\,e^{-t/\tau}",
                        NEG, [0, 2.62, 0], 24)
        eq_c.align_to([6.8, 0, 0], m.RIGHT)
        eq_i = ecuacion(r"i_C(t)=\frac{I_m}{\sqrt{2}}\cos\big(\omega t+45^\circ\big)+\frac{I_m}{2}\,e^{-t/\tau}",
                        POS, [0, 2.62, 0], 24)
        eq_i.next_to(eq_c, m.LEFT, buff=0.25)
        self.play(m.FadeIn(ex), m.FadeIn(marcas), run_time=0.8)
        self.pie("Expresiones que se grafican: tensión y corriente del capacitor", 26)
        self.play(m.FadeIn(ley[0]), m.FadeIn(ley[4]), run_time=0.7)
        self.play(m.FadeIn(eq_c, shift=m.DOWN * 0.15), m.FadeIn(ley[1]), m.FadeIn(ley[3]), run_time=0.8)
        self.wait(0.8)
        self.pie("La corriente del capacitor sale de derivar su tensión: C dv/dt", 26)
        self.play(m.FadeIn(eq_i, shift=m.DOWN * 0.15), m.FadeIn(ley[2]), run_time=0.8)
        self.wait(1.5)
        tT = m.ValueTracker(0)

        def curvas():
            t = tT.get_value()
            g = m.VGroup(curva(P, fs, 0, min(t, t1), GRAY, 3))
            tr = curva(P, ftr, 0, min(t, 6.0), FIELD, 3)
            g.add(m.DashedVMobject(tr, num_dashes=30))
            g.add(curva(P, fi, 0, t, POS, 4, 500), m.Dot(P(t, fi(t)), radius=0.07, color=POS))
            g.add(curva(P, fc, 0, t, NEG, 5, 500), m.Dot(P(t, fc(t)), radius=0.07, color=NEG))
            return g

        self.add(m.always_redraw(curvas))
        self.pie("Al conectar: la corriente salta de inmediato, mientras la tensión parte de 0", 24)
        self.play(tT.animate.set_value(6.0), run_time=4.0, rate_func=m.linear)
        self.pie("Régimen permanente: la corriente del capacitor va 90° adelantada respecto a su tensión", 24)
        self.play(tT.animate.set_value(t1), run_time=4.0, rate_func=m.linear)
        self.pie("Al retirar la fuente: la tensión decae sin saltos; la corriente se invierte de golpe", 24)
        fd = ecuacion(r"v_C(t)=v_C(t_1)\,e^{-(t-t_1)/\tau}", NEG, P(t1 + 2.6, 0.75))
        fdi = ecuacion(r"i_C(t)=-\frac{v_C(t_1)}{R}\,e^{-(t-t_1)/\tau}", POS, P(t1 + 2.6, -0.75))
        self.play(m.FadeIn(fd, shift=m.UP * 0.15), m.FadeIn(fdi, shift=m.UP * 0.15), run_time=0.7)
        self.play(tT.animate.set_value(tf), run_time=3.5, rate_func=m.linear)
        self.wait(3.0)
        self.limpiar()

    # ================= 12. Resumen =================
    def escena_resumen(self):
        self.titulo("Resumen")
        pts = [
            r"\text{Planteamiento: LKT y } i=C\,\frac{dv_C}{dt}\ \Rightarrow\ \tau\,\frac{dv_C}{dt}+v_C=v_s(t),\ \ \tau=RC",
            r"\text{Solución: } v_C=v_h+v_p,\ \text{con } v_h=K\,e^{-t/\tau}\ \text{(respuesta natural)}",
            r"K\ \text{sale de la condición inicial, usando } v_C(0^+)=v_C(0^-)",
            r"\text{DC: } v_C(t)=v_C(\infty)+\big[v_C(0^+)-v_C(\infty)\big]\,e^{-t/\tau}",
            r"\text{AC: } v_p\ \text{senoidal de la misma } \omega,\ \text{amplitud } \frac{V_m}{\sqrt{1+(\omega\tau)^2}},"
            r"\ \varphi=\arctan(\omega\tau)",
            r"\text{Después de unos } 5\tau \text{ el transitorio desaparece y queda el régimen permanente}",
        ]
        items = []
        for i, s in enumerate(pts):
            num = T(str(i + 1), 26, "#FFFFFF")
            circ = m.Circle(radius=0.24, fill_color=TITLE, fill_opacity=1, stroke_width=0)
            marca = m.VGroup(circ, num.move_to(circ.get_center()))
            items.append(m.VGroup(marca, MT(s, 30)).arrange(m.RIGHT, buff=0.3))
        col = m.VGroup(*items).arrange(m.DOWN, aligned_edge=m.LEFT, buff=0.3).move_to([0, 0.1, 0])
        for row in items:
            self.play(m.FadeIn(row, shift=m.RIGHT * 0.25), run_time=0.9)
            self.wait(1.4)
        self.wait(2.5)
        self.limpiar(1.0)


if __name__ == "__main__":
    os.makedirs(SALIDA, exist_ok=True)
    CircuitoRC().render(VIDEO)
    print("Video guardado en:", VIDEO)
