#!/usr/bin/env python
# -*- coding: utf-8 -*-
import MySQLdb
import re
import pyconll
import collections
from collections import defaultdict
import unicodedata as ud
import spacy
from numpy import mean, array

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


mappings=[  #23
    ['abuso', 'NOUN'],
    ['accennare', 'VERB'], 
    ['accesso', 'NOUN'], 
    ['acclamare', 'VERB'],
    ['accompagnare', 'VERB'],
    ['area', 'NOUN'], 
    ['complesso', 'NOUN'],
    ['contare','NOUN'],
    ['fallire', 'VERB'], 
    ['gola', 'NOUN'],
    ['interpretare', 'NOUN'],
    ['istituzione', 'NOUN'], 
    ['latino', 'NOUN'],
    ['legione', 'NOUN'],
    ['mare', 'NOUN'],
    ['materiale', 'NOUN'],
    ['popolare', 'VERB'], 
    ['portare', 'VERB'],
    ['terapia', 'NOUN'],
    ['trasmettere', 'VERB'],
    ['volume', 'NOUN'],
    ['zaffiro', 'NOUN'],
    ['zona', 'NOUN']
]

tocheck=[ #20
    ['aborto', 'NOUN'],        
    ['abbandonare', 'VERB'],
    ['acquisto', 'NOUN'],
    ['adattamento', 'NOUN'],
    ['americano', 'NOUN'],
    ['causare', 'VERB'],
    ['colonna', 'NOUN'],
    ['conseguire', 'VERB'],
    ['dovere', 'VERB'],
    ['firmare', 'VERB'],
    ['futuro', 'NOUN'],
    ['imperatore', 'NOUN'],
    ['provocare', 'VERB'],
    ['ricavare', 'VERB'],
    ['tabacco', 'NOUN'],
    ['uccisione', 'NOUN'],
    ['villaggio', 'NOUN'],
    ['votazione', 'NOUN'],
    ['yogurt', 'NOUN'],
    ['zucchero', 'NOUN']
]

testing=[]
allsimilar=[]

#seleziona da lista di lemmi mappati
with open("listamapdb.txt", "r", encoding="utf-8") as maps:
    for line in maps:
        line=re.sub(r"\n","", line)
        line=line.split("\t")
        for elem in mappings:
            if(line[0]==elem[0] and line[1]==elem[1]):
                testing.append(line)

nlp=spacy.load("it_core_news_md")

with open("corrected_si.txt", "r", encoding="utf-8") as si, open("testmapping.txt", "w+", encoding="utf-8") as out:
    print("Test dei lemmi mappati in IWNMAPDB \n La media aritmetica delle similarity si trova in fondo al documento", file=out)
    #prendi le definizioni dal sense inventory
    for line in si:
        #elimina i \n che derivano dalla selezione di line
        line=re.sub(r"\n","", line)
        line=line.split("\t")
        for elem in testing:
            #check di lemma e pos
            if(line[0]==elem[0] and line[1]==elem[1]):
                #check di usemid e synsetid
                if(line[7]==elem[2] and line[3]==elem[3]):
                    print("\n", file=out)
                    print(line[0], line[1], file=out)
                    #aggiungi il punto alle definizioni per migliore risultato di similarity
                    if(line[4].endswith('.')):
                        defpsc=str(line[4])
                    else:
                        defpsc=str(line[4])+"."
                    
                    if(line[9].endswith('.')):
                        defiwn=str(line[9])
                    else:
                        defiwn=str(line[9])+"."
                    #usa nlp()
                    doc1=nlp(defpsc)
                    doc2=nlp(defiwn)
                    simil = doc1.similarity(doc2)
                    allsimilar.append(simil)
                    #stampa risultati
                    print("SIMPLE: "+ str(line[3])+"\t"+defpsc+"\nIWN: "+str(line[7])+"\t"+defiwn, file=out)
                    print(simil, file=out)
    print("\nMEDIA VALORI DI SIMILARITY:", file=out)
    print(mean(allsimilar),file=out)

with open("corrected_si.txt", "r", encoding="utf-8") as si, open("testnonmappati.txt", "w+", encoding="utf-8") as output:
    print("LEMMA\tPOS\tUSEMID\tSYNSETID\tSENSEID\tDEFINIZIONE PSC\tDEFINIZIONE IWN\tSIMILARITY", file=output)
    for line in si:
        #elimina i \n che derivano dalla selezione di line
        line=re.sub(r"\n","", line)
        line=line.split("\t")
        for elem in tocheck:
            nomapids=[]
            if(line[0]==elem[0] and line[1]==elem[1]):
                if(line[3] != 'None'):
                    usem=str(line[3])
                    cursor.execute("SELECT synset1id, word2id FROM iwnmapdb.iwn2psc WHERE word2id LIKE (%s) ", (usem,))
                    row3=cursor.fetchall()
                    if(not row3): #se il lemma non è mappato
                        nomapids.append([line[0], line[1], usem, line[4]])
            #per ogni usem non mappato:
            #entra in iwn e seleziona le coppie lemma pos
            #cerca l'elemento con maggiore similarity
            #scegli le similarity più vicine al threshold! O che lo superino  
            if(nomapids):
                for elem in nomapids:
                    mapiwn=[]
                    lemma = elem[0]
                    if(elem[3].endswith('.')):
                        defpsc=str(elem[3])
                    else:
                        defpsc=str(elem[3])+"."
                    if(UnicodeEncodeError):
                        lemma = ud.normalize('NFKD', lemma).encode('ASCII', 'ignore')
                    #QUERY IWN
                    cursor.execute("SELECT synsetid, senseid, lemma, pos, definition FROM newiwn.wordsxsensesxsynsets WHERE lemma LIKE (%s)", (lemma,))
                    row1=cursor.fetchall()
                    for row in row1:
                        if(row is not None):
                            pos=str(elem[1])
                            pos1=str(row[3])
                            pos1=upos(pos1)
                            match = re.fullmatch(str(pos1), pos)
                            if match:
                                if(row[4]!=''):
                                    mapiwn.append([row[0], row[1], row[2], pos1, row[4]])
                    
                    for item in mapiwn:
                        if(item[4].endswith('.')):
                            defiwn=str(item[4])
                        else:
                            defiwn=str(item[4])+"."
                        doc1=nlp(defpsc)
                        doc2=nlp(defiwn)
                        simil = doc1.similarity(doc2)
                        print(str(item[2])+"\t"+str(item[3])+"\t"+str(elem[2])+"\t"+str(item[0])+"\t"+str(item[1])+"\t"+str(defpsc)+"\t"+str(defiwn)+"\t"+str(simil), file=output)