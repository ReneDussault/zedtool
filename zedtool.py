import sys
import math
from PyQt5 import QtWidgets, QtGui, QtCore


class SelectionOverlay(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.start = QtCore.QPoint()
        self.end = QtCore.QPoint()
        self.drawing = False

        self.setWindowTitle("Screen Area Selector")
        self.setWindowFlags(
            QtCore.Qt.FramelessWindowHint | 
            QtCore.Qt.WindowStaysOnTopHint | 
            QtCore.Qt.Tool
        )

        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setCursor(QtCore.Qt.CrossCursor)

        desktop = QtWidgets.QApplication.desktop()
        self.setGeometry(desktop.geometry())

        self.shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("Esc"), self)
        self.shortcut.activated.connect(self.quit_app)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.activateWindow()
        self.setFocus()

        print("Overlay started. Drag with left mouse button to select area. Press ESC to exit.")


    def quit_app(self):
        print("Escape pressed. Exiting.")
        QtWidgets.QApplication.instance().quit()


    def paintEvent(self, event):
        qp = QtGui.QPainter(self)

        qp.fillRect(self.rect(), QtGui.QColor(0, 0, 0, 60))

        if self.drawing and not self.start.isNull() and not self.end.isNull():
            selection_rect = QtCore.QRect(self.start, self.end).normalized()

            # selected area transparent
            mask = QtGui.QRegion(self.rect())
            mask = mask.subtracted(QtGui.QRegion(selection_rect))

            qp.setClipRegion(mask)
            qp.fillRect(self.rect(), QtGui.QColor(0, 0, 0, 120))
            qp.setClipRect(self.rect())

            # green border
            qp.setPen(QtGui.QPen(QtGui.QColor(0, 255, 0), 2))
            qp.drawRect(selection_rect)

            # selected dimensions
            width = selection_rect.width()
            height = selection_rect.height()
            if width > 0 and height > 0:
                gcd = math.gcd(width, height)
                ratio = f"{width // gcd}:{height // gcd}"
                dimensions = f"{width}x{height} ({ratio})"

                qp.setPen(QtGui.QColor(255, 255, 255))
                qp.setFont(QtGui.QFont("Arial", 10, QtGui.QFont.Bold))

                text_rect = QtCore.QRect(
                    selection_rect.right() - 200, 
                    selection_rect.bottom() + 5, 
                    200, 
                    20
                )
                qp.fillRect(text_rect, QtGui.QColor(0, 0, 0, 180))
                qp.drawText(text_rect, QtCore.Qt.AlignCenter, dimensions)


    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.drawing = True
            self.start = event.pos()
            self.end = event.pos()
            self.update()


    def mouseMoveEvent(self, event):
        if self.drawing:
            self.end = event.pos()
            self.update()


    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton and self.drawing:
            self.drawing = False
            self.end = event.pos()

            # get rectangle data
            rect = QtCore.QRect(self.start, self.end).normalized()
            width = rect.width()
            height = rect.height()

            if width > 0 and height > 0:
                gcd = math.gcd(width, height)
                ratio = f"{width // gcd}:{height // gcd}"

                # show result
                QtWidgets.QMessageBox.information(
                    self, "Selection Result",
                    f"Width: {width} px\nHeight: {height} px\nAspect Ratio: {ratio}"
                )
                QtWidgets.QApplication.instance().quit()
            else:
                self.start = QtCore.QPoint()
                self.end = QtCore.QPoint()
                self.update()


    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.quit_app()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    overlay = SelectionOverlay()
    overlay.show()
    overlay.raise_()
    overlay.activateWindow()
    
    sys.exit(app.exec_())