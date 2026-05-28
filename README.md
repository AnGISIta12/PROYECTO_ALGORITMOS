# Shikaku Game

Un juego interactivo del puzzle **Shikaku** desarrollado en Python con Pygame. Incluye un solucionador automático usando algoritmos de backtracking.

## Descripción

Shikaku es un puzzle que desafía tu lógica y habilidades de resolución de problemas. El objetivo es dividir una grilla en rectángulos siguiendo reglas específicas.

### Reglas del Juego
- **Divide la grilla en rectángulos** que no se solapan
- **Cada rectángulo debe contener exactamente UN número**
- **Ese número indica el área exacta del rectángulo** (filas × columnas)

Ejemplo: Un número 6 podría ser un rectángulo de 2×3 o 3×2.

##  Controles

| Acción | Descripción |
|--------|-------------|
| **Clic izquierdo** | Dibuja un rectángulo arrastrando desde una celda |
| **Clic derecho** | Borra el rectángulo en esa celda |
| **Botón "Resolver"** | El algoritmo resuelve el puzzle automáticamente |
| **Botón "Limpiar"** | Borra todos los rectángulos dibujados |
| **Botón "Siguiente ▶"** | Carga un puzzle diferente |

##  Características

✅ **Interfaz gráfica intuitiva** con Pygame  
✅ **4 puzzles predefinidos** (fácil 5×5, medio 6×6, difícil 7×7, maestro 8×8)  
✅ **Generador aleatorio** de tableros 6×6 y 8×8  
✅ **Modo Humano o Sintético** con resolución instantánea o animada  
✅ **Solucionador automático** modular en `solver.py` usando backtracking  
✅ **Validación en tiempo real** de las soluciones  
✅ **Colores distintivos** para cada rectángulo dibujado  
✅ **Mensajes de feedback** sobre el estado del puzzle  

##  Instalación

### Requisitos
- Python 3.7 o superior
- Pygame

### Pasos

1. **Clona o descarga este repositorio:**
   ```bash
   git clone https://github.com/tuusuario/shikaku-game.git
   cd shikaku-game
   ```

2. **Instala las dependencias:**
   ```bash
   pip install pygame
   ```

3. **Ejecuta el juego:**
   ```bash
   python shikaku.py
   ```

## 🧠 Algoritmo de Resolución

El solucionador implementa **backtracking** en el nuevo módulo `solver.py` y trabaja junto con la interfaz de `shikaku.py`:

1. Para cada número (pista) en la grilla, calcula todos los rectángulos posibles que cubran esa celda con el área correcta
2. Intenta asignar rectángulos de forma recursiva sin solapamientos
3. Verifica que cada rectángulo contenga exactamente una pista
4. Si encuentra una contradicción, retrocede (backtrack) y prueba otra opción
5. Retorna la solución completa cuando todas las celdas están cubiertas correctamente

> El módulo `solver.py` ahora separa la lógica de búsqueda de la interfaz gráfica, lo que facilita el mantenimiento y permite animar el proceso de backtracking desde `shikaku.py`.

## 📁 Estructura del Proyecto

```
shikaku-game/
├── shikaku.py      # Archivo principal del juego y la interfaz gráfica
├── solver.py       # Lógica del solucionador/backtracking separada del UI
├── README.md       # Este archivo
└── .gitignore      # (Opcional) Archivos ignorados por Git
```

##  Ejemplo de Uso

1. Ejecuta el programa
2. Se cargará un puzzle predefinido
3. Haz clic y arrastra para dibujar rectángulos
4. Intenta resolver el puzzle manualmente o usa el botón "Resolver"
5. Si resuelves correctamente, verás: **"¡Puzzle resuelto! 🎉"**
6. Presiona "Siguiente ▶" para cargar otro puzzle

## 👥 Autores

- **Vanesa Florez**
- **Angy Bautista**

Proyecto del curso **Análisis de Algoritmos 2026-10**

## 📝 Licencia

Este proyecto es de código abierto. Siéntete libre de modificarlo y compartirlo.

## 🐛 Troubleshooting

### El juego no inicia
- Asegúrate de tener Python instalado: `python --version`
- Verifica que pygame esté instalado: `pip list | grep pygame`

### Error de importación de pygame
```bash
pip install --upgrade pygame
```

### El juego es lento
- Cierra otras aplicaciones pesadas
- Reduce la resolución si es necesario

**¡Disfruta resolviendo puzzles!**
