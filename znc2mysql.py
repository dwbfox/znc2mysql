import znc
import zncmysql

class znc2mysql(znc.Module):
    description = "Passively record IRC logs to a MySQL database"
    regex = re.compile('^\seen (.+)$')
    logger = None

    def OnLoad(self, args, msg):
        self.PutModule("<<irc2mysql loaded.>>")
        return znc.CONTINUE


    def OnChanMsg(self, nick, channel, message):
        msg = message.s
        name = nick.GetNick()
        chan = channel.GetName()
        ircdb = zncmysql()
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
