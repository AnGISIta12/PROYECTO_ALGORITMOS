"""
Shikaku - Interfaz Gráfica de Usuario (Estructura Avanzada - Paleta Clara Premium)
Proyecto Análisis de Algoritmos 2026-10
Pontificia Universidad Javeriana
"""

import pygame
import sys
import math
import random
from solver import resolver, obtener_rectangulos_posibles, celdas_de_rect

# ── PALETA DE COLORES CLARA PREMIUM (RESTAURADA) ──────────────────────────────
FONDOS_GRADIENTE = [(240, 244, 248), (218, 226, 236)] # Degradado suave de fondo
COLOR_PANEL      = (255, 255, 255)      # Panel lateral blanco limpio
COLOR_GRID_BG    = (255, 255, 255)      # Fondo de la grilla blanco
GRILLA_LINEA     = (186, 199, 213)      # Líneas de la grilla gris/azul
TEXTO_PRINCIPAL  = (16, 42, 67)         # Azul oscuro para títulos
TEXTO_SECUNDARIO = (72, 101, 129)        # Gris/azul para etiquetas secundarias

# Paletas de Botones Estilizados
COLOR_PRIMARY    = (33, 150, 243)       # Azul brillante (Selección/Modos)
COLOR_PRIMARY_H  = (66, 165, 245)       # Hover azul
COLOR_SUCCESS    = (36, 150, 63)        # Verde (Resolver/Animar)
COLOR_SUCCESS_H  = (46, 175, 76)        # Hover verde
COLOR_DANGER     = (211, 47, 47)        # Rojo (Limpiar)
COLOR_DANGER_H   = (229, 57, 53)        # Hover rojo

# Colores Pastel para los Bloques (Restaurados)
COLORES_PASTEL = [
    (139, 218, 242),   # Celeste pastel
    (163, 230, 177),   # Verde menta pastel
    (255, 179, 186),   # Rosa pastel
    (255, 223, 186),   # Naranja pastel
    (255, 255, 186),   # Amarillo pastel
    (225, 190, 231),   # Morado pastel
    (178, 235, 242),   # Turquesa pastel
    (255, 204, 188)    # Coral pastel
]

PUZZLES = [
    {"nombre": "Principiante 5×5", "filas": 5, "cols": 5, "pistas": [(0,0,4),(0,3,3),(1,2,4),(2,4,3),(3,0,3),(2,1,2),(3,2,4),(4,1,1),(4,4,1)]},
    {"nombre": "Intermedio 6×6", "filas": 6, "cols": 6, "pistas": [(0,1,3),(0,4,3),(1,0,4),(1,2,4),(1,4,4),(3,1,3),(3,4,3),(4,0,4),(4,2,4),(4,4,4)]},
    {"nombre": "Experto 7×7", "filas": 7, "cols": 7, "pistas": [(0,1,3),(0,3,4),(0,5,2),(1,0,4),(1,2,2),(1,5,4),(2,3,4),(3,0,4),(3,2,1),(3,5,4),(4,2,4),(4,4,1),(5,0,4),(5,5,3),(6,3,3),(6,5,2)]},
    {"nombre": "Maestro 8×8", "filas": 8, "cols": 8, "pistas": [(0,2,4),(0,6,8),(1,0,6),(1,4,4),(3,1,8),(3,5,12),(4,3,2),(4,7,4),(5,0,4),(6,4,6),(7,1,2),(7,6,4)]}
]

class ShikakuClaroPro:
    def __init__(self):
        pygame.init()
        self.ancho_pantalla = 1050
        self.alto_pantalla  = 680
        self.pantalla = pygame.display.set_mode((self.ancho_pantalla, self.alto_pantalla))
        pygame.display.set_caption("Shikaku Solver Pro - Pontificia Universidad Javeriana")
        
        # Fuentes nativas compatibles con Emojis
        self.font_title = pygame.font.SysFont("Segoe UI", 20, bold=True)
        self.font_label = pygame.font.SysFont("Segoe UI", 12, bold=True)
        self.font_ui    = pygame.font.SysFont("Segoe UI Emoji", 13, bold=False)
        self.font_grid  = pygame.font.SysFont("Segoe UI", 18, bold=True)
        
        self.puzzle_idx = 0
        self.modo_juego = "Humano"
        self.velocidad_anim = 150  # Delay en milisegundos para la animación
        self.mensaje = "Bienvenido al Panel de Control"
        self.mensaje_color = TEXTO_PRINCIPAL
        
        self.rects_usuario = []
        self.dibujando = False
        self.celda_inicio = None
        self.celda_actual = None
        self.hover_rect = None
        
        self.cargar_puzzle(self.puzzle_idx)
        
    def cargar_puzzle(self, idx):
        p = PUZZLES[idx]
        self.filas = p["filas"]
        self.cols  = p["cols"]
        self.pistas = p["pistas"]
        self.nombre_puzzle = p["nombre"]
        self.rects_usuario = []
        self._calcular_geometria_grilla()
        
    def generar_aleatorio(self, dim):
        self.mensaje = "Generando mapa dinámico..."
        intentos = 0
        while intentos < 50:
            pistas_test = []
            num_pistas = dim + 2
            celdas_usadas = set()
            for _ in range(num_pistas):
                f, c = random.randint(0, dim-1), random.randint(0, dim-1)
                if (f, c) not in celdas_usadas:
                    pistas_test.append((f, c, random.choice([2, 3, 4, 6])))
                    celdas_usadas.add((f, c))
            
            sol = resolver(pistas_test, dim, dim)
            if sol:
                nuevas_pistas = []
                for idx, r in enumerate(sol):
                    area = (r[2]-r[0]+1) * (r[3]-r[1]+1)
                    nuevas_pistas.append((r[0], r[1], area))
                
                self.filas = dim
                self.cols = dim
                self.pistas = nuevas_pistas
                self.nombre_puzzle = f"Aleatorio {dim}×{dim}"
                self.rects_usuario = []
                self._calcular_geometria_grilla()
                self.mensaje = "✨ Nuevo mapa generado"
                return
            intentos += 1
        self.mensaje = "❌ Intente de nuevo el mapa aleatorio"

    def _calcular_geometria_grilla(self):
        area_juego_x = 280
        ancho_disp = self.ancho_pantalla - area_juego_x - 60
        alto_disp  = self.alto_pantalla - 100
        
        self.tam_celda = min(ancho_disp // self.cols, alto_disp // self.filas)
        self.grid_x = area_juego_x + (ancho_disp - self.tam_celda * self.cols) // 2
        self.grid_y = 50 + (alto_disp - self.tam_celda * self.filas) // 2

    def pixel_a_celda(self, px, py):
        col = (px - self.grid_x) // self.tam_celda
        fila = (py - self.grid_y) // self.tam_celda
        if 0 <= fila < self.filas and 0 <= col < self.cols:
            return (int(fila), int(col))
        return None

    def dibujar_fondo_gradiente(self):
        """Dibuja el fondo degradado original claro en el área derecha."""
        for y in range(self.alto_pantalla):
            factor = y / self.alto_pantalla
            r = int(FONDOS_GRADIENTE[0][0] + factor * (FONDOS_GRADIENTE[1][0] - FONDOS_GRADIENTE[0][0]))
            g = int(FONDOS_GRADIENTE[0][1] + factor * (FONDOS_GRADIENTE[1][1] - FONDOS_GRADIENTE[0][1]))
            b = int(FONDOS_GRADIENTE[0][2] + factor * (FONDOS_GRADIENTE[1][2] - FONDOS_GRADIENTE[0][2]))
            pygame.draw.line(self.pantalla, (r, g, b), (280, y), (self.ancho_pantalla, y))

    def dibujar(self):
        self.dibujar_fondo_gradiente()
        self._dibujar_panel_lateral()
        
        # Área de juego (Matriz)
        gx, gy = self.grid_x, self.grid_y
        t_celda = self.tam_celda
        pygame.draw.rect(self.pantalla, COLOR_GRID_BG, (gx, gy, t_celda*self.cols, t_celda*self.filas))
        
        # Pintar rectángulos creados con tonos pasteles translúcidos
        for i, (r0, c0, r1, c1) in enumerate(self.rects_usuario):
            base_color = COLORES_PASTEL[i % len(COLORES_PASTEL)]
            x, y = gx + c0*t_celda, gy + r0*t_celda
            w, h = (c1-c0+1)*t_celda, (r1-r0+1)*t_celda
            
            surf = pygame.Surface((w, h), pygame.SRCALPHA)
            surf.fill((*base_color, 200)) # Opacidad suave pastel original
            self.pantalla.blit(surf, (x, y))
            
            borde_color = (int(base_color[0]*0.6), int(base_color[1]*0.6), int(base_color[2]*0.6))
            borde_w = 3 if self.hover_rect == (r0, c0, r1, c1) else 1
            
            # Línea arreglada correctamente con self.hover_rect
            pygame.draw.rect(self.pantalla, TEXTO_PRINCIPAL if self.hover_rect == (r0, c0, r1, c1) else borde_color, (x, y, w, h), borde_w)
            
        # Dibujar previsualización dinámica de arrastre
        if self.dibujando and self.celda_inicio and self.celda_actual:
            r0, r1 = min(self.celda_inicio[0], self.celda_actual[0]), max(self.celda_inicio[0], self.celda_actual[0])
            c0, c1 = min(self.celda_inicio[1], self.celda_actual[1]), max(self.celda_inicio[1], self.celda_actual[1])
            x, y = gx + c0*t_celda, gy + r0*t_celda
            w, h = (c1-c0+1)*t_celda, (r1-r0+1)*t_celda
            
            surf_previa = pygame.Surface((w, h), pygame.SRCALPHA)
            surf_previa.fill((33, 150, 243, 100))
            self.pantalla.blit(surf_previa, (x, y))
            pygame.draw.rect(self.pantalla, COLOR_PRIMARY, (x, y, w, h), 2)

        # Líneas internas de la cuadrícula
        for f in range(self.filas):
            for c in range(self.cols):
                pygame.draw.rect(self.pantalla, GRILLA_LINEA, (gx + c*t_celda, gy + f*t_celda, t_celda, t_celda), 1)
        pygame.draw.rect(self.pantalla, TEXTO_PRINCIPAL, (gx, gy, t_celda*self.cols, t_celda*self.filas), 3)

        # Círculos y números de las pistas
        for (f, c, num) in self.pistas:
            cx, cy = gx + c*t_celda + t_celda//2, gy + f*t_celda + t_celda//2
            pygame.draw.circle(self.pantalla, (245, 248, 250), (cx, cy), t_celda // 2 - 6)
            pygame.draw.circle(self.pantalla, TEXTO_SECUNDARIO, (cx, cy), t_celda // 2 - 6, 1)
            txt = self.font_grid.render(str(num), True, TEXTO_PRINCIPAL)
            self.pantalla.blit(txt, (cx - txt.get_width()//2, cy - txt.get_height()//2))

        # Indicador superior del mapa
        txt_mapa = self.font_title.render(f" Mapa: {self.nombre_puzzle}", True, TEXTO_PRINCIPAL)
        self.pantalla.blit(txt_mapa, (gx, 20))

        pygame.display.flip()

    def _dibujar_panel_lateral(self):
        # Panel Estructural Lateral Izquierdo (Fondo Claro Limpio)
        pygame.draw.rect(self.pantalla, COLOR_PANEL, (0, 0, 280, self.alto_pantalla))
        pygame.draw.line(self.pantalla, GRILLA_LINEA, (280, 0), (280, self.alto_pantalla), 1)
        
        lbl_panel = self.font_title.render(">>Panel de Control", True, TEXTO_PRINCIPAL)
        self.pantalla.blit(lbl_panel, (20, 20))
        pygame.draw.line(self.pantalla, GRILLA_LINEA, (20, 55), (260, 55), 1)
        
        self.botones = {}
        mouse_p = pygame.mouse.get_pos()
        
        def crear_boton(texto, x, y, w, h, paleta_normal, paleta_hover, key, t_blanco=True):
            rect = pygame.Rect(x, y, w, h)
            self.botones[key] = rect
            hover = rect.collidepoint(mouse_p)
            color = paleta_hover if hover else paleta_normal
            pygame.draw.rect(self.pantalla, color, rect, border_radius=6)
            col_t = (255, 255, 255) if t_blanco else TEXTO_PRINCIPAL
            txt_surf = self.font_ui.render(texto, True, col_t)
            self.pantalla.blit(txt_surf, (x + w//2 - txt_surf.get_width()//2, y + h//2 - txt_surf.get_height()//2))
            return hover

        # ── SECCIÓN 1: SELECTOR DE NIVELES ───────────────────────────────────
        lbl_niv = self.font_label.render("SELECCIONAR NIVEL BASE", True, TEXTO_SECUNDARIO)
        self.pantalla.blit(lbl_niv, (20, 75))
        
        y_offset = 100
        for i, p in enumerate(PUZZLES):
            es_activo = (self.puzzle_idx == i)
            p_normal = COLOR_PRIMARY if es_activo else (230, 235, 241)
            crear_boton(f"🔹 {p['nombre']}", 20, y_offset, 240, 32, p_normal, COLOR_PRIMARY_H, f"nv_{i}", t_blanco=es_activo)
            y_offset += 38

        # ── SECCIÓN 2: GENERADOR COMPATIBLE ─────────────────────────────────
        pygame.draw.line(self.pantalla, GRILLA_LINEA, (20, y_offset + 5), (260, y_offset + 5), 1)
        lbl_gen = self.font_label.render("GENERADOR ALEATORIO DINÁMICO", True, TEXTO_SECUNDARIO)
        self.pantalla.blit(lbl_gen, (20, y_offset + 15))
        
        crear_boton("⚡ Generar 6×6", 20, y_offset + 40, 115, 35, (200, 214, 229), COLOR_PRIMARY_H, "gen_6", t_blanco=False)
        crear_boton("⚡ Generar 8×8", 145, y_offset + 40, 115, 35, (200, 214, 229), COLOR_PRIMARY_H, "gen_8", t_blanco=False)
        y_offset += 90

        # ── SECCIÓN 3: PERFILES DE JUEGO (HUMANO / SINTÉTICO) ───────────────
        pygame.draw.line(self.pantalla, GRILLA_LINEA, (20, y_offset + 5), (260, y_offset + 5), 1)
        lbl_modo = self.font_label.render("PERFIL DE JUEGO ACTIVO", True, TEXTO_SECUNDARIO)
        self.pantalla.blit(lbl_modo, (20, y_offset + 15))
        
        c_hum = COLOR_PRIMARY if self.modo_juego == "Humano" else (230, 235, 241)
        c_sin = COLOR_PRIMARY if self.modo_juego == "Sintético" else (230, 235, 241)
        crear_boton("👤 Humano", 20, y_offset + 40, 115, 35, c_hum, COLOR_PRIMARY_H, "modo_hum", t_blanco=(self.modo_juego == "Humano"))
        crear_boton("🤖 Sintético", 145, y_offset + 40, 115, 35, c_sin, COLOR_PRIMARY_H, "modo_sin", t_blanco=(self.modo_juego == "Sintético"))
        y_offset += 95

        # ── SECCIÓN 4: COMANDOS DEL SOLVER Y PANEL DE MENSAJES ───────────────
        pygame.draw.line(self.pantalla, GRILLA_LINEA, (20, y_offset + 5), (260, y_offset + 5), 1)
        lbl_ctrl = self.font_label.render("EJECUCIÓN DEL ALGORITMO", True, TEXTO_SECUNDARIO)
        self.pantalla.blit(lbl_ctrl, (20, y_offset + 15))
        
        if self.modo_juego == "Sintético":
            crear_boton("🔥 RESOLVER INSTANTÁNEO", 20, y_offset + 40, 240, 38, COLOR_SUCCESS, COLOR_SUCCESS_H, "run_solve")
            crear_boton("🎬 ANIMAR BACKTRACKING", 20, y_offset + 85, 240, 38, (124, 58, 237), (109, 40, 217), "run_anim")
        else:
            crear_boton("🔒 Manual: Arrastrar Clic Izq.", 20, y_offset + 40, 240, 38, (240, 244, 248), (240, 244, 248), "bloqueado", t_blanco=False)
            
        crear_boton("🧹 LIMPIAR TABLERO", 20, self.alto_pantalla - 110, 240, 35, COLOR_DANGER, COLOR_DANGER_H, "clear")
        
        # Display de Consola Inferior
        pygame.draw.rect(self.pantalla, (240, 244, 248), (15, self.alto_pantalla - 60, 250, 45), border_radius=4)
        pygame.draw.rect(self.pantalla, GRILLA_LINEA, (15, self.alto_pantalla - 60, 250, 45), 1, border_radius=4)
        txt_msg = self.font_ui.render(self.mensaje, True, self.mensaje_color)
        self.pantalla.blit(txt_msg, (25, self.alto_pantalla - 48))

    def verificar_solucion(self):
        ocupado = {}
        for r0, c0, r1, c1 in self.rects_usuario:
            for f in range(r0, r1 + 1):
                for c in range(c0, c1 + 1):
                    if (f, c) in ocupado: return False, "⚠️ Bloques encimados detectados"
                    ocupado[(f, c)] = True
        
        if len(ocupado) != self.filas * self.cols:
            return False, f"💡 Faltan {self.filas * self.cols - len(ocupado)} celdas"
            
        for r0, c0, r1, c1 in self.rects_usuario:
            area = (r1 - r0 + 1) * (c1 - c0 + 1)
            pistas_en = [(f, c, n) for (f, c, n) in self.pistas if r0 <= f <= r1 and c0 <= c <= c1]
            if len(pistas_en) != 1 or pistas_en[0][2] != area:
                return False, "❌ Área o número incorrecto"
        return True, "🎉 ¡Puzzle completado con éxito! 🎉"

    def animar_backtracking(self):
        self.rects_usuario = []
        self.mensaje = "Calculando trayectorias..."
        
        opciones = []
        for (fila, col, num) in self.pistas:
            ops = obtener_rectangulos_posibles(fila, col, num, self.filas, self.cols)
            opciones.append(ops)
            
        asignados = [None] * len(self.pistas)
        ocupado = {}
        
        def backtrack_visual(idx):
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()

            if idx == len(self.pistas): return True
            
            for rect in opciones[idx]:
                celdas = celdas_de_rect(*rect)
                if any(c in ocupado for c in celdas): continue
                
                pistas_en_rect = sum(1 for (pr, pc, _) in self.pistas if rect[0] <= pr <= rect[2] and rect[1] <= pc <= rect[3])
                if pistas_en_rect != 1: continue
                
                for c in celdas: ocupado[c] = idx
                asignados[idx] = rect
                
                self.rects_usuario = [r for r in asignados if r is not None]
                self.dibujar()
                pygame.time.delay(self.velocidad_anim)
                
                if backtrack_visual(idx + 1): return True
                
                for c in celdas: del ocupado[c]
                asignados[idx] = None
                
                self.rects_usuario = [r for r in asignados if r is not None]
                self.dibujar()
                pygame.time.delay(self.velocidad_anim)
                
            return False

        if backtrack_visual(0):
            self.mensaje = "✅ Solución secuencial lista"
            self.mensaje_color = COLOR_SUCCESS
        else:
            self.mensaje = "❌ Sin solución matemática"
            self.mensaje_color = COLOR_DANGER

    def ejecutar(self):
        clock = pygame.time.Clock()
        while True:
            mx, my = pygame.mouse.get_pos()
            celda_m = self.pixel_a_celda(mx, my)
            
            if celda_m:
                self.celda_actual = celda_m
                for r in self.rects_usuario:
                    if r[0] <= celda_m[0] <= r[2] and r[1] <= celda_m[1] <= r[3]:
                        self.hover_rect = r; break
                else: self.hover_rect = None
            else: self.hover_rect = None
                
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                    
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    for i in range(len(PUZZLES)):
                        if self.botones[f"nv_{i}"].collidepoint(event.pos):
                            self.puzzle_idx = i
                            self.cargar_puzzle(i)
                            self.mensaje = f"Cargado: {PUZZLES[i]['nombre']}"
                            self.mensaje_color = TEXTO_PRINCIPAL
                    
                    if self.botones["clear"].collidepoint(event.pos):
                        self.rects_usuario = []
                        self.mensaje = "Tablero reseteado"
                        self.mensaje_color = TEXTO_PRINCIPAL
                    elif self.botones["modo_hum"].collidepoint(event.pos):
                        self.modo_juego = "Humano"
                        self.rects_usuario = []
                    elif self.botones["modo_sin"].collidepoint(event.pos):
                        self.modo_juego = "Sintético"
                        self.rects_usuario = []
                    elif self.botones["gen_6"].collidepoint(event.pos):
                        self.generar_aleatorio(6)
                    elif self.botones["gen_8"].collidepoint(event.pos):
                        self.generar_aleatorio(8)
                    elif self.modo_juego == "Sintético" and self.botones["run_solve"].collidepoint(event.pos):
                        sol = resolver(self.pistas, self.filas, self.cols)
                        if sol:
                            self.rects_usuario = sol
                            self.mensaje = "✅ Solución instantánea"
                            self.mensaje_color = COLOR_SUCCESS
                        else: 
                            self.mensaje = "❌ Imposible solucionar"
                            self.mensaje_color = COLOR_DANGER
                    elif self.modo_juego == "Sintético" and self.botones["run_anim"].collidepoint(event.pos):
                        self.animar_backtracking()
                        
                    if self.modo_juego == "Humano" and celda_m:
                        if event.button == 1:
                            self.dibujando = True
                            self.celda_inicio = celda_m
                        elif event.button == 3:
                            self.rects_usuario = [r for r in self.rects_usuario if not (r[0]<=celda_m[0]<=r[2] and r[1]<=celda_m[1]<=r[3])]
                            
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1 and self.dibujando:
                        self.dibujando = False
                        if self.celda_inicio and self.celda_actual:
                            r0, r1 = min(self.celda_inicio[0], self.celda_actual[0]), max(self.celda_inicio[0], self.celda_actual[0])
                            c0, c1 = min(self.celda_inicio[1], self.celda_actual[1]), max(self.celda_inicio[1], self.celda_actual[1])
                            
                            if any(r0<=f<=r1 and c0<=c<=c1 for (f, c, _) in self.pistas):
                                self.rects_usuario = [r for r in self.rects_usuario if (r[2]<r0 or r[0]>r1 or r[3]<c0 or r[1]>c1)]
                                self.rects_usuario.append((r0, c0, r1, c1))
                                ok, msg = self.verificar_solucion()
                                self.mensaje = msg
                                self.mensaje_color = COLOR_SUCCESS if ok else TEXTO_PRINCIPAL
                            else:
                                self.mensaje = "⚠️ El bloque debe tener una pista"
                                self.mensaje_color = COLOR_DANGER
                                
            self.dibujar()
            clock.tick(60)

if __name__ == "__main__":
    juego = ShikakuClaroPro()
    juego.ejecutar()