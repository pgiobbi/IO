# -*- coding: utf-8 -*-
"""
Created on Wed Jan 31 15:00:22 2018

@author: pierm

Python module that makes basic I/O operations easier
Version 1.6.1

------------
History log:
v1.6.1
-IO.readfile returns a list instead of a numpy array if read_strings==True
v1.6.0
-IO.readfile : fixed bug that wouldn't read the last character of the last line
-IO.readfile : added read_strings to read strings
-IO.writefile : no need to provide a 2d or 3d array
-IO.writefile : automatic labels available
-IO.readfile/IO.writefile : works with rank 3 arrays as well
"""

def readfile(filename, comments = '#', float_separation = '.',
             delimiter = ' ', read_strings=False):
    """
    Reads input file easily.

    Parameters
    ----------
    filename : string
        Name of the file containing data you wish to load. Provide only the
        filename if you file is in the cwd, provide full path otherwise.

    comments : string, array_like, optional
        Lines beginning with this character are going to be ignored.
        It support even different comment characters, but please try to avoid it
        e.g. comments = '#; %@' oppure comments = ['#', ';', ' ', '%', '@']

    float_separation : string, optional
        Character used to separate whole numbers from decimal numbers
        Italians .etc., use ','

    delimiter : string, optional
        String used to separate data on the lines.
        Unless you chose a funky delimiter (e.g. ``%``(please don't)), readfile
        is going to ignore whatever is not [number,+,-,E,e], therefore
        everything else is going to be treated as a delimiter and is going to
        separate columns. It is however important if you wish to load strings
        (see read_strings)

    read_strings : bool, optional
        If True, the procedure is not going to read numbers but strings instead

    Returns
    -------
    out : list
        numpy.array() (rank=2d/3d) containing the loaded data. If data is
        corrupted and the number of number per line is non costant then the
        procedure will return a list instead and raise a warning. If the file
        was created with IO.writefile there will be a comment which allows
        IO.readfile to read even rank=3d.

    Examples
    --------
    Data from '2-Alluminio1.txt'con comma delimiter (``,``) and line comments
    beginning with ``"``

    >>> import IO
    >>> dati = IO.readfile('2-Alluminio1.txt', comments='"', float_delimiter=',')

    Notes
    -----
    Are you lazy and don't want to put IO.py in your working directory?
    Just open the terminal and type
    >>> pip show numpy
    In my case c:\users\pierm\anaconda2\lib\site-packages
    And put IO.py there! So you won't need to copy it in every folder
    """

    try:
        with open(filename,"r") as f:
            #Read all file lines as string and save them in a list
            out=[]
            lettura=f.readlines()
            wrapevery=None
            j=-1
            for riga in lettura:
                j+=1    #Row counter
                #Ignore line if the first character is a comment character
                if riga[0] in comments:
                    # Handle arrays with rank=3
                    if 'wrapevery' in riga:
                        wrapevery=int(riga.split('wrapevery = ')[-1].split()[0])
                        #It works, but don't alter the file!
                        #Cool way of avoiding blank characters
                    continue
                stringa=''
                riga_i=[]

                if not read_strings:
                    #Do this if your data are strings
                    for char in riga:
                        if char==float_separation:
                            if stringa=='':
                                stringa+='0.'
                            else:
                                stringa+='.'
                        #Take advantage of ASCII to convert strings to float
                        #Reading only numbers, +, -, E, e
                        elif  (ord(char)>=48 and ord(char)<=57) or ord(char)==43  \
                            or ord(char)==45  or ord(char)==69  or ord(char)==101 \
                            and char!=delimiter:

                            #Error handling: ignore 'E' or 'e' if string is
                            #still empty
                            if stringa=='' and (ord(char)==69  or ord(char)==101):
                                continue

                            stringa+=char
                        else:
                            if stringa!='':
                                riga_i.append(float(stringa))
                            stringa=''

                    #Add characters to string if we are at the end of the line
                    if stringa!='':
                        riga_i.append(float(stringa))

                    #Salva line in read data if it is not empty
                    if riga_i!=[]:
                        out.append(riga_i)

                else:   #Do this if you want to read strings
                    i=0
                    for char in riga:
                        #newline is \n but it counts as a single character
                        if (char==delimiter and stringa!='') or i==len(riga)-1:
                            if stringa!='':
                                riga_i.append(stringa)
                                stringa=''
                        else:
                            if char!=delimiter:
                                stringa+=char
                            if j==len(lettura)-1 and i==len(riga)-1:
                                stringa+=riga[i]  #last line, last character
                        i+=1
                    if riga_i!=[]:
                        out.append(riga_i)


            #Checking wheter len(line) is constant for all lines
            lengths=[]

            for i in range(len(out)):
                lun=len(out[i])
                flag=0
                if lengths==[]:
                    lengths.append([lun, [i]])
                else:
                    for j in range(len(lengths)):
                        if lengths[j][0]==lun:
                            lengths[j][1].append(i)
                            flag=1
                            break
                    if not flag:
                        lengths.append([lun, [i]])

            if len(lengths)>1:
                print "Warning: not all lines have the same shape"
                maximum=0
                for i in range(len(lengths)):
                    lun=len(lengths[i][1])
                    if lun>maximum:
                        maximum=lun
                        indice=i
                print "Most frequent lenght : %i (%i counts) " \
                        %(lengths[indice][0], maximum)
                print "Check rows : ",
                for i in range(len(lengths)):
                    if i!=indice:
                        for j in range(len(lengths[i][1])):
                            if j<len(lengths[i][1])-1:
                                char=","
                            else:
                                char=" "

                            print "%i%c" %(lengths[i][1][j],char),
                print ""


            try:
                #Try returning a numpy array
                import numpy as np
                out=np.array(out)
                if wrapevery is not None:
                    out=out.reshape(out.shape[0],-1,wrapevery)
                if read_strings==True:
                    out=out.tolist()
                return out

            except ImportError:
                #Return a list if numpy in not available
                print "Could not load numpy module"
                print "Returning data as a 2D list"
                return out

    except IOError:
         print "Could not read file: %s" %filename


def writefile(filename,  dati, max_char=11, decimal_places=8, delimiter='   ',
              dtype='e', mode='w', comments = '#', labels=True,
              row_comment=False, main_comment=None):
    """
    Writes list/np.array 2d to file that you can easily read with IO.readfile

    Parameters
    ---------
    filename : string
        Name of the file you want to save your data to

    dati : list
        2d list/np.array to write to file. It used to work even if number of
        numbers per line was not constant, but numpy doesn't like that.
        3d is supported as well thanks to wrapevery (see below)

    max_char : int, optional
        Number of allocated places for the whole number

    decimal_places : int, optional
        Number of allocated places for decimals

    delimiter : char, optional
        delimiter to separate columns. default = blanks

    dtype : char, optional
        Data type. Choose between {'e'/'E'->exponential, 'f'->float,'i'->int}
        Remember that in order to provide the necessary places for the e/E
        format you need that max_char>=decimal_places+7. So the procedure is
        going to override you parameters if you fail to do that.
        It has been implemented for 'f' as well, but only for numbers that
        are in (-10,10)

    mode : string, optional
        Write action : {'w'=write, 'a'=append}.
        Warning! Check on character not implemented!

    comments : char, optional
        Character you wish to start your comment lines with

    main_comment : string, optional
        Main comment to save at the start of the file. Nicely boxed, using
        the comment character you provided in ``comments``

    labels : list, optional, {True, None}
        String list (printed after ``main_comment``) to describe columns data
        e.g. labels=['time', 'velocity']
        This line is commented with the character ``comments``
        Set labels=True if you want to auto generate the labels (not so smart)

    row_comment : bool, optional
        If data is a square matrix, it prints ``labels`` even at the start of
        each line, with NO character ``comments`` before. Nicely formatted, and
        as long as you don't use labels with numbers,+,- you won't have any
        problems loading the file with IO.readfile, but not everyone uses it
        so choose wisely!

    Notes
    -----
    Data on the file are read as a 2d list/array and wrapevery allows you
    to load 3d lists/arrays as well by reshaping
    E.g. Iterating N Markov chains for N_ITER iterations in a 3d space.
    data.shape=(N_ITER, N, 3). Wrapevery works if data are saved in this way:
        [(X,Y,Z)_1stchain, (X,Y,Z)_2ndchain, ... , (X,Y,Z)_Nthchain ]1stiter
        [(X,Y,Z)_1stchain, (X,Y,Z)_2ndchain, ... , (X,Y,Z)_Nthchain ]2nditer
        ...
        [(X,Y,Z)_1stchain, (X,Y,Z)_2ndchain, ... , (X,Y,Z)_Nthchain ]N_ITERthiter
    Use IO.readfile to load it seamlessly!
    """

    try:
        with open(filename, mode) as f:
            #Overriding places provided if they are not enough for good print
            if dtype=='e':
                max_char=max(max_char,decimal_places+7)
            elif dtype=='f':
                max_char=max(max_char,decimal_places+3)

            try:
                import numpy as np
            except ImportError:
                print "Could not load numpy module"

            wrapevery=None        #Parameter needed to save rank=3 arrays
            if np.array(dati).ndim==1:  #To save rank=1
                dati=[dati]
            elif np.array(dati).ndim==3:   #To save rank=3
                wrapevery=np.array(dati).shape[-1]

            #Print main comment
            if main_comment is not None:
                stringa=''
                for i in range(len(main_comment)):
                    stringa+='='
                f.write("%s%s\n" %(comments[0],stringa))
                f.write("%s%s\n" %(comments[0],main_comment))
                f.write("%s%s\n\n" %(comments[0],stringa))

            #Wrapevery comment to let IO.readfile know that rank=3
            if wrapevery is not None:
                f.write("%1s wrapevery = %i\n" %(comments[0],wrapevery))
                dati=np.array(dati).reshape(len(dati),-1)

            #Generate automatic labels (uscing ASCII, not so smart)
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

            #Needed later to avoid printing delimiter at the end of the line
            delim=delimiter
            for i in range(len(dati)):
                if row_comment:
                    if len(dati)!=len(dati[0]):
                        print "No square matrix!"
                        return
                    f.write("%*s%s" %(caratteri, labels[i][:caratteri], delimiter))
                for j in range(len(dati[i])):
                    #Needed to avoid printing delimiter at the end of the line
                    if j==len(dati[i])-1:
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
        print "Could not open file: %s" %filename

def show_matrix(matrix, prec=0, row_index=False):
    """
    Print nicely a matrix on screen. Made to print connection matrices
    Ignore this, just use numpy instead...
    This works well only if all values of the matrix need the same number of
    places

    Parameters
    ----------
    matrix : list
        Matrix to print in a formatted way on screen

    prec : float, optional
        last digit of precision i.e. 1E-4

    row_index : bool, optional
        Set True if you want to print i at the beginning of the line
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
                    if row_index: 
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
