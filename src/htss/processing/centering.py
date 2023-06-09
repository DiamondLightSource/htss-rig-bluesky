import numpy as np
from scipy import ndimage
from xarray import Dataset


def find_center_of_mass(
    dataset: Dataset,
    x_axis_demand_label: str = "sample_stage_x_user_setpoint",
    x_axis_label: str = "sample_stage_x",
    image_label: str = "det_image",
) -> Dataset:
    """
    Find the center of mass as a function of x

    Args:
        dataset: Xarray dataset from databroker
        x_axis_demand_label: The label of the array for the X axis demand values
        x_axis_label: The label of the array for the X axis
        image_label: The label of the array for the array of image data.
            Defaults to "det_image"
    """

    averaged = dataset.groupby(dataset[x_axis_demand_label]).mean()
    averaged_images = np.array(averaged[image_label][:, 0, :, :])
    com_x, com_y = _center_of_mass(averaged_images)
    return Dataset(
        {
            x_axis_label: averaged[x_axis_label],
            "center_of_mass_x": com_x,
            "center_of_mass_y": com_y,
        }
    )


def find_sum(
    dataset: Dataset,
    x_axis_demand_label: str = "sample_stage_x_user_setpoint",
    x_axis_label: str = "sample_stage_x",
    image_label: str = "det_image",
) -> Dataset:
    """
    Find the image sums

    Args:
        dataset: Xarray dataset from databroker
        x_axis_demand_label: The label of the array for the X axis demand values
        x_axis_label: The label of the array for the X axis
        image_label: The label of the array for the array of image data.
            Defaults to "det_image"
    """

    summed = dataset.groupby(dataset[x_axis_demand_label]).sum()
    summed_images = np.array(summed[image_label][:, 0, :, :])
    image_sums = np.sum(np.array(summed_images), axis=(1, 2))
    return Dataset(
        {
            x_axis_label: summed[x_axis_label],
            f"{image_label}_sum": image_sums,
        }
    )


def _center_of_mass(images: np.ndarray) -> np.ndarray:
    return np.transpose(
        np.array([ndimage.measurements.center_of_mass(image) for image in images])
    )
