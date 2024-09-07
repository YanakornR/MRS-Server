from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO
import re
import nltk
from nltk.corpus import stopwords 
from nltk.tokenize import word_tokenize 
from nltk.stem.wordnet import WordNetLemmatizer
import glob
import os 

"""
- pretext_process(inputfile, outputfile, tag_dict)
    variable
    --------------
    inputfile = string, dir of input documents
    outputfile = string, dir of output pretext documents
    tag_dict = dictionary, tag : txt that contain tag words

    example
    --------------
    >>> inputfile = "pdf_folder/"
    >>> output = "pretext_folder/"
    >>> tag_dict =  {'DS': 'diseaselist.txt', 'ST':'symptomlist.txt'}
    >>> import_pdf_file(inputfile, output, tag_dict)

"""
def extract_pdf_text(pdf):
    # convert pdf data to txt format

    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, laparams=laparams)
    fp = open(pdf, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0
    caching = True
    pagenos=set()

    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True):
        interpreter.process_page(page)
        

    text = retstr.getvalue()

    fp.close()
    device.close()
    retstr.close()
    
    return text.lower()

def create_words_list(listpath):
    tag_dict = dict()
    words_token = []
    allwords = []

    for tag in listpath:
        if tag not in tag_dict:
            tag_dict[tag] = []
    for tag in listpath:
        #text_list = open(listpath[tag], 'r', encoding="utf-8-sig")
        text_list = open(listpath[tag], 'r', encoding="cp1252")
        for word in text_list:
            tag_name = word.lower().replace(' ', '_').replace('\n','')
            if tag_name not in tag_dict[tag]:
                tag_dict[tag].append(tag_name)
                
            word_list = word.lower().split()
            if word_list not in words_token:
                words_token.append(word_list)
            for tn in word_list:
                if tn not in allwords:
                    allwords.append(tn)

    return tag_dict, words_token, allwords

def remove_stopwords(string, allwords):
    remove_newline = string.replace('\n', ' ')
    remove_ref = re.sub('\[\d+\]', '', remove_newline.strip())
    split_words = nltk.word_tokenize(remove_ref)
    nouns_words = ''
    for (word, pos) in nltk.pos_tag(split_words): 
        
        if word in allwords:
            nouns_words += word + ' '
        else:
            if pos[0] == 'N' and word.isalnum():
                # convert to base tense
                c1 = WordNetLemmatizer().lemmatize(word)
                nouns_words += WordNetLemmatizer().lemmatize(c1, 'v') + ' '
          
                
        
    return nouns_words

def tokenization(sentence, wordlist):
    """ Match a string with serveral words.

    Parameter
    ---------
    sentence : string, text read from document per line.
    wordlist : list, contain word list for do word tokenization.

    Returns
    ---------
    tokenized : list
            Return list variable contain word of sentences
            and words that have several word will be represented as one.

    Examples
    ---------
    >>> sentence = "This is new york and it's one of the world biggest cities"
    >>> wordlist = [["new","york"], ["biggest", "cities"]]
    >>> tokenized = tokenization(sentence, wordlist)
    ["This", "is", "new_york", "and", "it's", "one", "of", "the", "world", "biggest_cities"]

    """
    sentence = sentence.split()
    mwe_tokenizer = nltk.tokenize.MWETokenizer(wordlist)
    tokenized = mwe_tokenizer.tokenize(sentence)
    my_tokenized = ''
    for token in tokenized:
        my_tokenized += token
        my_tokenized += ' '

    return my_tokenized

def word_tagged(sentence, tag_dict):
    words = sentence.split()
    word_tag = ''
    for w in words:
        w_tag = None
        for tag in tag_dict:
            if w in tag_dict[tag]:
                w_tag = tag
                break
        if w_tag:
            word_tag += w + '|' + w_tag
        else:
            word_tag += w + '|NN'
        word_tag += ' '
    return word_tag

def pretext_process(inputfile, outputfile, tag_dict):
    pdf = extract_pdf_text(inputfile)
    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
    split_sentences = tokenizer.tokenize(pdf)
    my_tag_dict, words_token, allwords = create_words_list(tag_dict)
    pretext = ''
    for sents in split_sentences:
        rms_sents = remove_stopwords(sents, allwords)
        tkn_sents = tokenization(rms_sents, words_token)
        tag_sents = word_tagged(tkn_sents, my_tag_dict)
        if len(tkn_sents) > 1:
            pretext += tag_sents
            pretext += '\n'
    
    write_file = open(outputfile, 'w', encoding='utf-8')
    write_file.write(pretext)

def import_pdf_file(inputfilepath, outputfilepath, listpath):

    try:
        os.mkdir(outputfilepath)
    except:
        pass
    alltag = create_words_list(listpath)

    for file in glob.glob(inputfilepath+"/*.pdf"):
        filename = os.path.basename(file)
        print(filename)
        pretext_process(file, outputfilepath+"/"+filename.replace('.pdf','.txt'), listpath)

#my_tag =  {'DS': 'import_pdf/diseases/wordlist/diseaselist.txt', 'ST':'import_pdf/diseases/wordlist/symptomlist.txt'}
#import_pdf_file("import_pdf/diseases/Wiki/", "pretext/disease",my_tag)


# Temp
path = 'Med_Datasets_17112020/Preprocessing_Results/226_diseases_without_COVID-19'
def read_disease_text_list(path, output):
    my_tag =  {'DS': 'Med_Datasets_17112020/medresources/diseaseswiki.txt_lc.txt', 'ST':'Med_Datasets_17112020/medresources/symptomswiki.txt_lc.txt'}
    my_tag_dict, words_token, allwords = create_words_list(my_tag)
    for file in glob.glob(path+'/*.txt'):
        filename = os.path.basename(file)
        if 'untagged' in filename:
            print(filename)
            pretext = ''
            content = open(file, 'r',encoding='cp1252')
            for line in content:
                tkn_sents = tokenization(line.strip().lower(), words_token)
                tag_sents = word_tagged(tkn_sents, my_tag_dict)
                if len(tkn_sents) > 1:
                    pretext += tag_sents
                    pretext += '\n'

            write_file = open(output+filename, 'w', encoding='utf-8')
            write_file.write(pretext)

            
#read_disease_text_list(path, 'Present_dataset/withoutcovid/')


