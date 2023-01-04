import h5py
import numpy as np
import psutil
from time import perf_counter
from spatial_spectrum import SpatialSpectrum

bin_factor = 2

def rebin(arr, bin_factor):
    # reshape the array to group the elements by energy and angle bins
    arr = arr.reshape(arr.shape[0]//bin_factor, bin_factor, arr.shape[1]//bin_factor, bin_factor, arr.shape[2], arr.shape[3])

    # take the mean along the energy and angle bins
    arr = np.mean(arr, axis=(1,3))

    return arr


# Get the total available system RAM
total_ram = psutil.virtual_memory().total

# Get the used system RAM
used_ram = psutil.virtual_memory().used

# Calculate the available system RAM
available_ram = total_ram - used_ram

# Print the available system RAM
print(f'Available system RAM: {available_ram:.2f} bytes')
print(f'Available system RAM: {available_ram/1073741824:.2f} GB')

start = perf_counter()
# Open the .h5 file
with h5py.File('data/Copy of S3_zap_0005.h5', 'r') as f:
    # Get the dataset
    dset: np.ndarray = f['/Data/Count']

    # Get the dataset shape
    n_ene, n_ang, n_x, n_z = dset.shape
    print(dset.shape)

    size_of_spectrum = n_ene * n_ang * dset[0, 0, 0, 0].itemsize
    print(f'Size of spectrum: {size_of_spectrum/1073741824:.2f} GB')

    # Calculate the number of spectra that can be loaded into ram
    max_spectra_in_ram = int(0.8 * available_ram // size_of_spectrum)
    print(f'Max spectra in ram: {max_spectra_in_ram}')

    num_chunks = max(int(n_x * n_z // max_spectra_in_ram), 1)
    print(f'Size of chunks: {max_spectra_in_ram*size_of_spectrum/1073741824:.2f} GB')
    print(f'Number of chunks: {1 + num_chunks}')

    edc_array = np.zeros((n_x, n_z, n_ene))
    binned_data = np.zeros((n_x, n_z, n_ene//bin_factor, n_ang//bin_factor))
    i_chunk = 0
    i = 0
    while i < n_x * n_z:
        print(f'Chunk {i_chunk}')
        print(f'{i/(n_x*n_z)*100:.2f}%')
        i_chunk += 1
        x_vals, z_vals = [], []
        for _ in range(max_spectra_in_ram):
            i += 1
            if i >= n_x * n_z:
                break
            x = i % n_x
            z = i // n_x
            x_vals.append(x)
            z_vals.append(z)
        data = dset[:, :, min(x_vals):max(x_vals), min(z_vals):max(z_vals)]
        # print(data.shape)
        # plt.imshow(data[:,:,10,10])
        # plt.show()
        binned_data = rebin(data, bin_factor)
        # print(binned_data.shape)
        # plt.imshow(binned_data[:,:,10,10])
        # plt.show()
        data = data.sum(axis=1).transpose(1, 2, 0)
        edc_array[min(x_vals):max(x_vals), min(z_vals):max(z_vals), :] = data



print(f'Size of edc array: {edc_array.nbytes/1073741824} GB')
print(f'Size of binned data: {binned_data.nbytes/1073741824} GB')
print(f'Elapsed time: {(perf_counter() - start)/60:.2f} minutes')
