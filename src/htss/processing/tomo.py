import logging
from dataclasses import dataclass
from typing import Tuple, TypeVar

import numpy as np
from tqdm.autonotebook import tqdm
from xarray import Dataset

LOGGER = logging.getLogger("VisualHulls")


@dataclass
class VisualHullsParams:
    """
    Parameters for a Visual Hulls reconstruction
    """

    # Pixel row representing the center of sample rotation.
    center_of_rotation: float

    # Pixel values below this threshold are interpreted
    # as part of the object. Pixel values above the
    # threshold are interpreted as part of the background.
    threshold: float

    # Determines resolution of reconstruction,
    # 1 gives highest resolution, >1 gives lower resolution
    # but faster reconstruction.
    step: int = 1


def reconstruct(
    params: VisualHullsParams,
    data: Dataset,
    image_label: str = "det_image",
    theta_label: str = "sample_stage_theta",
) -> np.ndarray:
    images = np.array(data[image_label][:, 0, :, :])
    theta_values = np.array(data[theta_label])
    return _reconstruct(params, images, theta_values)


def _reconstruct(
    params: VisualHullsParams, data: np.ndarray, theta_values: np.ndarray
) -> np.ndarray:
    """
    :param params: Visual Hulls settings
    :param data: Frames from data acquisition, shape: (n, w, h)
                 n = number of frames
                 w = frame width
                 h = frame height
    :param theta_values: 1D array of rotation values of the sameple
                         corresponding to frames, shape: (n,)
    :return: 3D reconstruction, shape: (n, n, h)
    """

    n_frames, width, height = data.shape

    out_buf = np.zeros(shape=(n_frames, n_frames, height), dtype=np.int8)

    sino_range = enumerate(tqdm(range(0, height, params.step)))
    for count, i in sino_range:
        LOGGER.info("processing sinogram %s" % i)
        # sinogram = data[:, 529:832, i]
        sinogram = data[:, :, i]
        result = process_frames(
            sinogram.T, theta_values, params.threshold, params.center_of_rotation
        )
        out_buf[:, :, count] = result
        count += 1
    return out_buf


def process_frames(
    data: np.ndarray, angles: np.ndarray, threshold: float, center_of_rotation: float
) -> np.ndarray:
    sinogram = binarize(data, threshold)
    return recon_hull(sinogram, center_of_rotation, angles)


def recon_hull(sino: np.ndarray, centre: float, angles: np.ndarray) -> np.ndarray:
    data_shape = (sino.shape[1], sino.shape[1])
    full = np.ones(data_shape)
    for i in range(len(angles)):
        map_array = mapping_array(data_shape, centre, np.deg2rad(angles[i]))
        map_array = np.clip(
            map_array.astype("int") + centre, 0, sino.shape[1] - 1
        ).astype("int")
        mask = sino[i, :][map_array]
        full -= 1 - mask
    data_range = full.max() - full.min()
    full += data_range / 4
    full[full < 0.5] = 0
    return full


def mapping_array(array_shape: Tuple[int, int], center: float, theta: float):
    x, y = np.meshgrid(
        np.arange(-center, array_shape[0] - center),
        np.arange(-center, array_shape[1] - center),
    )
    return x * np.cos(theta) - y * np.sin(theta)


N = TypeVar("N")


def binarize(data: np.ndarray, threshold: N) -> np.ndarray:
    binarized = np.zeros_like(data)
    binarized[data < threshold] = 1
    return binarized
