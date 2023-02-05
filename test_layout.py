import numpy as np

import pyqtgraph as pg
from pyqtgraph.Qt import QtGui
#from kmean_functions import *
from h5file import *
import kmean_functions as kmf
from pyqtgraph.Qt import QtWidgets

from test import chunky_loader

global mode
mode='edc'
global section
section=[200,700,350,600]
HEIGHT=768
WIDTH=1366

pg.mkQApp()
win = QtWidgets.QMainWindow()
win.resize(WIDTH,HEIGHT)
win.show()


cw = QtWidgets.QWidget()
win.setCentralWidget(cw)

layout = QtWidgets.QGridLayout()
cw.setLayout(layout)
layout.setSpacing(0)

#layout.setColumnMinimumWidth(0,WIDTH/2)
#layout.setColumnMinimumWidth(1,WIDTH/2)
layout.setRowMinimumHeight(0,int(HEIGHT*1/3))
layout.setRowMinimumHeight(1,int(HEIGHT*1/3))
# pw1 is the left most plot
pw1 = pg.GraphicsLayoutWidget() 
layout.addWidget(pw1,0,0,2,2)
p1_figure=pw1.addPlot(row=0,col=1)
hz1 = pg.LinearRegionItem(orientation='horizontal', movable=True,brush=pg.mkBrush(None))
hz1.setZValue(500)
p1_figure.addItem(hz1)
lr1 = pg.LinearRegionItem(movable=True,brush=pg.mkBrush(None))
lr1.setZValue(500)
p1_figure.addItem(lr1)

p1_mdc = pw1.addPlot(row=2,col=1)
p1_mdc.setMaximumHeight(90)

p1_edc = pw1.addPlot(row=0,col=0)
p1_edc.setMaximumHeight(850)
p1_edc.setMaximumWidth(180)

# pw2 is the left most plot
pw2 = pg.GraphicsLayoutWidget() 
layout.addWidget(pw2,0,2,2,2)

p2_figure=pw2.addPlot(row=0,col=1)
hz2= pg.LinearRegionItem(orientation='horizontal', movable=True,brush=pg.mkBrush(None))
hz2.setZValue(500)
p2_figure.addItem(hz2)
lr2 = pg.LinearRegionItem(movable=True,brush=pg.mkBrush(None))
lr2.setZValue(500)
p2_figure.addItem(lr2)

p2_mdc = pw2.addPlot(row=1,col=1)
p2_mdc.setMaximumHeight(90)



p2_edc = pw2.addPlot(row=0,col=0)
p2_edc.setMaximumHeight(850)
p2_edc.setMaximumWidth(180)



# pw3 for the split display
pw3 = pg.PlotWidget(name='Plot3')
layout.addWidget(pw3,2,0,4,1)






#green is the black
button= QtWidgets.QPushButton('split_white')
layout.addWidget(button, 2, 3)
button1= QtWidgets.QPushButton('split_black')
layout.addWidget(button1, 2, 2)

button2= QtWidgets.QPushButton('updatefile')
layout.addWidget(button2, 4, 3)

button_iso= QtWidgets.QPushButton('show_iso')
layout.addWidget(button_iso, 4, 2)
button_save= QtWidgets.QPushButton('save_spatial')
layout.addWidget(button_save, 5, 2)

img1 = pg.ImageItem()
pw3.addItem(img1)
pw3.setAspectLocked()
roi_show=pg.ROI([0,0],[1,1],movable=False, rotatable=False, resizable=False)
pw3.addItem(roi_show)
colors = [
            (0,0,0),
            (255,0,0),
            (255, 255, 255),
            (0, 0, 255),
        ]

# color map
cmap = pg.ColorMap(pos=np.linspace(0.0, 1.0, 4), color=colors)

# setting color map to the image view
img1.setColorMap(cmap)


img_green=pg.ImageItem()
p1_figure.addItem(img_green,row=1,col=1)
hist1 = pg.HistogramLUTItem()
hist1.setImageItem(img_green)
pw1.addItem(hist1,row=0,col=2)

img_red=pg.ImageItem()
p2_figure.addItem(img_red,row=1,col=1)
hist2 = pg.HistogramLUTItem()
hist2.setImageItem(img_red)
pw2.addItem(hist2,row=0,col=2)

iso = pg.IsocurveItem(level=0, pen='g')
iso.setParentItem(img1)
iso.setZValue(5)



edcRadio = QtWidgets.QRadioButton('edc')
mdcRadio = QtWidgets.QRadioButton('mdc')
layout.addWidget(edcRadio, 3, 2)
layout.addWidget(mdcRadio, 3, 3)
edcRadio.setChecked(True)

def update_edc_mdc():
    global mode
    global data
    global ts1,ts2
    global data1, data2
    global bool_iso
    global x_range,z_range
    global E_range,k_range
    global section
    fileName1 = pg.widgets.FileDialog.FileDialog.getOpenFileName(parent = win)[0]
    # x_range,z_range=get_arrays_X_Z(fileName1)
    E_range,k_range=get_arrays_E_K(fileName1)
    section=[200,700,350,600]
    if mode=='edc':
        # spec,data=load_edc(fileName1,section)
        spec,data=chunky_loader(fileName1,2)
        x_range = {s.position[0] for s in spec}
        z_range = {s.position[1] for s in spec}
    # else:
    #     spec,data=load_mdc(fileName1,section)
    ts1,ts2=kmf.split(spec)

    d=np.zeros((data.shape[2],data.shape[3]))
    # for s in spec:
    #     if s.k[0]<0.5:
    #         d[s.index[0]][s.index[1]]=10
    for s in spec:
        d[s.index[0]][s.index[1]] = (s.k[0] + 0.25)*(1/1.25)
    print(d)

    roi_show.setPos(min(x_range), min(z_range))
    roi_show.setSize((max(x_range)-min(x_range), max(z_range)-min(z_range)))

    roi_show.setZValue(10)

    img1.setImage(d)
    # print(f"{(min(x_range), min(z_range), max(x_range), max(z_range))}")
    # print(f"{(min(x_range), min(z_range), max(x_range)-min(x_range), max(z_range)-min(z_range))}")
    # print((len(x_range),len(z_range)))
    # print(f"pixel size before rect: {img1.pixelSize()}")
    # print(f"{img1.width()=}, {img1.height()=}")
    img1.setRect(min(x_range), min(z_range), img1.width()*(max(x_range)-min(x_range))/len(x_range), img1.height()*(max(z_range)-min(z_range))/len(z_range))
    # print(f"{img1.boundingRect()=}")
    # print(f"pixel size before rect: {img1.pixelSize()}")

    bool_iso=False
    draw_iso()

    
    data1=kmf.get_ave_spec(ts1,data)

    img_green.setImage(data1)
    img_green.setRect(k_range[0],E_range[0],k_range[-1]-k_range[0],E_range[-1]-E_range[0])
    


    data2=kmf.get_ave_spec(ts2,data)
    img_red.setImage(data2)
    img_red.setRect(k_range[0],E_range[0],k_range[-1]-k_range[0],E_range[-1]-E_range[0])

    hz1.setRegion((E_range[0],E_range[-1]))
    hz2.setRegion((E_range[0],E_range[-1]))
    lr1.setRegion((k_range[0],k_range[-1]))
    lr2.setRegion((k_range[0],k_range[-1]))

    pw3.setRange(xRange=(min(x_range), max(x_range)), yRange=(min(z_range), max(z_range)))
    #return ts1,ts2;


def draw_iso():
    global bool_iso
    

    brightness=kmf.show_intensity(data)
    oneD_brightness=brightness.flatten()
    iso.setData(brightness)
    if(bool_iso):
        iso.setLevel(np.mean(oneD_brightness)*0.75)
    else:
        iso.setLevel(0)




def split_green():
    global data
    global ts1,ts2
    global data1, data2
    global x_range,z_range
    global E_range,k_range
    s1=ts2
    ts1,ts2=kmf.split(s1)
    
    d=np.zeros((data.shape[2],data.shape[3]))
    # for s in s1:
    #     if s.k[0]<0.5:
    #         d[s.index[0]][s.index[1]]=10
    #     else:
    #         d[s.index[0]][s.index[1]]=5

    for s in s1:
        d[s.index[0]][s.index[1]] = (s.k[0] + 0.25)*(1/1.25)



    img1.setImage(d)
    #img1.setRect(x_range[0],z_range[0],x_range[-1]-x_range[0], z_range[-1]-z_range[0])
    # img1.setRect(min(x_range), min(z_range), (max(x_range)-min(x_range)), (max(z_range)-min(z_range)))
    img1.setRect(min(x_range), min(z_range), img1.width()*(max(x_range)-min(x_range))/len(x_range), img1.height()*(max(z_range)-min(z_range))/len(z_range))


    
    data1=kmf.get_ave_spec(ts1,data)
    img_green.setImage(data1,clear=True)
    img_green.setRect(k_range[0],E_range[0],k_range[-1]-k_range[0],E_range[-1]-E_range[0])


    
    data2=kmf.get_ave_spec(ts2,data)
    img_red.setImage(data2,clear=True)
    img_red.setRect(k_range[0],E_range[0],k_range[-1]-k_range[0],E_range[-1]-E_range[0])

    pw3.setRange(xRange=(min(x_range), max(x_range)), yRange=(min(z_range), max(z_range)))


def split_red():
    global data
    global ts1,ts2
    global data1, data2
    global x_range,z_range
    global E_range,k_range
    s1=ts1
    ts1,ts2=kmf.split(s1)

    d=np.zeros((data.shape[2],data.shape[3]))
    # for s in s1:
    #     if s.k[0]<0.5:
    #         d[s.index[0]][s.index[1]]=10
    #     else:
    #         d[s.index[0]][s.index[1]]=5
    # for s in s1:
    #     if s.k[0]<0.5:
    #         d[s.index[0]][s.index[1]]=s.k[0]
    #     else:
    #         d[s.index[0]][s.index[1]]=1-s.k[0]
    for s in s1:
        d[s.index[0]][s.index[1]] = (s.k[0] + 0.25)*(1/1.25)


    img1.setImage(d)
    # img1.setRect(x_range[0],z_range[0],x_range[-1]-x_range[0], z_range[-1]-z_range[0])
    # img1.setRect(min(x_range), min(z_range), (max(x_range)-min(x_range)), (max(z_range)-min(z_range)))
    img1.setRect(min(x_range), min(z_range), img1.width()*(max(x_range)-min(x_range))/len(x_range), img1.height()*(max(z_range)-min(z_range))/len(z_range))
    


    
    data1=kmf.get_ave_spec(ts1,data)
    img_green.setImage(data1)
    img_green.setRect(k_range[0],E_range[0],k_range[-1]-k_range[0],E_range[-1]-E_range[0])

    
    data2=kmf.get_ave_spec(ts2,data)
    img_red.setImage(data2)
    img_red.setRect(k_range[0],E_range[0],k_range[-1]-k_range[0],E_range[-1]-E_range[0])
    
    pw3.setRange(xRange=(min(x_range), max(x_range)), yRange=(min(z_range), max(z_range)))

def change_iso():
    global bool_iso
    if (bool_iso):
        bool_iso=False
        draw_iso()
    else:
        bool_iso=True
        draw_iso()


def save_xz_image():
    img1.save("test.png")

button1.clicked.connect(split_red)
button2.clicked.connect(update_edc_mdc)
button.clicked.connect(split_green)
button_iso.clicked.connect(change_iso)
button_save.clicked.connect(save_xz_image)



def updatePlot1_edc():
    global data1, data2,lr1,E_range,k_range,section
    left_index=(lr1.getRegion()[0]-k_range[0])/(k_range[1]-k_range[0])
    right_index=(lr1.getRegion()[1]-k_range[0])/(k_range[1]-k_range[0])
    selected = data1[int(left_index):int(right_index),:]
    p1_edc.setYLink(p1_figure)
    p1_edc.plot(x=selected.mean(axis=0),y=E_range, clear=True)
    section[2]=left_index
    section[3]=right_index
    

lr1.sigRegionChangeFinished.connect(updatePlot1_edc)

def updatePlot1_mdc():
    global data1, data2,hz1,E_range,k_range,section
    lower_index=(hz1.getRegion()[0]-E_range[0])/(E_range[1]-E_range[0])
    upper_index=(hz1.getRegion()[1]-E_range[0])/(E_range[1]-E_range[0])
    selected = data1[:,int(lower_index):int(upper_index)]
    p1_mdc.setXLink(p1_figure)
    
    p1_mdc.plot(x=k_range,y=selected.mean(axis=1),clear=True)
    section[0]=lower_index
    section[1]=upper_index

hz1.sigRegionChangeFinished.connect(updatePlot1_mdc)


def updatePlot2_edc():
    global data1, data2,lr2,E_range,k_range
    left_index=(lr2.getRegion()[0]-k_range[0])/(k_range[1]-k_range[0])
    right_index=(lr2.getRegion()[1]-k_range[0])/(k_range[1]-k_range[0])
    selected = data2[int(left_index):int(right_index),:]
    p2_edc.setYLink(p2_figure)
    p2_edc.plot(x=selected.mean(axis=0),y=E_range, clear=True)

lr2.sigRegionChangeFinished.connect(updatePlot2_edc)

def updatePlot2_mdc():
    global data1, data2,hz2,E_range,k_range
    lower_index=(hz2.getRegion()[0]-E_range[0])/(E_range[1]-E_range[0])
    upper_index=(hz2.getRegion()[1]-E_range[0])/(E_range[1]-E_range[0])
    selected = data2[:,int(lower_index):int(upper_index)]
    p2_mdc.setXLink(p2_figure)
    
    p2_mdc.plot(x=k_range,y=selected.mean(axis=1),clear=True)

hz2.sigRegionChangeFinished.connect(updatePlot2_mdc)



def setLevelMode():
    global mode
    mode = 'edc' if edcRadio.isChecked() else 'mdc'
        

edcRadio.toggled.connect(setLevelMode)

if __name__ == '__main__':
    pg.exec()
    
