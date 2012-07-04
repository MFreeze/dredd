#!/usr/bin/env python
#-*- coding: utf-8 -*-

import sys
import ircbot
import irclib
import os
import urllib
import re
import dredd_base as dr
from  random import randrange,randint
from datetime import date

LISTE_CMD_PUB = ["!pop", "!roll", "!enfr", "!fren", "!wp", "!wpf", "!urb", "!port",
                 "!halp", "!down", "!jobs", "!bieber", "!weekend", "!dredd", "!popall"]
LISTE_CMD_PRIV = ["!push", "!id"]
LISTE_CMD_MASTER = ["!update", "!kick", "!topic", "!saychan", "!op"]
LISTE_BLAGUE = ["a+", "marie france", "marie-france", "sasha", "soeur", "pute", "concentré",
                "concentrer", "xd", "chmod", "><", "kikoo", "arwen", "chmod 777"]
PILE_MAX_SIZE = 16
INIT_PATIENCE = 4
WEEKEND = ['Déjà ?', 'T\'en est loin coco.', 'Nope :(', 'ça vient !', 'Preque \o/', 'Mais on est déjà en weekend, va te biturer !', 'C\'est déjà presque finis :(']

MASTER="trax"
MASTERPASS = "penis:666"

class Dredd(dr.DreddBase):
    def __init__(self, channel, nick, server, port=6667, hello="Ici, la Loi c'est moi.", 
                    master = "", masterpass = "", oppasswd = "", opname = "", list_cmd_pub=LISTE_CMD_PUB, 
                    list_cmd_pv=LISTE_CMD_PRIV, liste_blague=LISTE_BLAGUE,
                 list_cmd_gm=LISTE_CMD_MASTER, maspass = MASTERPASS):
        dr.__init__(self, channel, nick, server, port, hello, master, masterpass, oppasswd, opname)
        # Liste des commandes acceptées sur le chan
        self.ls_cmd_pb = list_cmd_pub
        # Liste des commandes acceptées en privé
        self.ls_cmd_pv = list_cmd_pv
        self.ls_cmd_gm = list_cmd_gm
        # Liste des mots provoquant une action de la part de Dredd
        self.ls_blague = liste_blague 
        # Création de la pile
        self.pile = list()
        # Indice de patience
        self.patience = INIT_PATIENCE

    # Fonction gérant le lancer de dés
    def _des(self, arg):
        dice = arg.split("d")
        sides = int(dice[1])
        num = int(dice[0])
        return sum(randrange(sides)+1 for die in range(num))

    # En cas de messages publiés sur le channel
    def on_pubmsg(self, c, e):
        a = e.arguments()[0].lower()

        # On cherche dans la phrase s'il y a une blague à faire
        for i in (self.ls_blague):
            if ((not a.find(i) == -1) and not ( irclib.nm_to_n(e.source()) == self.getnickname())) :
                self.execute_sentence(e, i)
                break

        # Puis on cherche si il s'agit d'une commande viable
        cmd = a.split()
        if cmd[0] in self.ls_cmd_pb:
            self.execute_action(e, e.arguments()[0])

        if randint(0,100) == 42:
            ts = self.tasoeur(a)
            if ts != None:
                c.privmsg(self.channel, "%s" % ts)

    def dredd(self, complement, c, auteur):
        c.privmsg(self.channel, "La version 1 est morte...")

