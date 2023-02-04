import numpy as np

import pyqtgraph as pg
from pyqtgraph.Qt import QtGui
from pyqtgraph.Qt import QtWidgets

from state_class import State

#from h5file import *
#import kmean_functions as kmf




class GUI:
    def __init__(self):
        #super().__init__()
        
        HEIGHT=768
        WIDTH=1366

        pg.mkQApp()
        self.win = QtWidgets.QMainWindow()
        self.win.resize(WIDTH,HEIGHT)
        self.state=State()




        self.cw = QtWidgets.QWidget()
        self.win.setCentralWidget(self.cw)

        layout = QtWidgets.QGridLayout()
        self.cw .setLayout(layout)
        layout.setSpacing(0)

        #layout.setColumnMinimumWidth(0,WIDTH/2)
        #layout.setColumnMinimumWidth(1,WIDTH/2)
        layout.setRowMinimumHeight(0,int(HEIGHT*1/3))
        layout.setRowMinimumHeight(1,int(HEIGHT*1/3))
        # left_img_box is the left most plot
        left_img_box = pg.GraphicsLayoutWidget() 
        layout.addWidget(left_img_box,0,0,2,2)
        left_figure=left_img_box.addPlot(row=0,col=1)
        hz1 = pg.LinearRegionItem(orientation='horizontal', movable=True,brush=pg.mkBrush(None))
        hz1.setZValue(500)
        left_figure.addItem(hz1)
        lr1 = pg.LinearRegionItem(movable=True,brush=pg.mkBrush(None))
        lr1.setZValue(500)
        left_figure.addItem(lr1)

        left_mdc = left_img_box.addPlot(row=2,col=1)
        left_mdc.setMaximumHeight(90)

        left_edc = left_img_box.addPlot(row=0,col=0)
        left_edc.setMaximumHeight(850)
        left_edc.setMaximumWidth(180)

        # right_img_box is the left most plot
        right_img_box = pg.GraphicsLayoutWidget() 
        layout.addWidget(right_img_box,0,2,2,2)

        right_figure=right_img_box.addPlot(row=0,col=1)
        hz2= pg.LinearRegionItem(orientation='horizontal', movable=True,brush=pg.mkBrush(None))
        hz2.setZValue(500)
        right_figure.addItem(hz2)
        lr2 = pg.LinearRegionItem(movable=True,brush=pg.mkBrush(None))
        lr2.setZValue(500)
        right_figure.addItem(lr2)

        right_mdc = right_img_box.addPlot(row=1,col=1)
        right_mdc.setMaximumHeight(90)



        right_edc = right_img_box.addPlot(row=0,col=0)
        right_edc.setMaximumHeight(850)
        right_edc.setMaximumWidth(180)



        # split_display_box for the split display
        split_display_box = pg.PlotWidget(name='Plot3')
        layout.addWidget(split_display_box,2,0,4,1)

        #green is the black
        button= QtWidgets.QPushButton('split_white')
        layout.addWidget(button, 2, 3)
        button1= QtWidgets.QPushButton('split_black')
        layout.addWidget(button1, 2, 2)

        #botton file updates a new file 
        button_updatefile= QtWidgets.QPushButton('updatefile')
        layout.addWidget(button_updatefile, 4, 3)
        button_updatefile.clicked.connect(self.update_file)

        button_iso= QtWidgets.QPushButton('show_iso')
        layout.addWidget(button_iso, 4, 2)
        button_save= QtWidgets.QPushButton('save_spatial')
        layout.addWidget(button_save, 5, 2)

        self.split_img = pg.ImageItem()
        split_display_box.addItem(self.split_img)
        split_display_box.setAspectLocked()

        self.roi_left=pg.ROI([0,0],[1,1],rotatable=False)
        split_display_box.addItem(self.roi_left)
        self.roi_left.setZValue(20)
        self.roi_left.sigRegionChangeFinished.connect(self.change_left_roi)

        self.roi_right=pg.CircleROI([2,2],radius=0.5)
        split_display_box.addItem(self.roi_right)
        self.roi_right.setZValue(20)
        self.roi_right.sigRegionChangeFinished.connect(self.change_right_roi)


        colors = [
        (0,0,0),
        (255,0,0),
        (255, 255, 255),
        (0, 0, 255),
        ]

        # color map
        cmap = pg.ColorMap(pos=np.linspace(0.0, 1.0, 4), color=colors)

        # setting color map to the image view
        self.split_img.setColorMap(cmap)


        self.img_left=pg.ImageItem()
        left_figure.addItem(self.img_left,row=1,col=1)
        hist1 = pg.HistogramLUTItem()
        hist1.setImageItem(self.img_left)
        left_img_box.addItem(hist1,row=0,col=2)

        self.img_right=pg.ImageItem()
        right_figure.addItem(self.img_right,row=1,col=1)
        hist2 = pg.HistogramLUTItem()
        hist2.setImageItem(self.img_right)
        right_img_box.addItem(hist2,row=0,col=2)


        edcRadio = QtWidgets.QRadioButton('edc')
        mdcRadio = QtWidgets.QRadioButton('mdc')
        layout.addWidget(edcRadio, 3, 2)
        layout.addWidget(mdcRadio, 3, 3)
        edcRadio.setChecked(True)
        edcRadio.toggled.connect(self.setLevelMode)
        self.mode = 'edc'

        
        

    def update_file(self):
        #todo
        self.state.load_data()
        self.update_all_figure()
        return

    def setLevelMode(self):
        
        self.mode = 'edc' if edcRadio.isChecked() else 'mdc'

    def update_all_figure(self):
        self.split_img.setImage(self.state.cluster_colors)
        self.change_left_roi()
        self.change_right_roi()
        self.set_img_left()
        self.set_img_right()
        #todo
        return

    def set_p1_figure(self):
        # todo
        # self.split_img.setImage(np.array([[[0.5,1,1],[1,1,0],[1,0,1]],[[0.5,1,1],[1,1,0],[1,0,1]]]))
        self.split_img.setImage(self.state.cluster_colors)
        return

    def set_img_left(self):
        self.img_left.setImage(self.state.left_img.transpose())
        return

    def set_img_right(self):
        # todo
        self.img_right.setImage(self.state.right_img.transpose())
        return

    def change_left_roi(self):
        self.state.set_left_coordinate(self.roi_left.pos())
        self.set_img_left()
        print(self.state.get_left_coordinate())

    def change_right_roi(self):
        self.state.set_right_coordinate(self.roi_right.pos())
        self.set_img_right()
        print(self.state.get_right_coordinate())



    


if __name__ == '__main__':
    g=GUI()
    g.set_p1_figure()
    print(g.state.get_left_coordinate())
    g.win.show()
    pg.exec()
    
   

    



