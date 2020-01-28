import matplotlib.pyplot as plt


def get_printable_y_value(y_value, index, groupLength, patches):
    # disabling extra labeling logic
    return y_value
    """ if 1st group has very less value e.g 10, we want to omit 2nd and 3rd group values
    threshold = 10
    if(index >= groupLength and patches[index % groupLength].get_height() < threshold):
        return 0  # if 0, we don't print in the graph
    else:
        return y_value
    """


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
            color='brown',
            va=va)                      # Vertically align label differently for
        # positive and negative values.


def plotChart(mergeddf):
    ax = plt.gca()
    colors = ['blue', 'green', 'red']
    labels = ['all', 'media(pic,voice,video)',
              'single letter']
    columnNames = ['count_allmsg', 'count_media', 'count_singleword']

    mergeddf = mergeddf.sort_values(
        by='count_allmsg', ascending=False).reset_index(drop=True)
    print(mergeddf)
    width = 1
    gap = .65
    barCenter = 0
    newGroupFirstCenter = -1
    nameLabels = []
    labelLocations = []
    for index, row in mergeddf.iterrows():
        nameLabels.append(row['sender'])
        barInfo = zip([row[columnNames[0]], row[columnNames[1]],
                       row[columnNames[2]]], colors, labels)
        for i, (h, c, l) in enumerate(barInfo):
            barCenter = i + newGroupFirstCenter
            if(i == 1):
                labelLocations.append(barCenter)
            plt.bar(barCenter, h, width=width,
                    color=c, zorder=-i, label=l if index == 0 else '')
        newGroupFirstCenter = (width+gap)+barCenter
    ax.set_xticks(labelLocations)
    ax.set_xticklabels(nameLabels, rotation=90, ha='center')
    handles, chartLabels = ax.get_legend_handles_labels()
    ax.legend(handles, chartLabels)
    fig = plt.gcf()
    fig.set_size_inches((20, 20), forward=False)
    add_value_labels(ax, 8)
    meanpoint = mergeddf[columnNames[0]].fillna(0).mean()
    meanlabel = 'mean '+str(int(meanpoint))
    ax.axhline(meanpoint, ls='--', color='r', label=meanlabel)
    plt.legend()
    plt.savefig('chart.png')
