import sys
from members import allMembersdf
from barChart import add_value_labels
import matplotlib.pyplot as plt
import pandas as pd
import re


def parse_file(text_file):
    '''Convert WhatsApp chat log text file to a Pandas dataframe.'''

    # some regex to account for messages taking up multiple lines
    pat = re.compile(
        r'^(\d{1,2}\/\d{1,2}\/\d{2}.*?)(?=^\d{1,2}\/\d{1,2}\/\d{2}.*?|\Z)', re.S | re.M)
    with open(text_file) as f:
        data = [m.group(1).strip().replace('\n', ' ')
                for m in pat.finditer(f.read())]

    sender = []
    message = []
    datetime = []
    for row in data:

        # timestamp is before the first dash
        datetime.append(row.split(' - ')[0])

        # sender is between am/pm, dash and colon
        try:
            s = re.search('[mM] - (.*?):', row).group(1)
            sender.append(s)
        except:
            sender.append('')

        # message content is after the first colon
        try:
            message.append(row.split(': ', 1)[1])
        except:
            message.append('')

    df = pd.DataFrame(zip(datetime, sender, message), columns=[
                      'timestamp', 'sender', 'message'])
    df['timestamp'] = pd.to_datetime(df.timestamp) + pd.Timedelta('13:30:00')

    # remove events not associated with a sender
    df = df[df.sender != ''].reset_index(drop=True)

    return df


# Printing number of messages by sender
if len(sys.argv) != 2:
    print('usage:{name} <chat file name>'.format(name=sys.argv[0]))
    exit(1)
df = parse_file(sys.argv[1])

allmsg_stat = df[['sender', 'message']].groupby(['sender'], sort=False)['message'].count(
).reset_index(name='count').sort_values(['count'], ascending=False).reset_index(drop=True)
# count of media omitted i.e forward images/video/voice msg
mediaPattern = r"(\<Media omitted\>)"
mediadf = df[df.message.str.match(mediaPattern)]
mediadf_stat = mediadf[['sender', 'message']].groupby(['sender'], sort=False)['message'].count(
).reset_index(name='count').sort_values(['count'], ascending=False).reset_index(drop=True)
mergeddf = pd.merge(left=allmsg_stat, right=mediadf_stat,
                    how='left', left_on='sender', right_on='sender')

singleWordMessagePattern = r"(.{1}$)"
singleWordDf = df[df.message.str.match(singleWordMessagePattern)]
singleWordDf_stat = singleWordDf[['sender', 'message']].groupby(['sender'], sort=False)['message'].count(
).reset_index(name='count').sort_values(['count'], ascending=False).reset_index(drop=True)
mergeddf = pd.merge(left=mergeddf, right=singleWordDf_stat,
                    how='left', left_on='sender', right_on='sender')
mergeddf.columns = ['sender', 'count_allmsg',
                    'count_media', 'count_singleword']

# whoever didn't send any messages
mergeddf = pd.merge(right=mergeddf, left=allMembersdf,
                    how='left', left_on='sender', right_on='sender')
mergeddf = mergeddf.fillna(0)
mergeddf = mergeddf.astype(
    {'count_allmsg': 'int64', 'count_media': 'int64', 'count_singleword': 'int64'})
ax = plt.gca()

mergeddf.plot(kind='bar', x='sender', y='count_allmsg', ax=ax,
              color='green', label='Total msg', align='edge')
mergeddf.plot(kind='bar', x='sender', y='count_media',
              color='blue', ax=ax, label='Media msg', align='edge')
mergeddf.plot(kind='bar', x='sender', y='count_singleword',
              color='red', ax=ax, label='Single Letter msg', align='edge')

fig = plt.gcf()
fig.set_size_inches((20, 20), forward=False)
add_value_labels(ax)
plt.savefig('chart.png')
# plt.show()


# uncomment to print folks did not sent any msg
# print(mergeddf[(mergeddf["count_x"]==0) & (mergeddf["count_y"]==0)])

print('Detail stat:')
print(mergeddf.sort_values(by='count_allmsg', ascending=False)[
      ['sender', 'count_allmsg', 'count_media', 'count_singleword']].reset_index(drop=True))
