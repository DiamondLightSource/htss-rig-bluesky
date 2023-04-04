import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Slider
from xarray import Dataset


def plot_images_vs_axis(
    dataset: Dataset, axis_label: str, image_label: str = "det_image"
) -> None:
    """
    Plot detector images against an axis. The plot includes a slider which changes the
    image as the axis moves. Example use case, plotting detector images against x
    position, dragging the slider shows the image at a particular value of x.

    Args:
        dataset: Xarray dataset from databroker
        axis_label: The label of the array for the axis to plot against
        image_label: The label of the array for the array of image data.
            Defaults to "det_image"

    Yields:
        Plan
    """

    images = dataset[image_label][:, 0, :, :]
    motor_positions = np.array(dataset[axis_label])

    fig, ax = plt.subplots()

    ax_index = fig.add_axes([0.1, 0.025, 0.4, 0.1])
    ax_index.margins(0.1)
    slider = Slider(
        ax=ax_index,
        label="Index",
        valmin=0,
        valmax=len(motor_positions),
        valinit=0,
        orientation="horizontal",
    )

    def update(val: float):
        idx = int(val)
        motor_pos = motor_positions[idx]
        ax.set_title(f"{axis_label}={motor_pos}")
        image = images[idx]
        ax.imshow(image)

    slider.on_changed(update)
    update(0)
    plt.show()
