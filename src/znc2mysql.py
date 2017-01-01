import znc
import re
import sys
import os
import logging
import pymysql.cursors
import json
import datetime

###########################################
#  MySQL class to handle 
#  Database connection and recording
###########################################
class zncmysql:

    connection = None
    logger = None

    def __init__(self):
        logger = logging.basicConfig(filename='irc2mysql.log', level=logging.DEBUG)
        try:
            self.connection = pymysql.connect(
                host='localhost',
                user='root',
                password='root',
                db='irc',
                cursorclass=pymysql.cursors.DictCursor
            )
        except Exception as e:
            logger.warning('Unable to connect to database: %s' % str())


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
                seen['seen'] = results['last_seen']
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


class znc2mysql(znc.Module):
    """znc2mysql
    ZNC module that facilitates the logging 
    functionliaty"""

    description = "Store IRC logs to a MySQL database"
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
                    logger.info('Queried user not found: %s' % queried_nick)
                    self.PutModule('Queried user not found: %s' % queried_nick)
                else:
                    self.PutModule('%s was last seen %s saying, "%s"' % (queried_nick, seen['seen'], seen['message']))
                    logger.info('%s was last seen %s saying, "%s"' % (queried_nick, seen['seen'], seen['message']))
        except Exception as e:
            logger.info('<<error>> %s' % str(e))
        finally:
            return znc.CONTINUE



