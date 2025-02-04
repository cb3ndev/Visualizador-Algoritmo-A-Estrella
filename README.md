Visualizador Algoritmo A Estrella
=======

### Requisitos
- python 3.12.5
- pygame 2.6.0 

### Contenido
El script "PATHfinding.py" permite observar el funcionamiento del algoritmo de ruta A* en una cuadrícula, el movimiento permitido es hacia 8 direcciones (arriba, abajo, izquierda, derecha y sus 4 diagonales correspondientes), para la heurística se uso la distancia de tipo "Diagonal" 

![Distancia][1]

Antes de observar el algoritmo, se debe ubicar el punto de inicio (cuadro verde) y la meta (cuadro rojo) arrastrandolos en la cuadrícula, además se puede colocar obstáculos al hacer click en la cuadrícula (click de nuevo para borrarlos). Para observar el funcionamiento del algoritmo dar click en el botón de siguiente, y dar click en el botón de ruta más corta para observar dicha ruta. 
Los costos observados se calculan y ubican en el diagrama de visualización de la siguiente forma:

![diagrama1][2]
![diagrama2][3]

Ejemplo de funcionamiento del Script "PATHfinding.py":

![ejemplo1][4]

El script "PATHfinding_arrows.py" tiene la misma lógica que el primer script con la única diferencia de que solo muestra los costos F, y permite observar como es que el algoritmo halla la ruta más corta por medio de flechas, las flechas apuntan a su celda "Padre", es decir la celda desde la cuál se hizo el análisis para determinar sus costos según el algoritmo A estrella. 

Ejemplo de funcionamiento del Script "PATHfinding_arrows.py":

![ejemplo2][5]

Script creado para el video:
https://youtu.be/hQa9JTtq4Ok

Links (Fuentes)
------------------------
- http://theory.stanford.edu/~amitp/GameProgramming/
- http://theory.stanford.edu/~amitp/GameProgramming/AStarComparison.html#the-a-star-algorithm
- http://theory.stanford.edu/~amitp/GameProgramming/Heuristics.html#a-starx27s-use-of-the-heuristic

[1]: https://raw.githubusercontent.com/cb3ndev/Visualizador-Algoritmo-A-Estrella/refs/heads/main/img/diagonal.jpg
[2]: https://raw.githubusercontent.com/cb3ndev/Visualizador-Algoritmo-A-Estrella/refs/heads/main/img/diagrama1.JPG
[3]: https://raw.githubusercontent.com/cb3ndev/Visualizador-Algoritmo-A-Estrella/refs/heads/main/img/diagrama2.JPG
[4]: https://raw.githubusercontent.com/cb3ndev/Visualizador-Algoritmo-A-Estrella/refs/heads/main/img/ejemplo1.jpg
[5]: https://raw.githubusercontent.com/cb3ndev/Visualizador-Algoritmo-A-Estrella/refs/heads/main/img/ejemplo2.jpg