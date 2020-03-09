
import mysql.connector
import datetime


def insertToDb(entries):

    mydb = mysql.connector.connect(
        host="<host>",
        user="<user>",
        passwd="<passwd>",
        database="<databasename>"
    )

    mycursor = mydb.cursor()

    sql = "insert into <tablename> (<col1>,<col2>,<col3>,<col4>)  VALUES ( %s, %s ,%s, %s)"

    mycursor.executemany(sql, entries)

    mydb.commit()

    print(mycursor.rowcount, "was inserted.")


if __name__ == "__main__":
    # execute only if run as a script
    insertToDb([('col1-value', 'col2-val', 'col3-val', 'col4-val')])
