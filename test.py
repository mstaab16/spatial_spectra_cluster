import h5py
import numpy as np
import psutil
from time import perf_counter
from spatial_spectrum import SpatialSpectrum
import kmean_functions as kmf

def rebin(arr, bin_factor):
    # reshape the array to group the elements by energy and angle bins
    print(f"in rebin, shape of arr: {arr.shape}")
    arr = arr.reshape(arr.shape[0], arr.shape[1], arr.shape[2]//bin_factor, bin_factor , arr.shape[3]//bin_factor, bin_factor)

    # take the mean along the energy and angle bins
    arr = np.mean(arr, axis=(3,5))

    return arr

def chunky_loader(filename: str, bin_factor: int, context = None) -> tuple[list[kmf.Spectrum], np.ndarray]:
# Get the total available system RAM
    total_ram = psutil.virtual_memory().total

# Get the used system RAM
    used_ram = psutil.virtual_memory().used

# Calculate the available system RAM
    available_ram = total_ram - used_ram

# Print the available system RAM print(f'Available system RAM: {available_ram:.2f} bytes')
# print(f'Available system RAM: {available_ram/1073741824:.2f} GB')

    start = perf_counter()
# Open the .h5 file
    with h5py.File(filename, 'r') as f:
        # Get the dataset
        dset: np.ndarray = f['/Data/Count']

        # Get the dataset shape
        n_ene, n_ang, n_x, n_z = dset.shape
        # print(dset.shape)

        size_of_spectrum = n_ene * n_ang * dset[0, 0, 0, 0].itemsize
        # print(f'Size of spectrum: {size_of_spectrum/1073741824:.2f} GB')

        # Calculate the number of spectra that can be loaded into ram
        max_spectra_in_ram = int(0.8 * available_ram // size_of_spectrum)
        # print(f'Max spectra in ram: {max_spectra_in_ram}')

        num_chunks = max(int(n_x * n_z // max_spectra_in_ram), 1)
        # print(f'Size of chunks: {max_spectra_in_ram*size_of_spectrum/1073741824:.2f} GB')
        # print(f'Number of chunks: {1 + num_chunks}')

        edc_array = np.zeros((n_x, n_z, n_ene//bin_factor))
        binned_data = np.zeros((n_x, n_z, n_ene//bin_factor, n_ang//bin_factor))
        print(f"shape of binned_data: {binned_data.shape}")
        # TODO: I can't do this because that data variable will get too big.
        #       Try reverting back to old method and see if we can fix another way.
        # data = np.zeros((n_x, n_z, n_ene, n_ang))
        print(f"(n_x, n_z, n_ene, n_ang){(n_x, n_z, n_ene, n_ang)}")
        spectra, xz_array  =  [], []
        i_chunk = 0
        i = 0
        while i < n_x * n_z:
            # print(f'Chunk {i_chunk}')
            # print(f'{i/(n_x*n_z)*100:.2f}%')
            i_chunk += 1
            x_vals, z_vals = [], []
            for _ in range(max_spectra_in_ram):
                if context is not None:
                    emitting = i/(n_x * n_z)*100
                    emitting = min(emitting, 90)
                    context.progress.emit(int(emitting))
                i += 1
                if i >= n_x * n_z:
                    break
                x = i % n_x
                z = i // n_x
                x_vals.append(x)
                z_vals.append(z)
                xz_array.append((x, z))

            print(f"shape of dset{dset.shape}")
            data = dset[:, :, min(x_vals):max(x_vals)+1, min(z_vals):max(z_vals)+1].transpose((2, 3, 0, 1))
            # print(data.shape)
            # plt.imshow(data[:,:,10,10])
            # plt.show()
            print(f"shape of data{data.shape}")
            binned_data[min(x_vals):max(x_vals)+1, min(z_vals):max(z_vals)+1, :, :] = rebin(data, bin_factor)
            # print(binned_data.shape)
            # plt.imshow(binned_data[:,:,10,10])
            # plt.show()
            edc_array[min(x_vals):max(x_vals)+1, min(z_vals):max(z_vals)+1, :] = binned_data[min(x_vals):max(x_vals)+1, min(z_vals):max(z_vals)+1, :].sum(axis=3)
            print(f"shape of binned_data: {binned_data.shape}")

            xz_indecies = np.array(xz_array)
    
            x_offset = f['Data']['Axes2'].attrs['Offset']
            x_delta = f['Data']['Axes2'].attrs['Delta']
            x_count = f['Data']['Axes2'].attrs['Count']
            z_offset = f['Data']['Axes3'].attrs['Offset']
            z_delta = f['Data']['Axes3'].attrs['Delta']
            z_count = f['Data']['Axes3'].attrs['Count']

    
    xz_values = np.array([(x_offset + x*x_delta, z_offset + z*z_delta) for x, z in xz_indecies])

    print(f'Loading time: {(perf_counter() - start)/60:.2f} minutes')


    spectra = [kmf.Spectrum(position,edc_array[index[0],index[1],:],index) for position,index in zip(xz_values,xz_indecies)]
    # return SpatialSpectrum(edc_array, binned_data)
    if context is not None:
        context.progress.emit(100)
    return spectra, binned_data



# print(f'Size of edc array: {edc_array.nbytes/1073741824} GB')
# print(f'Size of binned data: {binned_data.nbytes/1073741824} GB')
# print(f'Elapsed time: {(perf_counter() - start)/60:.2f} minutes')
