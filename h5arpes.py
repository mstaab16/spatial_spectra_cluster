from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from itertools import count, islice
import time

class Threaded(QObject):
    result=pyqtSignal(int)
    progress=pyqtSignal(int)
    current_prime = pyqtSignal(int)

    def __init__(self, parent=None, **kwargs):
        super().__init__(parent, **kwargs)

    @pyqtSlot()
    def start(self): 
        print("Thread started")

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

class GUI(QWidget):
    requestPrime=pyqtSignal(int)

    def __init__(self, parent=None, **kwargs):
        super().__init__(parent, **kwargs)

        self._thread=QThread()
        self._threaded=Threaded(result=self.displayPrime)
        self.requestPrime.connect(self._threaded.calculatePrime)
        self._thread.started.connect(self._threaded.start)
        self._threaded.moveToThread(self._thread)
        self._threaded.progress.connect(self.displayProgress)
        self._threaded.current_prime.connect(self.displayCurrentPrime)
        # self._threaded.aboutToQuit.connect(self._thread.quit)
        self._thread.start()

        l=QVBoxLayout(self)
        self._iterationLE=QLineEdit(self, placeholderText="Iteration (n)")
        l.addWidget(self._iterationLE)
        self._requestBtn=QPushButton(
                "Calculate Prime", self, clicked=self.primeRequested)
        l.addWidget(self._requestBtn)
        self._busy=QProgressBar(self)
        l.addWidget(self._busy)
        self._resultLbl=QLabel("Result:", self)
        l.addWidget(self._resultLbl)
        self._currentLbl=QLabel("Current:", self)
        l.addWidget(self._currentLbl)

    @pyqtSlot()
    def primeRequested(self):
        try: 
            n=int(self._iterationLE.text())
        except ValueError:
            return
        self.requestPrime.emit(n)
        self._resultLbl.setText("Result: ")
        self._busy.setRange(0,100)
        self._iterationLE.setEnabled(False)
        self._requestBtn.setEnabled(False)

    @pyqtSlot(int)
    def displayCurrentPrime(self, n):
        self._currentLbl.setText(f"Current: {n}")

    @pyqtSlot(int)
    def displayProgress(self, n):
        self._busy.setValue(n)

    @pyqtSlot(int)
    def displayPrime(self, prime):
        self._resultLbl.setText("Result: {}".format(prime))
        # self._busy.setRange(0,0)
        self._busy.reset()
        self._iterationLE.setEnabled(True)
        self._requestBtn.setEnabled(True)

if __name__=="__main__":
    from sys import exit, argv

    a=QApplication(argv)
    g=GUI()
    g.show()
    exit(a.exec())
