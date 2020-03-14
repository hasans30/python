import hashlib
import uuid
import os
import pytz
import json
import datetime
from dateutil import parser


class LastUpdate:
    text_file = 'lastupdate.txt'
    lastupdate = ''
    pastLastUpdatedRecord = False

    def __init__(self, foldername):
        self.lastupdate = ''
        self.haveSeenLastUpdatedRecord = False
        self.text_file = os.path.join(foldername, self.text_file)
        pass

    def shouldInsert(self, timestamp, sender, text):
        filedata = self.getLastUpdatedEntry()
        self.updateHaveSeenLastUpdatedRecord(timestamp, sender, text)
        return filedata['time'] < timestamp or (
            self.haveSeenLastUpdatedRecord == True and
            filedata['time'] == timestamp and filedata['sender'] != sender and filedata['text'] != text)

    def updateHaveSeenLastUpdatedRecord(self, timestamp, sender, text):
        if self.haveSeenLastUpdatedRecord == False and timestamp == self.lastupdate['time'] and self.lastupdate['text'] == text and self.lastupdate['sender'] == sender:
            self.haveSeenLastUpdatedRecord = True

    def updateInsertTimestamp(self, timestamp, sender, text):
        data = {
            'time': timestamp,
            'sender': sender,
            'text': text
        }
        with open(self.text_file, 'w') as f:
            f.write(json.dumps(data, indent=4, sort_keys=True, default=str))

    def getLastUpdatedEntry(self):
        if os.path.exists(self.text_file) == False:
            self.lastupdate = {
                'time': parser.parse('1970-01-01 00:00:00+05:30'),
                'sender': 'sender',
                'text': 'text'
            }
            return self.lastupdate
        if(self.lastupdate == ''):
            with open(self.text_file, 'r') as f:
                entry = f.read()
                self.lastupdate = json.loads(str(entry))
                self.lastupdate['time'] = parser.parse(
                    self.lastupdate['time'])
        return self.lastupdate


if __name__ == '__main__':

    lu = LastUpdate('.')
    tmpfile = lu.text_file+str(uuid.uuid4())
    # clean up
    if os.path.exists(lu.text_file):
        print('moving existing file to:'+tmpfile)
        os.rename(lu.text_file, tmpfile)
    expected = {
        'time': parser.parse('1970-01-01 00:00:00+05:30'),
        'sender': 'sender',
        'text': 'text'
    }
    assert lu.getLastUpdatedEntry(
    ) == expected, "getLatestUpdateEntry Failed"

    tmp_dt = '3/12/20, 11:05 AM'
    tmp_dt = datetime.datetime.strptime(tmp_dt, '%m/%d/%y, %I:%M %p')
    pstpdt = pytz.timezone('US/Pacific')
    tmp_dt = pstpdt.localize(tmp_dt)

    lu.updateInsertTimestamp(
        tmp_dt, 'sender', 'hello')
    assert lu.shouldInsert(
        tmp_dt, 'sender', 'hello') == True, "shouldInsert Failed"

    if os.path.exists(tmpfile):
        os.rename(tmpfile, lu.text_file)
    else:
        os.remove(lu.text_file)

    print('all test done')
