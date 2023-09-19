# Progetto di tesi interno ad [ELEXIS](https://elex.is/) presso l'[ILC-CNR](https://github.com/cnr-ilc): "Sviluppo di un Sense Inventory per task di Word Sense Disambiguation: il progetto ELEXIS"
## 🎓 Laurea triennale in Informatica Umanistica - a.a. 2019/2020


<div> <img src="https://apre.it/wp-content/uploads/2021/01/logo_uni-pisa.png" width="200" /> 
<img src="https://elex.is/wp-content/uploads/2018/10/ilc-400-300x238.png" width="150" />
</div>

<a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-nc-sa/4.0/80x15.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/4.0/">Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License</a>. 

# ITA

### Fasi del progetto di tesi:
Creazione di un Sense Inventory per task di Word Sense Disambiguation ed estensione del mapping di sensi basato sulle risorse ILC4CLARIN/ILC-CNR, con task di annotazione manuale del dataset di frasi e valutazione delle risorse utilizzate. 

### Programmi:

#### 📍 Sense Inventory
##### repository: *sense_inventory*
La creazione della risorsa si basa sulla selezione di lemmi da un dataset in formato CoNLL-U (*dataset2000wiki_Export_IT_2021-02-22_Corrected_v2.tsv*) derivato dalla traduzione italiana di un corpus annotato di frasi sviluppato in ELEXIS, annotato automaticamente e poi rivisto manualmente e tramite strumenti di correzione in Babelscape.
Il programma (*corrected.py*) prende in input il dataset, seleziona i lemmi estratti dalle frasi di cui quest'ultimo si compone e ne ricerca tutti i sensi correlati nelle risorse online open-source ILC4CLARIN (i lessici italiani [PAROLE-SIMPLE-CLIPS](https://dspace-clarin-it.ilc.cnr.it/repository/xmlui/handle/20.500.11752/ILC-88?show=full) e [ItalWordNet](https://dspace-clarin-it.ilc.cnr.it/repository/xmlui/handle/20.500.11752/ILC-62)) e ILC-CNR (un database di mapping di sensi dei lessici citati, *iwnmapdb*). 
I dati estrapolati e controllati vengono poi disposti nella struttura formale del Sense Inventory richiesta per i task ELEXIS, tale per ogni coppia lemma - PoS:
* Sensi presenti in PSC, non mappati
* Sensi mappati
* Sensi presenti in IWN, non mappati

L'insieme di lemmi trattati nel programma è stamapato nell'output *newdataset.txt*.
Il Sense Inventory è stampato in *corrected_si.txt*. Quest'ultimo output è stato anche trasformato in una risorsa di estensione *.xslx*.

#### 📍 Estensione del mapping di sensi
##### repository: *mapping_extension*
All'interno del programma (*maps.py*) si svolgono due fasi di test per la mappatura dei sensi tra i lessici ItalWordNet e PAROLE-SIMPLE CLIPS attraverso il calcolo della similarità tra vettori di parole tramite [spaCy](https://github.com/explosion/spaCy). Nella prima parte si analizzano i mapping già presente nel database *iwnmapdb* dell'ILC-CNR per arrivare ad un Threshold di similarità tra sensi delle mappature già sviluppate, da applicare a quelle potenziali. Nella seconda parte del codice viene analizzata la *similarity* tra sensi di diversi lemmi (selezionati manualmente) senza alcun senso mappato appunto; similarity che poi è stata confrontata col Threshold trovato precedentemente.
Il programma prende in input un file con la lista di lemmi mappati (*listamapdb.txt*) per un controllo sui lemmi selezionati manualmente e il formato finale del Sense Inventory (*corrected_si.txt*) per l'estrapolazione di informazioni sui sensi (definizione, IDs). Gli output sono rispettivamente *testmapping.txt* per la prima parte, con la lista di mapping analizzati e la loro *similarity*, oltre che la media aritmetica dell'insieme di similarità che corrisponde al Threshold; per la seconda, invece, *testnonmappati.txt*, in cui si trova l'elenco di mapping con la *similarity* tra tutti i sensi di ogni lemma. 

#### 📍 Percentuali di copertura delle risorse 
##### repository: *percents*
Il Sense Inventory funge anche da mezzo per un’analisi dell’attuale ampiezza dei database di cui abbiamo usufruito, in particolare per studiare la loro effettiva copertura ed efficienza rispetto alle necessità di ELEXIS e il loro stato dell’arte. Il programma (*rates.py*) serve alla raccolta e al trattamento dei dati ricavati dal Sense Inventory, per elaborare i numeri necessari a presentarli e a formulare un'analisi più accurata.
Il programma prende in input il dataset da cui è stato ricavato il Sense Inventory (*dataset2000wiki_Export_IT_2021-02-22_Corrected_v2.tsv*) e il Sense Inventory (*correctes_si.txt*) per ricreare il processo utilizzato per quest'ultimo, al fine di raccogliere dati durante l'elaborazione. Nell'output (*numbers.txt*) sono stampati i risultati dell'analisi.

#### 📍 Selezione di frasi per annotazione manuale
##### repository: *sentences_selector*
Questo semplice programma (*sceltafrasi.py*) prende in input il dataset in formato CoNLL-U (*dataset2000wiki_Export_IT_2021-02-22_Corrected_v2.tsv*) e assegna ad ogni frase in esso contenuta il numero di lemmi presenti in entrambi i database di riferimento, PSC e IWN, per poi stampare tutti i dati nell'output (*sentences.txt*). In questo modo rende più semplice la scelta delle frasi per il task di annotazione manuale. Le frasi sono state poi selezionate manualmente, a causa di alcune particolarità sintattiche da prendere in considerazione a livello non automatico.

---

# ENG

### Thesis project phases:
Building of a Sense Inventory for Word Sense Disambiguation tasks and extension of sense mapping based on ILC4CLARIN/ILC-CNR resources, with tasks for manual annotation of the phrase dataset and evaluation of the resources used. 

### Programs:

#### 📍 Sense Inventory
##### repository: *sense_inventory*
The creation of the resource is based on the selection of lemmas from a dataset in CoNLL-U format (*dataset2000wiki_Export_IT_2021-02-22_Corrected_v2.tsv*) derived from the Italian translation of an annotated corpus of sentences developed in ELEXIS, automatically annotated and then reviewed manually and through correction tools in Babelscape.
The program (*corrected.py*) takes as input the dataset, selects the lemmas extracted from the sentences of which it is composed and searches for all the related senses in the open-source online resources ILC4CLARIN (the Italian lexicons [PAROLE-SIMPLE-CLIPS](https://dspace-clarin-it.ilc.cnr.it/repository/xmlui/handle/20.500.11752/ILC-88?show=full) and [ItalWordNet](https://dspace-clarin-it.ilc.cnr.it/repository/xmlui/handle/20.500.11752/ILC-62)) and ILC-CNR (a sense mapping database of the cited lexicons, *iwnmapdb*). 
The extrapolated and checked data are then arranged in the formal structure of the Sense Inventory required for the ELEXIS tasks, such that for each lemma - PoS pair:
* Senses present in PSC, not mapped
* Mapped senses
* Senses present in IWN, not mapped.

The set of lemmas treated in the program is stapled in the output *newdataset.txt*.
The Sense Inventory is printed in *corrected_si.txt*. The latter output has also been transformed into a resource extension *.xslx*.

#### 📍 Sense mapping extension
##### repository: *mapping_extension*
Within the program (*maps.py*) we carry out two test phases for sense mapping between the ItalWordNet and WORD-SIMPLE CLIPS lexicons by calculating the similarity between word vectors using [spaCy](https://github.com/explosion/spaCy). In the first part the mappings already present in the ILC-CNR database *iwnmapdb* are analysed to arrive at a threshold of similarity between senses of the mappings already developed, to be applied to potential ones. In the second part of the code the *similarity* between senses of different lemmas (manually selected) without any mapped sense is analysed; similarity that was then compared with the Threshold found previously.
The program takes as input a file with the list of mapped lemmas (*listamapdb.txt*) for a check on the manually selected lemmas and the final format of the Sense Inventory (*corrected_si.txt*) for the extrapolation of information on the senses (definition, IDs). The outputs are respectively *testmapping.txt* for the first part, with the list of analysed mappings and their *similarity*, as well as the arithmetic mean of the set of similarities corresponding to the Threshold; for the second one, instead, *testnonmapped.txt*, where the list of mappings with the *similarity* between all the senses of each lemma is found. 

#### 📍 Percentages of resource coverage 
##### repository: *percents*
The Sense Inventory also serves as a means for an analysis of the current extent of the databases we have used, in particular to study their actual coverage and efficiency with respect to the needs of ELEXIS and their state of the art. The program (*rates.py*) is used to collect and process the data obtained from the Sense Inventory, to process the numbers needed to present them and to formulate a more accurate analysis.
The program takes as input the dataset from which the Sense Inventory was derived (*dataset2000wiki_Export_IT_2021-02-22_Corrected_v2.tsv*) and the Sense Inventory (*corrected_si.txt*) to recreate the process used for the latter, in order to collect data during the processing. In the output (*numbers.txt*) the results of the analysis are printed.

#### 📍 Selection of sentences for manual annotation
##### repository: *sentences_selector*
This simple program (*sentences_selector.py*) takes as input the dataset in CoNLL-U format (*dataset2000wiki_Export_IT_2021-02-22_Corrected_v2.tsv*) and assigns to each sentence contained in it the number of lemmas present in both the reference databases, PSC and IWN, and then prints all the data in the output (*sentences.txt*). This makes it easier to select sentences for the manual annotation task. The sentences were then selected manually, due to some syntactic peculiarities that had to be taken into account on a non-automatic level.

