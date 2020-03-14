import re
import os
import numpy as np
import pandas as pd
import datetime as datetimelib
import pytz
from languagelib import detectLang
from checkLastUpdate import LastUpdate


def parse_file(text_file, allrecord=True):
    '''Convert WhatsApp chat log text file to a Pandas dataframe.'''
    inputfolder = os.path.dirname(text_file)
    lu = LastUpdate(inputfolder)
    # some regex to account for messages taking up multiple lines
    pat = re.compile(
        r'^(\d{1,2}\/\d{1,2}\/\d{2}.*?)(?=^\d{1,2}\/\d{1,2}\/\d{2}.*?|\Z)', re.S | re.M)
    with open(text_file, 'r', encoding='utf-8') as f:
        data = [m.group(1).strip().replace('\n', ' ')
                for m in pat.finditer(f.read())]

    sender = []
    message = []
    datetime = []
    language = []
    for row in data:

        # timestamp is before the first dash
        tmp_dt = row.split(' - ')[0]
        tmp_dt = datetimelib.datetime.strptime(tmp_dt, '%m/%d/%y, %I:%M %p')
        pstpdt = pytz.timezone('US/Pacific')
        tmp_dt = pstpdt.localize(tmp_dt)
        ist = pytz.timezone('Asia/Calcutta')
        tmp_dt = tmp_dt.astimezone(ist)

        # sender is between am/pm, dash and colon
        tmp_sender = ''
        tmp_msg = ''
        tmp_lang = ''
        try:
            tmp_sender = re.search('[mM] - (.*?):', row).group(1)
        # message content is after the first colon
            tmp_msg = (row.split(': ', 1)[1])
        # language spoken
            line = (row.split(': ', 1)[1])
            if(re.match(r"(\<Media omitted\>)", line)):
                tmp_lang = 'media'
            else:
                tmp_lang = (detectLang(line))

            if allrecord == True or lu.shouldInsert(tmp_dt, tmp_sender, tmp_msg):
                datetime.append(tmp_dt)
                sender.append(tmp_sender)
                message.append(tmp_msg)
                language.append(tmp_lang)
        except:
            tmp_lang = ''

    if allrecord == False and len(datetime) > 0:
        lu.updateInsertTimestamp(datetime[-1], sender[-1], message[-1])
    df = pd.DataFrame(zip(datetime, sender, message, language), columns=[
                      'timestamp', 'sender', 'message', 'language'])

    df['timestamp'] = pd.to_datetime(
        df.timestamp)
# .tz_convert('Asia/Calcutta')
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


def countSingleLetterMessage(df, mediaOmitted_stat):
    singleWordMessagePattern = r"(.{1}$)"
    singleWordDf = df[df.message.str.match(singleWordMessagePattern)]
    singleWordDf_stat = singleWordDf[['sender', 'message']].groupby(['sender'], sort=False)['message'].count(
    ).reset_index(name='count').sort_values(['count'], ascending=False).reset_index(drop=True)

    singleWordDf_stat = pd.merge(left=mediaOmitted_stat, right=singleWordDf_stat,
                                 how='left', left_on='sender', right_on='sender')
    singleWordDf_stat.columns = ['sender', 'count_allmsg',
                                 'count_media', 'count_singleword']

    return singleWordDf_stat


def getDateTimeAndFileName(sys):
    need_date_filter = False
    date_time_str = '1970-01-01 00:00:00'
    date_time_obj = datetimelib.datetime.strptime(
        date_time_str, '%Y-%m-%d %H:%M:%S')
    opFileName = 'chart-all.png'
    if (len(sys.argv) > 2):
        # possible timestamp in argument
        try:
            datevalue = datetime.datetime.strptime(sys.argv[2], '%Y-%m')
            date_time_obj = datevalue
            opFileName = 'chart'+sys.argv[2]+'.png'
            need_date_filter = True
        except:
            print('using default datetime')
    return date_time_obj, opFileName, need_date_filter
