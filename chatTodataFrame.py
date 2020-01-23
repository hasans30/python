import matplotlib.pyplot as plt
import pandas as pd
import re

def parse_file(text_file):
    '''Convert WhatsApp chat log text file to a Pandas dataframe.'''
    
    # some regex to account for messages taking up multiple lines
    pat = re.compile(r'^(\d{1,2}\/\d{1,2}\/\d{2}.*?)(?=^\d{1,2}\/\d{1,2}\/\d{2}.*?|\Z)', re.S | re.M)
    with open(text_file) as f:
        data = [m.group(1).strip().replace('\n', ' ') for m in pat.finditer(f.read())]

    sender = []; message = []; datetime = []
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

    df = pd.DataFrame(zip(datetime, sender, message), columns=['timestamp', 'sender', 'message'])
    df['timestamp'] = pd.to_datetime(df.timestamp )+ pd.Timedelta('13:30:00')

    # remove events not associated with a sender
    df = df[df.sender != ''].reset_index(drop=True)
    
    return df


# Printing number of messages by sender
df = parse_file('backup.nhs.txt')
allmsg_stat=df[['sender','message']].groupby(['sender'],sort=False)['message'].count().reset_index(name='count').sort_values(['count'],ascending=False).reset_index(drop=True)
print(allmsg_stat)
#count of media omitted i.e forward images/video/voice msg
mediaPattern = r"(\<Media omitted\>)" 
mediadf=df[df.message.str.match(mediaPattern)]
mediadf_stat=mediadf[['sender','message']].groupby(['sender'],sort=False)['message'].count().reset_index(name='count').sort_values(['count'],ascending=False).reset_index(drop=True)
mergeddf=pd.merge(left=allmsg_stat, right=mediadf_stat, how='left',left_on='sender', right_on='sender')
print(mergeddf)
# print(mediadf_stat.to_string(index=False))
ax = plt.gca()
mergeddf.plot(kind='bar',x='sender',y='count_x', ax=ax, label='Total msg')
mergeddf.plot(kind='bar' , x='sender', y='count_y', color='red', ax=ax, label='Media')
fig = plt.gcf()
fig.set_size_inches((11,8.5), forward=False)
plt.savefig('chart.png')
plt.show()