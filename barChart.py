def get_printable_y_value(y_value, index, groupLength, patches):
    """ if 1st group has very less value e.g 10, we want to omit 2nd and 3rd group values
    """
    threshold = 10
    if(index >= groupLength and patches[index % groupLength].get_height() < threshold):
        return 0  # if 0, we don't print in the graph
    else:
        return y_value


def add_value_labels(ax, spacing=5):
    """Add labels to the end of each bar in a bar chart.

    Arguments:
        ax (matplotlib.axes.Axes): The matplotlib object containing the axes
            of the plot to annotate.
        spacing (int): The distance between the labels and the bars.
    """
    patchLength = len(ax.patches)
    groupLength = int(patchLength/3)
    # For each bar: Place a label
    for rect in ax.patches:
        # Get X and Y placement of label from rect.
        y_value = rect.get_height()
        x_value = rect.get_x() + rect.get_width() / 2
        y_value = get_printable_y_value(
            y_value, ax.patches.index(rect), groupLength, ax.patches)
        # Number of points between bar and label. Change to your liking.
        space = spacing
        # Vertical alignment for positive values
        va = 'bottom'

        # If value of bar is negative: Place label below bar
        if y_value < 0:
            # Invert space to place label below
            space *= -1
            # Vertically align label at top
            va = 'top'

        # Use Y value as label and format number with one decimal place
        label = "" if y_value == 0 else "{:}".format(y_value)

        # Create annotation
        ax.annotate(
            label,                      # Use `label` as label
            (x_value, y_value),         # Place label at end of the bar
            xytext=(0, space),          # Vertically shift label by `space`
            textcoords="offset points",  # Interpret `xytext` as offset in points
            ha='center',                # Horizontally center label
            va=va)                      # Vertically align label differently for
        # positive and negative values.
