from ctypes import sizeof
from dataclasses import dataclass
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, QThread
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QProgressBar, QLabel
from itertools import count
import time
import numpy as np
import h5py
import sys

import psutil

# Get the total available system RAM
total_ram = psutil.virtual_memory().total

# Get the used system RAM
used_ram = psutil.virtual_memory().used

# Calculate the available system RAM
available_ram = total_ram - used_ram

# Print the available system RAM
print(f'Available system RAM: {available_ram/1073741824} bytes')

@dataclass
class SpatialSpectrum:
    filename: str = ""
    k_bin_factor: int = 2
    e_bin_factor: int = 2
    x_array: np.ndarray = np.array([])
    y_array: np.ndarray = np.array([])
    binned_spectra: np.ndarray = np.array([])
    binned_dcs: np.ndarray = np.array([])
    full_spectra: np.ndarray = np.array([])
    full_dcs: np.ndarray = np.array([])

    def __str__(self) -> str:
        return f"{self.filename}"

def rebin(arr, bin_factor):
    new_shape=np.array(arr.shape)//bin_factor
    shape=(new_shape[0],arr.shape[0]//new_shape[0], new_shape[1],arr.shape[1]//new_shape[1])
    return arr.reshape(shape).mean(-1).mean(1)


class _SpectrumLoaderObject(QObject):
    result=pyqtSignal(int)
    progress=pyqtSignal(int)
    current_prime = pyqtSignal(int)
    spatial_spectrum = pyqtSignal(SpatialSpectrum)

    def __init__(self, parent=None, **kwargs):
        super().__init__(parent, **kwargs)

    @pyqtSlot()
    def start(self):
        print(f"Loading data ...") #for {self.filename}")

    @pyqtSlot(int)
    def calculatePrime(self, n):
        # primes=(n for n in count(2) if all(n % d for d in range(2, n)))
        primes = []
        for i in count(2):
            # time.sleep(.01)
            # print(len(primes))
            if len(primes) > n:
                break
            if all(i % d for d in range(2, i)):
                primes.append(i)
                self.current_prime.emit(i)
                self.progress.emit(int((len(primes)/n)*100))
        self.result.emit(primes[-1])
        # self.result.emit(list(islice(primes, 0, n))[-1])

    @pyqtSlot(str, int, int)
    def _load_spatial_data(
            self,
            filename: str,
            k_bin_factor: int,
            e_bin_factor: int,
            ):

        #def load_edc(filename,section):
        with h5py.File(filename, "r") as f:

            print("Keys: %s" % f.keys())
            data = f['Data']['Count']
            print(data.nbytes)

            edc_array=[]
            xz_array=[]
            index_array=[]
            count_i=0
            count_j=0

            # d0,d1=get_arrays_X_Z(filename)
            data0 = f['Data']['Axes2']
            data1 = f['Data']['Axes3']
            d0_delta=data0.attrs['Delta']
            d0_count=data0.attrs['Count']
            d0_start=data0.attrs['Offset']

            d0=np.linspace(d0_start,d0_start+(d0_count-1)*d0_delta,num=d0_count)

            d1_delta=data1.attrs['Delta']
            d1_count=data1.attrs['Count']
            d1_start=data1.attrs['Offset']

            d1=np.linspace(d1_start,d1_start+(d1_count-1)*d1_delta,num=d1_count)
            nnn = 0
            for i in range(d0_count):
                for j in range(d1_count):
                    temp_index=(i,j)
                    index_array.append(temp_index)
                    temp_xz=(d0[i],d1[j])
                    xz_array.append(temp_xz)
                    temp_edc=data[:,:,i,j].sum(1)
                    # temp_edc=rebin(data[:,:,count_i,count_j],2).sum(1)
                    #temp_edc=data[:,section[2]:section[3],count_i,count_j].sum(1)
                    #temp_edc=data[section[0]:section[1],:,count_i,count_j].sum(0)
                    edc_array.append(temp_edc)
                    self.progress.emit(int((nnn)/(d0_count*d1_count))*100)
                    print(nnn)
                    nnn += 1



            spectra = [kmf.Spectrum(position,edc,index) for position,edc,index in zip(xz_array,edc_array,index_array)]
            spatial_spectra = SpatialSpectrum(filename, binned_dcs=spectra)
            self.result.emit(1)


class SpectrumLoaderWidget(QWidget):
    requestPrime=pyqtSignal(str, int, int)

    def __init__(self, parent=None, **kwargs):
        super().__init__(parent, **kwargs)
        self._thread = QThread()
        self._spectrum_loader = _SpectrumLoaderObject(result=self.displayPrime)
        #self.requestPrime.connect(self._spectrum_loader.calculatePrime)
        self.requestPrime.connect(self._spectrum_loader._load_spatial_data)
        self._thread.started.connect(self._spectrum_loader.start)
        self._spectrum_loader.moveToThread(self._thread)
        self._spectrum_loader.progress.connect(self.displayProgress)
        self._spectrum_loader.current_prime.connect(self.displayCurrentPrime)
        # self._spectrum_loader.aboutToQuit.connect(self._thread.quit)
        self._thread.start()
        l = QVBoxLayout(self)
        self._iterationLE=QLineEdit(self, placeholderText="Filename")
        l.addWidget(self._iterationLE)
        self._requestBtn=QPushButton(
                "Load Data", self, clicked=self.primeRequested)
        l.addWidget(self._requestBtn)
        self._busy=QProgressBar(self)
        l.addWidget(self._busy)
        self._resultLbl=QLabel("Result:", self)
        l.addWidget(self._resultLbl)
        self._currentLbl = QLabel("Current:", self)
        l.addWidget(self._currentLbl)

    @pyqtSlot()
    def primeRequested(self):
        try: 
            n=int(self._iterationLE.text())
        except ValueError:
            return
        # self.requestPrime.emit(n)
        self.requestPrime.emit("data/Copy of S2_zap_0002.h5", 1, 1)
        self._resultLbl.setText("Result: ")
        self._busy.setRange(0,100)
        self._iterationLE.setEnabled(False)
        self._requestBtn.setEnabled(False)

    @pyqtSlot(int)
    def displayCurrentPrime(self, n):
        self._currentLbl.setText(f"Current: {n}")
        self.data = n

    @pyqtSlot(int)
    def displayProgress(self, n):
        self._busy.setValue(n)

    @pyqtSlot(int)
    def displayPrime(self, prime):
        self._resultLbl.setText("Result: {}".format(prime))
        self._busy.reset()
        self._iterationLE.setEnabled(True)
        self._requestBtn.setEnabled(True)

    def load(self, filename: str) -> None:
        self.requestPrime.emit(filename)


if __name__=="__main__":
    from sys import exit, argv

    a=QApplication(argv)
    g=SpectrumLoaderWidget()
    g.show()
    a.exec()
    exit()
