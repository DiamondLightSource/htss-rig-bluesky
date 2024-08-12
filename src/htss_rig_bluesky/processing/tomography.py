import numpy as np
from xarray import Dataset


def normalize_tomography_data(
    projections: Dataset,
    flats: Dataset,
    darks: Dataset,
    image_label: str = "det_image",
) -> Dataset:
    """
    Normalize a tomography dataset applying the flats and darks
    to the projections

    Args:
        projections: Projections dataset
        flats: Flats dataset
        darks: Darks dataset
        image_label: Label for detector images in all 3 datasets.
            Defaults to "det_image".

    Returns:
        Dataset: A copy of the projections dataset with a new
            variable: "normalized_image"
    """

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
