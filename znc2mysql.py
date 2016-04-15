import znc
import re
import os
import datetime
import json
import pretty
import logging
import pymysql.cursors

class znc2mysql(znc.Module):
    description = "Passively record IRC logs to a MySQL database"
    regex = re.compile(b'^\seen (.+)$')
    logger = None

    def OnLoad(self, args, msg):
        self.PutModule('<<irc2mysql loaded.>>')
        self.PutModule('<<Dir: %s' % os.getcwd())
        return znc.CONTINUE


    def OnChanMsg(self, nick, channel, message):
        try:
            msg = message.s.encode('utf-8')
            name = nick.GetNick()
            chan = channel.GetName()
            ircdb = zncmysql()
            ircdb.insertUser(name, msg)
            ircdb.insertMessage(name, chan, msg)

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
            raise
        finally:
            return znc.CONTINUE

class zncmysql:

    connection = None
    logger = None
    settings = None

    def __init__(self):
        logger = logging.basicConfig(filename='irc2mysql.log', level=logging.DEBUG)
        with open('settings.json', 'r') as f:
            settings = json.loads(f.read())
        self.connection = pymysql.connect(
            host=settings['mysql']['host'],
            user=settings['mysql']['username'],
            password=settings['mysql']['password'],
            db=settings['mysql']['database'],
            cursorclass=pymysql.cursors.DictCursor
        )


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


if __name__ == '__main__':
    db = zncmysql()
    nick = 'reddit-bot'
    seen = db.userLastSeen(nick)
    print('%s was last seen %s saying, "%s"' % (nick, seen['seen'], seen['message']))
