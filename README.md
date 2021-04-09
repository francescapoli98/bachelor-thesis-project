# Progetto di tesi interno ad [ELEXIS](https://elex.is/)
## Laurea triennale in Informatica Umanistica - a.a. 2019/2020

### Fasi del progetto:
Creazione di un Sense Inventory per task di Word Sense Disambiguation ed estensione del mapping di sensibasato sulle risorse ILC4CLARIN/ILC-CNR, con task di annotazione manuale del dataset di frasi e valutazione delle risorse utilizzate. I 

---
### Programmi:

#### Sense Inventory
##### repository: *sense_inventory*
La creazione della risorsa si basa sulla selezione di lemmi da un dataset in formato CoNLL-U (*dataset2000wiki_Export_IT_2021-02-22_Corrected_v2.tsv*) derivato dalla traduzione italiana di un corpus annotato di frasi sviluppato in ELEXIS, annotato automaticamente e poi rivisto manualmente e tramite strumenti di correzione in Babelscape.
Il programma (*corrected.py*) prende il input il dataset, seleziona i lemmi estratti dalle frasi di cui quest'ultimo si compone e ne ricerca tutti i sensi correlati nelle risorse online open-source ILC4CLARIN (i lessici italiani [PAROLE-SIMPLE-CLIPS](https://dspace-clarin-it.ilc.cnr.it/repository/xmlui/handle/20.500.11752/ILC-88?show=full) e [ItalWordNet](https://dspace-clarin-it.ilc.cnr.it/repository/xmlui/handle/20.500.11752/ILC-62)) e ILC-CNR (un database di mapping di sensi dei lessici citati, *iwnmapdb*). 
I dati estrapolati e controllati vengono poi disposti nella struttura formale del Sense Inventory richiesta per i task ELEXIS, tale per ogni coppia lemma - PoS:
* Sensi presenti in PSC, non mappati
* Sensi mappati
* Sensi presenti in IWN, non mappati

L'insieme di lemmi trattai nel programma è stamapato nell'output *newdataset.txt*.
Il Sense Inventory è stampato in *corrected_si.txt*. Quest'ultimo output è stato anche trasformato in una risorsa di estensione *.xslx*.

#### Estensione del mapping di sensi
##### repository: *mapping_extension*
All'interno del programma (*maps.py*) si svolgono due fasi di test per la mappatura dei sensi tra i lessici ItalWordNet e PAROLE-SIMPLE CLIPS attraverso il calcolo della similarità tra vettori di parole tramite [spaCy](https://github.com/explosion/spaCy). Nella prima parte si analizzano i mapping già presente nel database *iwnmapdb* dell'ILC-CNR per arrivare ad un Threshold di similarità tra sensi delle mappature già sviluppate, da applicare a quelle potenziali. Nella seconda parte del codice viene analizzata la *similarity* tra sensi di diversi lemmi (selezionati manualmente) senza alcun senso mappato appunto; similarity che poi è stata confrontata col Threshold trovato precedentemente.
Il programma prende in input un file con la lista di lemmi mappati (*listamapdb.txt*) per un controllo sui lemmi selezionati manualmente e il formato finale del Sense Inventory (*corrected_si.txt*) per l'estrapolazione di informazioni sui sensi (definizione, IDs). Gli output sono rispettivamente *testmapping.txt* per la prima parte, con la lista di mapping analizzati e la loro *similarity*, oltre che la media aritmetica dell'insieme di similarità che corrisponde al Threshold; per la seconda, invece, *testnonmappati.txt*, in cui si trova l'elenco di mapping con la *similarity* tra tutti i sensi di ogni lemma. 

#### Statistiche di copertura delle risorse 
##### repository: *statistics*


#### Selezione di frasi per annotazione manuale
##### repository: *sentences_selector*
