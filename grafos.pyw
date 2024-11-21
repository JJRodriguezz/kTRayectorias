import sys
from PyQt5 import QtWidgets, QtGui
from grafos import Ui_MainWindow  # Asegúrate de que el archivo se llama así
from PyQt5.QtWidgets import QGraphicsScene

class GrafoApp(QtWidgets.QMainWindow):
    def __init__(self):
        super(GrafoApp, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Usar el graphicsView existente
        self.graphicsView = self.ui.graphicsView

        # Configurar la escena del QGraphicsView
        self.scene = QGraphicsScene()
        self.graphicsView.setScene(self.scene)

        # Conectar el botón para generar el grafo
        self.ui.pushButton.clicked.connect(self.dibujar_grafo)

    def dibujar_grafo(self):
        matriz = self.obtener_matriz()
        self.scene.clear()
        self.dibujar_nodos_y_aristas(matriz)

    def obtener_matriz(self):
        filas = self.ui.tableWidget.rowCount()
        columnas = self.ui.tableWidget.columnCount()
        matriz = []
        for i in range(filas):
            fila = []
            for j in range(columnas):
                item = self.ui.tableWidget.item(i, j)
                valor = int(item.text()) if item and item.text().isdigit() else 0
                fila.append(valor)
            matriz.append(fila)
        return matriz

    def dibujar_nodos_y_aristas(self, matriz):
        num_nodos = len(matriz)
        radius = 20
        spacing = 100
        posiciones = []

        # Dibujar nodos
        for i in range(num_nodos):
            x = i * spacing + 50
            y = 150
            posiciones.append((x, y))
            self.scene.addEllipse(x - radius, y - radius, 2 * radius, 2 * radius,
                                  pen=QtGui.QPen(), brush=QtGui.QBrush(QtGui.QColor("lightblue")))
            self.scene.addText(f"Nodo {i+1}").setPos(x - 10, y - 10)

        # Dibujar aristas
        for i in range(num_nodos):
            for j in range(i + 1, num_nodos):
                peso = matriz[i][j]
                if peso > 0:
                    x1, y1 = posiciones[i]
                    x2, y2 = posiciones[j]
                    self.scene.addLine(x1, y1, x2, y2, pen=QtGui.QPen(QtGui.QColor("black")))
                    mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
                    self.scene.addText(str(peso)).setPos(mid_x, mid_y)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = GrafoApp()
    window.show()
    sys.exit(app.exec_())