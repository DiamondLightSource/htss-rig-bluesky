import numpy as np
from xarray import Dataset


def normalize_tomography_data(
    projections: Dataset,
    flats: Dataset,
    darks: Dataset,
    image_label: str = "det_image",
) -> Dataset:
    projection_images = projections[image_label]
    flat_images = flats[image_label]
    dark_images = darks[image_label]

    average_flat = np.average(flat_images, axis=0)
    average_dark = np.average(dark_images, axis=0)

    normalized_images = (projection_images - average_dark) / (
        projection_images - average_flat
    )
    normalized_images = np.average(normalized_images, axis=1)

    return Dataset(
        {
            **projections,
            "normalized_image": (["time", "dim_1", "dim_2"], normalized_images),
        }
    )
