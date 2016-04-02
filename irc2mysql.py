import znc
import datetime
import pymysql.cursors

class irc2mysql(znc.Module):
    connection = None
    description = "Passively record IRC logs to a MySQL database"
    
    def __init__(self):
        self.connection = pymysql.connect(
            host='localhost',
            user='root',
            password='root',
            db='irc',
            cursorclass=pymysql.cursors.DictCursor
        )


    def OnLoad(self, args, msg):
        self.PutModule("<<irc2mysql loaded.>>")
        return znc.CONTINUE


    def OnChanMsg(self, nick, channel, message):
        msg = message.s
        name = nick.GetNick()
        chan = channel.GetName()
        self.insertUser(name, msg)
        self.insertMessage(name, chan, msg)


    def insertMessage(self, user, channel, message):
        uid = None
        # Get the ID of the user
        with self.connection.cursor() as cursor:
            try:
                cursor.execute("SELECT id FROM `users` WHERE nick=%s LIMIT 1", user)
                result = cursor.fetchone()
                uid = result['id']
            except:
                pass # TODO: handle this case

        self.connection.commit()

        # Insert the message
        with self.connection.cursor() as cursor:
            cursor.execute("INSERT INTO `messages` (`channel`, `user`, `message`) VALUES (%s, %s, %s)", (channel, uid, message))
        self.connection.commit()


    def insertUser(self, user, message):
        with self.connection.cursor() as cursor:
            cursor.execute("INSERT INTO `users` (`nick`, `last_message`) VALUES (%s, %s) ON DUPLICATE KEY UPDATE last_message=%s", (user, message, message))
        self.connection.commit()


    def getTimeStamp(self):
        return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


    def __del__(self):
        self.connection.close()

