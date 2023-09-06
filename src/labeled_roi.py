from PySide6 import QtGui
from PySide6.QtCore import QPointF
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QGraphicsTextItem
from pyqtgraph import RectROI


class LabeledROI(RectROI):
    """
    Normal ROI with a label attached.


    ============== =============================================================
    **Arguments**
    label          String for the label
    \**args        All extra keyword arguments are passed to ROI()
    ============== =============================================================

    """

    def __init__(self, *args, label=None, **kwargs):
        RectROI.__init__(self, *args, **kwargs)
        if label is not None:
            self.label = QGraphicsTextItem(label, self)
            self.label.setDefaultTextColor(QtGui.QColor('blue'))
            font = QFont("Times", pointSize=15, weight=QFont.Medium, italic=False)
            self.label.setFont(font)
            self.label.setPos(QPointF(self.boundingRect().center().x() - (self.label.boundingRect().width() / 2), self.state['size'][1]))
        else:
            self.label = None

    def paint(self, p, opt, widget):
        """ p es un objeto QPainter """
        super().paint(p, opt, widget)
        if self.label is not None:
            self.label.setPos(QPointF(self.boundingRect().center().x() - (self.label.boundingRect().width() / 2), self.state['size'][1]))
