#!/usr/bin/env python
#-*-coding:utf-8-*

import irc.bot
import irc.client
from threading import Timer
import signal
import sys
import getopt

import os
import urllib
import urllib.parse
import urllib.request
import re
from  random import randrange,randint
from datetime import date

OPTS={"chan":"#stux", "nick":"Dredd", "server":"dadaist.com", "port":1664, 
      "hello": "Ici la loi c'est moi.", "oppasswd":"BITE", "opname":"BITE", 
      "master":"trax", "masterpass":"penis:666"}

CONFIG_FILE="dredd.conf"

LISTE_CMD_PUB = ["!pop", "!roll", "!enfr", "!fren", "!wp", "!wpf", "!urb", "!port",
                 "!halp", "!down", "!jobs", "!bieber", "!weekend", "!dredd", "!popall", "!rr",
                 "!getscore"]
LISTE_CMD_PRIV = ["!push", "!id"]
LISTE_CMD_MASTER = ["!update", "!kick", "!topic", "!saychan", "!op", "!uban", "!reset"]
LISTE_BLAGUE = {"a+":("privmsg", "Je savais que vous alliez dire ça."),
                "++":("privmsg", "Je savais que vous alliez dire ça."),
                "marie france":("privmsg", "Mmmmmmmh, Marie France :)"),
                "marie-france":("privmsg", "Mmmmmmmh, Marie France :)"), 
                "sasha":("privmsg", "<3"), 
                "soeur":("privmsg", "Ta soeur porte des leggings!"), 
                "pute":("privmsg", "Juge pute!"),
                "concentré":("privmsg", "T'as qu'à aller dans un camps!"),
                "concentrer":("privmsg", "T'as qu'à aller dans un camps!"), 
                "xd":("kick", "MEIN LEBENSRAUM o/"), 
                "chmod":("kick", "La séance est levée."),
                "><":("kick", "Tas de cons!"), 
                "kikoo":("kick", "Désolé j'ai mes règles"), 
                "arwen":("kick", "Leia > *"),
                "chmod 777":("kick", "PUTAIIIIIIIIN"),
                "^^":("kick", "I'm back!")}

PILE_MAX_SIZE = 16
INIT_PATIENCE = 4
WEEKEND = ['Déjà ?', 'T\'en est loin coco.', 'Nope :(', 'ça vient !', 'Preque \o/', 'Mais on est déjà en weekend, va te biturer !', 'C\'est déjà presque finis :(']

MASTER="trax"
MASTERPASS="penis:666"

# TODO: Lecture des scores dans un fichier
SCORE_FILE="dredd.score"

OPTS={"chan":"#stux", "nick":"Dredd", "server":"dadaist.com", "port":1664, 
      "hello": "Ici la loi c'est moi.", "oppasswd":"BITE", "opname":"BITE", 
      "master":"trax", "masterpass":"penis:666", "liste_blague":LISTE_BLAGUE,
      "list_cmd_gm":LISTE_CMD_MASTER, "list_cmd_pv":LISTE_CMD_PRIV,
      "list_cmd_pub":LISTE_CMD_PUB, "weekend":WEEKEND, "name":"Joseph Dredd"}

CONFIG_FILE="dredd.conf"

class DreddBase(irc.bot.SingleServerIRCBot):
    def __init__(self, dico):
        server = irc.bot.ServerSpec(dico["server"], int(dico["port"]))
        # Utilisation de la classe SingleServerIRCBot comme classe parente
        irc.bot.SingleServerIRCBot.__init__(self, [server], dico["nick"], dico["name"], 60)
        #self.ircobj.add_global_handler("youreoper", self.rapport)
        #self.ircobj.add_global_handler("all_events", self.rapportbis)
        self.nick = dico["nick"]
        # Channel sur lequel sévit Dredd
        self.channel = dico["chan"]
        # Phrase d'accueil
        self.hello = dico["hello"]
        # Les différents mots de passe
        self.master = dico["master"]
        self.operpassword = dico["oppasswd"]
        self.opername = dico["opname"]
        self.banned=[]
        # Identité du maître
        self.masterpassword = dico["masterpass"]
        signal.signal(signal.SIGINT, self.quit)
        # Chargement des options
        self.services = {}
        try:
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
            self.banned.pop(self.banned.index(nick))

    def ban(self, channel, nick, comment="", time=1620):
        if nick not in self.banned:
            self.banned.append(nick)
        self.connection.kick(self.channel, nick, comment)
        self.connection.mode(self.channel, "+b %s" % nick)
        if (time > 0):
            t = Timer(time, self.unban, [nick])
            t.start()

    def on_youreoper(self, c, e):
        c.mode(self.channel, "+o %s" % self.nick)

    def rapportbis(self, c, e):
        print (e.eventtype())
    
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
        cmd = a.strip()
        if cmd[0] == "!id":
            auteur = e.source.nick
            complement = " ".join(cmd[1:])
            self.id(complement, c, auteur)

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

    def id(self, complement, c, auteur):
        if complement == self.masterpassword:
            self.master = auteur
            c.privmsg(auteur, "=)")
        else:
            c.privmsg(auteur, "Fous toi ton %s où je pense!" % complement)

    def quit(self):
        self.disconnect(self.channel, "I'll be back!")
        sys.exit(0)

class Dredd(DreddBase):
    def __init__(self, dico):
        DreddBase.__init__(self, dico)
        # Liste des commandes acceptées sur le chan
        self.ls_cmd_pb = dico["list_cmd_pub"]
        # Liste des commandes acceptées en privé
        self.ls_cmd_pv = dico["list_cmd_pv"]
        self.ls_cmd_gm = dico["list_cmd_gm"]
        self.week = dico["weekend"]
        # Liste des mots provoquant une action de la part de Dredd
        self.ls_blague = dico["liste_blague"]
        # Création de la pile
        self.pile = list()
        # Indice de patience
        self.patience = INIT_PATIENCE
        self.curscore = {}
        self.maxscore = {}
        self.bestguy = ""
        self.bestscore = 0
        signal.signal(signal.SIGINT, self.quit)

    # Fonction gérant le lancer de dés
    def _des(self, arg):
        dice = arg.split("d")
        sides = int(dice[1])
        num = int(dice[0])
        if num > 9999 or sides > 9999:
            return "WTF?!?"
        return sum(randrange(sides)+1 for die in range(num))

    # En cas de message privé
    def on_privmsg(self, c, e):
        self.do_command(e, e.arguments[0])

    # En cas de messages publiés sur le channel
    def on_pubmsg(self, c, e):
        a = e.arguments[0].lower()

        # On cherche dans la phrase s'il y a une blague à faire
        for i in (self.ls_blague.keys()):
            if ((not a.find(i) == -1) and not ( e.source.nick == self.getnickname())) :
                self.execute_sentence(e, i)
                break

        # Puis on cherche si il s'agit d'une commande viable
        cmd = a.split()
        if cmd[0] in self.ls_cmd_pb:
            self.execute_action(e, e.arguments[0])

        if randint(0,100) == 42:
            ts = self.tasoeur(a)
            if ts != None:
                c.privmsg(self.channel, "%s" % ts)

    def getscore(self, complement, c, auteur):
        if auteur not in self.maxscore.keys():
            c.privmsg(self.channel, "T'as pas joué, abruti!")
            self._patience(c, auteur)
        else:
            c.privmsg(self.channel, "Perso : en cours : %d, Meilleur : %d" % (self.curscore[auteur],
                                                                              self.maxscore[auteur]))
            c.privmsg(self.channel, "Meilleur joueur : %s (%d points)" % (self.bestguy,
                                                                          self.bestscore))

    def reset(self, complement, c, auteur):
        self.curscore = {}
        self.maxscore = {}
        self.bestscore = 0
        self.bestguy = ""
        c.privmsg(self.channel, "Nouveau départ.")

    def dredd(self, complement, c, auteur):
        c.privmsg(self.channel, "La version 1 est morte...")

    def rr(self, complement, c, auteur):
        if self._des("1d6") == 6:
            self.ban(self.channel, auteur, "Je vais le remettre au rayon surgelé")
            if auteur in self.curscore.keys():
                self.curscore[auteur] = 0
        else:
            if auteur in self.curscore.keys():
                self.curscore[auteur] += 1
                if self.maxscore[auteur] < self.curscore[auteur]:
                    c.privmsg(self.channel, "Nouveau meilleur score : %d" % self.curscore[auteur])
                    self.maxscore[auteur] = self.curscore[auteur]
            else:
                self.curscore[auteur] = 1
                c.privmsg(self.channel, "Nouveau meilleur score : %d" % self.curscore[auteur])
                self.maxscore[auteur] = self.curscore[auteur]
            if self.maxscore[auteur] > self.bestscore:
                self.bestscore = self.maxscore[auteur]
                self.bestguy = auteur

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

    def uban(self, complement, c, auteur):
        arg = complement.split()
        try:
            self.ban(self.channel, arg[0], "Une simple envie...", arg[1])
        except:
            pass

    def roll(self, complement, c, auteur):
        if len(complement) != 0:
            c.privmsg(self.channel, "%s" % (self._des(complement)))
        else:
            c.privmsg(self.channel, "%s" % (self._des("1d6")))

    def urb(self, complement, c, auteur):
        url = "http://urbandictionary.com/define.php?"
        url += urllib.parse.urlencode({"term":complement.lower()})
        c.privmsg(self.channel, "%s" % (url))

    def halp(self, complement, c, auteur):
        c.privmsg(self.channel, "%s %s" % ("Commandes disponibles sur le chan :", " ".join(self.ls_cmd_pb)))
        c.privmsg(self.channel, "%s %s" % ("Commandes disponibles en privé :", " ".join(self.ls_cmd_pv)))
        if (auteur == self.master):
            c.privmsg(self.master, "%s %s" % ("Commandes du grand maître :", " ".join(self.ls_cmd_gm)))

    # Permet de savoir si Steve Jobs est encore en vie
    def jobs(self, complement, c, auteur):
        html = urllib.request.urlopen("http://en.wikipedia.org/w/api.php?action=query&titles=Steve%20Jobs&prop=categories").read()
        rget = re.findall("deaths", str(html))
        if (len(rget) > 0):
            res = "Il est mort \o/"
        else:
            res = "Nope, encore en vie =("
        c.privmsg(self.channel, res)

    def bieber(self, complement, c, auteur):
        html = urllib.request.urlopen('http://en.wikipedia.org/w/api.php?action=query&titles=Justin%20Bieber&prop=categories').read()
        url = re.findall('deaths', str(html))
        if len(url) != 0:
            res = "Il est mort \o/"
        else:
            res = "Nope, encore en vie :("
        c.privmsg(self.channel, res)

    def get_port(self, serv):
        if (serv in self.services.keys()):
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
            url_obj = urllib.request.urlopen(complement)
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
        url += urllib.parse.urlencode({"search":complement.lower()})
        c.privmsg(self.channel, "%s" % (url))

    def wpf(self, complement, c, auteur):
        url = "http://fr.wikipedia.org/w/index.php?"
        url += urllib.parse.urlencode({"search":complement.lower()})
        c.privmsg(self.channel, "%s" % (url))

    def enfr(self, complement, c, auteur):
        url = "http://www.wordreference.com/enfr/" 
        url += urllib.request.pathname2url(complement.lower())
        c.privmsg(self.channel, "%s" % (url))

    def fren(self, complement, c, auteur):
        url = "http://www.wordreference.com/fren/" 
        url += urllib.request.pathname2url(complement.lower())
        c.privmsg(self.channel, "%s" % (url))

    def popall(self, complement, c, auteur):
        while len(self.pile) > 0:
            self.pop(complement, c, auteur)
        self.pop(complement, c, auteur)

    def port(self, complement, c, auteur):
        c.privmsg(self.channel, "%s : %s" % (complement, self.get_port(complement.lower())))

    def down(self, complement, c, auteur):
        c.privmsg(self.channel, self.is_down(complement, c, auteur))

    def weekend(self, complement, c, auteur):
        c.privmsg(self.channel, self.week[date.today().weekday()])

    # Gestion des commandes publiques
    def execute_action(self, e, arg):
        c = self.connection
        auteur = e.source.nick
        cmd = arg.split()
        if cmd[0] in self.ls_cmd_pb:
            # Récupération des arguments de la commande
            complement = ""
            complement += " ".join(cmd[1:])
            getattr(self, cmd[0][1:])(complement, c, auteur)


    # Gestion des blagues
    def execute_sentence(self, e, blague):
        c = self.connection
        auteur = e.source.nick
        action = self.ls_blague[blague]
        if action[0].strip() == "privmsg":
            getattr(c, action[0])(self.channel, action[1])
        else:
            getattr(c, action[0])(self.channel, auteur, action[1])

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
        self.quit()

    def quit(self, signal=0, frame=""):
        for i in self.banned:
            self.unban(i)
        self.connection.disconnect("I WILL SURVIVE!")
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
        auteur = e.source.nick
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
    try:
        opt, arg = getopt.getopt(sys.argv[1:], "c:")
    except getopt.GetoptError as err:
        print ("Erreur à la lecture des options, sélection des options par défaut")

    for o, a in opt: 
        if o == "c":
            CONFIG_FILE = a
        else:
            pass

    try:
        with open(CONFIG_FILE, "r") as f:
            for line in f:
                lopt = line.split("=")
                if lopt[0].strip() in OPTS.keys():
                    opt2 = lopt[1].replace("\n", "")
                    if lopt[0].strip() == "port":
                        OPTS["port"] = int(opt2.strip())
                    else:
                        OPTS[lopt[0].strip()] = opt2.strip()
    except:
        pass

    dredd=Dredd(OPTS)
    dredd.start()
