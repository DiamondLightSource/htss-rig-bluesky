from typing import Optional
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


def to_sinograms(
    normalized_projections: Dataset,
    image_label: str = "normalized_images",
    linear_position_label: str = "sample_stage_x",
) -> Dataset:
    ...


def determine_center_of_rotation(
    normalized_projections: Dataset,
    initial_guess: Optional[float] = None,
    image_label: str = "normalized_images",
    linear_position_label: str = "sample_stage_x",
) -> float:
    if initial_guess is None:
        images = normalized_projections[image_label]
        initial_guess = images.shape[2] / 2
    center_of_rotation = initial_guess
    linear_positions = np.array(normalized_projections[linear_position_label])
    for ind, x in enumerate(linear_positions):
        if x >= center_of_rotation and linear_positions[ind - 1] <= center_of_rotation:
            center_of_rotation = (ind - 1) + (
                center_of_rotation - linear_positions[ind - 1]
            ) / float(x - linear_positions[ind - 1])
            break
    return center_of_rotation
