import networkx as nx
import glob
import chardet
from collections import Counter

def create_graph(document, g_file):
    """Create co-occurrence graph of document by calculate
    word and edge frequency.

    Parameters
    ----------
    document : String, Path that contain document file.
    g_file : String, Path to contain output of graph file.
        if none, graph file create at current path.

    Returns
    --------
    Graph : gpickle file.

    Examples
    ---------
    >>> document = "document.txt"
    >>> g_file = "/graphfolder/graph.gpickle"
    >>> create_graph(document, g_file)

    """
    word_count = dict()
    word_tag = dict()
    link_count = dict()
    link_dict = dict()
    # create graph of all txt list in dir.
    if ".txt" not in document:
        path = document
        for file in glob.glob(path+"*.txt"):
            Text_file = open(file, 'r', encoding=_encode_type(file))
            for line in Text_file:
                # word frequencies
                word_list = line.split()
                for word in word_list:
                    if "|" in word:
                        word, tag = word.split("|")
                        word_tag[word] = tag
                    
                    if word in word_count:
                        word_count[word] += 1
                    else:
                        word_count[word] = 1

                # link frequencies
                for source in range(len(word_list)):
                    for target in range(source+1, len(word_list)):
                        if word_list[source] == word_list[target]:
                            continue

                        source_word = None
                        target_word = None
                        # Remove tag
                        if "|" in word_list[source]:
                            source_word = word_list[source].split('|')[0]
                        else:
                            source_word = word_list[source]

                        if "|" in word_list[target]:
                            target_word = word_list[target].split('|')[0]
                        else:
                            target_word = word_list[target]

                        # Sort the letters
                        sort_word = sorted([source_word, target_word])
                        pair_word = sort_word[0] + "|" + sort_word[1]

                        if pair_word in link_count:
                            link_count[pair_word] += 1
                        else:
                            link_count[pair_word] = 1
              
        link_cost, link_dict = _calculate_link_cost(word_count, link_count)
        _write_graph_to_gpickle_format(g_file, word_count, word_tag, link_count, link_dict, link_cost)

    # create graph of single text file.
    else:
        Text_file = open(document, 'r', encoding=_encode_type(document))
        for line in Text_file:
            # word frequencies
            word_list = line.split()
            for word in word_list:
                if "|" in word:
                    word, tag = word.split("|")
                    word_tag[word] = tag
                
                if word in word_count:
                    word_count[word] += 1
                else:
                    word_count[word] = 1

            # link frequencies
            for source in range(len(word_list)):
                for target in range(source+1, len(word_list)):
                    if word_list[source] == word_list[target]:
                        continue

                    source_word = None
                    target_word = None
                    # Remove tag
                    if "|" in word_list[source]:
                        source_word = word_list[source].split('|')[0]
                    else:
                        source_word = word_list[source]

                    if "|" in word_list[target]:
                        target_word = word_list[target].split('|')[0]
                    else:
                        target_word = word_list[target]

                    # Sort the letters
                    sort_word = sorted([source_word, target_word])
                    pair_word = sort_word[0] + "|" + sort_word[1]

                    if pair_word in link_count:
                        link_count[pair_word] += 1
                    else:
                        link_count[pair_word] = 1
            
        link_cost, link_dict = _calculate_link_cost(word_count, link_count)

        _write_graph_to_gpickle_format(g_file, word_count, word_tag, link_count, link_dict, link_cost)

def _write_graph_to_gpickle_format(g_file, word_count, word_tag, link_count, link_dict, link_cost):
    G = nx.Graph()

    for node in word_count:
        if node in word_tag:
            G.add_node(node, occur=word_count[node], tag=word_tag[node])
        else:
            G.add_node(node, occur=word_count[node])

    for edge in link_count:
        nodes = edge.split('|')
        G.add_edge(nodes[0], nodes[1], count=link_count[edge],
                   dice=link_dict[edge], cost=link_cost[edge])

    print(nx.info(G))
    nx.write_gpickle(G, g_file)

def _calculate_link_dice(word_count, wordlink, countab):
    
    wordlist = wordlink.split('|')
    countA = word_count[wordlist[0]]
    countB = word_count[wordlist[1]]
    countAB = countab

    helpk = 0
    if countB <= countA:
        helpk = countB
    else:
        helpk = countA

    if countAB >= helpk:
        countAB = helpk

    dicevalue = (2*countAB)/(countA+countB)

    if dicevalue > 1:
        dicevalue = 1.0

    return dicevalue

def _calculate_link_cost(word_count, link_count):
    link_cost = dict()
    link_dict = dict()
    for wordpair in link_count:
        dice = _calculate_link_dice(word_count, wordpair, link_count[wordpair])
        link_dict[wordpair] = dice
        cost = 1/(dice+0.01)
        link_cost[wordpair] = cost
    return link_cost, link_dict

def _encode_type(file):

    rawdata = open(file, 'rb').read()
    FileCode = chardet.detect(rawdata)

    return FileCode['encoding']

#create_graph('Present_dataset/220Disease/', "graph/220Diseases.gpickle")

def add_node_document(doc_file, g_file):
    G = nx.read_gpickle(g_file)
    open_file = open(doc_file, 'r', encoding=_encode_type(doc_file))

    for line in open_file:
        node, doc = line.rstrip("\n").split(':')
        if node in G.nodes:
            G.node[node]['document'] = doc
    nx.write_gpickle(G, g_file)
    
#add_node_document('import_pdf/diseases/wordlist/node_doc.txt', 'graph/4disease.gpickle')