#!/usr/bin/env python
# -*- coding: utf-8 -*-

import MySQLdb
import re
import pyconll
import collections
from collections import defaultdict
import unicodedata as ud
import csv
import pandas

#funzione che modifica gli accenti nel file di lemmi e pos in lettera + apostrofo
#così da risultare la stessa formattazione del simplelexicon ed evitare di ignorare le parole accentate
def accent(string):

    switch = {('à', "a"+"'"),
              ('è', "e"+"'"),
              ('é', "e"+"'"),
              ('ì', "i"+"'"),
              ('ò', "o"+"'"),
              ('ù', "u"+"'")}

    for case in switch:
        if(case[0] in string):
            s = re.sub(case[0],case[1],string)
            return(str(s))
    return(str(string))

##FUNZIONE PER CAMBIARE LE POS DAL DB IN UD
##ovviamente devi modificarla
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


def ordina(dict):
    return sorted(dict.items(), key = lambda x: x[1][0])


#CONNESSIONE DB
connect = MySQLdb.connect(
    host = 'localhost',
    user = 'root',
    passwd = '',
    port = 3306)

cursor = connect.cursor()
cursor.execute("USE simplelexicon")
cursor.execute("USE newiwn")
cursor.execute("USE iwnmapdb")
cursor.execute("SHOW TABLES")

with open('dataset2000wiki_Export_IT_2021-02-22_Corrected_v2.tsv', 'r', encoding='utf-8') as tsv, open('corrected_si.txt', 'w+', encoding='utf-8') as output, open('newdataset.txt', 'w+', encoding='utf-8') as lemmi:
    all_lemmas= {}
    lemmaid = 0
    for line in tsv:
        tabs=[]
        words = line.split('\t')
        for word in words:
            tabs.append(word)
        if(len(tabs)>2):
            pos = tabs[3]
            if (pos == 'VERB' or pos == 'NOUN' or pos == 'ADV' or pos == 'ADJ'):
                lemma=tabs[2]
                lemma = re.sub(r'\.|\,|\:|\!|\?|\;|\_|\'|\"', '', lemma)
                lemmaid = lemmaid+1
                all_lemmas[lemmaid]= [str(lemma).lower(), str(pos)]
    #controlla se non c'è già una coppia lemma-pos
    #se non c'è aggiungi
    temp = []
    lemmas = dict()
    for key, value in all_lemmas.items():
        if value not in temp:
            temp.append(value)
            lemmas[key] = value

    lemmas=ordina(lemmas)
    print(lemmas, file=lemmi)


    print("LEMMA\tPOS\tDEFINIZIONE CONCATENATA PSC-IWN\tUSEMID PSC\tDEFINIZIONE PSC\tESEMPIO PSC\tTIPO SEMANTICO PSC\tSYNSETID IWN\tSENSEID IWN\tDEFINIZIONE IWN\t\n", file=output)
    for key,value in lemmas:
        numero = re.findall(r'\d', value[0])
        if (not numero):
            lemma=value[0]
            pos=value[1]
            #pos=str(pos)
            iwn={}
            psc={}
            mapdb=[]
            mappings=[]

            ##ITALWORDNET
            lemmaIWN = lemma
            if(UnicodeEncodeError):
                lemmaIWN = ud.normalize('NFKD', lemma).encode('ASCII', 'ignore')
            #QUERY IWN
            cursor.execute("SELECT synsetid, senseid, lemma, pos, definition FROM newiwn.wordsxsensesxsynsets WHERE lemma LIKE (%s)", (lemmaIWN,))
            row1=cursor.fetchall()
            for row in row1:
                if(row is not None):
                    lemma1=row[1]
                    pos1=str(row[3])
                    pos1=upos(pos1)
                    match = re.fullmatch(str(pos1), pos)
                    if match:
                        if(row[4]):
                            iwn[lemma1]=[row[0], row[2], pos1, row[4]]
                        if(row[4]==''):
                            iwn[lemma1]=[row[0], row[2], pos1, 'None'] 

            ##SIMPLELEXICON
            #cambio gli accenti con la formattazione del simplelexicon
            lemmaSL = accent(lemma)
            #riporto tutto in utf-8
            lemmaSL = lemmaSL.encode("utf-8")
            #QUERY PSC
            cursor.execute("SELECT idUsem, naming, pos, exemple,definition FROM simplelexicon.usem WHERE naming LIKE (%s) ", (lemmaSL, ))
            row2=cursor.fetchall()
            #salvo tutto in un dizionario generico di psc
            for row in row2:
                if(row is not None):
                    lemma2=row[0]
                    pos2=str(row[2])
                    pos2=upos(pos2)
                    match=re.fullmatch(str(pos2),pos)
                    if(match):
                        ##QUA AGGIUNGO ANCHE L'ELEMENTO SEMANTICO
                        cursor.execute("SELECT template FROM simplelexicon.usemtemplates LEFT JOIN simplelexicon.templates ON usemtemplates.idTemplate = templates.idTemplate WHERE usemtemplates.idUsem LIKE (%s)  ", (lemma2, ))
                        template=cursor.fetchone()
                        if(template is not None):
                            templ=template[0]
                        else:
                            templ = 'None'
                        if(row[4] is not None):
                            psc[lemma2]=[row[1], pos2, row[3], row[4], templ]
                        else:
                            psc[lemma2]=[row[1], pos2, row[3], 'None', templ]

            ##MAPPING
            for elem in psc.items():
                usemid = elem[0]
                usemid = usemid.encode("utf-8")
                cursor.execute("SELECT synset1id, word2id FROM iwnmapdb.iwn2psc WHERE word2id LIKE (%s) ", (usemid,))
                row3=cursor.fetchall()
                if(row3):
                    for row in row3:
                        if(row is not None):
                            mapdb.append(row)

            ##PRINT DEGLI USEM SENZA MAPPING
            mappati=[]
            if(mapdb):
                for elem in psc:
                    for line in mapdb:
                        if(elem in line[1]):
                            mappati.append(elem)
                for elem in psc:
                    if(elem not in mappati):
                        print(str(lemma)+"\t"+str(psc[elem][1])+"\t"+str(psc[elem][3])+" <> None\t"+str(elem)+"\t"+str(psc[elem][3])+"\t"+str(psc[elem][2])+"\t"+str(psc[elem][4])+"\tNone\tNone\tNone", file=output)

            if(not mapdb):
                for elem in psc:
                    print(str(lemma)+"\t"+str(psc[elem][1])+"\t"+str(psc[elem][3])+" <> None\t"+str(elem)+"\t"+str(psc[elem][3])+"\t"+str(psc[elem][2])+"\t"+str(psc[elem][4])+"\tNone\tNone\tNone", file=output)

            ##stampa mapping:
            delete=[]
            for elem in mapdb:
                usem = elem[1]
                if(usem in psc):
                    synsetid = elem[0]
                    for item in iwn:
                        syn = iwn[item][0]
                        match = re.fullmatch(str(syn), str(synsetid))
                        if(match):
                            ## quando ci sono due definizioni e sono diverse, stampa "definizione simple <> definizione iwn"
                            ## quando ci sono due definizioni e sono identiche, controlla e stampa una volta
                            ## quando ce n'è solo una, stampa senza <> (diamante) e NULL
                            definition1=str(psc[usem][3])
                            definition2=str(iwn[item][3])
                            findnone1=re.findall('None', definition1)
                            findnone2=re.findall('None', definition2)
                            if(findnone1 and findnone2):
                                print(str(lemma)+"\t"+str(pos)+"\t"+"None"+"\t"+str(usem)+"\t"+str(psc[usem][3])+"\t"+str(psc[usem][2])+"\t"+str(psc[usem][4])+"\t"+str(iwn[item][0])+"\t"+str(item)+"\t"+str(iwn[item][3]), file=output)
                            definition1=re.sub(r'\.','',definition1)
                            definition2=re.sub(r'\.','',definition2)
                            same=re.fullmatch(definition1, definition2)
                            if same:
                                print(str(lemma)+"\t"+str(psc[usem][1])+"\t"+str(psc[usem][3])+"\t"+str(usem)+"\t"+str(psc[usem][3])+"\t"+str(psc[usem][2])+"\t"+str(psc[usem][4])+"\t"+str(iwn[item][0])+"\t"+str(item)+"\t"+str(iwn[item][3]), file=output)
                            else:
                                print(str(lemma)+"\t"+str(psc[usem][1])+"\t"+str(psc[usem][3])+" <> "+str(iwn[item][3])+"\t"+str(usem)+"\t"+str(psc[usem][3])+"\t"+str(psc[usem][2])+"\t"+str(psc[usem][4])+"\t"+str(iwn[item][0])+"\t"+str(item)+"\t"+str(iwn[item][3]), file=output)
                            if(item not in delete):
                                delete.append(item)
            #tolgo i lemmi già stampati nel mapping dal dizionario di iwn per evitare che vengano ristampati
            if(delete):
                for item in delete:
                    del(iwn[item])


            ##stampa dei sensi iwn senza mapping:
            for elem in iwn:
                print(str(lemma)+"\t"+str(iwn[elem][2])+"\tNone <> "+str(iwn[elem][3])+"\tNone\tNone\tNone\tNone\t"+str(iwn[elem][0])+"\t"+str(elem)+"\t"+str(iwn[elem][3]), file=output)

