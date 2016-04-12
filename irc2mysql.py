import znc
import re
import datetime
import pretty
import logging
import pymysql.cursors


class znc2mysql:

    connection = None

    def __init__(self):
        self.connection = pymysql.connect(
            host='localhost',
            user='root',
            password='root',
            db='irc',
            cursorclass=pymysql.cursors.DictCursor
        )


    def userLastSeen(self, nick):
        with self.connection.cursor() as cursor:
            try:
                seen = {}
                uid = self.getUIDByNick(nick)
                cursor.execute("SELECT last_seen, last_message FROM `users` WHERE nick=%s", nick)
                results = cursor.fetchone()
                seen['seen'] = pretty.date(results['last_seen'], short=False)
                seen['message'] = results['last_message']
                return seen
            except Exception as e:
                print('Error: %s', str(e))
                return None


    def getUIDByNick(self, nick):
        with self.connection.cursor() as cursor:
            try:
                cursor.execute("SELECT id FROM `users` WHERE nick=%s LIMIT 1", nick)
                result = cursor.fetchone()
                return result['id']
            except:
                return None


    def insertMessage(self, user, channel, message):
        uid = self.getUIDByNick(user)
        self.connection.commit()
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

class irc2mysql(znc.Module):
    description = "Passively record IRC logs to a MySQL database"
    regex = re.compile('^\seen (.+)$')
    logger = None

    def __init__(self):
        logger = logging.basicConfig(filename='irc2mysql.log', level=logging.DEBUG)


    def OnLoad(self, args, msg):
        self.PutModule("<<irc2mysql loaded.>>")
        return znc.CONTINUE


    def OnChanMsg(self, nick, channel, message):
        msg = message.s
        name = nick.GetNick()
        chan = channel.GetName()
        ircdb = znc2mysql()
        ircdb.insertUser(name, msg)
        ircdb.insertMessage(name, chan, msg)

        try:
            matches = self.regex.match(msg)
            if matches is not None:
                queried_nick = matches.group(1)
                seen = db.userLastSeen(queried_nick)
                if seen is None:
                    logger.debug('Queried user not found: %s' % queried_nick)
                    self.PutModule('Queried user not found: %s' % queried_nick)
                else:
                    self.PutModule('%s was last seen %s saying, "%s"' % (queried_nick, seen['seen'], seen['message']))
                    logger.debug('%s was last seen %s saying, "%s"' % (queried_nick, seen['seen'], seen['message']))
        except Exception as e:
            self.PutModule('<<error>> parsing query (%s) for %s' % (str(e), msg))

if __name__ == '__main__':
    print('<<<active>>>')
    # Fetch last seen
    db = znc2mysql()
    nick = 'pepee'
    seen = db.userLastSeen(nick)
    print('%s was last seen %s saying, "%s"' % (nick, seen['seen'], seen['message']))
