import re
import numpy as np
import pandas as pd


def parse_file(text_file):
    '''Convert WhatsApp chat log text file to a Pandas dataframe.'''

    # some regex to account for messages taking up multiple lines
    pat = re.compile(
        r'^(\d{1,2}\/\d{1,2}\/\d{2}.*?)(?=^\d{1,2}\/\d{1,2}\/\d{2}.*?|\Z)', re.S | re.M)
    with open(text_file, encoding='utf-8') as f:
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


def countMedia(df, allmsg_stat):
    mediaPattern = r"(\<Media omitted\>)"
    mediadf = df[df.message.str.match(mediaPattern)]
    mediadf_stat = mediadf[['sender', 'message']].groupby(['sender'], sort=False)['message'].count(
    ).reset_index(name='count').sort_values(['count'], ascending=False).reset_index(drop=True)
    mergeddf = pd.merge(left=allmsg_stat, right=mediadf_stat,
                        how='left', left_on='sender', right_on='sender')
    return mergeddf


def countAllMessaages(df):
    return df[['sender', 'message']].groupby(['sender'], sort=False)['message'].count(
    ).reset_index(name='count').sort_values(['count'], ascending=False).reset_index(drop=True)


def mergeWithAllMembersData(mergeddf, allMembersdf):
    # whoever didn't send any messages
    mergeddf = pd.merge(right=mergeddf, left=allMembersdf,
                        how='outer', left_on='sender', right_on='sender')
    mergeddf = mergeddf.fillna(0)
    mergeddf = mergeddf.astype(
        {'count_allmsg': 'int64', 'count_media': 'int64', 'count_singleword': 'int64'})
    return mergeddf


def countSingleLetterMessage(df):
    singleWordMessagePattern = r"(.{1}$)"
    singleWordDf = df[df.message.str.match(singleWordMessagePattern)]
    singleWordDf_stat = singleWordDf[['sender', 'message']].groupby(['sender'], sort=False)['message'].count(
    ).reset_index(name='count').sort_values(['count'], ascending=False).reset_index(drop=True)
    return singleWordDf_stat
