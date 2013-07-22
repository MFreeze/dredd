#!/usr/bin/env python
#-*-coding:utf-8-*

import irc.bot
import irc.client
from threading import Timer
import signal
import sys
import getopt

OPTS={"chan":"#stux", "nick":"Dredd", "server":"dadaist.com", "port":1664, 
      "hello": "Ici la loi c'est moi.", "oppasswd":"BITE", "opname":"BITE", 
      "master":"mfreeze", "masterpass":"penis:666", "name":"Joseph Dredd",
      "bantime":300, "goodbye":"Je t'exploserai moi même la cervelle... personnellement!"}

CONFIG_FILE="dredd.conf"

def choseRightOne(dico, default, key):
    try :
        tmp = dico[key]
    except KeyError :
        tmp = default[key]
    return tmp

class DreddBase(irc.bot.SingleServerIRCBot):
    def __init__(self, dico=OPTS):
        default=OPTS
        server = irc.bot.ServerSpec(choseRightOne(dico, default, "server"), int(choseRightOne(dico, default, "port")))
        # Utilisation de la classe SingleServerIRCBot comme classe parente
        try :
            irc.bot.SingleServerIRCBot.__init__(self, [server], dico["nick"], dico["name"], 60)
        except KeyError :
            irc.bot.SingleServerIRCBot.__init__(self, [server], default["nick"], default["name"], 60)
        #self.ircobj.add_global_handler("youreoper", self.rapport)
        #self.ircobj.add_global_handler("all_events", self.rapportbis)
        # Define default options
        self.nick = choseRightOne(dico, default, "nick")
        # Channel sur lequel sévit Dredd
        self.channel = choseRightOne(dico, default, "chan")
        # Phrase d'accueil
        self.hello = choseRightOne(dico, default, "hello")
        # Les différents mots de passe
        self.master = choseRightOne(dico, default, "master")
        self.operpassword = choseRightOne(dico, default, "oppasswd")
        self.opername = choseRightOne(dico, default, "opname")
        self.banned=[]
        self.bantime=choseRightOne(dico, default, "bantime")
        # Identité du maître
        self.masterpassword = choseRightOne(dico, default, "masterpass")
        signal.signal(signal.SIGINT, self.quit)
        # Chargement des options
        self.services = {}
        self.goodbye=choseRightOne(dico, default, "goodbye")
        try :
            f = open("/etc/services", "r") #ro
            for line in f:
                if (not line.startswith("#")):
                    line = line.rstrip("\n").split("\t")
                    if (len(line) > 2):
                        if line[0] in self.services.keys():
                            # Si le service existe, on ajoute le port
                            self.services[line[0]] += ", %s" % line[2]
                        else:
                            self.services[line[0].lower()] = line[2]
            f.close()
        except Exception as e:
            print (e)
            print("Impossible de récupérer les services.")

    def unban(self, nick):
        self.connection.mode(self.channel, "-b %s" % nick)
        if nick in self.banned:
            print ("Unban : %s" % nick)
            self.banned.pop(self.banned.index(nick))

    def ban(self, channel, nick, comment=""):
        self.banned.append(nick)
        self.connection.kick(self.channel, nick, comment)
        self.connection.mode(self.channel, "+b %s" % nick)
        print ("Banned : %s" % nick)
        if (time > 0):
            t = Timer(self.bantime, self.unban, [nick])
            t.start()

    def on_youreoper(self, c, e):
        c.mode(self.channel, "+o %s" % self.nick)

    def rapportbis(self, c, e):
        print(e.eventtype())
    
    # Retourne le nick
    def getnickname(self):
        return self.nick

    # Action réalisée si le nick est utilisé
    def on_nicknameinuse(self, c, e):
        new = self.getnickname() + "_"
        c.nick(new)
        self.nick = new

    # Après la connexion au serveur, connexion au chan, puis petit coucou et récupération des droits
    def on_welcome(self, c, e):
        c.join(self.channel)
        c.privmsg(self.channel, self.hello)
        c.oper(self.opername, self.operpassword)

    # En cas de message privé
    def on_privmsg(self, c, e):
        a = e.arguments[0].lower()
        cmd = a.split(" ")
        if cmd[0] == "!id":
            auteur = e.source.nick
            complement = " ".join(cmd[1:])
            self.sid(complement, c, auteur)

    # En cas de connexion
    def on_join(self, c, e):
        qui = e.source.nick
        if (qui == self.master):
            c.privmsg(self.channel, "HEIL %s ! :3" % (qui))
            c.mode(qui, "+o")
        elif (qui.lower() == "djey"):
            c.privmsg(self.channel, "La fin du moooooooooonde! L'apacalypse est proche!")

    # En cas de déconnection
    def on_quit(self, c, e):
        qui = e.source.nick
        if (qui == self.master):
            self.master = OPTS["master"]

    # En cas de changement de nick
    def on_nick(self, c, e):
        qui = e.source.nick
        vers = e.target
        if (qui == self.master):
            self.master = vers

    def sid(self, complement, c, auteur):
        if complement == self.masterpassword:
            self.master = auteur
            c.privmsg(auteur, "=)")
        else :
            c.privmsg(auteur, "Fous toi ton %s où je pense!" % complement)

    def quit(self):
        self.disconnect(self.channel, "I'll be back!")
        self.die()

def readOptions(dico, cfg_file):
    try :
        with open(cfg_file, "r") as f:
            for line in f:
                lopt = line.split("=")
                dico[lopt[0].strip()] = lopt[1].strip()
    except :
        pass
    return dico

if __name__ == "__main__":
    try :
        opt, arg = getopt.getopt(sys.argv[1:], "c:")
    except getopt.GetoptError as err:
        print ("Erreur à la lecture des options, sélection des options par défaut")

    for o, a in opt: 
        if o == "c":
            CONFIG_FILE = a
        else :
            pass

    OPTS = readOptions(OPTS, CONFIG_FILE)

    dredd = DreddBase(OPTS)
    dredd.start()
