import pygame
import sys
import heapq
import math

# Inicializar Pygame
pygame.init()

# Dimensiones de la ventana
width, height = 1400, 780
win = pygame.display.set_mode((width, height))
pygame.display.set_caption("Pathfinding A*")

heuristic_weight = 1

# Colores
black = (0, 0, 0)
white = (255, 255, 255)
gray = (169, 169, 169)
green = (0, 255, 0)
red = (255, 0, 0)
yellow = (255, 255, 0)  # Lista abierta
light_blue = (173, 216, 230)  # Lista cerrada
purple = (172, 63, 176)  # Camino más corto

# Dimensiones de cada celda
# cell_size = 64
cell_size = 50

# Número de filas y columnas
cols = width // cell_size
rows = height // cell_size

# Estados de las celdas
FREE = 0
OBSTRUCTED = 1
START = 2
END = 3
OPEN = 6
CLOSED = 7
PATH = 8  # Estado de la celda para el camino más corto

# Inicializar la cuadrícula con todas las celdas libres
grid = [[FREE for _ in range(rows)] for _ in range(cols)]
g_score = {}  # Diccionario para almacenar el g-score de cada celda
h_score = {}  # Diccionario para almacenar el h-score de cada celda

# Posiciones de inicio y final
start_pos = (0, 0)
end_pos = (cols - 1, rows - 1)

# Asignar la celda de inicio y final
grid[start_pos[0]][start_pos[1]] = START
grid[end_pos[0]][end_pos[1]] = END

# Variables para el arrastre
dragging_start = False
dragging_end = False

# Variables para el modo paso a paso
step_by_step = False
open_set = []
came_from = {}
current = None
next_step = False
previous_steps = []
opened_in_step = []  # Lista de celdas abiertas en cada paso
path_found = False  # Ruta encontrada
path = []  # Ruta más corta

# Crear fuente para los botones y texto
font = pygame.font.SysFont(None, 36)

def draw_arrow(surface, color, start, end, arrow_size=20, arrow_angle=20):
    pygame.draw.line(surface, color, start, end, 3)  # Línea principal más gruesa

    # Calcular los ángulos para las líneas de la punta de la flecha
    angle = math.atan2(end[1] - start[1], end[0] - start[0])
    angle1 = angle + math.radians(arrow_angle)
    angle2 = angle - math.radians(arrow_angle)

    # Calcular las posiciones de las líneas de la punta de la flecha
    end1 = (end[0] - arrow_size * math.cos(angle1), end[1] - arrow_size * math.sin(angle1))
    end2 = (end[0] - arrow_size * math.cos(angle2), end[1] - arrow_size * math.sin(angle2))

    # Dibujar la punta de la flecha
    pygame.draw.line(surface, color, end, end1, 3)
    pygame.draw.line(surface, color, end, end2, 3)


# Función para dibujar la cuadrícula
def draw_grid(show_arrows=False, only_path=False):
    for x in range(cols):
        for y in range(rows):
            rect = pygame.Rect(x * cell_size, y * cell_size, cell_size, cell_size)
            if grid[x][y] == FREE:
                pygame.draw.rect(win, white, rect)
            elif grid[x][y] == OBSTRUCTED:
                pygame.draw.rect(win, black, rect)
            elif grid[x][y] == START:
                pygame.draw.rect(win, green, rect)
            elif grid[x][y] == END:
                pygame.draw.rect(win, red, rect)
            elif grid[x][y] == OPEN:
                pygame.draw.rect(win, yellow, rect)
            elif grid[x][y] == CLOSED:
                pygame.draw.rect(win, light_blue, rect)
            elif grid[x][y] == PATH:
                if not only_path:
                    pygame.draw.rect(win, purple, rect)
                else:
                    pygame.draw.rect(win, white, rect)

            pygame.draw.rect(win, gray, rect, 1)


show_arrows = False  # Nueva variable para controlar si las flechas deben mostrarse

def draw_arrows_on_path():
    line_thickness = 3  # Grosor de la línea

    for x, y in path:
        if (x, y) in came_from:
            from_x, from_y = came_from[(x, y)]

            if (from_x, from_y) != (x, y):  # Asegurarse de no dibujar la flecha en el mismo nodo
                # Calcular el centro del nodo actual
                start_x = x * cell_size + cell_size // 2
                start_y = y * cell_size + cell_size // 2

                # Calcular el centro del nodo de origen
                end_x = from_x * cell_size + cell_size // 2
                end_y = from_y * cell_size + cell_size // 2

                # Dibujar la línea desde el centro del nodo actual al centro del nodo de origen
                pygame.draw.line(win, purple, (start_x, start_y), (end_x, end_y), line_thickness)


# Función para calcular la heurística diagonal
def heuristic(a, b):
    dx = abs(a[0] - b[0])
    dy = abs(a[1] - b[1])
    D1 = 10  # Costo de moverse horizontal o verticalmente
    D2 = 14  # Costo de moverse en diagonal
    return D1 * (dx + dy) + (D2 - 2 * D1) * min(dx, dy)

# Función para encontrar los vecinos de una celda con sus costos
def get_neighbors(node):
    neighbors = []
    x, y = node
    # Movimientos adyacentes y diagonales
    for dx, dy, cost in [(-1, 0, 10), (1, 0, 10), (0, -1, 10), (0, 1, 10),
                         (-1, -1, 14), (-1, 1, 14), (1, -1, 14), (1, 1, 14)]:
        nx, ny = x + dx, y + dy
        if 0 <= nx < cols and 0 <= ny < rows and grid[nx][ny] != OBSTRUCTED:
            neighbors.append(((nx, ny), cost))
    return neighbors

# Función para realizar el algoritmo A* de forma paso a paso
def a_star_step():
    global current, next_step, path_found, path, step_by_step

    if current is None:
        if not open_set:
            return []
        _, current = heapq.heappop(open_set)
        previous_steps.append(current)
        opened_in_step.append([])  # Añadir nueva lista para este paso

    if current == end_pos:
        path = reconstruct_path(came_from, current)
        path_found = True
        step_by_step = False  # Detener la ejecución paso a paso
        return path

    for neighbor, move_cost in get_neighbors(current):
        tentative_g_score = g_score[current] + move_cost
        tentative_h_score = heuristic(neighbor, end_pos)

        if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
            came_from[neighbor] = current
            g_score[neighbor] = tentative_g_score
            h_score[neighbor] = tentative_h_score
            
            f_score = tentative_g_score + heuristic_weight * (tentative_h_score + 0.001 * tentative_h_score)

            heapq.heappush(open_set, (f_score, neighbor))
            print(f"Nodo {neighbor} -> f_score: {f_score}, g_score: {tentative_g_score}, h_score: {tentative_h_score}")

            if grid[neighbor[0]][neighbor[1]] not in [START, END]:
                grid[neighbor[0]][neighbor[1]] = OPEN
                if opened_in_step:  # Asegurarse de que la lista no esté vacía
                    opened_in_step[-1].append(neighbor)  # Registrar el nodo como abierto en este paso

    if grid[current[0]][current[1]] not in [START, END]:
        grid[current[0]][current[1]] = CLOSED

    current = None
    next_step = False
    draw_grid()
    pygame.display.flip()

    return []


# Función para inicializar el algoritmo A*
def init_a_star():
    global open_set, came_from, g_score, h_score, current, previous_steps, opened_in_step, path_found, path
    open_set = []
    heapq.heappush(open_set, (0, start_pos))
    came_from = {}
    g_score[start_pos] = 0
    h_score[start_pos] = heuristic(start_pos, end_pos)
    current = None
    previous_steps = []
    opened_in_step = []
    path_found = False
    path = []

# Función para reconstruir el camino encontrado
def reconstruct_path(came_from, current):
    path = []
    while current in came_from:
        path.append(current)
        current = came_from[current]

    path.reverse()  # Invertimos la lista para dibujar desde el inicio al final
    return path

# Función para reiniciar la cuadrícula sin cambiar los obstáculos, inicio y meta
def reset_grid():
    global g_score, h_score, step_by_step, path_found, path, current, open_set, came_from, previous_steps, opened_in_step

    # Limpiar las celdas que no sean obstáculos, inicio, ni meta
    for x in range(cols):
        for y in range(rows):
            if grid[x][y] not in [OBSTRUCTED, START, END]:
                grid[x][y] = FREE

    # Reiniciar los datos del algoritmo
    g_score = {}
    h_score = {}
    step_by_step = False
    path_found = False
    path = []
    current = None
    open_set = []
    came_from = {}
    previous_steps = []
    opened_in_step = []

    # Redibujar la cuadrícula
    draw_grid()
    pygame.display.flip()

# Función para reiniciar completamente la cuadrícula (incluyendo obstáculos, inicio y meta)
def reset_all_grid():
    global grid, start_pos, end_pos
    # Reiniciar todas las celdas a libres
    grid = [[FREE for _ in range(rows)] for _ in range(cols)]
    start_pos = (0, 0)
    end_pos = (cols - 1, rows - 1)
    grid[start_pos[0]][start_pos[1]] = START
    grid[end_pos[0]][end_pos[1]] = END
    reset_grid()  # También reinicia los datos del algoritmo

# Función para dibujar los botones
def draw_buttons():
    reset_all_button = pygame.Rect(50, height - 50, 120, 40)
    pygame.draw.rect(win, gray, reset_all_button)
    win.blit(font.render("Reset_all", True, black), (60, height - 45))

    reset_button = pygame.Rect(200, height - 50, 150, 40)
    pygame.draw.rect(win, gray, reset_button)
    win.blit(font.render("Reset", True, black), (210, height - 45))

    if path_found:
        path_button = pygame.Rect(400, height - 50, 195, 40)
        pygame.draw.rect(win, gray, path_button)
        win.blit(font.render("Ruta más corta", True, black), (410, height - 45))
        return reset_button, reset_all_button, path_button
    else:
        step_button = pygame.Rect(400, height - 50, 150, 40)
        pygame.draw.rect(win, gray, step_button)
        win.blit(font.render("Siguiente", True, black), (410, height - 45))
        return reset_button, reset_all_button, step_button

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            grid_x = x // cell_size
            grid_y = y // cell_size

            reset_button, reset_all_button, action_button = draw_buttons()

            if reset_button.collidepoint(event.pos):
                reset_grid()
                show_arrows = False  # Ocultar las flechas al hacer reset
            elif reset_all_button.collidepoint(event.pos):
                reset_all_grid()
                show_arrows = False  # Ocultar las flechas al hacer reset total
            elif path_found and action_button.collidepoint(event.pos):
                show_arrows = True  # Activar la visualización de las flechas
            elif not path_found and action_button.collidepoint(event.pos):
                if not step_by_step:
                    init_a_star()  # Inicializar el algoritmo para paso a paso
                    step_by_step = True
                next_step = True
            elif (grid_x, grid_y) == start_pos:
                dragging_start = True
            elif (grid_x, grid_y) == end_pos:
                dragging_end = True
            else:
                if grid[grid_x][grid_y] == FREE:
                    grid[grid_x][grid_y] = OBSTRUCTED
                elif grid[grid_x][grid_y] == OBSTRUCTED:
                    grid[grid_x][grid_y] = FREE

        if event.type == pygame.MOUSEBUTTONUP:
            dragging_start = False
            dragging_end = False

        if event.type == pygame.MOUSEMOTION:
            x, y = pygame.mouse.get_pos()
            grid_x = x // cell_size
            grid_y = y // cell_size

            if dragging_start:
                if (grid_x, grid_y) != end_pos:
                    grid[start_pos[0]][start_pos[1]] = FREE
                    start_pos = (grid_x, grid_y)
                    grid[start_pos[0]][start_pos[1]] = START

            if dragging_end:
                if (grid_x, grid_y) != start_pos:
                    grid[end_pos[0]][end_pos[1]] = FREE
                    end_pos = (grid_x, grid_y)
                    grid[end_pos[0]][end_pos[1]] = END

    win.fill(white)
    draw_grid()
    draw_buttons()

    if show_arrows:  # Dibujar las flechas si la bandera está activada
        draw_arrows_on_path()

    if step_by_step and next_step:
        path = a_star_step()  # Ejecutar un paso del algoritmo

    pygame.display.flip()
