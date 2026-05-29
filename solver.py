"""
Shikaku - Solucionador Sintético (Backtracking)
Vanesa Florez y Angy Bautista
Proyecto Análisis de Algoritmos 2026-10
Pontificia Universidad Javeriana
"""

def obtener_rectangulos_posibles(fila, col, num, filas, cols):
    """Calcula todas las combinaciones de rectángulos de área 'num' que cubren la celda (fila, col)."""
    resultado = []
    try:
        for h in range(1, filas + 1):
            if num % h != 0: 
                continue
            w = num // h
            if w > cols: 
                continue
            
            # Desplazar el rectángulo para ver en qué posiciones encierra la pista
            for r0 in range(max(0, fila - h + 1), min(filas - h, fila) + 1):
                for c0 in range(max(0, col - w + 1), min(cols - w, col) + 1):
                    resultado.append((r0, c0, r0 + h - 1, c0 + w - 1))
    except Exception:
        return []
    return resultado

def celdas_de_rect(r0, c0, r1, c1):
    """Retorna la lista de todas las coordenadas (r, c) dentro de un rectángulo."""
    return [(r, c) for r in range(r0, r1 + 1) for c in range(c0, c1 + 1)]

def resolver(pistas, filas, cols):
    """
    Algoritmo de Backtracking principal para solucionar el Shikaku.
    Retorna una lista de tuplas (r0, c0, r1, c1) o None si no hay solución.
    """
    try:
        opciones = []
        for (fila, col, num) in pistas:
            ops = obtener_rectangulos_posibles(fila, col, num, filas, cols)
            if not ops: 
                return None
            opciones.append(ops)
        
        asignados = [None] * len(pistas)
        ocupado = {}
        
        def backtrack(idx):
            if idx == len(pistas): 
                return True
                
            for rect in opciones[idx]:
                celdas = celdas_de_rect(*rect)
                
                # Poda 1: Intersección con otros rectángulos
                if any(c in ocupado for c in celdas): 
                    continue
                
                # Poda 2: Verificar que no encierre más de una pista
                pistas_en_rect = sum(1 for (pr, pc, _) in pistas if rect[0] <= pr <= rect[2] and rect[1] <= pc <= rect[3])
                if pistas_en_rect != 1: 
                    continue
                
                # Registrar celdas ocupadas
                for c in celdas: 
                    ocupado[c] = idx
                asignados[idx] = rect
                
                if backtrack(idx + 1): 
                    return True
                
                # Backtrack (Deshacer cambio)
                for c in celdas: 
                    del ocupado[c]
                asignados[idx] = None
                
            return False
        
        if backtrack(0): 
            return asignados
    except Exception as e:
        print(f"Error en backtracking: {e}")
    return None