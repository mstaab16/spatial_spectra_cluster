
import h5py
import numpy as np
import kmean_functions as kmf

def get_by_coord(file_name, xz_list,bin_factor=1):
    """
    input: 
        filename="path"
        xz_list=[(x1,z1),(x2,z2)...]

    returns:
        data_list=[(data at x1,z1),(data at x2,z2)...]

    """


    with h5py.File(file_name, "r") as f:
        data_list=[]
        for x,z in xz_list:
            current_data=rebin(f['Data']['Count'][:,:,x,z],bin_factor=bin_factor)

            data_list.append()
  
        
    return data_list


def load_data_file(filename):
    with h5py.File(filename, "r") as f:

        data = f['Data']['Count'][()]   
    return data


def get_arrays_X_Z(filename):
    with h5py.File(filename, "r") as f:

        #print("Keys: %s" % f.keys())
        data0 = f['Data']['Axes2']
        data1 = f['Data']['Axes3']
        #print("Keys: %s" % data0.attrs.keys())
        d0_delta=data0.attrs['Delta']
        d0_count=data0.attrs['Count']
        d0_start=data0.attrs['Offset']

        d0=np.linspace(d0_start,d0_start+(d0_count-1)*d0_delta,num=d0_count)
   

        d1_delta=data1.attrs['Delta']
        d1_count=data1.attrs['Count']
        d1_start=data1.attrs['Offset']

        d1=np.linspace(d1_start,d1_start+(d1_count-1)*d1_delta,num=d1_count)

    return d0,d1


def load_edc(filename,section):
    with h5py.File(filename, "r") as f:

        print("Keys: %s" % f.keys())
        data = f['Data']['Count'][()]   
        print(data.shape)

    edc_array=[]
    xz_array=[]
    index_array=[]
    count_i=0
    count_j=0
  
    d0,d1=get_arrays_X_Z(filename)
    for i in data[0,0,:,0]:
        for j in data[0,0,0,:]:
            temp_index=(count_i,count_j)
            index_array.append(temp_index)
            temp_xz=(d0[count_i],d1[count_j])
            xz_array.append(temp_xz)
            temp_edc=data[:,section[2]:section[3],count_i,count_j].sum(1)
            #temp_edc=data[section[0]:section[1],:,count_i,count_j].sum(0)
            edc_array.append(temp_edc)
            count_j+=1
        count_i+=1
        count_j=0
  
  
    spectra = [kmf.Spectrum(position,edc,index) for position,edc,index in zip(xz_array,edc_array,index_array)]
    return spectra, data

def load_mdc(filename,section):
    with h5py.File(filename, "r") as f:

        print("Keys: %s" % f.keys())
        data = f['Data']['Count'][()]   
        print(data.shape)

    edc_array=[]
    xz_array=[]
    index_array=[]
    count_i=0
    count_j=0
  
    d0,d1=get_arrays_X_Z(filename)
    for i in data[0,0,:,0]:
        for j in data[0,0,0,:]:
            temp_index=(count_i,count_j)
            index_array.append(temp_index)
            temp_xz=(d0[count_i],d1[count_j])
            xz_array.append(temp_xz)
            temp_edc=data[section[0]:section[1],:,count_i,count_j].sum(0)
            #temp_edc=data[section[0]:section[1],:,count_i,count_j].sum(0)
            edc_array.append(temp_edc)
            count_j+=1
        count_i+=1
        count_j=0
  
  
    spectra = [kmf.Spectrum(position,edc,index) for position,edc,index in zip(xz_array,edc_array,index_array)]
    return spectra, data



def rebin(arr, bin_factor):
    new_shape=arr.shape//bin_factor
    shape=(new_shape[0],arr.shape[0]//new_shape[0], new_shape[1],arr.shape[1]//new_shape[1])
    return arr.reshape(shape).mean(-1).mean(1)


def get_arrays_E_K(filename):
    with h5py.File(filename, "r") as f:

        #print("Keys: %s" % f.keys())
        data0 = f['Data']['Axes0']
        data1 = f['Data']['Axes1']
        #print("Keys: %s" % data0.attrs.keys())
        d0_center=data0.attrs['Center']
    
        d0_delta=data0.attrs['Delta']
        d0_start=d0_center-532*d0_delta
        d0_end=d0_center+532*d0_delta
        #TODO: divide by the bin_factor here
        d0=np.linspace(d0_start,d0_end,num=data0.attrs['Count']//2)

        d1_center=data1.attrs['Center']
    
        d1_delta=data1.attrs['Delta']
        d1_start=d1_center-490*d1_delta
        d1_end=d1_center+490*d1_delta
        #TODO: divide by the bin_factor here
        d1=np.linspace(d1_start,d1_end,num=data1.attrs['Count']//2)
    return d0,d1

def get_arrays_X_Z(filename):
    with h5py.File(filename, "r") as f:

        #print("Keys: %s" % f.keys())
        data0 = f['Data']['Axes2']
        data1 = f['Data']['Axes3']
        #print("Keys: %s" % data0.attrs.keys())
        d0_delta=data0.attrs['Delta']
        d0_count=data0.attrs['Count']
        d0_start=data0.attrs['Offset']

        d0=np.linspace(d0_start,d0_start+(d0_count-1)*d0_delta,num=d0_count)
   

        d1_delta=data1.attrs['Delta']
        d1_count=data1.attrs['Count']
        d1_start=data1.attrs['Offset']

        d1=np.linspace(d1_start,d1_start+(d1_count-1)*d1_delta,num=d1_count)

    return d0,d1
