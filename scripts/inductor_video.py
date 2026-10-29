import os

import numpy as np
import manimgx as m

# Fondo blanco (debe fijarse antes de construir la escena)
m.config.background_color = "#FFFFFF"

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
FIGURAS = os.path.join(RAIZ, "figuras")
SALIDA = os.path.join(RAIZ, "videos_salida")
VIDEO = os.path.join(SALIDA, "inductor.mp4")

# ---------------- Paleta (fondo blanco) ----------------
INK = "#1F2933"
GRAY = "#6B7280"
TITLE = "#0B3C5D"
POS = "#D32F2F"
NEG = "#1565C0"
GREEN = "#2E7D32"
MAG = "#7B1FA2"        # campo magnético B
COPPER = "#B8731F"     # espiras de cobre
CORE = "#90A4AE"       # núcleo
CORE_T = "#455A64"
CARD = "#F3F4F6"
LINEC = "#D1D5DB"

# ---------------- Identificación institucional ----------------
UNIVERSIDAD = "Universidad de Antioquia"
DEPARTAMENTO = "Departamento de Ingeniería Electrónica y de Telecomunicaciones"
CURSO = "Circuitos Eléctricos I"

# ---------------- Geometría de la bobina ----------------
SX, SY = -2.6, 0.7     # centro
SW, SR, NT = 4.0, 0.75, 10   # longitud, radio, número de espiras
YW = -1.5              # y del cable inferior del circuito
V0 = 9.0               # V (fuente)
R0 = 9.0               # Ω
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


def flecha(p0, p1, color=MAG, sw=4, head=0.17):
    p0, p1 = np.array(p0, float), np.array(p1, float)
    d = (p1 - p0) / np.linalg.norm(p1 - p0)
    n = np.array([-d[1], d[0], 0.0])
    return m.VGroup(L(p0, p1, color, sw),
                    L(p1, p1 - head * d + 0.09 * n, color, sw), L(p1, p1 - head * d - 0.09 * n, color, sw))


def doble(p0, p1, color=GRAY, sw=3, head=0.16):
    p0, p1 = np.array(p0, float), np.array(p1, float)
    d = (p1 - p0) / np.linalg.norm(p1 - p0)
    n = np.array([-d[1], d[0], 0.0])
    return m.VGroup(
        L(p0, p1, color, sw),
        L(p0, p0 + head * d + 0.08 * n, color, sw), L(p0, p0 + head * d - 0.08 * n, color, sw),
        L(p1, p1 - head * d + 0.08 * n, color, sw), L(p1, p1 - head * d - 0.08 * n, color, sw),
    )


def espira(x, cy, r, color=COPPER, sw=4, w=0.3):
    """Una vuelta vista de lado: mitad trasera tenue, mitad delantera sólida."""
    def media(t0, t1):
        return m.ParametricFunction(lambda t: np.array([x + w / 2 * np.cos(t), cy + r * np.sin(t), 0.0]),
                                    t_range=[t0, t1, 0.05], color=color, stroke_width=sw, fill_opacity=0)
    atras = media(np.pi / 2, 3 * np.pi / 2).set_stroke(opacity=0.35)
    return m.VGroup(atras, media(-np.pi / 2, np.pi / 2))


def xs_espiras(cx, largo, n):
    return [cx - largo / 2 + (i + 0.5) * largo / n for i in range(n)]


def bobina(cx=SX, cy=SY, largo=SW, r=SR, n=NT, sw=4):
    return m.VGroup(*[espira(x, cy, r, sw=sw) for x in xs_espiras(cx, largo, n)])


def campo_interior(cx=SX, cy=SY, largo=SW, ys=(-0.45, 0.0, 0.45), color=MAG, sw=4):
    return m.VGroup(*[flecha([cx - largo / 2 + 0.25, cy + y, 0], [cx + largo / 2 - 0.25, cy + y, 0], color, sw)
                      for y in ys])


def retornos(cx=SX, cy=SY, largo=SW, r=SR, color=MAG, sw=2.5):
    """Líneas de campo que regresan por fuera: salen por la derecha y entran por la izquierda."""
    out = []
    for a, b in ((largo / 2 + 0.35, r + 0.5), (largo / 2 + 0.7, r + 0.95)):
        for s in (1, -1):
            arco = m.ParametricFunction(
                lambda u, a=a, b=b, s=s: np.array([cx + a * np.cos(np.pi * u), cy + s * b * np.sin(np.pi * u), 0.0]),
                t_range=[0, 1, 0.02], color=color, stroke_width=sw, fill_opacity=0)
            yb = cy + s * b
            head = m.VGroup(L([cx - 0.07, yb, 0], [cx + 0.09, yb + 0.08, 0], color, sw),
                            L([cx - 0.07, yb, 0], [cx + 0.09, yb - 0.08, 0], color, sw))
            out += [arco, head]
    return m.VGroup(*out)


def resistor(x0, x1, y, picos=6, amp=0.18, color=INK, sw=4):
    dx = (x1 - x0) / picos
    pts = [np.array([x0, y, 0.0])]
    pts += [np.array([x0 + (k + 0.5) * dx, y + amp * (1 if k % 2 == 0 else -1), 0.0]) for k in range(picos)]
    pts.append(np.array([x1, y, 0.0]))
    return m.VMobject(color=color, stroke_width=sw).set_points_as_corners(pts)


def bob_dyn(n, r, largo):
    """Bobina con terminales y campo interior, para valores dinámicos de N, radio y longitud."""
    xs = xs_espiras(SX, largo, n)
    items = [espira(x, SY, r) for x in xs]
    sw = float(np.clip(4.0 * (n / NT) / (largo / SW), 2.5, 12))
    items.append(campo_interior(SX, SY, largo, (-0.45 * r / SR, 0.0, 0.45 * r / SR), MAG, sw))
    for x in (xs[0], xs[-1]):
        items += [L([x, SY - r, 0], [x, SY - r - 0.6, 0], INK, 4), m.Dot([x, SY - r - 0.6, 0], radius=0.07, color=INK)]
    return m.VGroup(*items)


class InductorVideo(m.Scene):
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
        self.escena_corriente()
        self.escena_glosario()
        self.escena_geometria()
        self.escena_nucleo()
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
        t1 = T("El inductor", 70, TITLE).move_to([0, -0.5, 0])
        t2 = T("Campo magnético, flujo y núcleo", 32, GRAY).move_to([0, -1.4, 0])
        bob = bobina(0, -2.75, 2.8, 0.36, 8, sw=3)
        fl = flecha([-1.2, -2.75, 0], [1.2, -2.75, 0], MAG, 3, 0.15)
        self.play(*[m.FadeIn(b) for b in bloque], m.FadeIn(uni), m.FadeIn(dep), m.FadeIn(cur), m.Create(sep),
                  run_time=1.4)
        self.play(m.FadeIn(t1, shift=m.UP * 0.3), run_time=1.0)
        self.play(m.FadeIn(t2), m.Create(bob), run_time=1.0)
        self.play(m.FadeIn(fl), run_time=0.8)
        self.wait(2.0)
        self.limpiar()

    # ================= 2. Qué es =================
    def escena_que_es(self):
        self.titulo("¿Qué es un inductor?")
        xs = xs_espiras(SX, SW, NT)
        nucleo = m.Rectangle(width=SW + 0.5, height=2 * SR * 0.75, fill_color=CORE, fill_opacity=0.25,
                             stroke_width=0).move_to([SX, SY, 0])
        bob = bobina()
        term = m.VGroup(*[m.VGroup(L([x, SY - SR, 0], [x, SY - SR - 0.9, 0]),
                                   m.Dot([x, SY - SR - 0.9, 0], radius=0.07, color=INK)) for x in (xs[0], xs[-1])])
        lab_esp = T("Espiras (N vueltas)", 22, COPPER).move_to([SX, SY - SR - 0.45, 0])
        lab_nuc = T("Núcleo", 22, CORE_T).move_to([SX + SW / 2 + 0.85, SY, 0])
        seccion = m.Ellipse(width=0.3, height=2 * SR, fill_color=MAG, fill_opacity=0.15, stroke_color=MAG,
                            stroke_width=2).move_to([SX - SW / 2 - 0.25, SY, 0])
        lab_A = T("Sección A", 22, GRAY).move_to([SX - SW / 2 - 1.25, SY, 0])
        yl = SY + SR + 0.45
        dimL = doble([SX - SW / 2, yl, 0], [SX + SW / 2, yl, 0])
        txtL = T("Longitud ℓ", 24, GRAY).move_to([SX, yl + 0.4, 0])

        self.play(m.FadeIn(nucleo), m.Create(bob), run_time=1.6)
        self.play(m.FadeIn(term), m.FadeIn(lab_esp), m.FadeIn(lab_nuc), run_time=1.0)
        self.play(m.Create(dimL), m.FadeIn(txtL), m.FadeIn(seccion), m.FadeIn(lab_A), run_time=1.2)

        def punto(color):
            return m.Dot(radius=0.09, color=color)

        b1 = m.VGroup(T("Un conductor enrollado", 28), T("en espiras (bobina)", 28)).arrange(
            m.DOWN, aligned_edge=m.LEFT, buff=0.08)
        b2 = m.VGroup(T("Almacena energía en el", 28), T("campo magnético que crea", 28)).arrange(
            m.DOWN, aligned_edge=m.LEFT, buff=0.08)
        b3 = m.VGroup(T("Inductancia (en henrios, H):", 28), MT(r"L=\frac{\lambda}{i}", 44, TITLE)).arrange(
            m.DOWN, aligned_edge=m.LEFT, buff=0.15)
        panel = m.VGroup(b1, b2, b3).arrange(m.DOWN, aligned_edge=m.LEFT, buff=0.55)
        panel.move_to([4.35, 0.2, 0]).align_to([1.7, 0, 0], m.LEFT)
        marcas = [punto(c).next_to(b, m.LEFT, buff=0.2).align_to(b[0], m.UP).shift(m.DOWN * 0.1)
                  for b, c in ((b1, COPPER), (b2, MAG), (b3, GREEN))]
        campo = campo_interior()
        for b, mk in zip((b1, b2, b3), marcas):
            anims = [m.FadeIn(b, shift=m.RIGHT * 0.2), m.FadeIn(mk)]
            if b is b2:
                anims.append(m.FadeIn(campo))
            self.play(*anims, run_time=1.0)
            self.wait(1.6)
        self.wait(1.0)
        self.limpiar()

    # ================= 2b. Definición y análisis dimensional =================
    def escena_definicion(self):
        self.titulo("Inductancia: definición y análisis dimensional")
        f = MT(r"L=\frac{\lambda}{i}", 84, tex_to_color_map={"L": GREEN, r"\lambda": MAG, "i": POS}).move_to(
            [-4.6, 2.1, 0])
        self.play(m.FadeIn(f, shift=m.UP * 0.2), run_time=1.2)

        filas = [
            ("L", GREEN, "Inductancia (parámetro concentrado), en H"),
            (r"\lambda", MAG, "Enlace de flujo, λ = N Φ, en Wb"),
            ("i", POS, "Corriente por la bobina, en A"),
        ]
        grupo = []
        for i, (sim, col, txt) in enumerate(filas):
            fila = m.VGroup(MT(sim, 40, col), T(txt, 24)).arrange(m.RIGHT, buff=0.3)
            fila.move_to([0, 2.75 - i * 0.6, 0]).align_to([-2.3, 0, 0], m.LEFT)
            grupo.append(fila)
        for fila in grupo:
            self.play(m.FadeIn(fila, shift=m.RIGHT * 0.2), run_time=0.9)
            self.wait(0.7)
        self.pie("λ e i son variables (minúsculas); L es un parámetro concentrado (mayúscula)", 24)
        self.wait(1.5)

        cab = T("Análisis dimensional", 24, GRAY).move_to([-6.8, 0.8, 0], aligned_edge=m.LEFT)
        l1 = MT(r"[L]=\frac{[\lambda]}{[i]}=\frac{\mathrm{Wb}}{\mathrm{A}}=\mathrm{H}", 34).move_to(
            [-6.8, 0.15, 0], aligned_edge=m.LEFT)
        n1 = T("(1 henrio = 1 weber por amperio)", 22, GREEN).move_to([0.4, 0.15, 0], aligned_edge=m.LEFT)
        l2 = MT(r"[\lambda]=\mathrm{Wb}=\mathrm{V\cdot s}=\mathrm{kg\cdot m^{2}\cdot s^{-2}\cdot A^{-1}},"
                r"\qquad [i]=\mathrm{A}", 30).move_to([-6.8, -0.8, 0], aligned_edge=m.LEFT)
        l3 = MT(r"[L]=\frac{\mathrm{kg\cdot m^{2}\cdot s^{-2}\cdot A^{-1}}}{\mathrm{A}}"
                r"=\mathrm{kg\cdot m^{2}\cdot s^{-2}\cdot A^{-2}}", 30).move_to([-6.8, -1.85, 0], aligned_edge=m.LEFT)
        l4 = m.VGroup(T("Dimensiones:", 24, GRAY), MT(r"[L]=\mathrm{M\,L^{2}\,T^{-2}\,I^{-2}}", 30)).arrange(
            m.RIGHT, buff=0.3).move_to([-6.8, -2.7, 0], aligned_edge=m.LEFT)

        self.play(m.FadeIn(cab), m.FadeIn(l1, shift=m.RIGHT * 0.2), run_time=1.2)
        self.play(m.FadeIn(n1), run_time=0.8)
        self.pie("En un inductor, [L] = [λ] / [i]: webers por amperio", 26)
        self.wait(1.5)
        self.play(m.FadeIn(l2, shift=m.RIGHT * 0.2), run_time=1.2)
        self.pie("El weber es V·s: la tensión inducida es la rapidez con que cambia el flujo", 24)
        self.wait(2.0)
        self.play(m.FadeIn(l3, shift=m.RIGHT * 0.2), run_time=1.2)
        self.wait(1.2)
        self.play(m.FadeIn(l4), run_time=0.8)
        self.pie("Resultado: 1 H = 1 V·s/A = kg·m²·s⁻²·A⁻²", 24)
        self.wait(3.0)
        self.limpiar()

    # ================= 3. Corriente y campo =================
    def escena_corriente(self):
        self.titulo("Al conectar la fuente: corriente y campo magnético")
        xs = xs_espiras(SX, SW, NT)
        xf, xl = xs[0], xs[-1]
        xb, xr0, xr1 = -3.4, -2.3, -1.3
        iT = m.ValueTracker(0)

        bob = bobina()
        circuito = m.VGroup(
            L([xf, SY - SR, 0], [xf, YW, 0]), L([xl, SY - SR, 0], [xl, YW, 0]),
            L([xf, YW, 0], [xb - 0.1, YW, 0]), L([xb + 0.1, YW, 0], [xr0, YW, 0]), L([xr1, YW, 0], [xl, YW, 0]),
            L([xb - 0.1, YW - 0.4, 0], [xb - 0.1, YW + 0.4, 0], INK, 6),
            L([xb + 0.1, YW - 0.22, 0], [xb + 0.1, YW + 0.22, 0], INK, 6),
            resistor(xr0, xr1, YW),
        )
        etq = m.VGroup(T("V₀ = 9 V", 22).move_to([xb, YW - 0.65, 0]),
                       T("R = 9 Ω", 22).move_to([(xr0 + xr1) / 2, YW - 0.65, 0]))
        self.play(m.Create(bob), m.Create(circuito), m.FadeIn(etq), run_time=1.8)

        campo = campo_interior()
        campo.add_updater(lambda g: g.set_stroke(opacity=float(iT.get_value())))
        ret = retornos()
        ret.add_updater(lambda g: g.set_stroke(opacity=0.6 * float(iT.get_value())))
        fi = m.VGroup(flecha([xf, YW + 0.25, 0], [xf, YW + 0.85, 0], POS, 4, 0.15),
                      MT("i", 30, POS).move_to([xf - 0.3, YW + 0.55, 0]))
        fi.add_updater(lambda g: g.set_opacity(float(np.clip(4 * iT.get_value(), 0, 1))))
        self.add(campo, ret, fi)

        def lectura():
            q = float(iT.get_value())
            return T(f"i = {coma(q * V0 / R0, 2)} A        v = {coma(V0 * (1 - q))} V", 26, GRAY).move_to(
                [SX, -2.6, 0])

        self.add(m.always_redraw(lectura))
        self.pie("Al cerrar el circuito, la corriente empieza a crecer y con ella el campo magnético B", 24)
        self.wait(1.5)
        self.pie("Al cambiar el flujo se induce una tensión que se opone al cambio (ley de Lenz)", 24)
        carga = lambda t: (1 - np.exp(-4 * t)) / (1 - np.exp(-4))
        self.play(iT.animate.set_value(1), run_time=8, rate_func=carga)
        self.pie("Por eso la corriente no salta: crece de forma gradual hasta i = V₀ / R", 24)
        self.wait(2.0)

        b_lbl = MT(r"\vec{B}", 34, MAG).move_to([SX + SW / 2 + 1.05, SY, 0])
        self.play(m.FadeIn(b_lbl), run_time=0.6)

        def par(titulo, formula):
            return m.VGroup(T(titulo, 24, GRAY), MT(formula, 36)).arrange(m.DOWN, aligned_edge=m.LEFT, buff=0.12)

        p1 = par("Campo dentro del solenoide (ideal)", r"B=\frac{\mu_0 N i}{\ell}")
        p2 = par("Enlace de flujo", r"\lambda=N\,\Phi=N\,B\,A")
        p3 = par("Inductancia", r"L=\frac{\lambda}{i}=\frac{\mu_0 N^{2} A}{\ell}")
        panel = m.VGroup(p1, p2, p3).arrange(m.DOWN, aligned_edge=m.LEFT, buff=0.4)
        panel.move_to([4.4, 0.4, 0]).align_to([1.7, 0, 0], m.LEFT)
        for p in (p1, p2, p3):
            self.play(m.FadeIn(p, shift=m.RIGHT * 0.2), run_time=1.0)
            self.wait(1.4)
        self.pie("Con i constante ya no hay tensión inducida: la energía queda guardada en B", 24)
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
            (r"\lambda", "Enlace de flujo (flujo total en las N espiras)", "Wb  (weber)", MAG),
            ("i", "Corriente por la bobina", "A  (amperio)", POS),
            ("v", "Tensión entre los terminales", "V  (voltio)", NEG),
            ("L", "Inductancia (parámetro concentrado)", "H  (henrio)", GREEN),
            (r"\Phi", "Flujo magnético por una espira, Φ = B A", "Wb", INK),
            ("B", "Densidad de flujo magnético (campo B)", "T = Wb/m²", INK),
            (r"\mu_0", "Permeabilidad del vacío (4π × 10⁻⁷ H/m)", "H/m", INK),
            (r"\mu_r", "Permeabilidad relativa del núcleo (μ / μ₀)", "adimensional", CORE_T),
            ("N", "Número de espiras", "adimensional", INK),
            (r"A,\ \ell", "Área de la sección y longitud de la bobina", "m²,  m", INK),
        ]
        items = []
        for i, (sim, sig, uni, col) in enumerate(filas):
            y = 2.45 - i * 0.41
            g = m.VGroup(
                MT(sim, 32, col).move_to([xs, y, 0]),
                T(sig, 22).move_to([xm, y, 0], aligned_edge=m.LEFT),
                T(uni, 24, col if col != INK else TITLE).move_to([xu, y, 0], aligned_edge=m.LEFT),
            )
            items.append(g)
        self.play(m.FadeIn(cab), run_time=0.6)
        self.play(m.FadeIn(m.VGroup(*items), lag_ratio=0.18), run_time=4.5)

        nota = m.VGroup(
            T("Minúsculas: variables de circuito que cambian en el tiempo (λ, i, v).", 20, GRAY),
            T("Mayúsculas: parámetros concentrados y valores constantes (L, V₀, I₀).", 20, GRAY),
        ).arrange(m.DOWN, aligned_edge=m.LEFT, buff=0.08).move_to([-6.8, -1.9, 0], aligned_edge=m.LEFT)
        self.play(m.FadeIn(nota), run_time=0.8)
        self.wait(2.0)

        ch = T("Comprobación dimensional de las ecuaciones", 22, TITLE).move_to([-6.8, -2.45, 0], aligned_edge=m.LEFT)
        c1 = MT(r"B=\frac{\mu_0 N i}{\ell}:\ \frac{\mathrm{H}}{\mathrm{m}}\frac{\mathrm{A}}{\mathrm{m}}"
                r"=\frac{\mathrm{Wb}}{\mathrm{m^{2}}}", 24)
        c2 = MT(r"v=L\frac{di}{dt}:\ \mathrm{H}\,\frac{\mathrm{A}}{\mathrm{s}}=\mathrm{V}", 24)
        c3 = MT(r"L=\frac{\mu_0 N^{2} A}{\ell}:\ \frac{\mathrm{H}}{\mathrm{m}}\frac{\mathrm{m^{2}}}{\mathrm{m}}"
                r"=\mathrm{H}", 24)
        fila = m.VGroup(c1, c2, c3).arrange(m.RIGHT, buff=0.55).move_to([0.2, -3.05, 0])
        self.play(m.FadeIn(ch), run_time=0.6)
        for c in (c1, c2, c3):
            self.play(m.FadeIn(c, shift=m.UP * 0.15), run_time=0.9)
            self.wait(0.9)
        self.wait(2.0)
        self.limpiar()

    # ================= 4. Geometría =================
    def escena_geometria(self):
        self.titulo("De qué depende la inductancia")
        nT = m.ValueTracker(NT)
        rT = m.ValueTracker(SR)
        lT = m.ValueTracker(SW)
        dyn = m.always_redraw(lambda: bob_dyn(int(round(nT.get_value())), rT.get_value(), lT.get_value()))
        self.play(m.FadeIn(dyn), run_time=1.0)

        f = MT(r"L=\frac{\mu_0 N^{2} A}{\ell}", 52, TITLE).move_to([4.4, 2.0, 0]).align_to([1.7, 0, 0], m.LEFT)
        k = T("μ₀ = 4π × 10⁻⁷ H/m", 24, GRAY).next_to(f, m.DOWN, buff=0.25, aligned_edge=m.LEFT)
        self.play(m.FadeIn(f), m.FadeIn(k), run_time=1.0)

        def lect():
            n = int(round(nT.get_value())) / NT
            a = (rT.get_value() / SR) ** 2
            ll = lT.get_value() / SW
            return m.VGroup(
                T(f"N = {coma(n, 2)} N₀", 28),
                T(f"A = {coma(a, 2)} A₀", 28),
                T(f"ℓ = {coma(ll, 2)} ℓ₀", 28),
                T(f"L = {coma(n * n * a / ll, 2)} L₀", 30, TITLE),
            ).arrange(m.DOWN, aligned_edge=m.LEFT, buff=0.2).move_to([4.4, -0.8, 0]).align_to([1.7, 0, 0], m.LEFT)

        self.add(m.always_redraw(lect))
        self.pie("L mide cuánto flujo enlaza la bobina por cada amperio de corriente")
        self.wait(1.0)
        self.pie("Más espiras (N mayor): cada vuelta aporta campo y enlaza flujo, L crece con N²")
        self.play(nT.animate.set_value(2 * NT), run_time=3, rate_func=m.smooth)
        self.wait(1.2)
        self.pie("Mayor sección (A mayor): más flujo atraviesa cada espira, L aumenta")
        self.play(rT.animate.set_value(0.92), run_time=2.5, rate_func=m.smooth)
        self.wait(1.2)
        self.pie("Bobina más larga con las mismas espiras (ℓ mayor): B se debilita, L disminuye")
        self.play(lT.animate.set_value(5.0), run_time=2.5, rate_func=m.smooth)
        self.wait(2.0)
        self.limpiar()

    # ================= 5. Núcleo magnético =================
    def escena_nucleo(self):
        self.titulo("El núcleo magnético")
        CW, CH = SW + 0.5, 2 * SR * 0.75
        xc0 = SX + SW / 2 + 0.6          # borde izquierdo del núcleo, fuera de la bobina
        xc1 = SX - CW / 2                # núcleo centrado
        xcT = m.ValueTracker(xc0)

        def frac():
            return float(np.clip((SX + SW / 2 - xcT.get_value()) / SW, 0, 1))

        rng = np.random.default_rng(3)
        th0 = rng.uniform(-np.pi, np.pi, (2, 8))
        delta = ((rng.normal(0, 0.12, (2, 8)) - th0 + np.pi) % (2 * np.pi)) - np.pi

        def nucleo():
            return m.Rectangle(width=CW, height=CH, fill_color=CORE, fill_opacity=0.35, stroke_color=CORE_T,
                               stroke_width=2).move_to([xcT.get_value() + CW / 2, SY, 0])

        def dominios():
            fr = frac()
            a = fr * fr * (3 - 2 * fr)
            it = []
            for j in range(2):
                for i in range(8):
                    c = np.array([xcT.get_value() + (i + 0.5) * CW / 8, SY + (j - 0.5) * 0.56, 0.0])
                    th = th0[j, i] + a * delta[j, i]
                    u = np.array([np.cos(th), np.sin(th), 0.0])
                    it.append(flecha(c - 0.15 * u, c + 0.15 * u, CORE_T, 3, 0.1))
            return m.VGroup(*it)

        slab = m.always_redraw(nucleo)
        dom = m.always_redraw(dominios)
        bob = bobina()
        campo = campo_interior(ys=(-0.62, 0.0, 0.62), sw=3)
        campo.add_updater(lambda g: g.set_stroke(width=3 + 6 * frac()))
        lab_i = T("Corriente i constante por la bobina", 24, GRAY).move_to([SX, SY - SR - 0.6, 0])
        self.play(m.FadeIn(slab), m.FadeIn(dom), m.FadeIn(bob), m.FadeIn(campo), m.FadeIn(lab_i), run_time=1.2)
        self.pie("Un material ferromagnético tiene dominios magnéticos orientados al azar")
        self.wait(2.0)
        self.pie("Al entrar en la bobina, los dominios se alinean con el campo y lo refuerzan")
        self.play(xcT.animate.set_value(xc1), run_time=5.5, rate_func=m.smooth)
        self.wait(1.0)

        h1 = T("Núcleo ferromagnético (μr ≫ 1)", 28, CORE_T)
        h2 = T("(i constante)", 22, GRAY)
        fB = MT(r"B=\mu_r\,B_0", 36)
        fL = MT(r"L=\mu_r\,L_0=\frac{\mu_r\,\mu_0 N^{2} A}{\ell}", 36, TITLE)
        fm = MT(r"\mu=\mu_r\,\mu_0", 32, GRAY)
        panel = m.VGroup(h1, h2, fB, fL, fm).arrange(m.DOWN, aligned_edge=m.LEFT, buff=0.22)
        panel.move_to([4.4, 0.6, 0]).align_to([1.7, 0, 0], m.LEFT)
        self.play(m.FadeIn(h1), m.FadeIn(h2), run_time=0.8)
        for fmx in (fB, fL, fm):
            self.play(m.FadeIn(fmx, shift=m.RIGHT * 0.2), run_time=0.9)
            self.wait(1.2)
        self.pie("B₀ y L₀: valores con núcleo de aire.  μr: permeabilidad relativa (sin unidades)", 24)
        self.wait(3.0)
        self.pie("Con la misma corriente hay mucho más flujo: la inductancia se multiplica por μr", 24)
        self.wait(3.0)
        self.limpiar()

    # ================= 6. Propiedades del núcleo =================
    def escena_propiedades(self):
        self.titulo("Qué aporta el núcleo")
        cab = T("Permeabilidad relativa μr (valores típicos)", 24, GRAY).move_to([-6.8, 2.5, 0], aligned_edge=m.LEFT)
        filas = [("Vacío", "1"), ("Aire", "≈ 1"), ("Aluminio, cobre", "≈ 1"), ("Níquel", "≈ 100 a 600"),
                 ("Ferritas", "≈ 10 a 10⁴"), ("Acero al silicio", "≈ 10³ a 10⁴"), ("Mu-metal", "≈ 10⁴ a 10⁵")]
        tabla = m.VGroup()
        for i, (nom, val) in enumerate(filas):
            y = 1.7 - i * 0.58
            tabla.add(T(nom, 26).move_to([-6.6, y, 0], aligned_edge=m.LEFT))
            tabla.add(T(val, 26, TITLE).move_to([-1.35, y, 0], aligned_edge=m.RIGHT))
        nota = T("Aproximados: en los ferromagnéticos μr depende de B", 20, GRAY).move_to(
            [-6.6, -2.7, 0], aligned_edge=m.LEFT)
        self.play(m.FadeIn(cab), run_time=0.6)
        self.play(m.FadeIn(tabla, lag_ratio=0.12), run_time=2.5)
        self.play(m.FadeIn(nota), run_time=0.4)

        datos = [
            ("1. Mayor inductancia", ["L = μr L₀: mismo tamaño,", "muchas menos espiras para la misma L"], GREEN),
            ("2. Guía el flujo", ["Concentra el campo dentro del núcleo", "y reduce el flujo disperso"], MAG),
            ("3. Límites: saturación y pérdidas", ["Por encima de cierto B, μr cae (saturación);",
                                                  "histéresis y corrientes parásitas calientan el núcleo"], POS),
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
        self.pie("Por eso los núcleos se laminan o se hacen de ferrita, y se trabaja lejos de la saturación", 24)
        self.wait(3.0)
        self.limpiar()

    # ================= 7. Relación tensión–corriente =================
    def escena_tension_corriente(self):
        self.titulo("Relación tensión–corriente en el inductor")

        def par(titulo, formula, color=INK, buff=0.12):
            return m.VGroup(T(titulo, 22, GRAY), MT(formula, 36, color)).arrange(m.DOWN, aligned_edge=m.LEFT, buff=buff)

        p1 = par("Ley de Faraday, con λ = L i (L constante):",
                 r"v(t)=\frac{d\lambda}{dt}=L\,\frac{di}{dt}")
        p2 = par("Integrando (la primitiva):", r"i(t)=\frac{1}{L}\int_{-\infty}^{t} v(\tau)\,d\tau")
        p3 = par("Desde un instante inicial t₀:",
                 r"i(t)=i(t_0)+\frac{1}{L}\int_{t_0}^{t} v(\tau)\,d\tau", TITLE, buff=0.3)
        nota = m.VGroup(
            T("i(t₀): corriente inicial (la «memoria» del inductor)", 20, GRAY),
            T("τ: variable de integración", 20, GRAY),
        ).arrange(m.DOWN, aligned_edge=m.LEFT, buff=0.08)
        col = m.VGroup(p1, p2, p3, nota).arrange(m.DOWN, aligned_edge=m.LEFT, buff=0.35)
        col.move_to([-3.0, 0.1, 0]).align_to([-6.8, 0, 0], m.LEFT)
        caja = m.SurroundingRectangle(p3[1], buff=0.15, color=TITLE, stroke_width=2)

        self.play(m.FadeIn(p1, shift=m.RIGHT * 0.2), run_time=1.0)
        self.pie("La tensión en el inductor es proporcional a la rapidez con que cambia la corriente", 24)
        self.wait(1.5)
        self.play(m.FadeIn(p2, shift=m.RIGHT * 0.2), run_time=1.0)
        self.pie("La corriente acumula toda la historia de la tensión aplicada al inductor", 24)
        self.wait(1.5)
        self.play(m.FadeIn(p3, shift=m.RIGHT * 0.2), m.Create(caja), run_time=1.2)
        self.play(m.FadeIn(nota), run_time=0.6)
        self.pie("Lo ocurrido antes de t₀ queda resumido en la corriente inicial i(t₀)", 24)
        self.wait(2.0)

        # ---- ejemplo: pulso de tensión constante ----
        x0, x1, xa, xb = 2.0, 6.6, 2.9, 5.0     # eje t: origen, fin, t₀, t₁
        yv, yi = 0.9, -1.9                      # origen de cada gráfica
        hV, i0, hI = 0.9, 0.3, 1.1              # altura de V₀, i(t₀) y del aumento de i

        def ejes(y, nombre, color):
            return m.VGroup(
                m.Arrow([x0, y, 0], [x1, y, 0], buff=0, color=GRAY, stroke_width=3),
                m.Arrow([x0, y, 0], [x0, y + 1.45, 0], buff=0, color=GRAY, stroke_width=3),
                MT(nombre, 28, color).move_to([x0 + 0.45, y + 1.45, 0]),
                MT("t", 26, GRAY).move_to([x1 + 0.2, y - 0.2, 0]),
            )

        marcas = m.VGroup(
            m.DashedLine([xa, yi, 0], [xa, yv + 1.2, 0], color=LINEC, stroke_width=2),
            m.DashedLine([xb, yi, 0], [xb, yv + 1.2, 0], color=LINEC, stroke_width=2),
            MT("t_0", 26, GRAY).move_to([xa, yi - 0.3, 0]),
            MT("t_1", 26, GRAY).move_to([xb, yi - 0.3, 0]),
        )
        etq = m.VGroup(
            MT("V_0", 26, NEG).move_to([x0 - 0.3, yv + hV, 0]),
            MT("i(t_0)", 24, POS).move_to([x0 - 0.5, yi + i0, 0]),
        )
        tT = m.ValueTracker(x0)

        def curvas():
            x = tT.get_value()

            def tension(s):
                return hV if xa <= s < xb else 0.0

            def corriente(s):
                return i0 + hI * float(np.clip((s - xa) / (xb - xa), 0, 1))

            ss = np.linspace(x0, max(x, x0 + 1e-3), 200)
            pv = [np.array([s, yv + tension(s), 0.0]) for s in ss]
            pi = [np.array([s, yi + corriente(s), 0.0]) for s in ss]
            return m.VGroup(
                m.VMobject(color=NEG, stroke_width=5).set_points_as_corners(pv),
                m.VMobject(color=POS, stroke_width=5).set_points_as_corners(pi),
            )

        self.pie("Ejemplo: entre t₀ y t₁ se aplica una tensión constante V₀", 24)
        self.play(m.FadeIn(ejes(yv, "v(t)", NEG)), m.FadeIn(ejes(yi, "i(t)", POS)), m.FadeIn(marcas), m.FadeIn(etq),
                  run_time=1.0)
        self.add(m.always_redraw(curvas))
        self.play(tT.animate.set_value(x1 - 0.1), run_time=4.0, rate_func=m.linear)
        pend = MT(r"\text{pendiente}=\frac{V_0}{L}", 24, POS).next_to([xb, yi + 0.7, 0], m.RIGHT, buff=0.12)
        self.play(m.FadeIn(pend), run_time=0.6)
        self.pie("Con tensión constante, i crece linealmente; si v = 0, i se mantiene", 24)
        self.wait(2.5)
        self.pie("i no puede cambiar de forma instantánea: exigiría una tensión infinita", 24)
        self.wait(2.5)
        self.pie("En DC (i constante), v = L di/dt = 0: el inductor actúa como cortocircuito", 24)
        self.wait(3.0)
        self.pie("Dualidad con el capacitor: se intercambian v ↔ i y C ↔ L", 24)
        self.wait(2.5)
        self.limpiar()

    # ================= 8. Energía =================
    def escena_energia(self):
        self.titulo("¿Dónde se guarda la energía?")
        vol = m.Rectangle(width=SW, height=2 * SR, fill_color=MAG, fill_opacity=0.08,
                          stroke_color=MAG, stroke_width=2).move_to([SX, SY, 0])
        self.play(m.FadeIn(vol), m.FadeIn(bobina()), run_time=1.0)
        self.play(m.FadeIn(campo_interior()), m.FadeIn(retornos().set_stroke(opacity=0.6)), run_time=1.0)
        lbl = T("Energía almacenada en el campo B", 24, MAG).move_to([SX, -1.55, 0])
        self.play(m.FadeIn(lbl), run_time=0.6)
        self.pie("El trabajo hecho contra la tensión inducida queda almacenado en el campo magnético", 24)

        a = T("Energía almacenada (w, en julios)", 24, GRAY)
        f1 = MT(r"w=\tfrac{1}{2}\,L\,i^{2}=\tfrac{1}{2}\,\lambda\,i=\dfrac{\lambda^{2}}{2L}", 30)
        b = T("Densidad de energía (u, en J/m³)", 24, GRAY)
        f2 = MT(r"u=\dfrac{B^{2}}{2\mu}", 36, TITLE)
        c = T("con μ = μr μ₀ (en el aire, μr ≈ 1)", 22, GRAY)
        chk = MT(r"\frac{\mathrm{T^{2}}}{\mathrm{H/m}}=\frac{\mathrm{J}}{\mathrm{m^{3}}}", 28)
        panel = m.VGroup(a, f1, b, f2, c, chk).arrange(m.DOWN, aligned_edge=m.LEFT, buff=0.2)
        panel.move_to([4.4, 0.2, 0]).align_to([1.7, 0, 0], m.LEFT)
        for grp in ((a, f1), (b, f2, c), (chk,)):
            self.play(*[m.FadeIn(x, shift=m.RIGHT * 0.2) for x in grp], run_time=1.0)
            self.wait(2.0)
        self.pie("Al abrir el circuito esa energía busca salida: por eso puede saltar una chispa", 24)
        self.wait(3.0)
        self.limpiar()

    # ================= 9. Resumen =================
    def escena_resumen(self):
        self.titulo("Resumen")
        pts = [
            ("Inductor: conductor enrollado en espiras, con o sin núcleo.", TITLE),
            ("La corriente crea un campo B; el enlace de flujo es λ = N Φ.", TITLE),
            ("Inductancia: L = λ / i = μ N² A / ℓ, medida en henrios (H = Wb/A).", TITLE),
            ("Un núcleo ferromagnético refuerza B y aumenta L (μr ≫ 1), hasta saturar.", TITLE),
            ("Relación v–i: v = L di/dt,  i(t) = i(t₀) + (1/L) ∫ v dτ desde t₀.", TITLE),
            ("Energía: w = ½ L i², guardada en el campo magnético.", TITLE),
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
    InductorVideo().render(VIDEO)
    print("Video guardado en:", VIDEO)
