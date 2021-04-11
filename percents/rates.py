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

with open('dataset2000wiki_Export_IT_2021-02-22_Corrected_v2.tsv', 'r', encoding='utf-8') as tsv:
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

    iwntot=[]
    psctot=[]
    lemmiwn=[]
    lemmipsc=[]
    iwnnodef=[]
    pscnodef=[] 
    

    for lemma in lemmas:
        lem=lemma[1][0]
        numero = re.findall(r'\d', lem)
        if (not numero):
            pos=str(lemma[1][1])
            lemmapos=[lem,pos]

            ##ITALWORDNET
            lemmaIWN = lem
            if(UnicodeEncodeError):
                lemmaIWN = ud.normalize('NFKD', lem).encode('ASCII', 'ignore')
            #QUERY IWN
            cursor.execute("SELECT synsetid, senseid, lemma, pos, definition FROM newiwn.wordsxsensesxsynsets WHERE lemma LIKE (%s)", (lemmaIWN,))
            row1=cursor.fetchall()
            if(row1):
                for row in row1:
                    pos1=str(row[3])
                    pos1=upos(pos1)
                    match = re.fullmatch(pos1, pos)
                    if match:
                        if(lemmapos not in lemmiwn):
                            lemmiwn.append(lemmapos)
                        newrow=[row[0], row[1], row[2], pos1, row[4]]
                        iwntot.append(newrow)
                        if(row[4] == ''):
                            iwnnodef.append(row)
            
            ##SIMPLELEXICON
            #cambio gli accenti con la formattazione del simplelexicon
            lemmaSL = accent(lem)
            #riporto tutto in utf-8
            lemmaSL = lemmaSL.encode("utf-8")
            #QUERY PSC
            cursor.execute("SELECT idUsem, naming, pos, definition FROM simplelexicon.usem WHERE naming LIKE (%s) ", (lemmaSL, ))
            row2=cursor.fetchall()
            if(row2):
                for row in row2:
                    if(row is not None):
                        lemma2=row[0]
                        pos2=str(row[2])
                        pos2=upos(pos2)
                        match=re.fullmatch(str(pos2),pos)
                        if(match):
                            if(lemmapos not in lemmipsc):
                                lemmipsc.append(lemmapos)
                            newrow=[row[0], row[1], pos2, row[3]]
                            psctot.append(newrow)
                            if(row[3] is None):
                                pscnodef.append(row)


##STATISTICHE

with open("numbers.txt", "w+", encoding="utf-8") as out:  

    #TOTALE LEMMI
    print("STATISTICHE:\n", file=out)
    lemmi=len(lemmas)
    iwn=len(lemmiwn)
    psc=len(lemmipsc)
    print("Nel dataset sono presenti {} lemmi tra nomi, verbi, aggettivi e avverbi.".format(lemmi), file=out)

    print("I lemmi presenti in iwn sono {}".format(iwn), file=out)
    print("Percentuale di lemmi presenti in iwn: {0:.2f}%".format( float(iwn*100)/float(lemmi) )+"e lemmi assenti:{0:.2f}%".format( float((lemmi-iwn)*100)/float(lemmi) ), file=out )
    
    print("I lemmi presenti in psc sono {}".format(psc), file=out)
    print("Percentuale di lemmi presenti in psc: {0:.2f}%".format( float(psc*100)/float(len(lemmas)) )+", assenti: {0:.2f}%".format(float((lemmi-psc)*100)/float(lemmi)), file=out )

    coperturatot=[]
    parzialeiwn=[]
    parzialepsc=[]
    for elem in lemmiwn:
        if(elem in lemmipsc):
            coperturatot.append(elem)
        else:
            parzialeiwn.append(elem)
    for elem in lemmipsc:
        if(elem not in lemmiwn):
            parzialepsc.append(elem)
    print("I lemmi con copertura totale (presenti in entrambi i database di IWN e PSC) sono {}".format(len(coperturatot)), file=out)
    print("I lemmi con copertura parziale sono {}, {} si trovano solo in IWN e {} solo in PSC.".format( (len(parzialeiwn)+len(parzialepsc)), len(parzialeiwn), len(parzialepsc) ), file=out)
    print("Percentuale di lemmi con copertura totale: {0:.1f}%".format(float(len(coperturatot)*100)/float(lemmi)) +"e parziale: {0:.1f}%".format(float((len(parzialeiwn)+len(parzialepsc))*100)/float(lemmi)), file=out)
    
    mappati=[]
    yesmap=[]
    nomap=[]
    for elem in psctot:
        lempos=[elem[1], elem[2]]
        if(lempos in coperturatot):
            usemid=elem[0]
            usemid = usemid.encode("utf-8")
            cursor.execute("SELECT synset1id, word2id FROM iwnmapdb.iwn2psc WHERE word2id LIKE (%s) ", (usemid,))
            row3=cursor.fetchall()
            if(row3):
                if(lempos not in yesmap):
                    yesmap.append(lempos)
                for row in row3:
                    mappati.append([lempos[0], lempos[1], row])
    
    for lemma in lemmas:
        lem=lemma[1][0]
        numero = re.findall(r'\d', lem)
        if (not numero):
            pos=lemma[1][1]
            lemmpos=[lem, pos]
            if(lemmpos not in yesmap):
                nomap.append(lemmpos)
    
    print("Il numero totale di sensi mappati è {}".format(len(mappati)) +", ovvero il {0:.2f}%".format(float(len(mappati)*100)/float(len(iwntot)+len(psctot))), file=out)
    print("I lemmi con almeno un mapping sono {}".format(len(yesmap))+", ovvero il {0:.2f}%".format(float(len(yesmap)*100)/float(lemmi)),file=out)
    print("I lemmi non mappati con alcun senso invece sono {}".format(len(nomap))+", ovvero il {0:.2f}%".format(float(len(nomap)*100)/float(lemmi)),file=out)

    print("TOTALE sensi tra IWN e PSC (unione):{}".format(len(psctot)+len(iwntot)), file=out)
    print("Totale sensi IWN:"+str(len(iwntot)), file=out)
    print("Totale sensi PSC:"+str(len(psctot)), file=out)

    intersection=[]
    for elem in lemmipsc:
        if(elem in lemmiwn):
            intersection.append(elem)
    print("Lemmi presenti sia in PSC sia in IWN (intersezione):"+str(len(intersection)), file=out)


    adjectives=[]
    for elem in nomap:
        if(elem[1]=='ADJ' or elem[1]=='ADV'):
            adjectives.append(elem)
    print("Percentuale di aggettivi e avverbi tra i NON MAPPATI: {0:.2f}%".format( float(len(adjectives)*100)/float(len(nomap)) ), file=out )

    lemmisi=[]
    for item in lemmiwn:
        lemmisi.append(item)
    for item in lemmipsc:
        if item not in lemmisi:
            lemmisi.append(item)
    print("Totale lemmi Sense Inventory: "+str(len(lemmisi)), file=out)

    
    senses_si = len(open('corrected_si.txt').readlines())
    print("Numero di sensi nel Sense Inventory:"+str(senses_si-2), file=out)

    adj=[]
    adv=[]
    noun=[]
    verb=[]
    for lemma in lemmas:
        if(lemma[1][1] == 'ADJ'):
            adj.append(lemma[1])
        if(lemma[1][1] == 'ADV'):
            adv.append(lemma[1])
        if(lemma[1][1] == 'NOUN'):
            noun.append(lemma[1])
        if(lemma[1][1] == 'VERB'):
            verb.append(lemma[1])
    print("NUMERO DI POS NEL DATASET:\nAggettivi:"+str(len(adj))+"\nAvverbi:"+str(len(adv))+"\nNomi:"+str(len(noun))+"\nVerbi:"+str(len(verb)), file=out)


    adjsi=[]
    advsi=[]
    nounsi=[]
    verbsi=[]
    for lemma in lemmisi:
        if(lemma[1] == 'ADJ'):
            adjsi.append(lemma)
        if(lemma[1] == 'ADV'):
            advsi.append(lemma)
        if(lemma[1] == 'NOUN'):
            nounsi.append(lemma)
        if(lemma[1] == 'VERB'):
            verbsi.append(lemma)
    print("NUMERO DI POS NEL SENSE INVENTORY (lemmi):\nAggettivi:"+str(len(adjsi))+"\nAvverbi:"+str(len(advsi))+"\nNomi:"+str(len(nounsi))+"\nVerbi:"+str(len(verbsi)), file=out)

cursor.close() 