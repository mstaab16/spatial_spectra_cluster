from __future__ import print_function
import dataclasses
from dataclasses import dataclass
import numpy as np
import numpy.typing as npt
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
import matplotlib.colors as mcolors

from chunky_loader import chunky_loader

@dataclass()
class Spectrum:
    k_bin_factor: int = 1
    e_bin_factor: int = 1
    data: npt.NDArray = np.array([])
    pos: npt.NDArray = np.array([])
    metadata: dict = dataclasses.field(default_factory=dict)


@dataclass()
class Cluster:
    parent_i: int
    centroid: npt.NDArray
    # list of indices into the ClusteredSpectra.spectra list
    spectra: list[int] = dataclasses.field(default_factory=list)
    children_i: list[int] = dataclasses.field(default_factory=list)
    color: str = "black"

    cluster_colors = list(mcolors.XKCD_COLORS.values())
    
    def __post_init__(self):
        self.color = np.random.choice(self.cluster_colors)
        self.cluster_colors.remove(self.color)


@dataclass()
class ClusteredSpectra:
    data: npt.NDArray
    spectra: tuple[Spectrum]
    # This is the linked list of spectra representing the tree
    _clusters: list[Cluster] = dataclasses.field(default_factory=list)
    # spectra: list[Spectrum] = dataclasses.field(default_factory=list)

    def __post_init__(self):
        print("post init")
        self._clusters.append(Cluster(parent_i=0, spectra=list(range(len(self.spectra))), centroid = np.array([0,0])))
        self._cluster_k(4)
        # print("clusters appended")
        # self._fake_cluster()
        # print("post init done")
        self._print_cluster_tree(0)

    def get_spectra(self, cluster_i: int) -> list[Spectrum]:
        return [self.spectra[i] for i in self._clusters[cluster_i].spectra]

    def get_cluster_labels(self,  spectrum: Spectrum) -> list[int]:
        if "index" not in spectrum.metadata:
            raise ValueError(f"Spectrum {spectrum} does not have an index.")
        spectra_i = spectrum.metadata["index"]
        return self._get_cluster_labels(spectra_i)

    def _get_cluster_labels(self, spectra_i: int) -> list[int]:
        labels = []
        for i, cluster in enumerate(self._clusters):
            if spectra_i in cluster.spectra:
                labels.append(i)
        if len(labels) == 0:
            raise ValueError("Spectrum not found in clusters.")
        return labels

    def make_subcluster(self, cluster_i: int, spectra_i: list[int], centroid: npt.NDArray):
        """Make a subcluster of the given cluster."""
        self._clusters.append(Cluster(parent_i=cluster_i, spectra=spectra_i, centroid=centroid))
        self._clusters[cluster_i].children_i.append(len(self._clusters) - 1)

    def _cluster_k(self, k:int):
        """Cluster the spectra using Kmeans with k=2"""
        pca_components = 500
        data = self.data
        classifier = KMeans(n_clusters=k)
        flattened_data = data.reshape(data.shape[0]*data.shape[1], data.shape[2]*data.shape[3])
        print(f"{flattened_data.shape=}")
        pca = PCA(n_components=pca_components)
        pca_data = pca.fit_transform(flattened_data)
        print(f"{pca_data.shape=}")

        classifier.fit(pca_data)
        labels = classifier.labels_.reshape(data.shape[0], data.shape[1])
        cluster_centers = classifier.cluster_centers_
        print(f"{cluster_centers.shape=}")
        centroids = np.array([pca.inverse_transform(center) for center in cluster_centers]).reshape(k, data.shape[2], data.shape[3])
        print(f"{centroids.shape=}")
        # 

        for cluster_i in np.unique(np.ravel(labels)):
            spectra_i = np.argwhere(labels == cluster_i).tolist()
            spectra = [i for i, spectrum in enumerate(self.spectra) if spectrum.data.tolist() in spectra_i]
            self.make_subcluster(0, spectra, centroids[cluster_i])

    def get_cluster_by_spectrum_position_index(self, spectrum_position_index: tuple[int,int]) -> int:
        """Get the cluster index that contains the spectrum at the given position index."""
        cluster = self._clusters[0]
        for cluster_i in self.walk_clusters(0):
            isin = spectrum_position_index in [spectrum.data.tolist() for spectrum in self.get_spectra(cluster_i)]
            if isin:
                cluster = self._clusters[cluster_i]
        return cluster

    def _fake_cluster(self):
        """Fake clustering by taking a random half of the spectra."""
        first_cluster_indices = np.random.choice(self._clusters[0].spectra, size=len(self.spectra) // 2)
        second_cluster_indices = np.setdiff1d(self._clusters[0].spectra, first_cluster_indices)
        self.make_subcluster(0, list(first_cluster_indices), np.random.random((2)))
        self.make_subcluster(0, list(second_cluster_indices), np.random.random((2)))

        # # break cluster 1 into two
        first_cluster_indices = np.random.choice(self._clusters[1].spectra, size=len(self._clusters[1].spectra) // 2)
        second_cluster_indices = np.setdiff1d(self._clusters[1].spectra, first_cluster_indices)
        self.make_subcluster(1, list(first_cluster_indices), np.random.random((2)))
        self.make_subcluster(1, list(second_cluster_indices), np.random.random((2)))

        # # break cluster 2 into two
        first_cluster_indices = np.random.choice(self._clusters[2].spectra, size=len(self._clusters[2].spectra) // 2)
        second_cluster_indices = np.setdiff1d(self._clusters[2].spectra, first_cluster_indices)
        self.make_subcluster(2, list(first_cluster_indices), np.random.random((2)))
        self.make_subcluster(2, list(second_cluster_indices), np.random.random((2)))



    def _print_cluster_tree(self, cluster_i: int, level: int = 0):
        print("-- " * level + f" {cluster_i} num_spectra: {len(self.get_spectra(cluster_i))} color: {self._clusters[cluster_i].color}")
        for child_i in self._clusters[cluster_i].children_i:
            self._print_cluster_tree(child_i, level + 1)


    def walk_clusters(self, cluster_i: int, level: int = 0):
        yield cluster_i
        for child_i in self._clusters[cluster_i].children_i:
            yield from self.walk_clusters(child_i, level + 1)


def main():
    data, spectra = chunky_loader("data/Copy of S2_zap_0002.h5", bin_factor=2)
    print(f"Loaded {len(spectra)} spectra.")
    print(f"Data shape: {data.shape}")
    clustered_spectra = ClusteredSpectra(spectra)

if __name__ == "__main__":
    main()
