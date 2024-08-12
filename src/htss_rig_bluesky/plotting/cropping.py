import matplotlib.pyplot as plt
from matplotlib.widgets import RectangleSelector
from xarray import Dataset

from htss_rig_bluesky.plans.detector import Roi


def croppable_plot(
    dataset: Dataset,
    image_label: str = "det_image",
    index: int = 0,
) -> Roi:
    """
    Plot a single detector image and allow the user to select a
    region for use in cropping.

    Args:
        dataset: Xarray dataset from databroker
        index: Index in the data to plot. Defaults to 0

    Returns:
        Region of interest

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
