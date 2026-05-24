"""
Shikaku - Proyecto Análisis de Algoritmos 2026-10
Vanesa Florez y Angy Bautista

Cómo jugar:
  - Clic izquierdo: empieza a dibujar un rectángulo desde una celda
  - Clic derecho: borra el rectángulo de esa celda
  - Botón "Resolver": el algoritmo resuelve el puzzle automáticamente
  - Botón "Nuevo puzzle": carga un puzzle distinto
  - Botón "Limpiar": borra todos los rectángulos dibujados

Reglas del Shikaku:
  - Divide la grilla en rectángulos
  - Cada rectángulo debe contener exactamente UN número
  - Ese número indica el área exacta del rectángulo (filas x columnas)
"""

import pygame
import sys
import random
from copy import deepcopy

# ── Colores ──────────────────────────────────────────────────────────────────
BLANCO      = (255, 255, 255)
NEGRO       = (  0,   0,   0)
GRIS_CLARO  = (220, 220, 220)
GRIS        = (160, 160, 160)
AZUL        = ( 70, 130, 200)
AZUL_CLARO  = (180, 210, 255)
VERDE       = ( 60, 180,  80)
ROJO        = (220,  60,  60)
AMARILLO    = (255, 230,  80)
NARANJA     = (255, 150,  50)
COLORES_RECT = [
    (173, 216, 230),  # azul claro
    (144, 238, 144),  # verde claro
    (255, 182, 193),  # rosa
    (255, 255, 153),  # amarillo
    (216, 191, 216),  # lavanda
    (255, 200, 150),  # durazno
    (180, 230, 180),  # menta
    (200, 200, 255),  # lila
    (255, 220, 180),  # melocotón
    (180, 255, 255),  # cian claro
]

# ── Puzzles predefinidos ──────────────────────────────────────────────────────
# Formato: lista de (fila, columna, número)  →  grilla NxN
PUZZLES = [
    # Puzzle 1 – 5x5 fácil (solución verificada)
    {
        "nombre": "Fácil 5×5",
        "filas": 5, "cols": 5,
        "pistas": [
            (0,0,4),(0,3,3),
            (1,2,4),(2,4,3),
            (3,0,3),(2,1,2),
            (3,2,4),(4,1,1),(4,4,1),
        ]
    },
    # Puzzle 2 – 6x6 medio (solución verificada)
    {
        "nombre": "Medio 6×6",
        "filas": 6, "cols": 6,
        "pistas": [
            (0,1,3),(0,4,3),
            (1,0,4),(1,2,4),(1,4,4),
            (3,1,3),(3,4,3),
            (4,0,4),(4,2,4),(4,4,4),
        ]
    },
    # Puzzle 3 – 7x7 difícil (solución verificada)
    {
        "nombre": "Difícil 7×7",
        "filas": 7, "cols": 7,
        "pistas": [
            (0,1,3),(0,3,4),(0,5,2),
            (1,0,4),(1,2,2),(1,5,4),
            (2,3,4),(3,0,4),(3,2,1),
            (3,5,4),(4,2,4),(4,4,1),
            (5,0,4),(5,5,3),(6,3,3),(6,5,2),
        ]
    },
]

# ── Solucionador (Backtracking) ───────────────────────────────────────────────
def obtener_rectangulos_posibles(fila, col, num, filas, cols):
    """Genera todos los rectángulos que tienen área=num y contienen la celda (fila,col)."""
    resultado = []
    for h in range(1, filas + 1):
        if num % h != 0:
            continue
        w = num // h
        if w > cols:
            continue
        # El rectángulo puede empezar en distintas posiciones respecto a la pista
        for r0 in range(max(0, fila - h + 1), min(filas - h, fila) + 1):
            for c0 in range(max(0, col - w + 1), min(cols - w, col) + 1):
                resultado.append((r0, c0, r0 + h - 1, c0 + w - 1))
    return resultado


def celdas_de_rect(r0, c0, r1, c1):
    return [(r, c) for r in range(r0, r1 + 1) for c in range(c0, c1 + 1)]


def resolver(pistas, filas, cols):
    """
    Backtracking: asigna un rectángulo a cada pista sin solapamientos.
    Retorna lista de rectángulos (r0,c0,r1,c1) en el mismo orden que pistas,
    o None si no hay solución.
    """
    # Pre-calcular opciones para cada pista
    opciones = []
    for (fila, col, num) in pistas:
        ops = obtener_rectangulos_posibles(fila, col, num, filas, cols)
        opciones.append(ops)

    asignados = [None] * len(pistas)
    ocupado = {}   # celda -> índice de pista

    def backtrack(idx):
        if idx == len(pistas):
            return True
        for rect in opciones[idx]:
            celdas = celdas_de_rect(*rect)
            # Verificar que no haya solapamiento
            if any(c in ocupado for c in celdas):
                continue
            # Verificar que el rectángulo contenga exactamente una pista
            pistas_en_rect = sum(
                1 for (pr, pc, _) in pistas if rect[0] <= pr <= rect[2] and rect[1] <= pc <= rect[3]
            )
            if pistas_en_rect != 1:
                continue
            # Asignar
            for c in celdas:
                ocupado[c] = idx
            asignados[idx] = rect
            if backtrack(idx + 1):
                return True
            # Deshacer
            for c in celdas:
                del ocupado[c]
            asignados[idx] = None
        return False

    if backtrack(0):
        return asignados
    return None


# ── Clase principal del juego ─────────────────────────────────────────────────
class Shikaku:
    def __init__(self):
        pygame.init()
        self.ancho_pantalla = 700
        self.alto_pantalla  = 680
        self.pantalla = pygame.display.set_mode((self.ancho_pantalla, self.alto_pantalla))
        pygame.display.set_caption("Shikaku – Análisis de Algoritmos 2026")

        self.fuente_grande = pygame.font.SysFont("Arial", 28, bold=True)
        self.fuente_media  = pygame.font.SysFont("Arial", 20, bold=True)
        self.fuente_chica  = pygame.font.SysFont("Arial", 14)

        self.puzzle_idx = 0
        self.cargar_puzzle(self.puzzle_idx)

        self.dibujando   = False   # ¿el usuario está arrastrando?
        self.celda_inicio = None
        self.celda_actual = None
        self.mensaje      = ""
        self.color_msg    = NEGRO

    def cargar_puzzle(self, idx):
        p = PUZZLES[idx]
        self.filas     = p["filas"]
        self.cols      = p["cols"]
        self.pistas    = p["pistas"]   # lista (fila, col, num)
        self.nombre    = p["nombre"]
        # Mapa rápido celda → número
        self.mapa_pistas = {(f, c): n for (f, c, n) in self.pistas}
        # Rectángulos del usuario: lista de (r0,c0,r1,c1)
        self.rects_usuario = []
        self.resuelto = False
        self._calcular_geometria()

    def _calcular_geometria(self):
        margen_top  = 110
        margen_izq  = 40
        espacio_bot = 100
        ancho_grid  = self.ancho_pantalla - margen_izq * 2
        alto_grid   = self.alto_pantalla  - margen_top - espacio_bot
        self.tam_celda = min(ancho_grid // self.cols, alto_grid // self.filas)
        self.grid_x = margen_izq + (ancho_grid - self.tam_celda * self.cols) // 2
        self.grid_y = margen_top

    def celda_en_pixel(self, fila, col):
        x = self.grid_x + col * self.tam_celda
        y = self.grid_y + fila * self.tam_celda
        return x, y

    def pixel_a_celda(self, px, py):
        col = (px - self.grid_x) // self.tam_celda
        fila = (py - self.grid_y) // self.tam_celda
        if 0 <= fila < self.filas and 0 <= col < self.cols:
            return (fila, col)
        return None

    # ── Dibujo ────────────────────────────────────────────────────────────────
    def dibujar(self):
        self.pantalla.fill((245, 245, 250))
        self._dibujar_titulo()
        self._dibujar_rects_usuario()
        self._dibujar_rect_en_curso()
        self._dibujar_grilla()
        self._dibujar_pistas()
        self._dibujar_botones()
        self._dibujar_mensaje()
        pygame.display.flip()

    def _dibujar_titulo(self):
        txt = self.fuente_grande.render(f"Shikaku  –  {self.nombre}", True, NEGRO)
        self.pantalla.blit(txt, (self.ancho_pantalla // 2 - txt.get_width() // 2, 12))
        subtxt = self.fuente_chica.render(
            "Clic izq: dibujar rectángulo  |  Clic der: borrar  |  Cada número = área del rectángulo",
            True, GRIS)
        self.pantalla.blit(subtxt, (self.ancho_pantalla // 2 - subtxt.get_width() // 2, 48))

    def _dibujar_rects_usuario(self):
        for i, (r0, c0, r1, c1) in enumerate(self.rects_usuario):
            color = COLORES_RECT[i % len(COLORES_RECT)]
            x, y = self.celda_en_pixel(r0, c0)
            w = (c1 - c0 + 1) * self.tam_celda
            h = (r1 - r0 + 1) * self.tam_celda
            pygame.draw.rect(self.pantalla, color, (x, y, w, h))
            pygame.draw.rect(self.pantalla, AZUL, (x, y, w, h), 3)

    def _dibujar_rect_en_curso(self):
        if self.dibujando and self.celda_inicio and self.celda_actual:
            r0 = min(self.celda_inicio[0], self.celda_actual[0])
            c0 = min(self.celda_inicio[1], self.celda_actual[1])
            r1 = max(self.celda_inicio[0], self.celda_actual[0])
            c1 = max(self.celda_inicio[1], self.celda_actual[1])
            x, y = self.celda_en_pixel(r0, c0)
            w = (c1 - c0 + 1) * self.tam_celda
            h = (r1 - r0 + 1) * self.tam_celda
            s = pygame.Surface((w, h), pygame.SRCALPHA)
            s.fill((100, 150, 255, 80))
            self.pantalla.blit(s, (x, y))
            pygame.draw.rect(self.pantalla, AZUL, (x, y, w, h), 2)

    def _dibujar_grilla(self):
        t = self.tam_celda
        for f in range(self.filas):
            for c in range(self.cols):
                x, y = self.celda_en_pixel(f, c)
                pygame.draw.rect(self.pantalla, NEGRO, (x, y, t, t), 1)
        # Borde exterior más grueso
        gx, gy = self.celda_en_pixel(0, 0)
        pygame.draw.rect(self.pantalla, NEGRO,
                         (gx, gy, t * self.cols, t * self.filas), 3)

    def _dibujar_pistas(self):
        t = self.tam_celda
        for (fila, col, num) in self.pistas:
            x, y = self.celda_en_pixel(fila, col)
            # Círculo de fondo
            cx, cy = x + t // 2, y + t // 2
            r = t // 2 - 3
            pygame.draw.circle(self.pantalla, NEGRO, (cx, cy), r)
            pygame.draw.circle(self.pantalla, BLANCO, (cx, cy), r - 2)
            # Número
            txt = self.fuente_media.render(str(num), True, NEGRO)
            self.pantalla.blit(txt, (cx - txt.get_width() // 2, cy - txt.get_height() // 2))

    def _dibujar_botones(self):
        y_bot = self.grid_y + self.filas * self.tam_celda + 15
        self.botones = {}

        botones_info = [
            ("resolver",  "Resolver",    VERDE,  BLANCO),
            ("limpiar",   "Limpiar",     NARANJA, BLANCO),
            ("siguiente", "Siguiente ▶", AZUL,   BLANCO),
        ]
        total = len(botones_info)
        bw, bh = 150, 42
        espacio = 20
        total_ancho = total * bw + (total - 1) * espacio
        x0 = self.ancho_pantalla // 2 - total_ancho // 2

        for i, (key, label, color, txt_color) in enumerate(botones_info):
            bx = x0 + i * (bw + espacio)
            rect = pygame.Rect(bx, y_bot, bw, bh)
            self.botones[key] = rect
            pygame.draw.rect(self.pantalla, color, rect, border_radius=8)
            pygame.draw.rect(self.pantalla, NEGRO, rect, 2, border_radius=8)
            txt = self.fuente_media.render(label, True, txt_color)
            self.pantalla.blit(txt, (bx + bw // 2 - txt.get_width() // 2,
                                     y_bot + bh // 2 - txt.get_height() // 2))

    def _dibujar_mensaje(self):
        if self.mensaje:
            txt = self.fuente_media.render(self.mensaje, True, self.color_msg)
            y_msg = self.grid_y + self.filas * self.tam_celda + 70
            self.pantalla.blit(txt, (self.ancho_pantalla // 2 - txt.get_width() // 2, y_msg))

    # ── Lógica ────────────────────────────────────────────────────────────────
    def verificar_solucion(self):
        """Verifica si los rectángulos del usuario resuelven el puzzle."""
        ocupado = {}
        for r0, c0, r1, c1 in self.rects_usuario:
            for f in range(r0, r1 + 1):
                for c in range(c0, c1 + 1):
                    if (f, c) in ocupado:
                        return False, "¡Rectángulos solapados!"
                    ocupado[(f, c)] = (r0, c0, r1, c1)

        # Toda la grilla cubierta
        if len(ocupado) != self.filas * self.cols:
            return False, "Faltan celdas por cubrir"

        # Cada rectángulo tiene exactamente una pista con el número correcto
        for r0, c0, r1, c1 in self.rects_usuario:
            area = (r1 - r0 + 1) * (c1 - c0 + 1)
            pistas_en = [(f, c, n) for (f, c, n) in self.pistas
                         if r0 <= f <= r1 and c0 <= c <= c1]
            if len(pistas_en) != 1:
                return False, "Un rectángulo debe tener exactamente 1 número"
            if pistas_en[0][2] != area:
                return False, f"Área incorrecta: el {pistas_en[0][2]} necesita área {pistas_en[0][2]}"

        return True, "¡Puzzle resuelto! 🎉"

    def agregar_rect(self, r0, c0, r1, c1):
        """Agrega un rectángulo del usuario, eliminando los que se solapan."""
        nuevos = []
        for rect in self.rects_usuario:
            # Verificar solapamiento
            solapado = not (rect[2] < r0 or rect[0] > r1 or rect[3] < c0 or rect[1] > c1)
            if not solapado:
                nuevos.append(rect)
        nuevos.append((r0, c0, r1, c1))
        self.rects_usuario = nuevos

    def borrar_rect_en(self, fila, col):
        self.rects_usuario = [
            r for r in self.rects_usuario
            if not (r[0] <= fila <= r[2] and r[1] <= col <= r[3])
        ]

    # ── Eventos ───────────────────────────────────────────────────────────────
    def manejar_eventos(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos

                # Botones
                if hasattr(self, 'botones'):
                    if self.botones.get("resolver") and self.botones["resolver"].collidepoint(mx, my):
                        self._accion_resolver()
                        continue
                    if self.botones.get("limpiar") and self.botones["limpiar"].collidepoint(mx, my):
                        self.rects_usuario = []
                        self.mensaje = "Grilla limpiada"
                        self.color_msg = GRIS
                        continue
                    if self.botones.get("siguiente") and self.botones["siguiente"].collidepoint(mx, my):
                        self.puzzle_idx = (self.puzzle_idx + 1) % len(PUZZLES)
                        self.cargar_puzzle(self.puzzle_idx)
                        self.mensaje = f"Cargado: {self.nombre}"
                        self.color_msg = AZUL
                        continue

                # Clic en grilla
                celda = self.pixel_a_celda(mx, my)
                if celda:
                    if event.button == 1:   # izquierdo → dibujar
                        self.dibujando = True
                        self.celda_inicio = celda
                        self.celda_actual = celda
                    elif event.button == 3: # derecho → borrar
                        self.borrar_rect_en(*celda)
                        self.mensaje = ""

            elif event.type == pygame.MOUSEMOTION:
                if self.dibujando:
                    celda = self.pixel_a_celda(*event.pos)
                    if celda:
                        self.celda_actual = celda

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and self.dibujando:
                    self.dibujando = False
                    if self.celda_inicio and self.celda_actual:
                        r0 = min(self.celda_inicio[0], self.celda_actual[0])
                        c0 = min(self.celda_inicio[1], self.celda_actual[1])
                        r1 = max(self.celda_inicio[0], self.celda_actual[0])
                        c1 = max(self.celda_inicio[1], self.celda_actual[1])
                        self.agregar_rect(r0, c0, r1, c1)
                        ok, msg = self.verificar_solucion()
                        self.mensaje = msg
                        self.color_msg = VERDE if ok else GRIS
                    self.celda_inicio = None
                    self.celda_actual = None

    def _accion_resolver(self):
        self.mensaje = "Resolviendo..."
        self.color_msg = AZUL
        self.dibujar()
        solucion = resolver(self.pistas, self.filas, self.cols)
        if solucion:
            self.rects_usuario = solucion
            self.mensaje = "¡Solución encontrada por el algoritmo! 🤖"
            self.color_msg = VERDE
        else:
            self.mensaje = "No se encontró solución"
            self.color_msg = ROJO

    # ── Loop principal ────────────────────────────────────────────────────────
    def ejecutar(self):
        clock = pygame.time.Clock()
        while True:
            self.manejar_eventos()
            self.dibujar()
            clock.tick(60)


if __name__ == "__main__":
    juego = Shikaku()
    juego.ejecutar()
