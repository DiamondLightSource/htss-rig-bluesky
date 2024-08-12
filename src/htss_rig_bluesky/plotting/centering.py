import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from xarray import Dataset

from htss_rig_bluesky.processing.centering import find_center_of_mass, find_sum


def plot_sum_and_center_of_mass(
    dataset: Dataset,
    x_axis_demand_label: str = "sample_stage_x_user_setpoint",
    x_axis_label: str = "sample_stage_x",
    image_label: str = "det_image",
) -> None:
    """
    Plot the sum and center of mass data for a scan, intended to be used with data from
    the scan_center plan

    Args:
        dataset: Dataset containing data
        x_axis_demand_label: Dataset label for x axis demand values.
            Defaults to "sample_stage_x_user_setpoint".
        x_axis_label (str, optional): Dataset label for x axis values.
            Defaults to "sample_stage_x".
        image_label (str, optional): Dataset label for detector images.
            Defaults to "det_image".
    """

    com_dataset = find_center_of_mass(
        dataset, x_axis_demand_label, x_axis_label, image_label
    )
    sum_dataset = find_sum(dataset, x_axis_demand_label, x_axis_label, image_label)
    x_positions = np.array(com_dataset[x_axis_label])

    axs: tuple[Axes, ...]
    fig, axs = plt.subplots(2)

    centroid_axis, sum_axis = axs

    centroid_axis.plot(x_positions, com_dataset["center_of_mass_x"])
    centroid_axis.plot(x_positions, com_dataset["center_of_mass_y"])
    centroid_axis.set_xlabel("X")
    centroid_axis.set_ylabel("Center of Mass")
    centroid_axis.set_title("Centroid")

    sum_axis.plot(x_positions, sum_dataset["det_image_sum"])
    sum_axis.set_xlabel("X")
    sum_axis.set_ylabel("Image Sum")
    sum_axis.set_title("Sum")

    plt.show()
