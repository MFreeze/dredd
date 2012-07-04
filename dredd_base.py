#!/usr/bin/env python
#-*- coding: utf-8 -*-

import ircbot
import irclib

CHAN="#stux"
NICK="Dredd"
SERV="dadaist.com"
PORT=1664
HELLO="Ici la loi c'est moi."
OPPASSWD="BITE"
OPLOGIN="BITE"

MASTER="trax"
MASTERPASS = "penis:666"

class DreddBase(ircbot.SingleServerIRCBot):
    def __init__(self, channel, nick, server, port=6667, hello="Ici, la Loi c'est moi.", 
                 master = "", masterpass = "", oppasswd = "", opname = ""):
        # Utilisation de la classe SingleServerIRCBot comme classe parente
        ircbot.SingleServerIRCBot.__init__(self, [(server, port)], nick, 60)
        #self.ircobj.add_global_handler("youreoper", self.rapport)
        #self.ircobj.add_global_handler("all_events", self.rapportbis)
        self.nick = nick
        # Channel sur lequel sévit Dredd
        self.channel = channel
        # Phrase d'accueil
        self.hello = hello
        # Les différents mots de passe
        self.master = master
        self.operpassword = oppasswd
        self.opername = opname
        # Identité du maître
        self.masterpassword = masterpass
        self.services = {}
        try:
            f = open("/etc/services") #ro
            for line in f:
                if (not line.startswith("#")):
                    line = line.rstrip("\n").split("\t")
                    if (len(line) > 2):
                        if line[0] in self.services:
                            # Si le service existe, on ajoute le port
                            self.services[line[0]] += ", %s" % line[2]
                        else:
                            self.services[line[0].lower()] = line[2]
                    f.close()
        except:
            print("Impossible de récupérer les services.")

    def on_youreoper(self, c, e):
        c.mode(self.channel, "+o %s" % self.nick)

    def rapportbis(self, c, e):
        print e.eventtype()
    
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
        a = e.arguments()[0].lower()
        cmd = a.strip()
        if cmd[0] == "!id":
            auteur = irclib.nm_to_n(e.source())
            complement = " ".join(cmd[1:])
            self.id(complement, c, auteur)

    # En cas de connexion
    def on_join(self, c, e):
        qui = irclib.nm_to_n(e.source())
        if (qui == self.master):
            c.privmsg(self.channel, "HEIL %s ! :3" % (qui))
            c.mode(qui, "+o")
        elif (qui.lower() == "amz"):
            c.privmsg(self.channel, "TITS OR GTFO!")
        elif (qui.lower() == "djey"):
            c.privmsg(self.channel, "La fin du moooooooooonde! L'apacalypse est proche!")

    # En cas de déconnection
    def on_quit(self, c, e):
        qui = irclib.nm_to_n(e.source())
        if (qui == self.master):
            self.master = MASTER

    # En cas de changement de nick
    def on_nick(self, c, e):
        qui = irclib.nm_to_n(e.source())
        vers = irclib.nm_to_n(e.target())
        if (qui == self.master):
            self.master = vers

    def id(self, complement, c, auteur):
        if complement == self.masterpassword:
            self.master = auteur
            c.privmsg(auteur, "=)")
        else:
            c.privmsg(auteur, "Fous toi ton %s où je pense!" % complement)

if __name__ == "__main__":
    dredd = DreddBase(CHAN, NICK, SERV, PORT, HELLO, MASTER, MASTERPASS, OPPASSWD, OPLOGIN)
    dredd.start()
