from dataclasses import dataclass
import numpy as np

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
