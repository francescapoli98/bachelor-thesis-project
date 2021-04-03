#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import MySQLdb
import re
import math
import pyconll
from collections import defaultdict

def upos(pos):
    switch = {('A', "ADJ"),
              ('AG', "ADJ"),
              ('AV', "ADV"),
              ('N', "NOUN"),
              ('V', "VERB")}
    for case in switch:
        match=re.fullmatch(str(case[0]), pos)
        if(match):
            s = re.sub(case[0],case[1],pos)
            return(str(s))
    return(str(pos))

#CONNESSIONE DB
connect = MySQLdb.connect(
    host = 'localhost',
    user = 'root',
    passwd = '',
    port = 3306)

cursor = connect.cursor()
cursor.execute("USE simplelexicon")
cursor.execute("USE newiwn")
cursor.execute("SHOW TABLES")

##INIZIO A LAVORARE SULLA MIA META'
with open('sentences.txt','w+', encoding='utf-8') as outfile:
    corpus = pyconll.load_from_file("dataset2000wiki_UDPIPE.conllu")
    frasi={}
    for sentence in corpus:
        counting=0
        sentid=int(sentence.meta_value('sent_id'))
        if(sentid>1036):
            for token in sentence:
                if (token.upos == 'VERB' or token.upos == 'NOUN' or token.upos == 'ADV' or token.upos == 'ADJ'):
                    word=(token.lemma).strip().encode("utf-8")
                    firstpos=str(token.upos)
                    cursor.execute("SELECT lemma, pos FROM newiwn.wordsxsensesxsynsets WHERE lemma LIKE (%s)", (word,))
                    catch=cursor.fetchone()
                    if(catch):
                        pos=str(catch[1])
                        pos=upos(pos)
                        check=re.fullmatch(pos, firstpos)
                        if(check):
                            cursor.execute("SELECT naming, pos FROM simplelexicon.usem WHERE naming LIKE (%s)", (word,))
                            catch2=cursor.fetchone()
                            if(catch2):
                                pos2=str(catch2[1])
                                pos2=upos(pos2)
                                check2=re.fullmatch(pos2, firstpos)
                                if(check2):
                                    counting=counting+1
            frasi[sentid]=[(sentence.meta_value('text')), (counting)]
    print(frasi, file=outfile)