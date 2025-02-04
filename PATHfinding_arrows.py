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

heuristic_weigth = 1

# Colores
black = (0, 0, 0)
white = (255, 255, 255)
gray = (169, 169, 169)
green = (0, 255, 0)
red = (255, 0, 0)
yellow = (255, 255, 0)  # Lista abierta
light_blue = (173, 216, 230)  # Lista cerrada
purple = (209, 125, 212)  # Camino más corto
text_color = black  # Color del texto

# Dimensiones de cada celda
cell_size = 90

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
g_score = {}  # Diccionario para almacenar el costo g de cada celda
h_score = {}  # Diccionario para almacenar el costo H de cada celda

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
text_font = pygame.font.SysFont(None, int(cell_size / 2.7))  # Fuente para el texto del costo
text_font_big = pygame.font.SysFont(None, int(cell_size / 1.94))  # Fuente para el texto del costo

# Función para dibujar la flecha
def draw_arrow(surface, color, start, end, arrow_size=10, arrow_angle=30):
    pygame.draw.line(surface, color, start, end, 2)  # Línea principal

    # Calcular los ángulos para las líneas de la punta de la flecha
    angle = math.atan2(end[1] - start[1], end[0] - start[0])
    angle1 = angle + math.radians(arrow_angle)
    angle2 = angle - math.radians(arrow_angle)

    # Calcular las posiciones de las líneas de la punta de la flecha
    end1 = (end[0] - arrow_size * math.cos(angle1), end[1] - arrow_size * math.sin(angle1))
    end2 = (end[0] - arrow_size * math.cos(angle2), end[1] - arrow_size * math.sin(angle2))

    # Dibujar la punta de la flecha
    pygame.draw.line(surface, color, end, end1, 2)
    pygame.draw.line(surface, color, end, end2, 2)

# Función para dibujar la cuadrícula
def draw_grid(show_weights=True, show_path=False):
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
                pygame.draw.rect(win, purple, rect)

            # Mostrar el f-score en la celda (simple suma de g + h)
            if show_weights and (grid[x][y] in [OPEN, CLOSED, END, PATH]):
                if (x, y) in g_score and (x, y) in h_score:
                    f_score = g_score[(x, y)] + h_score[(x, y)]  # Simple suma de g + h
                    f_text = text_font_big.render(str(f_score), True, text_color)
                    f_rect = f_text.get_rect(center=(x * cell_size + cell_size // 2, y * cell_size + cell_size // 2))
                    win.blit(f_text, f_rect)

            # Dibujar una flecha dentro del nodo apuntando al nodo de donde vino
            if (x, y) in came_from:  # Dibujar solo si el nodo viene de otro nodo
                from_x, from_y = came_from[(x, y)]
                
                if (from_x, from_y) != (x, y):  # Asegurarse de no dibujar la flecha en el mismo nodo
                    # Calcular el centro del nodo actual (donde estará la flecha)
                    center_x = x * cell_size + cell_size // 2
                    center_y = y * cell_size + cell_size // 2

                    # Calcular la posición desde la que viene la flecha (en el borde del nodo actual)
                    offset = 35  # Mover la flecha más cerca del borde
                    start_offset = 25  # Mover el inicio de la flecha lejos del centro
                    if from_x < x:  # Viene de la izquierda
                        line_start_x = center_x - offset
                        line_end_x = center_x - start_offset
                    elif from_x > x:  # Viene de la derecha
                        line_start_x = center_x + offset
                        line_end_x = center_x + start_offset
                    else:
                        line_start_x = line_end_x = center_x
                    
                    if from_y < y:  # Viene de arriba
                        line_start_y = center_y - offset
                        line_end_y = center_y - start_offset
                    elif from_y > y:  # Viene de abajo
                        line_start_y = center_y + offset
                        line_end_y = center_y + start_offset
                    else:
                        line_start_y = line_end_y = center_y

                    # Dibujar la flecha
                    draw_arrow(win, black, (line_end_x, line_end_y), (line_start_x, line_start_y))

            pygame.draw.rect(win, gray, rect, 1)



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
            
            f_score = tentative_g_score + heuristic_weigth * (tentative_h_score + 0.001 * tentative_h_score)

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
            elif reset_all_button.collidepoint(event.pos):
                reset_all_grid()
            elif path_found and action_button.collidepoint(event.pos):
                for pos in path:
                    if pos != end_pos:  # Verifica si la posición no es el nodo final
                        grid[pos[0]][pos[1]] = PATH
                draw_grid(show_weights=False, show_path=True)
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
    
    if step_by_step and next_step:
        path = a_star_step()  # Ejecutar un paso del algoritmo

    pygame.display.flip()
