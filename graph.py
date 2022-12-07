class Graph:

    class Vertice:

        ''' Método constructor de la clase vertice '''
        def __init__(self, id):
            self.id = id # id --> Nombre o diferenciador del grafo
            self.coordenadas = None
            self.predecesor = None
            self.distancia = float('inf')
            self.visitado = False
            self.vecinos = []
        
        ''' Añade un id de un vertice de id (v) distinto como un vecino '''
        def agregar_vecino(self, v, p):
            if not v in self.vecinos:
                self.vecinos.append((v, p)) # Añadimos el id del vertice como vecino
    
    ''' Método constructor de la clase grafo '''
    def __init__(self):
        self.vertices = {}
        self.camino =[]

    ''' Añade o actualiza un vertice con cierto idn (v) '''
    def agregar_vertice(self, v):
        if not v in self.vertices:
            self.vertices[v] = self.Vertice(v) # Añadimos el vertice al diccionario
    
    def generar_arista(self, a, b, p):
        if a in self.vertices and b in self.vertices:
            self.vertices[a].agregar_vecino(b, p)
            self.vertices[b].agregar_vecino(a, p)

    def minimo(self, lista):
        if len(lista) > 0:
            min = self.vertices[lista[0]].distancia
            v = lista[0]
            for element in lista:
                if min > self.vertices[element].distancia:
                    min = self.vertices[element].distancia
                    v = element 
            return v
    
    def camino_vertice(self, a, b):
        camino = []
        actual = b
        while actual != None:
            camino.insert(0, actual)
            actual = self.vertices[actual].predecesor
        self.camino =  camino

    def dijkstra(self, a):
        if a in self.vertices:
            self.vertices[a].distancia = 0
            actual = a
            no_visitados = []

            for v in self.vertices:
                if v != a:
                    self.vertices[v].distancia = float('inf') # Todas las distancias como infinito
                self.vertices[v].predecesor = None # Predecesores nulos
                no_visitados.append(v) # Añadir nodos a no visitados

            while len(no_visitados) > 0:
                for arista in self.vertices[actual].vecinos:
                    if self.vertices[arista[0]].visitado == False:
                        if self.vertices[actual].distancia + arista[1] < self.vertices[arista[0]].distancia:
                            self.vertices[arista[0]].distancia = self.vertices[actual].distancia + arista[1]
                            self.vertices[arista[0]].predecesor = actual

                self.vertices[actual].visitado = True
                no_visitados.remove(actual)
                actual = self.minimo(no_visitados)
        else:
            return False
