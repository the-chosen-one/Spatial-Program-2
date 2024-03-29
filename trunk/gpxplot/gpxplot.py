from PyQt4.QtCore import *
from PyQt4.QtGui import *
import pyqtgraph, gpxpy, numpy, sys

# Global with all plotables:
axis_options = {}

# wrapper that adds the function:
def axisOption(name):
    def wrapper(func):
        axis_options[name] = func
        return func
    return wrapper

# Helper functions to extract the desired data:
@axisOption('distance')
def getDistance(pts):
    """ Extract distance in km """
    prev = pts[0]
    deltas = []
    for pt in pts:
        deltas.append(pt.distance_3d(prev) * 0.001)
        prev = pt
    return numpy.array(deltas).cumsum()

@axisOption('time')
def getTime(pts):
    """ extract time in seconds """
    t0 = pts[0].time
    t = [(pt.time - t0).total_seconds() for pt in pts]
    return numpy.array(t)

@axisOption('speed')
def getSpeed(pts):
    # in km/h
    v = [p1.speed(p2) for p1, p2 in zip(pts[:-1], pts[1:])]
    v.append(0.0) # fixup length for plot
    v = numpy.array(v) * (3600.0 / 1000.0)
    # zero v > 30 km/h
    highs = v > 30.0
    v[highs] = 0
    return v

@axisOption('filtered speed')
def getFilteredSpeed(pts):
    v = getSpeed(pts)
    # smooth with hanning filter:
    N = 10
    w = numpy.hanning(N*2+1) # generate window with odd number of points
    v = numpy.convolve(w/w.sum(), v)[N:-N]
    return v

@axisOption('beats per minute')
def getBeatsPerMinute(pts):
    bpm = [pt.hr for pt in pts]
    bpm = numpy.array(bpm)
    return bpm

@axisOption('beats per kilometer')
def getBeatsPerKilometer(pts):
    # beats / km
    return (getBeatsPerMinute(pts) * 60) / getFilteredSpeed(pts)

class TrackModel(QAbstractListModel):
    def __init__(self):
        QAbstractListModel.__init__(self)
        self.segments = []
        self.doFillModel()
    def doFillModel(self):
        """ Loads all gpx files in the current directory. """
        d = QDir()
        for fn in d.entryList(["*.gpx"]):
            fn = str(fn)
            with open(fn, 'r') as f:
                gpx = gpxpy.parse(f)
            for track in gpx.tracks:
                for segment in track.segments:
                    if segment.length_3d() > 500.0:
                        # Only segments longer then 500.0 meters
                        segment.filename = fn
                        segment.plot = False
                        self.segments.append(segment)
    def rowCount(self, parent=None):
        return len(self.segments)
    def data(self, idx, role):
        segment = self.segments[idx.row()]
        if role == Qt.DisplayRole:
            return segment.filename
        elif role == Qt.CheckStateRole:
            return Qt.Checked if segment.plot else Qt.Unchecked
        return QVariant()
    def setData(self, idx, value, role):
        if role == Qt.CheckStateRole:
            segment = self.segments[idx.row()]
            segment.plot = value.toBool()
            self.dataChanged.emit(idx, idx)
            return True
        return QAbstractListModel.setData(self, idx, value, role)
    def flags(self, idx):
        return QAbstractListModel.flags(self, idx) | Qt.ItemIsUserCheckable
    
class GpxPlot(QWidget):
    def __init__(self):
        QWidget.__init__(self, None)
        l = QVBoxLayout(self)
        self.plotWidget = pyqtgraph.PlotWidget()
        l.addWidget(self.plotWidget)
        self.xCombo = QComboBox()
        self.xCombo.addItems(axis_options.keys())
        self.xCombo.activated[str].connect(self.comboChange)
        self.yCombo = QComboBox()
        self.yCombo.addItems(axis_options.keys())
        self.yCombo.activated[str].connect(self.comboChange)
        l.addWidget(self.xCombo)
        l.addWidget(self.yCombo)
        self.tableView = QListView()
        l.addWidget(self.tableView)

        self.trackModel = TrackModel()
        self.tableView.setModel(self.trackModel)
        self.trackModel.dataChanged.connect(self.updatePlots)
    def comboChange(self, txt):
        self.updatePlots()
    def modelChange(self, topLeft, bottomRight):
        self.updatePlots()
    def updatePlots(self):
        xtype = str(self.xCombo.currentText())
        ytype = str(self.yCombo.currentText())
        pi = self.plotWidget.getPlotItem()
        pi.clear()
        pi.setLabel('bottom', text=xtype)
        pi.setLabel('left', text=ytype)
        pen = pyqtgraph.mkPen({'color': "r", 'width': 2})

        # Select the tracks to plot:
        for segment in [g for g in self.trackModel.segments if g.plot]:
            pts = segment.points
            x = axis_options[xtype](pts)
            y = axis_options[ytype](pts)
            pi.plot(x, y, pen=pen)

app = QApplication(sys.argv)
gp = GpxPlot()
gp.show()
app.exec_()