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
