import sys
from members import allMembersdf
from barChart import add_value_labels, plotChart
import pandas as pd
import utilities
import re

# Printing number of messages by sender
if len(sys.argv) != 2:
    print('usage:{name} <chat file name>'.format(name=sys.argv[0]))
    exit(1)

df = utilities.parse_file(sys.argv[1])

allmsg_stat = utilities.countAllMessaages(df)
mediaOmitted_stat = utilities.countMedia(df, allmsg_stat)
singleWordDf_stat = utilities.countSingleLetterMessage(df, mediaOmitted_stat)
mergeddf = utilities.mergeWithAllMembersData(singleWordDf_stat, allMembersdf)
# drawing chart
plotChart(mergeddf)
