#!/usr/bin/env python
#-*- coding: utf-8 -*-

import sys
import ircbot
import irclib
import os
import urllib
import re
from  random import randrange,randint
from datetime import date

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
        print e
        self.do_command(e, e.arguments()[0])

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

    def tasoeur(self, complement):
        res = re.search(r'(le|du|la|un|une|mon|ma) ([a-zA-Zéàùôê]+)',complement)
        if res != None:
            if res.group(2) != None:
                if res.group(1) in ('le', 'du', 'un', 'mon'):
                    return "Un " + res.group(2) + " amphibien qui plus est."
                else:
                    return "C'est ta soeur la " + res.group(2)
        else:
            return None


    def roll(self, complement, c, auteur):
        if len(complement) != 0:
            c.privmsg(self.channel, "%s" % (self._des(complement)))
        else:
            c.privmsg(self.channel, "%s" % (self._des("1d6")))

    def urb(self, complement, c, auteur):
        url = "http://urbandictionary.com/define.php?"
        url += urllib.urlencode({"term":complement.lower()})
        c.privmsg(self.channel, "%s" % (url))

    def halp(self, complement, c, auteur):
        c.privmsg(self.channel, "%s %s" % ("Commandes disponibles sur le chan :", " ".join(self.ls_cmd_pb)))
        c.privmsg(self.channel, "%s %s" % ("Commandes disponibles en privé :", " ".join(self.ls_cmd_pv)))
        if (auteur == self.master):
            c.privmsg(self.master, "%s %s" % ("Commandes du grand maître :", " ".join(self.ls_cmd_gm)))

    # Permet de savoir si Steve Jobs est encore en vie
    def jobs(self, complement, c, auteur):
        html = urllib.urlopen("http://en.wikipedia.org/w/api.php?action=query&titles=Steve%20Jobs&prop=categories").read()
        rget = re.findall("deaths", html)
        if (len(rget) > 0):
            res = "Il est mort \o/"
        else:
            res = "Nope, encore en vie =("
        c.privmsg(self.channel, res)

    def bieber(self, complement, c, auteur):
        html = urllib.urlopen('http://en.wikipedia.org/w/api.php?action=query&titles=Justin%20Bieber&prop=categories').read()
        url = re.findall('deaths', html)
        if len(url) != 0:
            res = "Il est mort \o/"
        else:
            res = "Nope, encore en vie :("
        c.privmsg(self.channel, res)

    def get_port(self, serv):
        if (serv in self.services):
            return self.services[serv]
        else:
            return "Service inconnu"

    # Teste patience, si celle ci atteint 0, on kicke
    def _patience(self, c, auteur):
        self.patience -= 1
        if self.patience <= 0:
            c.kick(self.channel,auteur, "Le chan est désormais pacifié.")
            self.patience = INIT_PATIENCE

    # Teste si un lien est down
    def is_down(self, complement, c, auteur):
        mes = ""
        try:
            url_obj = urllib.urlopen(complement)
            if url_obj.getcode() == 200:
                mes += "Ta connexion est en carton."
            elif url_obj.getcode() == 404:
                mes += "Ca n'existe pas sur le serveur."
            else:
                mes += "Ca ne marche pas."
        except:
            mes += "Une url valide ça te dit quelque chose?"
            self._patience(c, auteur)
            return mes

    def pop(self, complement, c, auteur):
        if len(self.pile) > 0:
            c.privmsg(self.channel, "%s - %s left" % (self.pile.pop(), str(len(self.pile))))
        else:
            c.privmsg(self.channel, "Rien dans la pile")
            self._patience(c, auteur)

    def wp(self, complement, c, auteur):
        url = "http://en.wikipedia.org/w/index.php?"
        url += urllib.urlencode({"search":complement.lower()})
        c.privmsg(self.channel, "%s" % (url))

    def wpf(self, complement, c, auteur):
        url = "http://fr.wikipedia.org/w/index.php?"
        url += urllib.urlencode({"search":complement.lower()})
        c.privmsg(self.channel, "%s" % (url))

    def enfr(self, complement, c, auteur):
        url = "http://www.wordreference.com/enfr/" 
        url += urllib.pathname2url(complement.lower())
        c.privmsg(self.channel, "%s" % (url))

    def fren(self, complement, c, auteur):
        url = "http://www.wordreference.com/fren/" 
        url += urllib.pathname2url(complement.lower())
        c.privmsg(self.channel, "%s" % (url))

    def popall(self, complement, c, auteur):
        while len(self.pile) > 0:
            self.pop(complement, c, auteur)
        self.pop(complement, c, auteur)

    def port(self, complement, c, auteur):
        c.privmsg(self.channel, "%s : %s" % complement, self.get_port(complement.lower()))

    def down(self, complement, c, auteur):
        c.privmsg(self.channel, self.is_down(complement, auteur, c))

    def weekend(self, complement, c, auteur):
        c.privmsg(self.channel, WEEKEND[date.today().weekday()])

    # Gestion des commandes publiques
    def execute_action(self, e, arg):
        c = self.connection
        auteur = irclib.nm_to_n(e.source())

        cmd = arg.split()

        if cmd[0] in self.ls_cmd_pb:
            # Récupération des arguments de la commande
            complement = " ".join(cmd[1:])
            getattr(self, cmd[0][1:])(complement, c, auteur)



    # Gestion des blagues
    def execute_sentence(self, e, blague):
        c = self.connection
        auteur = irclib.nm_to_n(e.source())

        if (blague == "a+" or blague == "++"):
            c.privmsg(self.channel, "Je savais que vous alliez dire ça.")
        elif (blague == "marie france" or blague == "marie-france"):
            c.privmsg(self.channel, "Mmmmmmmh, Marie France :)")
        elif (blague == "sasha"):
            c.privmsg(self.channel, "<3")
        elif (blague == "pute"):
            c.privmsg(self.channel, "Juge pute!")
        elif (blague == "concentré" or blague == "concentrer"):
            c.privmsg(self.channel, "T'as qu'à aller dans un camps !")
        elif (blague == "xd"):
            c.kick(self.channel, auteur, "MEIN LEBENSRAUM \o/")
        elif (blague == "chmod"):
            c.kick(self.channel, auteur, "La séance est levée.")
        elif (blague == "kikoo"):
            c.kick(self.channel, auteur, "Désolé, j'ai mes règles.")
        elif (blague == "arwen"):
            c.kick(self.channel, auteur, "Leia > *")
        elif (blague == "soeur"):
            c.privmsg(self.channel, "Ta soeur porte des leggings")
        elif (blague == "chmod 777"):
            c.kick(self.channel, auteur, "PUTAIIIIIIN")

    def saychan(self, complement, c, auteur):
        c.privmsg(self.channel, complement)

    # TODO: Si complement == "", kicke un type au hasard
    def kick(self, complement, c, auteur):
        c.kick(self.channel, complement, "Dans ta face ...")
        self.patience += 2
    
    def op(self, complement, c, auteur):
        if complement == "":
            complement = auteur
        c.mode(self.channel, "+o %s" % complement)

    def update(self, complement, c, auteur):
        os.system("sleep 2 && %s a" % sys.argv[0])
        c.disconnect(self.channel, "I'll be back!")
        sys.exit(0)

    def quit(self, complement, c, auteur):
        c.disconnect(self.channel, "I WILL SURVIVE!")
        sys.exit(0)

    def topic(self, complement, c, auteur):
        c.topic(self.channel, complement)

    def push(self, complement, c, auteur):
        if len(self.pile) < PILE_MAX_SIZE:
            self.pile.append(complement)
            self.patience += 1
            c.privmsg(auteur, "C'est noté.")
        else:
            c.privmsg(auteur, "Pile pleine!")
            self._patience(c, auteur)

    def id(self, complement, c, auteur):
        if complement == self.masterpassword:
            self.master = auteur
            c.privmsg(auteur, "=)")
        else:
            c.privmsg(auteur, "Fous toi ton %s où je pense!" % complement)
            self._patience(c, auteur)

    # Liste des actions réalisées en réponse à des messages privés
    def do_command(self, e, arg):

        # Utilisation du masque irclib.nm_to_n pour récupérer l'auteur du message
        auteur = irclib.nm_to_n(e.source())
        c = self.connection

        cmd = arg.split()
        complement = ""
        boo = False


        # On vérifie la validité de la commande
        if cmd[0] in self.ls_cmd_pv or cmd[0] in self.ls_cmd_gm:

            # Récupération des arguments de la commande
            complement = " ".join(cmd[1:])
            if cmd[0] in self.ls_cmd_gm :
                if auteur != self.master:
                    c.kick(self.channel, auteur, "Fallait pas me prendre pour un con.")
                    self.patience += 2
                    boo = True
                else:
                    try:
                        boo = True
                        getattr(self, cmd[0][1:])(complement, c, auteur) 
                    except:
                        pass
            else:
                try:
                    boo = True
                    getattr(self, cmd[0][1:])(complement, c, auteur) 
                except:
                    pass
        if not boo:
            c.privmsg(auteur, "Mais ta gueule !")
            self._patience(c, auteur)


if __name__ == "__main__":
    dredd = DreddBase(CHAN, NICK, SERV, PORT, HELLO, MASTER, MASTERPASS, OPPASSWD, OPLOGIN)
    dredd.start()
