"""
Shikaku - Interfaz Gráfica de Usuario (GUI)
Proyecto Análisis de Algoritmos 2026-10
Pontificia Universidad Javeriana
"""

import pygame
import sys
import math
# CONEXIÓN INTERFAZ-SOLVER: Importamos el módulo sintético de forma limpia
from solver import resolver

# ── PALETA DE COLORES PREMIUM ────────────────────────────────────────────────
FONDOS_GRADIENTE = [(240, 244, 248), (218, 226, 236)] 
GRILLA_FONDO     = (255, 255, 255)
GRILLA_LINEA     = (186, 199, 213)
TEXTO_PRINCIPAL  = (16, 42, 67)
TEXTO_SECUNDARIO = (72, 101, 129)

BTN_RESOLVER  = {"normal": (36, 150, 63),   "hover": (46, 175, 76),   "texto": (255, 255, 255)}
BTN_LIMPIAR   = {"normal": (211, 47, 47),   "hover": (229, 57, 53),   "texto": (255, 255, 255)}
BTN_SIGUIENTE = {"normal": (33, 150, 243),  "hover": (66, 165, 245),  "texto": (255, 255, 255)}

COLORES_RECT = [
    (139, 218, 242), (163, 230, 177), (255, 179, 186), (255, 223, 186),
    (255, 255, 186), (225, 190, 231), (178, 235, 242), (255, 204, 188),
]

# ── BANCO DE NIVELES (7 PUZZLES) ─────────────────────────────────────────────
PUZZLES = [
    {"nombre": "Nivel 1: Principiante (5×5)", "filas": 5, "cols": 5, "pistas": [(0,0,4),(0,3,3),(1,2,4),(2,4,3),(3,0,3),(2,1,2),(3,2,4),(4,1,1),(4,4,1)]},
    {"nombre": "Nivel 2: Recluta (5×5)", "filas": 5, "cols": 5, "pistas": [(0,1,2),(0,4,5),(1,2,4),(2,0,3),(3,3,4),(4,0,2),(4,2,3),(4,4,2)]},
    {"nombre": "Nivel 3: Intermedio (6×6)", "filas": 6, "cols": 6, "pistas": [(0,1,3),(0,4,3),(1,0,4),(1,2,4),(1,4,4),(3,1,3),(3,4,3),(4,0,4),(4,2,4),(4,4,4)]},
    {"nombre": "Nivel 4: Desafío Grilla (6×6)", "filas": 6, "cols": 6, "pistas": [(0,0,6),(0,5,2),(2,1,4),(2,3,6),(3,2,2),(3,4,4),(5,0,6),(5,4,6)]},
    {"nombre": "Nivel 5: Avanzado (7×7)", "filas": 7, "cols": 7, "pistas": [(0,1,3),(0,3,4),(0,5,2),(1,0,4),(1,2,2),(1,5,4),(2,3,4),(3,0,4),(3,2,1),(3,5,4),(4,2,4),(4,4,1),(5,0,4),(5,5,3),(6,3,3),(6,5,2)]},
    {"nombre": "Nivel 6: Destreza Lógica (7×7)", "filas": 7, "cols": 7, "pistas": [(0,0,7),(0,6,2),(2,2,6),(2,4,4),(3,1,9),(3,5,3),(4,3,4),(5,0,6),(6,2,4),(6,6,4)]},
    {"nombre": "Nivel 7: Maestro Backtracking (8×8)", "filas": 8, "cols": 8, "pistas": [(0,2,4),(0,6,8),(1,0,6),(1,4,4),(3,1,8),(3,5,12),(4,3,2),(4,7,4),(5,0,4),(6,4,6),(7,1,2),(7,6,4)]}
]

class EfectoVisual:
    def __init__(self):
        self.spinner_angle = 0
        self.mensaje_timer = 0
        self.mensaje_actual = ""
        self.mensaje_color = TEXTO_PRINCIPAL
    
    def actualizar(self):
        if self.mensaje_timer > 0:
            self.mensaje_timer -= 1
            if self.mensaje_timer == 0:
                self.mensaje_actual = ""
        self.spinner_angle = (self.spinner_angle + 10) % 360

class Shikaku:
    def __init__(self):
        pygame.init()
        self.ancho_pantalla = 800
        self.alto_pantalla  = 660  
        self.pantalla = pygame.display.set_mode((self.ancho_pantalla, self.alto_pantalla))
        pygame.display.set_caption("Shikaku Puzzle - Javeriana 2026")
        
        # FUENTES COMPATIBLES CON EMOJIS (Evita los cuadros vacíos en Windows)
        self.fuente_titulo = pygame.font.SysFont("Segoe UI", 30, bold=True)
        self.fuente_sub    = pygame.font.SysFont("Segoe UI Emoji", 13, bold=False)
        self.fuente_pistas = pygame.font.SysFont("Segoe UI", 20, bold=True)
        self.fuente_botones= pygame.font.SysFont("Segoe UI Emoji", 14, bold=False)
        
        self.efectos = EfectoVisual()
        self.puzzle_idx = 0
        self.cargar_puzzle(self.puzzle_idx)
        
        self.dibujando = False
        self.celda_inicio = None
        self.celda_actual = None
        self.resolviendo = False
        self.hover_rect = None
        
    def cargar_puzzle(self, idx):
        p = PUZZLES[idx]
        self.filas = p["filas"]
        self.cols  = p["cols"]
        self.pistas = p["pistas"]
        self.nombre = p["nombre"]
        self.rects_usuario = []
        self._calcular_geometria()
        self.mostrar_mensaje(f"📂 {self.nombre} cargado", TEXTO_PRINCIPAL, 120)
    
    def _calcular_geometria(self):
        margen_top, margen_izq, espacio_bot = 110, 60, 150
        ancho_disponible = self.ancho_pantalla - margen_izq * 2
        alto_disponible  = self.alto_pantalla - margen_top - espacio_bot
        self.tam_celda = min(ancho_disponible // self.cols, alto_disponible // self.filas)
        self.grid_x = margen_izq + (ancho_disponible - self.tam_celda * self.cols) // 2
        self.grid_y = margen_top
        
    def celda_en_pixel(self, fila, col):
        return self.grid_x + col * self.tam_celda, self.grid_y + fila * self.tam_celda
    
    def pixel_a_celda(self, px, py):
        col = (px - self.grid_x) // self.tam_celda
        fila = (py - self.grid_y) // self.tam_celda
        if 0 <= fila < self.filas and 0 <= col < self.cols:
            return (int(fila), int(col))
        return None
    
    def mostrar_mensaje(self, texto, color, duracion=120):
        self.efectos.mensaje_actual = texto
        self.efectos.mensaje_color = color
        self.efectos.mensaje_timer = duracion

    def dibujar_fondo_gradiente(self):
        for y in range(self.alto_pantalla):
            factor = y / self.alto_pantalla
            r = int(FONDOS_GRADIENTE[0][0] + factor * (FONDOS_GRADIENTE[1][0] - FONDOS_GRADIENTE[0][0]))
            g = int(FONDOS_GRADIENTE[0][1] + factor * (FONDOS_GRADIENTE[1][1] - FONDOS_GRADIENTE[0][1]))
            b = int(FONDOS_GRADIENTE[0][2] + factor * (FONDOS_GRADIENTE[1][2] - FONDOS_GRADIENTE[0][2]))
            pygame.draw.line(self.pantalla, (r, g, b), (0, y), (self.ancho_pantalla, y))

    def dibujar(self):
        self.dibujar_fondo_gradiente()
        self._dibujar_encabezado()
        self._dibujar_grilla_base()
        self._dibujar_rects_usuario()
        self._dibujar_rect_en_curso()
        self._dibujar_grilla_lineas()
        self._dibujar_pistas()
        self._dibujar_botones()
        self._dibujar_mensaje()
        if self.resolviendo:
            self._dibujar_spinner()
        pygame.display.flip()
    
    def _dibujar_encabezado(self):
        txt_titulo = self.fuente_titulo.render("SHIKAKU PUZZLE", True, TEXTO_PRINCIPAL)
        self.pantalla.blit(txt_titulo, (self.ancho_pantalla // 2 - txt_titulo.get_width() // 2, 15))
        txt_sub = self.fuente_sub.render(
            "✨ Arrastra Click Izquierdo para crear  |  ❌ Click Derecho para borrar un bloque", True, TEXTO_SECUNDARIO
        )
        self.pantalla.blit(txt_sub, (self.ancho_pantalla // 2 - txt_sub.get_width() // 2, 55))
        pygame.draw.line(self.pantalla, GRILLA_LINEA, (100, 85), (self.ancho_pantalla - 100, 85), 1)

    def _dibujar_grilla_base(self):
        t = self.tam_celda
        gx, gy = self.celda_en_pixel(0, 0)
        pygame.draw.rect(self.pantalla, GRILLA_FONDO, (gx, gy, t * self.cols, t * self.filas))

    def _dibujar_grilla_lineas(self):
        t = self.tam_celda
        for f in range(self.filas):
            for c in range(self.cols):
                x, y = self.celda_en_pixel(f, c)
                pygame.draw.rect(self.pantalla, GRILLA_LINEA, (x, y, t, t), 1)
        gx, gy = self.celda_en_pixel(0, 0)
        pygame.draw.rect(self.pantalla, TEXTO_PRINCIPAL, (gx, gy, t * self.cols, t * self.filas), 3)

    def _dibujar_rects_usuario(self):
        for i, (r0, c0, r1, c1) in enumerate(self.rects_usuario):
            base_color = COLORES_RECT[i % len(COLORES_RECT)]
            x, y = self.celda_en_pixel(r0, c0)
            w = (c1 - c0 + 1) * self.tam_celda
            h = (r1 - r0 + 1) * self.tam_celda
            
            surf_rect = pygame.Surface((w, h), pygame.SRCALPHA)
            surf_rect.fill((*base_color, 200)) 
            self.pantalla.blit(surf_rect, (x, y))
            
            borde_color = (int(base_color[0]*0.6), int(base_color[1]*0.6), int(base_color[2]*0.6))
            if self.hover_rect == (r0, c0, r1, c1):
                pygame.draw.rect(self.pantalla, TEXTO_PRINCIPAL, (x, y, w, h), 3)
            else:
                pygame.draw.rect(self.pantalla, borde_color, (x, y, w, h), 2)

    def _dibujar_rect_en_curso(self):
        if self.dibujando and self.celda_inicio and self.celda_actual:
            r0, r1 = min(self.celda_inicio[0], self.celda_actual[0]), max(self.celda_inicio[0], self.celda_actual[0])
            c0, c1 = min(self.celda_inicio[1], self.celda_actual[1]), max(self.celda_inicio[1], self.celda_actual[1])
            x, y = self.celda_en_pixel(r0, c0)
            w = (c1 - c0 + 1) * self.tam_celda
            h = (r1 - r0 + 1) * self.tam_celda
            
            surf_previa = pygame.Surface((w, h), pygame.SRCALPHA)
            surf_previa.fill((33, 150, 243, 120))
            self.pantalla.blit(surf_previa, (x, y))
            pygame.draw.rect(self.pantalla, (33, 150, 243), (x, y, w, h), 2)

    def _dibujar_pistas(self):
        t = self.tam_celda
        for (fila, col, num) in self.pistas:
            x, y = self.celda_en_pixel(fila, col)
            cx, cy = x + t // 2, y + t // 2
            pygame.draw.circle(self.pantalla, (245, 248, 250), (cx, cy), t // 2 - 6)
            pygame.draw.circle(self.pantalla, TEXTO_SECUNDARIO, (cx, cy), t // 2 - 6, 1)
            txt = self.fuente_pistas.render(str(num), True, TEXTO_PRINCIPAL)
            self.pantalla.blit(txt, (cx - txt.get_width() // 2, cy - txt.get_height() // 2))

    def _dibujar_botones(self):
        y_bot = self.grid_y + self.filas * self.tam_celda + 20
        self.botones = {}
        botones_info = [
            ("resolver",  "🔍 RESOLVER",   BTN_RESOLVER),
            ("limpiar",   "🧹 LIMPIAR",    BTN_LIMPIAR),
            ("siguiente", "➡️ SIGUIENTE",  BTN_SIGUIENTE),
        ]
        bw, bh = 160, 42
        espacio = 20
        total_ancho = len(botones_info) * bw + (len(botones_info) - 1) * espacio
        x0 = self.ancho_pantalla // 2 - total_ancho // 2
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        un_hover_activo = False
        for i, (key, label, paleta) in enumerate(botones_info):
            bx = x0 + i * (bw + espacio)
            rect = pygame.Rect(bx, y_bot, bw, bh)
            self.botones[key] = rect
            
            if rect.collidepoint(mouse_x, mouse_y):
                color = paleta["hover"]
                un_hover_activo = True
            else:
                color = paleta["normal"]
            
            pygame.draw.rect(self.pantalla, color, rect, border_radius=6)
            txt = self.fuente_botones.render(label, True, paleta["texto"])
            self.pantalla.blit(txt, (bx + bw // 2 - txt.get_width() // 2, y_bot + bh // 2 - txt.get_height() // 2))
            
        if un_hover_activo:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    def _dibujar_mensaje(self):
        if self.efectos.mensaje_actual:
            txt = self.fuente_botones.render(self.efectos.mensaje_actual, True, self.efectos.mensaje_color)
            y_msg = self.alto_pantalla - 40 
            fondo_rect = pygame.Rect(self.ancho_pantalla // 2 - txt.get_width() // 2 - 15, y_msg - 5, txt.get_width() + 30, txt.get_height() + 10)
            pygame.draw.rect(self.pantalla, (255, 255, 255), fondo_rect, border_radius=4)
            pygame.draw.rect(self.pantalla, GRILLA_LINEA, fondo_rect, 1, border_radius=4)
            self.pantalla.blit(txt, (self.ancho_pantalla // 2 - txt.get_width() // 2, y_msg))

    def _dibujar_spinner(self):
        centro_x, centro_y = self.ancho_pantalla - 40, 30
        radio = 10
        for i in range(8):
            angulo = self.efectos.spinner_angle + i * 45
            x = int(centro_x + radio * math.cos(math.radians(angulo)))
            y = int(centro_y + radio * math.sin(math.radians(angulo)))
            alpha = max(30, 255 - i * 30)
            s = pygame.Surface((5, 5), pygame.SRCALPHA)
            pygame.draw.circle(s, (33, 150, 243, alpha), (2, 2), 2)
            self.pantalla.blit(s, (x - 2, y - 2))

    def verificar_solucion(self):
        ocupado = {}
        for r0, c0, r1, c1 in self.rects_usuario:
            for f in range(r0, r1 + 1):
                for c in range(c0, c1 + 1):
                    if (f, c) in ocupado: 
                        return False, "⚠️ ¡Hay rectángulos encimados!"
                    ocupado[(f, c)] = (r0, c0, r1, c1)
        
        if len(ocupado) != self.filas * self.cols:
            return False, f"💡 Celdas libres restantes: {self.filas * self.cols - len(ocupado)}"
        
        for r0, c0, r1, c1 in self.rects_usuario:
            area = (r1 - r0 + 1) * (c1 - c0 + 1)
            pistas_en = [(f, c, n) for (f, c, n) in self.pistas if r0 <= f <= r1 and c0 <= c <= c1]
            if len(pistas_en) != 1: 
                return False, "🛑 Cada bloque debe encerrar EXACTAMENTE un número"
            if pistas_en[0][2] != area: 
                return False, f"❌ Área errónea: se requiere tamaño {pistas_en[0][2]}"
        
        return True, "🎉 ¡EXCELENTE! ¡PUZZLE COMPLETADO CON ÉXITO! 🎉"

    def agregar_rect(self, r0, c0, r1, c1):
        if r0 > r1 or c0 > c1: 
            return
        tiene_pista = any(r0 <= f <= r1 and c0 <= c <= c1 for (f, c, _) in self.pistas)
        if not tiene_pista:
            self.mostrar_mensaje("⚠️ El bloque debe encerrar al menos un número", BTN_LIMPIAR["normal"], 100)
            return
        
        nuevos = []
        for rect in self.rects_usuario:
            solapado = not (rect[2] < r0 or rect[0] > r1 or rect[3] < c0 or rect[1] > c1)
            if not solapado: 
                nuevos.append(rect)
        nuevos.append((r0, c0, r1, c1))
        self.rects_usuario = nuevos
        
        ok, msg = self.verificar_solucion()
        self.mostrar_mensaje(msg, BTN_RESOLVER["normal"] if ok else TEXTO_SECUNDARIO, 140)

    def borrar_rect_en(self, fila, col):
        antes = len(self.rects_usuario)
        self.rects_usuario = [r for r in self.rects_usuario if not (r[0] <= fila <= r[2] and r[1] <= col <= r[3])]
        if len(self.rects_usuario) < antes:
            ok, msg = self.verificar_solucion()
            self.mostrar_mensaje(msg, TEXTO_SECUNDARIO, 100)

    def manejar_eventos(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            elif event.type == pygame.MOUSEMOTION:
                mx, my = event.pos
                celda = self.pixel_a_celda(mx, my)
                if celda:
                    self.celda_actual = celda
                    for rect in self.rects_usuario:
                        if rect[0] <= celda[0] <= rect[2] and rect[1] <= celda[1] <= rect[3]:
                            self.hover_rect = rect
                            break
                    else: 
                        self.hover_rect = None
                else: 
                    self.hover_rect = None
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if hasattr(self, 'botones'):
                    if self.botones["resolver"].collidepoint(mx, my):
                        self._accion_resolver()
                        continue
                    if self.botones["limpiar"].collidepoint(mx, my):
                        self.rects_usuario = []
                        self.mostrar_mensaje("🧹 Tablero limpio", BTN_LIMPIAR["normal"], 90)
                        continue
                    if self.botones["siguiente"].collidepoint(mx, my):
                        self.puzzle_idx = (self.puzzle_idx + 1) % len(PUZZLES)
                        self.cargar_puzzle(self.puzzle_idx)
                        continue
                
                celda = self.pixel_a_celda(mx, my)
                if celda:
                    if event.button == 1:
                        self.dibujando = True
                        self.celda_inicio = celda
                        self.celda_actual = celda
                    elif event.button == 3:
                        self.borrar_rect_en(*celda)
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and self.dibujando:
                    self.dibujando = False
                    if self.celda_inicio and self.celda_actual:
                        r0, r1 = min(self.celda_inicio[0], self.celda_actual[0]), max(self.celda_inicio[0], self.celda_actual[0])
                        c0, c1 = min(self.celda_inicio[1], self.celda_actual[1]), max(self.celda_inicio[1], self.celda_actual[1])
                        self.agregar_rect(r0, c0, r1, c1)
                    self.celda_inicio, self.celda_actual = None, None

    def _accion_resolver(self):
        if self.resolviendo: 
            return
        self.resolviendo = True
        self.mostrar_mensaje("🤖 El Solucionador Sintético está calculando...", BTN_SIGUIENTE["normal"], 0)
        self.dibujar()
        
        try:
            # LLAMADO AL MÓDULO CONECTADO EXTERNO
            solucion = resolver(self.pistas, self.filas, self.cols)
            if solucion:
                self.rects_usuario = solucion
                self.mostrar_mensaje("✅ ¡Solución perfecta encontrada por Backtracking! 🤖", BTN_RESOLVER["normal"], 200)
            else:
                self.mostrar_mensaje("❌ Este mapa no posee solución válida", BTN_LIMPIAR["normal"], 180)
        except Exception:
            self.mostrar_mensaje("❌ Error de comunicación con el solucionador", BTN_LIMPIAR["normal"], 180)
        finally:
            self.resolviendo = False

    def ejecutar(self):
        clock = pygame.time.Clock()
        while True:
            self.manejar_eventos()
            self.efectos.actualizar()
            self.dibujar()
            clock.tick(60)

if __name__ == "__main__":
    juego = Shikaku()
    juego.ejecutar()