import sys
import os
import datetime
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QGraphicsView, QAction, QFileDialog, QTableWidget, QTableWidgetItem, QDialog, QVBoxLayout
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPen
from PyQt5.QtCore import Qt, QPointF

class CoordinatesTableWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Coordinates Table")
        self.table_widget = QTableWidget(self)
        self.table_widget.setColumnCount(2)
        self.table_widget.setHorizontalHeaderLabels(["X", "Y"])
        layout = QVBoxLayout(self)
        layout.addWidget(self.table_widget)
        
        self.loadCoordinatesFromFile()

    def addCoordinateToTable(self, x, y):
        row_position = self.table_widget.rowCount()
        self.table_widget.insertRow(row_position)
        self.table_widget.setItem(row_position, 0, QTableWidgetItem(str(x)))
        self.table_widget.setItem(row_position, 1, QTableWidgetItem(str(y)))

    def loadCoordinatesFromFile(self):
        if hasattr(self.parent(), "points_of_interest"):
            for point in self.parent().points_of_interest:
                self.addCoordinateToTable(point.x(), point.y())

class ImageViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.image = None
        self.points_of_interest = []
        self.save_file_path = self.generateFilePath()

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Image Viewer")
        self.setGeometry(100, 100, 800, 600)

        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene)
        self.setCentralWidget(self.view)

        open_action = QAction("Open Image", self)
        open_action.triggered.connect(self.openImage)

        self.toolbar = self.addToolBar("Toolbar")
        self.toolbar.addAction(open_action)

        self.view.setScene(self.scene)
        self.view.setMouseTracking(True)
        self.view.mousePressEvent = self.mousePressEvent

        self.showCoordinatesTable()

    def generateFilePath(self):
        current_datetime = datetime.datetime.now()
        filename = current_datetime.strftime("%Y-%m-%d_%H-%M-%S.txt")
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)

    def openImage(self):
        options = QFileDialog.Options()
        filePath, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Images (*.png *.jpg *.bmp);;All Files (*)", options=options)

        if filePath:
            self.image = QImage(filePath)
            pixmap = QPixmap.fromImage(self.image)
            self.scene.clear()
            self.scene.addPixmap(pixmap)
            self.points_of_interest = []
            self.updateScene()

    def mousePressEvent(self, event):
        if self.image and event.button() == Qt.LeftButton:
            point = self.view.mapToScene(event.pos())
            self.points_of_interest.append(point)
            self.updateScene()
            self.savePoints()
            if hasattr(self, "table_window"):
                self.table_window.addCoordinateToTable(point.x(), point.y())

    def updateScene(self):
        self.scene.clear()
        pixmap = QPixmap.fromImage(self.image)
        self.scene.addPixmap(pixmap)

        painter = QPainter(pixmap)
        pen = QPen(Qt.red)
        painter.setPen(pen)

        for point in self.points_of_interest:
            painter.drawEllipse(point, 5, 5)

        painter.end()
        self.view.setScene(self.scene)

    def savePoints(self):
        with open(self.save_file_path, 'a') as file:
            idx = len(self.points_of_interest) - 1
            point = self.points_of_interest[-1]
            file.write(f"{idx}, {point.x()}, {point.y()}\n")

    def showCoordinatesTable(self):
        self.table_window = CoordinatesTableWindow(self)
        self.table_window.move(self.geometry().right() + 10, self.geometry().top())
        self.table_window.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageViewer()
    window.show()
    sys.exit(app.exec_())
