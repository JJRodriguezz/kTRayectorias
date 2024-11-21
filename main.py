import sys
import numpy as np
import random
from PyQt5 import QtWidgets, QtGui, QtCore
from grafos_ui import Ui_MainWindow
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsTextItem, QGraphicsItem

class Nodo(QGraphicsEllipseItem):
    def __init__(self, x, y, radius, id, app):
        super(Nodo, self).__init__(-radius, -radius, 2 * radius, 2 * radius)
        self.setBrush(QtGui.QBrush(QtGui.QColor("lightblue")))
        self.setPen(QtGui.QPen(QtCore.Qt.black))
        self.id = id
        self.setFlag(QGraphicsEllipseItem.ItemIsMovable)
        self.setFlag(QGraphicsEllipseItem.ItemSendsGeometryChanges)
        self.text_item = QGraphicsTextItem(f"Nodo {self.id}", self)
        self.text_item.setPos(-10, -10)
        self.app = app
        self.aristas = []

    def agregar_arista(self, arista):
        self.aristas.append(arista)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange:
            for arista in self.aristas:
                arista.actualizar_posiciones()
        return super().itemChange(change, value)

class Arista(QGraphicsLineItem):
    def __init__(self, nodo1, nodo2, peso, scene):
        super(Arista, self).__init__()
        self.nodo1 = nodo1
        self.nodo2 = nodo2
        self.peso = peso
        self.scene = scene
        self.text_item = QGraphicsTextItem(str(self.peso))
        self.scene.addItem(self.text_item)
        self.actualizar_posiciones()
        self.setFlag(QGraphicsLineItem.ItemIsSelectable)
        self.setPen(QtGui.QPen(QtCore.Qt.black))

    def actualizar_posiciones(self):
        x1, y1 = self.nodo1.scenePos().x(), self.nodo1.scenePos().y()
        x2, y2 = self.nodo2.scenePos().x(), self.nodo2.scenePos().y()
        self.setLine(x1, y1, x2, y2)
        self.text_item.setPos((x1 + x2) / 2, (y1 + y2) / 2)

    def mousePressEvent(self, event):
        self.setPen(QtGui.QPen(QtCore.Qt.red, 3))
        self.nodo1.setPen(QtGui.QPen(QtCore.Qt.red, 3))
        self.nodo2.setPen(QtGui.QPen(QtCore.Qt.red, 3))
        super().mousePressEvent(event)

class GrafoApp(QtWidgets.QMainWindow):
    def __init__(self):
        super(GrafoApp, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.lblTitulo2 = QtWidgets.QLabel(self)
        self.lblTitulo2.setGeometry(600, 50, 100, 100)
        pixmap = QtGui.QPixmap("Recurso-1-8.png").scaled(110, 110, QtCore.Qt.KeepAspectRatio)
        self.lblTitulo2.setPixmap(pixmap)

        self.graphicsView = self.ui.graphicsView
        self.scene = QGraphicsScene()
        self.graphicsView.setScene(self.scene)

        self.ui.btnPintarGrafo.clicked.connect(self.dibujar_grafo)
        self.ui.btnCalcularTrayectoriasK2.clicked.connect(self.calcular_trayectorias_k2)
        self.ui.btnCalcularTrayectoriasK3.clicked.connect(self.calcular_trayectorias_k3)

        # Conectar el clic en el encabezado de tableWidget para generar una matriz aleatoria
        self.ui.tableWidget.horizontalHeader().sectionClicked.connect(self.llenar_matriz_aleatoria)

        # Conectar el cambio en tableWidget para actualizar tableAdyacencia automáticamente
        self.ui.tableWidget.itemChanged.connect(self.actualizar_matriz_adyacencia)

        self.nodos = []
        self.aristas = []

    def actualizar_matriz_adyacencia(self):
        """Actualizar tableAdyacencia automáticamente con la matriz de adyacencia"""
        matriz_pesos = self.obtener_matriz()
        # Generar matriz de adyacencia a partir de la matriz de pesos
        matriz_adyacencia = [[1 if matriz_pesos[i][j] > 0 #Llenar con 1's cuando hay alguna conexión
        else 0 for j in range(len(matriz_pesos[i]))] for i in range(len(matriz_pesos))] #Llenar con 0's cuando no hay conexion
    
        filas = len(matriz_adyacencia)
        columnas = len(matriz_adyacencia[0]) if filas > 0 else 0 #Establecer las dimensiones de la tabla para poder 
        self.ui.tableAdyacencia.setRowCount(filas)               #plasmar la matriz correctamente
        self.ui.tableAdyacencia.setColumnCount(columnas)
    
        for i in range(filas):
            for j in range(columnas):
                item = QtWidgets.QTableWidgetItem(str(matriz_adyacencia[i][j])) #Se recorre la matriz de adyacencia y para cada entrada
                self.ui.tableAdyacencia.setItem(i, j, item)                     #Se crea un elemento con el número correspondiente
                                                                                #para llenar la tabla con la matriz obtenida
    def calcular_trayectorias_k2(self):
        """Calcular la matriz A^2 de la matriz de adyacencia y mostrar en tableTrayectorias2"""
        matriz_adyacencia = self.obtener_matriz_adyacencia()
        trayectoria_2 = self.calcular_trayectorias_k(matriz_adyacencia, 2)
        self.mostrar_resultado_tabla(trayectoria_2, self.ui.tableTrayectorias2)

    def calcular_trayectorias_k3(self):
        """Calcular la matriz A^3 de la matriz de adyacencia y mostrar en tableTrayectorias3"""
        matriz_adyacencia = self.obtener_matriz_adyacencia()
        trayectoria_3 = self.calcular_trayectorias_k(matriz_adyacencia, 3)
        self.mostrar_resultado_tabla(trayectoria_3, self.ui.tableTrayectorias3)

    def calcular_trayectorias_k(self, matriz, k):
        """Calcular las trayectorias A^k de la matriz de adyacencia"""
        matriz_np = np.array(matriz) #Convertir la matriz en arreglo para trabajar con numpy
        matriz_potencia_k = np.linalg.matrix_power(matriz_np, k) #Elevar la matriz al exponente deseado
        return matriz_potencia_k.tolist() #Volver a convertir el arreglo en matriz para que pueda imprimiser en la tabla de QT

    def mostrar_resultado_tabla(self, matriz, table):
        """Mostrar la matriz de trayectorias en la tabla especificada"""
        num_filas = len(matriz)
        num_columnas = len(matriz[0])
        table.setRowCount(num_filas)
        table.setColumnCount(num_columnas)
        for i, fila in enumerate(matriz):
            for j, valor in enumerate(fila):
                item = QtWidgets.QTableWidgetItem(str(valor))
                table.setItem(i, j, item)
                
    def obtener_matriz_adyacencia(self):
        """Obtener la matriz de adyacencia de tableAdyacencia"""
        filas = self.ui.tableAdyacencia.rowCount()
        columnas = self.ui.tableAdyacencia.columnCount()
        matriz_adyacencia = [
            [int(self.ui.tableAdyacencia.item(i, j).text()) if self.ui.tableAdyacencia.item(i, j) else 0
            for j in range(columnas)]      #Extraer los valores de cada celda, poniendo los 0's y 1's correspondientes
            for i in range(filas)          
        ]                                  #Convierte los datos en una lista de lists (una matriz)
        return matriz_adyacencia

    def obtener_matriz(self):
        """Obtener la matriz de pesos de tableWidget"""
        filas = self.ui.tableWidget.rowCount()
        columnas = self.ui.tableWidget.columnCount()    #Lo mismo que la de arriba pero esta solo extrae la matriz de pesos, NO es binaria
        matriz = [[int(self.ui.tableWidget.item(i, j).text()) if self.ui.tableWidget.item(i, j) else 0 for j in range(columnas)] for i in range(filas)]
        return matriz

    def dibujar_grafo(self):
        """Dibujar el grafo a partir de la matriz de adyacencia"""
        self.scene.clear()
        self.nodos.clear()
        self.aristas.clear()
        matriz = self.obtener_matriz()
        self.dibujar_nodos_y_aristas(matriz)

    def dibujar_nodos_y_aristas(self, matriz):
        """Dibujar los nodos y aristas en la escena"""
        num_nodos = len(matriz)
        radius = 20
        width = self.graphicsView.width() - 100
        height = self.graphicsView.height() - 100
        for i in range(num_nodos):
            x = random.randint(50, width)
            y = random.randint(50, height)
            nodo = Nodo(x, y, radius, i + 1, self)
            nodo.setPos(x, y)
            self.scene.addItem(nodo)
            self.nodos.append(nodo)

        for i in range(num_nodos):
            for j in range(i + 1, num_nodos):
                peso = matriz[i][j]
                if peso > 0:
                    nodo1 = self.nodos[i]
                    nodo2 = self.nodos[j]
                    arista = Arista(nodo1, nodo2, peso, self.scene)
                    self.aristas.append(arista)
                    self.scene.addItem(arista)
                    nodo1.agregar_arista(arista)
                    nodo2.agregar_arista(arista)

    def llenar_matriz_aleatoria(self, index):
        """Genera una matriz aleatoria de pesos con distintos niveles de conexión.
        Dependiendo de la densidad de conexión generada aleatoriamente, algunos 
        nodos pueden estar completamente conectados entre sí, mientras que otros 
        estarán parcialmente conectados o desconectados.
        """
        filas = self.ui.tableWidget.rowCount()
        
        # Generar una "densidad de conexión" aleatoria para esta matriz
        # Esto define la probabilidad de conexión entre nodos:
        # un valor alto indica más conexiones, un valor bajo menos conexiones.
        densidad_conexion = random.uniform(0.3, 1.0)  # 0.3 permite menos conexiones, 1.0 es completamente conectado
        
        for i in range(filas):
            for j in range(filas):
                if i == j:
                    # Diagonal principal en 0 porque no hay bucles en los nodos
                    valor = '0'
                else:
                    # Generar una conexión aleatoriamente en función de la densidad
                    # mayor densidad = mayor probabilidad de tener conexión
                    if random.random() < densidad_conexion:
                        # Generar un peso de conexión aleatorio si hay conexión
                        valor = str(random.randint(1, 100))
                    else:
                        # Sin conexión (peso 0)
                        valor = '0'
                
                # Establecer el valor en la celda correspondiente
                self.ui.tableWidget.setItem(i, j, QtWidgets.QTableWidgetItem(valor))

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = GrafoApp()
    window.show()
    sys.exit(app.exec_())