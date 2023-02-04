import h5py
import numpy as np
import psutil
from time import perf_counter
from spatial_spectrum import SpatialSpectrum
import kmean_functions as kmf


from dataclasses import dataclass
import dataclasses
import numpy.typing as npt
@dataclass()
class Spectrum:
    k_bin_factor: int = 1
    e_bin_factor: int = 1
    data: npt.NDArray = np.array([])
    pos: npt.NDArray = np.array([])
    metadata: dict = dataclasses.field(default_factory=dict)

    def __post_init__(self):
        print(f"post init of {self.pos}")

def rebin(arr, bin_factor):
    # reshape the array to group the elements by energy and angle bins
    print(f"in rebin, shape of arr: {arr.shape}")
    arr = arr.reshape(arr.shape[0], arr.shape[1], arr.shape[2]//bin_factor, bin_factor , arr.shape[3]//bin_factor, bin_factor)

    # take the mean along the energy and angle bins
    arr = np.mean(arr, axis=(3,5))

    return arr

def chunky_loader(filename: str, bin_factor: int, context = None) -> tuple[npt.NDArray, tuple[Spectrum]]:
# Get the total available system RAM
    total_ram = psutil.virtual_memory().total

# Get the used system RAM
    used_ram = psutil.virtual_memory().used

# Calculate the available system RAM
    available_ram = total_ram - used_ram

# Print the available system RAM print(f'Available system RAM: {available_ram:.2f} bytes')
    print(f'Available system RAM: {available_ram/1073741824:.2f} GB')

    start = perf_counter()
# Open the .h5 file
    with h5py.File(filename, 'r', rdcc_nbytes=available_ram, rdcc_nslots=1e7) as f:
    # with h5py.File(filename, 'r', rdcc_nbytes=1024**2*4000, rdcc_nslots=1e7) as f:
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
                emitting = i/(n_x * n_z)*100
                emitting = min(emitting, 90)
                if context is not None:
                    context.progress.emit(int(emitting))
                else:
                    print(f"{emitting}%")
                i += 1
                if i >= n_x * n_z:
                    break
                x = i % n_x
                z = i // n_x
                x_vals.append(x)
                z_vals.append(z)
                xz_array.append((x, z))

            data = dset[:, :, min(x_vals):max(x_vals)+1, min(z_vals):max(z_vals)+1].transpose((2, 3, 0, 1))
            binned_data[min(x_vals):max(x_vals)+1, min(z_vals):max(z_vals)+1, :, :] = rebin(data, bin_factor)
            edc_array[min(x_vals):max(x_vals)+1, min(z_vals):max(z_vals)+1, :] = binned_data[min(x_vals):max(x_vals)+1, min(z_vals):max(z_vals)+1, :].sum(axis=3)
            # data = np.zeros((n_ene, n_ang, max(x_vals)-min(x_vals)+1, max(z_vals)-min(z_vals)+1))
            # data[:, :, x_vals, z_vals] = np.copy(dset[:, :, x_vals, z_vals])
            # data = data.transpose((2, 3, 0, 1))
            # binned_data[x_vals, z_vals, :, :] = rebin(data, bin_factor)
            # edc_array[x_vals, z_vals, :] = binned_data[x_vals, z_vals, :].sum(axis=3)

            xz_indicies = np.array(xz_array)
    

    
        x_offset = f['Data']['Axes2'].attrs['Offset']
        x_delta = f['Data']['Axes2'].attrs['Delta']
        x_count = f['Data']['Axes2'].attrs['Count']
        z_offset = f['Data']['Axes3'].attrs['Offset']
        z_delta = f['Data']['Axes3'].attrs['Delta']
        z_count = f['Data']['Axes3'].attrs['Count']

    xz_values = np.array([(x_offset + x*x_delta, z_offset + z*z_delta) for x, z in xz_indicies])

    print(f'Loading time: {(perf_counter() - start)/60:.2f} minutes')


    # spectra = [kmf.Spectrum(position, edc_array[index[0],index[1],:], index) for position,index in zip(xz_values,xz_indecies)]
    spectra = tuple(Spectrum(2, 2, index, position) for position,index in zip(xz_values,xz_indicies))
    # return SpatialSpectrum(edc_array, binned_data)
    if context is not None:
        context.progress.emit(100)
    #return spectra, binned_data
    return binned_data, spectra



# print(f'Size of edc array: {edc_array.nbytes/1073741824} GB')
# print(f'Size of binned data: {binned_data.nbytes/1073741824} GB')
# print(f'Elapsed time: {(perf_counter() - start)/60:.2f} minutes')
