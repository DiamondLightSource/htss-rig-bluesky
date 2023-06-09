import matplotlib.pyplot as plt
from matplotlib.widgets import RectangleSelector
from xarray import Dataset

from htss.plans.detector import Roi


def croppable_plot(
    dataset: Dataset,
    image_label: str = "det_image",
    index: int = 0,
) -> Roi:
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

    image = dataset[image_label][index, 0, :, :]
    crop_bounds = Roi(0, 0, 0, 0)

    def on_select(eclick, erelease) -> None:
        crop_bounds.min_x = eclick.xdata
        crop_bounds.min_y = eclick.ydata
        crop_bounds.size_x = erelease.xdata - eclick.xdata
        crop_bounds.size_y = erelease.ydata - eclick.ydata

    fig, ax = plt.subplots(1)

    ax_index = fig.add_axes([0.1, 0.025, 0.4, 0.1])
    ax_index.margins(0.1)
    selector = RectangleSelector(
        ax,
        on_select,
        useblit=True,
        button=[1, 3],
        spancoords="pixels",
        interactive=True,
    )
    selector.set_active(True)
    # fig.canvas.mpl_connect("key_press_event", selector)

    ax.imshow(image)
    plt.show()

    return crop_bounds
