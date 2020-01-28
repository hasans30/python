import sys
from members import allMembersdf
from barChart import add_value_labels, plotChart
import pandas as pd
import utilities
import re
from dateutil.relativedelta import relativedelta

# Printing number of messages by sender
if len(sys.argv) < 2:
    print('usage:{name} <chat file name> <2020-01>'.format(name=sys.argv[0]))
    exit(1)

date_time_obj, opFileName, filter_needed = utilities.getDateTimeAndFileName(sys)
df = utilities.parse_file(sys.argv[1])

if filter_needed:
    nextmonth = (date_time_obj + relativedelta(months=1))
    df = df[(df['timestamp'] >= date_time_obj) & (df['timestamp'] < nextmonth)]

allmsg_stat = utilities.countAllMessaages(df)
mediaOmitted_stat = utilities.countMedia(df, allmsg_stat)
singleWordDf_stat = utilities.countSingleLetterMessage(df, mediaOmitted_stat)
mergeddf = utilities.mergeWithAllMembersData(singleWordDf_stat, allMembersdf)
# drawing chart
plotChart(mergeddf, opFileName)
