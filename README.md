# whatsapp-chat-analysis

ref. https://www.zeolearn.com/magazine/introduction-to-text-mining-in-whatsapp-chats-using-python

Mine WhatsApp chat data a draw awesome inferences. Phrase Frequency plotting and a lot more!

Libraries used:

- nltk
- numpy
- matplotlib

pushtodb.py - it pushed data to sql db. remember to setup ENGINE_POWER env. var as connection string
analyse.py - it analyzes and draws chart

the utility parse method assumes file has date time format as month-day-year hh:mm pm format.
you have to chagne to required format as specified in https://strftime.org/ (https://stackoverflow.com/questions/26763344/convert-pandas-column-to-datetime)
:tada:
