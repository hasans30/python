import sys
import os
import pandas as pd
import utilities
from sqlalchemy import create_engine


# Printing number of messages by sender
if len(sys.argv) < 2 or os.environ.get('ENGINE_POWER') == None:
    print(
        'usage:{name} <chat file folder - latest will be picked up>'.format(name=sys.argv[0]))
    print('Also, ensure connection string is set in ENGINE_POWER')
    exit(1)
filename = utilities.GetLatestFile(sys.argv[1], "/WhatsApp*")
print('Reading chat from '+filename)
df = utilities.parse_file(filename, allrecord=False)
# print(df.head(2))
engine = create_engine(os.environ['ENGINE_POWER'])
df.to_sql('chat_text', con=engine, if_exists='append', index=False)
print('done')
