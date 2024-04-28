import re
import os
import glob
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

    actiondatetime = []
    actor = []
    action = []
    actedon = []

    lastdate = None
    lastsender = None
    lastmessage = None

    for row in data:
        # timestamp is before the first dash
        tmp_dt = row.split(' - ')[0]
        tmp_dt = datetimelib.datetime.strptime(tmp_dt, '%m/%d/%y, %H:%M')
        pstpdt = pytz.timezone('US/Pacific')
        tmp_dt = pstpdt.localize(tmp_dt)
        ist = pytz.timezone('Asia/Calcutta')
        tmp_dt = tmp_dt.astimezone(ist)

        # sender is between am/pm, dash and colon
        tmp_sender = ''
        tmp_msg = ''
        tmp_lang = ''
        try:
            actions = get_action_type(row)
            if actions != None: 
                actiondatetime.append(tmp_dt)
                actor.append(actions.group(1))
                action.append(actions.group(2))
                actedon.append(actions.group(3))

                lastdate = tmp_dt
                lastsender = actions.group(1)
                lastmessage = actions.group(2)

            # it is not action type - process as message. else process as action
            else:
                tmp_sender = re.search('.* - (.*?):', row).group(1)
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
                    lastdate = tmp_dt
                    lastsender = tmp_sender
                    lastmessage = tmp_msg

        except:
            tmp_lang = ''

    if allrecord == False and lastdate != None:
        lu.updateInsertTimestamp(lastdate, lastsender, lastmessage)
    df = pd.DataFrame(zip(datetime, sender, message, language), columns=[
                      'timestamp', 'sender', 'message', 'language'])

    df['timestamp'] = pd.to_datetime(
        df.timestamp)
# .tz_convert('Asia/Calcutta')
    # remove events not associated with a sender
    df = df[df.sender != ''].reset_index(drop=True)

    # action dataframe
    df_action = pd.DataFrame(
        zip(actiondatetime, actor, action, actedon), columns=['timestamp', 'actor', 'action', 'actedon'])

    return df, df_action


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


def GetLatestFile(dirname, pattern):
    list_of_files = glob.glob(dirname+pattern)
    latest_file = ''
    try:
        latest_file = max(list_of_files, key=os.path.getctime)
    except:
        pass
    return latest_file


def parse_action(text):
    return get_action_type(text)


def get_action_type(text):
    if len(text.split(':')) > 2:
        return None
    pat = ".*- (.+[^:]) (left|added|created group|removed|now an admin|changed this group.s icon|changed the subject from |changed the group description |no longer an admin |was added |deleted this group.s icon|joined from the community|requested to join.)(.*)"
    compiled = re.compile(pat)
    allmatches = compiled.match(text)
    return allmatches


def print_sender_count(df):
    n_days =180 
    print(f"printing information from past : {n_days} days")

    given_timestamp = max(df['timestamp'])
    seven_days_ago = given_timestamp - datetimelib.timedelta(days=n_days)
    df_last_n_days = df[df['timestamp'] > seven_days_ago]
    # Calculate message_count
    message_count = df_last_n_days['sender'].value_counts()
    # Print message_count
    print(message_count.to_frame().rename(columns={'sender': 'count'}).reset_index().to_string(index=True))

if __name__ == "__main__":
    df,dfAction = parse_file("./data/WhatsApp Chat with IIEST SIG DataSciences ComputerSciences.txt");
    print_sender_count(df)
    left = parse_action(
        "3a/1/20, 8:01 PM - Person1 left")
    assert(left.group(1) == 'Person1')
    changedicon = parse_action(
        "11/21/19, 10:28 PM - Person1 changed this group's icon")
    assert(changedicon.group(1) == 'Person1')
    normalmsg = parse_action(
        "11/5/19, 9:44 PM - Person2: hello friends why you left..example")
    assert(normalmsg == None)
    deletedicon = parse_action(
        "12/6/19, 11:10 AM - fn ln deleted this group's icon")
    assert(deletedicon.group(1) == 'fn ln')
    changedSubject = parse_action(
        '12/14/19, 7:45 PM - fn ln changed the subject from "abc..." to "Happy Birthday xyz')
    assert(changedSubject.group(1) == 'fn ln')
    added = parse_action("12/9/19, 12:12 AM - fnd2 added fnd1")
    assert(added.group(1) == 'fnd2')
    removed = parse_action("2/20/20, 9:24 PM - fnd2 removed +11 11111 11111")
    assert(removed.group(1) == 'fnd2')
    file = GetLatestFile(
        R'C:\Users\msheikh\OneDrive\Documents\Angikaar\chat', "/WhatsApp*")
    print(file)
