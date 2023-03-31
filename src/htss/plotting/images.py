import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Slider
from xarray import Dataset


def plot_images_vs_axis(
    dataset: Dataset, axis_label: str, image_label: str = "det_image"
) -> None:
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


def plot_orthogonal(recon: np.ndarray) -> None:
    width, height, depth = recon.shape

    fig, axarr = plt.subplots(2, 2)

    fig.subplots_adjust(bottom=0.5)
    ax_x = fig.add_axes([0.1, 0.3, 0.4, 0.1])
    ax_y = fig.add_axes([0.1, 0.2, 0.4, 0.1])
    ax_z = fig.add_axes([0.1, 0.1, 0.4, 0.1])

    x_slider = Slider(
        ax=ax_x,
        label="X",
        valmin=0,
        valmax=width,
        valinit=0,
        orientation="horizontal",
    )
    y_slider = Slider(
        ax=ax_y,
        label="Y",
        valmin=0,
        valmax=height,
        valinit=0,
        orientation="horizontal",
    )
    z_slider = Slider(
        ax=ax_z,
        label="Z",
        valmin=0,
        valmax=depth,
        valinit=0,
        orientation="horizontal",
    )

    def update(_: float):
        x_center = x_slider.val
        y_center = y_slider.val
        z_center = z_slider.val

        x = recon[x_center, :, :]
        y = recon[:, y_center, :]
        z = recon[:, :, z_center]

        axarr[0, 0].imshow(x)
        axarr[0, 1].imshow(y)
        axarr[1, 0].imshow(z)

    update(0)
    plt.show()
