# -*- coding: utf-8 -*-
"""
Created on Wed Jan 31 15:00:22 2018

@author: pierm

Programma che legge facilmente file, dividendolo in varie righe e colonne
Versione 1.6.1

------------
History log:
v1.6.1
-readfile ritorna una lista invece che un array numpy se read_strings==True
v1.6.0
-aggiunto a readfile la possibilita' di leggere stringhe
-writefile consente di stampare array 1d senza trasformazione esterna
-corretto bug readfile che non leggeva ultimo carattere ultima riga(str)
-aggiunto il parametro wrapevery per lettura/scrittura di matrici 3d
-aggiunta la possibilita' di creare labels automatiche per writefile
"""

def readfile(nomefile, comments = '#', float_separation = '.',
             delimiter = ' ', read_strings=False):
    """
    Legge facilmente file input.

    Parameters
    ----------
    nomefile : string
        Inserisci il nome del file dove vuoi leggere i dati e.g. "input.txt"
        N.B. Il file deve trovarsi nella stessa directory dello script che
        chiama il modulo IO!

    comments : string, array_like, optional
        Le righe del file che iniziano con un carattere del genere non vengono
        considerate. N.B. Deve essere un singolo carattere!
        e.g. comments = '#; %@' oppure comments = ['#', ';', ' ', '%', '@']

    float_separation : string, optional
        Carattere utilizzato per dividere cifre intere da cifre decimali
        Se il numero e' italiano porre float_separation = ','

    delimiter : string, optional
        Carattere utilizzato per definire inizio e fine delle varie colonne
        A meno di scelte curiose (e.g. '%') il programma considera validi
        soltanto (numeri,+,-,E,e). Tutto cio' che non e' di questo tipo viene
        considerato come un delimitatore e divide automaticamente le colonne
        e.g. Il programma divide automaticamente le colonne se trova spazi/tab,
        quindi in realta' e' inutile specificarlo. E' importante invece se si
        usa readfile per leggere stringhe (vedi parametro read_strings)

    read_strings : bool, optional
        Se True il programma non legge numeri ma legge stringhe

    Returns
    -------
    out : list
        Lista (2d) che contiene i vari dati letti. rows == righe file buone
        Se i dati sono stati scritti bene si dovrebbe avere ncols==costante

    Examples
    --------
    Dati da '2-Alluminio1.txt'con delimitatore decimale italiano (virgola) e
    commenti iniziano con virgolette (")

    >>> import IO
    >>> dati = IO.readfile('2-Alluminio1.txt', comments='"', float_delimiter=',')

    Notes
    -----
    Mettere IO.py nella stessa directory dei vari moduli python. Basta andare
    sul terminal e digitare
    >>> pip show numpy
    Nel mio caso c:\users\pierm\anaconda2\lib\site-packages
    Altrimenti tenere IO.py nella stessa cartella da dove si esegue lo script
    principale
    """

    try:
        with open(nomefile,"r") as f:
            #Legge tutte le righe come stringhe e le salva in array
            out=[]
            lettura=f.readlines()
            wrapevery=None
            j=-1
            for riga in lettura:
                j+=1    #Per contare riga
                #Trascura riga se il primo carattere e' un commento
                if riga[0] in comments:
                    # Per matrici con d>2
                    if 'wrapevery' in riga:
                        wrapevery=int(riga.split('wrapevery = ')[-1].split()[0])
                        #Attenzione, funziona solo se non si altera il file!
                        #Con l'ultima riga evita problemi di spazi tipo da fortran
                    continue
                stringa=''
                riga_i=[]

                if not read_strings:
                    #Questa funzione legge numeri, non stringhe
                    for char in riga:
                        if char==float_separation:
                            if stringa=='':
                                stringa+='0.'
                            else:
                                stringa+='.'
                        #legge solo numeri, +, -, E, e
                        elif  (ord(char)>=48 and ord(char)<=57) or ord(char)==43  \
                            or ord(char)==45  or ord(char)==69  or ord(char)==101 \
                            and char!=delimiter:

                            #Due nuove righe! attenzione! Per gestire meglio errori
                            if stringa=='' and (ord(char)==69  or ord(char)==101):
                            #se leggo E o e con la stringa ancora vuota rifiuto
                                continue

                            stringa+=char
                        else:
                            if stringa!='':
                                riga_i.append(float(stringa))
                            stringa=''

                    #Se gli ultimi caratteri della riga sono buoni li devo aggiungere
                    if stringa!='':
                        riga_i.append(float(stringa))

                    #Salva riga nei dati se non e' vuota
                    if riga_i!=[]:
                        out.append(riga_i)

                else:   #blocco se voglio leggere stringhe
                    i=0
                    for char in riga:
                        #newline e' \n ma viene contato come un solo carattere
                        if (char==delimiter and stringa!='') or i==len(riga)-1:
                            if stringa!='':
                                riga_i.append(stringa)
                                stringa=''
                        else:
                            if char!=delimiter:
                                stringa+=char
                            if j==len(lettura)-1 and i==len(riga)-1:
                                stringa+=riga[i]  #ultima riga ultimo carattere
                        i+=1
                    if riga_i!=[]:
                        out.append(riga_i)


            #Controllo se numero elementi delle righe e' costante
            lunghezze=[]

            for i in range(len(out)):
                lun=len(out[i])
                flag=0
                if lunghezze==[]:
                    lunghezze.append([lun, [i]])
                else:
                    for j in range(len(lunghezze)):
                        if lunghezze[j][0]==lun:
                            lunghezze[j][1].append(i)
                            flag=1
                            break
                    if not flag:
                        lunghezze.append([lun, [i]])

            if len(lunghezze)>1:
                print "Warning: not all lines have the same shape"
                maximum=0
                for i in range(len(lunghezze)):
                    lun=len(lunghezze[i][1])
                    if lun>maximum:
                        maximum=lun
                        indice=i
                print "Most frequent lenght : %i (%i counts) " \
                        %(lunghezze[indice][0], maximum)
                print "Check rows : ",
                for i in range(len(lunghezze)):
                    if i!=indice:
                        for j in range(len(lunghezze[i][1])):
                            if j<len(lunghezze[i][1])-1:
                                char=","
                            else:
                                char=" "

                            print "%i%c" %(lunghezze[i][1][j],char),
                print ""


            try:
                import numpy as np
                out=np.array(out)
                if wrapevery is not None:
                    out=out.reshape(out.shape[0],-1,wrapevery)
                if read_strings==True:
                    out=out.tolist()
                return out

            except ImportError:
                print "Could not load numpy module"
                print "Returning data as a 2D list"
                return out

    except IOError:
         print "Could not read file: %s" %nomefile


def writefile(nomefile,  dati, max_char=11, decimal_places=8, delimiter='   ',
              dtype='e', mode='w', comments = '#', labels=True,
              row_comment=False, main_comment=None):
    """
    Scrive su un file i valori di una lista/array 2d che possono poi essere
    facilmente letti grazie alla funzione readfile

    Parameters
    ---------
    nomefile : string
        Nome del file sul quale salvare i dati e.g. 'output.txt'

    dati : list
        Lista 2d da scrivere su file. Non e' necessario che essa abbia sempre
        lo stesso numero di elementi su ogni riga

    max_char : int, optional
        Numero di cifre assegnate per la stampa di ogni elemento di dati

    decimal_places : int, optional
        Numero di cifre assegnate per le cifre decimali

    delimiter : char, optional
        Delimitatore per dividere le varie colonne. Se non specificato sono
        degli spazi

    dtype : char, optional
        Tipo di formato dei dati. Lasciare 'e' per tipo esponenziale, 'f' per
        float o 'i' per interi. Assumendo 1*sign, 1*intero, 1*punto, 4*per esp
        e decimal_places*decimali abbiamo che max_char>=decimal_places+7.
        E' stata fatta la stessa cosa con 'f' ma e' valida soltanto per (-10,10)
        Nel caso non sia cosi' viene aumentata la dimensione di max_char

    mode : string, optional
        Modalita' di scrittura. 'w'=write. 'a'=append. Attenzione! Non viene
        effettuato un controllo sul carattere!

    comments : char, optional
        Carattere con il quale iniziare commenti ad inizio file

    main_comment : string, optional
        Stringa da stampare ad inizio file per descrivere brevemente i dati

    labels : list, optional {True, None}
        Lista di stringhe da scrivere dopo main_comment per descrivere le varie
        colonne.
        e.g. labels=['tempo', 'velocita']
        Nel file viene preposto il carattere comments.
        Se si vogliono autogenerare le labels porre labels=True

    row_comment : bool, optional
        Se la matrice dei dati e' quadrata stampa le labels anche all'inizio
        di ogni riga se True. ATTENZIONE! Potrebbe essere piu' difficile
        leggere i dati, ma non ci dovrebbero essere problemi con IO.readfile.
        Evitare labels che contengano +,-,. e numeri

    Notes
    -----
    I dati su file sono letti sotto forma di matrice 2d e wrapevery permette
    di leggere i dati e di trasformare la lettura in una matrice 3d.
    E.g. si hanno delle posizioni in 2d di nplanets oggetti in funzione del
    tempo. La procedura per salvare/accedere ai dati e':
        -)si salva il file nella forma [x1,y1,x2,y2,...,xnplanets,ynplanets]
          per ogni riga  (vedi wrapevery per IO.writefile)
        -)con wrapevery = 2 si ricostruisce la matrice out in
            out[nrows,nplanets,2].
        -)per accedere alla posizione x dell'i-esimo pianeta al tempo k:
            out[k,i,0]
    """

    try:
        with open(nomefile, mode) as f:
            if dtype=='e':
                max_char=max(max_char,decimal_places+7)
            elif dtype=='f':
                max_char=max(max_char,decimal_places+3)
                # Questo da le cifre MINIME necessarie, cioe' se il numero e'
                # in (-10, 10)! Meglio usare 'e' se non si e' sicuri

            try:
                import numpy as np
            except ImportError:
                print "Could not load numpy module"

            wrapevery=None        #Parametro per capire se salvare matrice 3d
            if np.array(dati).ndim==1:  #per salvare anche matrici 1d
                dati=[dati]
            elif np.array(dati).ndim==3:   #Per salvare anche matrici 3d
                wrapevery=np.array(dati).shape[-1]


            if main_comment is not None:    #stampa commento principale
                stringa=''
                for i in range(len(main_comment)):
                    stringa+='='
                f.write("%s%s\n" %(comments[0],stringa))
                f.write("%s%s\n" %(comments[0],main_comment))
                f.write("%s%s\n\n" %(comments[0],stringa))

            #Serve per lasciare un commento che stiamo salvando un array3d
            if wrapevery is not None:
                f.write("%1s wrapevery = %i\n" %(comments[0],wrapevery))
                dati=np.array(dati).reshape(len(dati),-1)

            #Serve per generare label automatiche (con poca fantasia in ASCII)
            if labels==True:
                if wrapevery is not None:
                    if len(dati[0])/wrapevery <= 26:
                        labels=[chr(97+i%wrapevery)+str(int(i/wrapevery)+1) \
                                for i in range(len(dati[0]))]
                    else:
                        print "Not enough characters to generate automatic labels"
                        print "Labels turned off"
                        labels=None
                else:
                    if len(dati[0])<= 26:
                        labels=[chr(97+i) for i in range(len(dati[0]))]
                    else:
                        print "Not enough characters to generate automatic labels"
                        print "Labels turned off"
                        labels=None

            if labels is not None:
                f.write("%s" %comments[0])
                caratteri=max_char
                if row_comment:
                    f.write("%*s%s" %(caratteri, delimiter, delimiter))
                for i in range(len(labels)):
                    f.write("%*s%s" %(caratteri, labels[i][:caratteri], delimiter))
                f.write("\n")
            flag=0
            delim=delimiter #Serve dopo altrimenti stampo delim a fine riga
            for i in range(len(dati)):
                if row_comment:
                    if len(dati)!=len(dati[0]):
                        print "No square matrix!"
                        return
                    f.write("%*s%s" %(caratteri, labels[i][:caratteri], delimiter))
                for j in range(len(dati[i])):
                    if j==len(dati[i])-1:   #altrimenti stampa delimiter anche
                                            #a fine riga
                        delim=''

                    if labels is not None and j==0:
                        caratteri=max_char+1
                    else:
                        caratteri=max_char
                    if dtype=='e':
                        f.write("%*.*e%s" %(caratteri, decimal_places, dati[i][j], delim))
                    elif dtype =='f':
                        f.write("%*.*f%s" %(caratteri, decimal_places, dati[i][j], delim))
                    elif dtype=='i':
                        f.write("%*i%s" %(caratteri, dati[i][j], delimiter))
                    else:
                        flag=1
                        f.write("%*.*f%s" %(caratteri, decimal_places, dati[i][j], delim))
                    delim=delimiter

                f.write("\n")
        if flag==1:
            print "Bad defined dtype. Switched to float format"
    except IOError:
        print "Could not open file: %s" %nomefile


def less(nomefile):
    """
    Funzione per guardare rapidamente il file da caricare

    Parameters
    ---------
    nomefile : string
        Nome del file sul quale salvare i dati e.g. 'output.txt'

    Returns
    -------
    out : list
        Lista (1d) che contiene le righe del file lette

    """

    try:
        with open(nomefile, 'r') as f:
            out=f.readlines()
        return out
    except IOError:
        print "Could not open file: %s" %nomefile

def show_matrix(matrix, prec=0, row_index=False):
    """
    Funzione per stampare in modo formattato una matrice. Attenzione, funziona
    in modo formattato soltanto se tutti i valori della matrici occupano lo
    stesso numero di cifre (da aggiornare)

    Parameters
    ----------
    matrix : list
        Lista(2d) da stampare a schermo in modo formattato

    prec : float, optional
        Ultima cifra significativa di precisione. E.g. 1E-4

    row_index : bool, optional
        Mettere True per stampare l'indice della riga a inizio riga, False
        altrimenti
    """

    try:
        import numpy as np
    except ImportError:
        print "Could not load numpy module"

    global lettere
    global cifre
    lettere=[chr(ord('A')+i) for i in range(len(matrix[0]))]

    if prec!=0:
        cifre=int(-np.log10(prec))
    else:
        cifre=1

    if row_index:
        cifre_index=int(np.log10(len(matrix)))+1
    else:
        cifre_index=1
    for i in range(-1, len(matrix)):
        for j in range(-1, len(matrix[0])):
            if j==-1:
                if i==-1:
                    lettera = " "
                else:
                    if row_index:  #Se voglio stampare i a inizio riga
                        lettera = str(i+1)
                    else:
                        lettera = lettere[i]
                print "%*s%s" %(cifre_index, lettera," | "),
            else:
                if i==-1:
                    if prec==0:
                        print lettere[j],
                    else:
                        print "%*s%s%*s" %(cifre/2+1,"",lettere[j],cifre-cifre/2," "),
                else:
                    if prec==0:
                        print "%i" %matrix[i][j],
                    else:
                        print "%.*f" %(cifre, matrix[i][j]),
        print ""
    print ""
