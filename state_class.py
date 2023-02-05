from PyQt6.QtCore import QObject, pyqtSignal
import pyqtgraph as pg
import numpy as np

from chunky_loader import chunky_loader
from clustered_spectra import ClusteredSpectra

def hex_to_rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    return np.array(tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3)))


class State(QObject):
    def __init__(self):
        super().__init__()
        self.mode = []  # all the display instructions are stored here
        self.left_coordinate=np.array([0,0],dtype=np.int64) # the position of the curser linked to the left image
        self.right_coordinate=np.array([0,0],dtype=np.int64) # the position of the curser linked to the right image
        self.left_img = np.array([])  # the image displayed on the left
        self.right_img = np.array([])  # the image displayed on the right
        self.cluster_colors = np.array([[0,0,0],[0,0,0]])

    def set_left_coordinate(self, coord):
        self.left_coordinate=np.array(coord,dtype=np.int64)
        self.left_img=self.clustered_spectra \
            .get_cluster_by_spectrum_position_index(self.left_coordinate.tolist()).centroid

    def get_left_coordinate(self):
        return self.left_coordinate

    def set_right_coordinate(self, coord):
        self.right_coordinate=np.array(coord,dtype=np.int64)
        self.right_img=self.clustered_spectra \
            .get_cluster_by_spectrum_position_index(self.right_coordinate.tolist()).centroid

    def get_right_coordinate(self):
        return self.right_coordinate

    def load_data(self):
        bin_factor = 2
        file_name = pg.widgets.FileDialog.FileDialog.getOpenFileName()[0]
        self.data_array, self.spectra = chunky_loader(file_name, bin_factor)
        self.clustered_spectra = ClusteredSpectra(self.data_array, self.spectra)
        self.cluster_colors = np.zeros((self.data_array.shape[0], self.data_array.shape[1], 3))
        self.cluster_labels = np.zeros((self.data_array.shape[0], self.data_array.shape[1]))

        for cluster in self.clustered_spectra.walk_clusters(0):
            running_avg_spectrum = np.zeros((self.data_array.shape[2], self.data_array.shape[3]))
            for spectrum in self.clustered_spectra._clusters[cluster].spectra:
                index = self.clustered_spectra.spectra[spectrum].data
                self.cluster_labels[index[0], index[1]] = cluster
                color_tuple = hex_to_rgb(self.clustered_spectra._clusters[cluster].color)
                self.cluster_colors[index[0], index[1], :] = color_tuple
                running_avg_spectrum += self.data_array[index[0], index[1], :, :]
            running_avg_spectrum /= len(self.clustered_spectra._clusters[cluster].spectra)
            self.clustered_spectra._clusters[cluster].centroid = running_avg_spectrum




