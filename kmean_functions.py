import numpy as np
from fcmeans import FCM
from matplotlib import pyplot as plt

class Spectrum:
        
    def __init__(self, position, edc, index):
        self.position = position #Array of length 2 (x,y)
        self.edc = edc  #Array of length  (intensity vs energy, but ignore energy scaling)\
        self.k = None
        self.index= index #similary to position but use integer index instead of real values

def show_intensity(data):
    temp_img=data.sum(0)
    temp_img=temp_img.sum(0)

    return temp_img

def split(spectra):
    thr=0.5
    X=np.array([x.edc for x in spectra])
    fcm = FCM(n_clusters=2)
    fcm.fit(X)

    sp=fcm.soft_predict(X)


    for i in range(len(spectra)):
        spectra[i].k=sp[i]


    temp_edc0=[]
    temp_position0=[]
    temp_index0=[]
    temp_edc1=[]
    temp_position1=[]
    temp_index1=[]
    waste_position=[]
    for spec in spectra:
        if spec.k[0]>thr:
            temp_edc0.append(spec.edc)
            temp_position0.append(spec.position)
            temp_index0.append(spec.index)
        if spec.k[1]>thr:
            temp_edc1.append(spec.edc)
            temp_position1.append(spec.position)
            temp_index1.append(spec.index)
        else:
            waste_position.append(spec.position)


    spectra1 = [Spectrum(position,edc,index) for position,edc,index in zip(temp_position1,temp_edc1,temp_index1)]
    spectra0 = [Spectrum(position,edc,index) for position,edc,index in zip(temp_position0,temp_edc0,temp_index0)]
    return spectra0, spectra1;


def get_ave_spec(spectra,data):
#    data0=np.zeros(shape=data.shape[2:])
#    print(data0.shape)
#    count=0
#    for spec in spectra:       
#        print(f"{(spec.index[0],spec.index[1])}")
#        data0+=data[spec.index[0],spec.index[1],::-1,:]
#        count+=1
#    data0=data0/count
#    data0=np.transpose(data0)
#    data0=np.flip(data0,axis=1)

    # sum all elements of data whose index appears in one of the spectra

    avg_spectrum = np.zeros(data.shape[2:])
    for spec in spectra:
        avg_spectrum += data[spec.index[0], spec.index[1], :, :]
    avg_spectrum /= len(spectra)
    avg_spectrum=np.transpose(avg_spectrum)
#    avg_spectrum=np.flip(avg_spectrum,axis=1)

    return avg_spectrum






