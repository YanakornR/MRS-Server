import networkx as nx
import operator
import random
import math 
import glob
import os
import chardet
from creategraph import _calculate_link_cost, _write_graph_to_gpickle_format
#G = nx.read_gpickle("graph/201th.gpickle")
G = None

def check_keyword_exist(graph_path, keywords):
    node = []
    global G
    if G is None:
        G = nx.read_gpickle(graph_path)
    for word in keywords:
        if G.has_node(word):
            node.append(word)
    return node

def disease_hop_activate(keywords):
    activate_list = []
    candidate = dict()
    disease = dict()
    current_hop = 0
    node_count = dict()
    node_distance = []
    sum_distance = dict()
    sum_path = dict()
    
    path = []
    for key in keywords:
        activate_list.append([key])
        node_distance.append({key : 0})
        path.append({key:[key]})
        
    while len(disease) <= 10:
        
        for circle in range(len(activate_list)):
            activate_node = activate_list[circle][current_hop]
            
            for neighbor in nx.neighbors(G, activate_node):
                if neighbor in keywords:
                    continue

                # distance from initial point.
                if neighbor not in node_distance[circle]:
                    
                    node_distance[circle][neighbor] = node_distance[circle][activate_node] + G[activate_node][neighbor]['cost']
                    
                    prev_path = path[circle][activate_node]
                    current_path = prev_path + [neighbor]
                    path[circle][neighbor] = current_path
                    
                    # sum distance to all keywords.
                    if neighbor in sum_distance:
                        sum_distance[neighbor] += node_distance[circle][neighbor]
                        sum_path[neighbor] += 1
                    else:
                        sum_distance[neighbor] = node_distance[circle][neighbor]
                        sum_path[neighbor] = 1

                
                # check intersect
                if neighbor in node_count:

                    if neighbor not in activate_list[circle]:
                        activate_list[circle].append(neighbor)
                        node_count[neighbor] += 1
                    
                    # if found node intersect, calculate average distance.
                    if node_count[neighbor] == len(keywords):
                        candidate[neighbor] = sum_distance[neighbor] / len(keywords)
                        if G.node[neighbor]['tag'] == 'DS' or G.node[neighbor]['tag'] == 'DT':
                            disease[neighbor] = float(format(sum_distance[neighbor] / len(keywords) , '.4f'))
            
                else:
                    activate_list[circle].append(neighbor)
                    node_count[neighbor] = 1
                     

        current_hop += 1
  
    return dict(sorted(disease.items(), key=operator.itemgetter(1))), dict(sorted(candidate.items(), key=operator.itemgetter(1))), path, sum_path

def get2node_path(source, target):
    activate_node = [source]
    node_path = {source:[source]}
    node_distance = {source:0}
    found_target = False

    for an in activate_node:
        
        for nb in nx.neighbors(G, an):
            if nb not in node_path:
                activate_node.append(nb)
                # path
                prev_path = node_path[an]
                current_path = prev_path + [nb]
                node_path[nb] = current_path

                #distance
                node_distance[nb] = node_distance[an] + G[an][nb]['cost']
            
                if nb == target:
                    found_target = True

        if found_target:
            break

    return node_path[target], node_distance[target]
   
def node_position(node, centroid):
    xc = 275
    yc = 275
    node_size = 10
    circle_coordinates = {
        'circle1':{'x1':225,'x2':325,'y1':225,'y2':325,'r':50},
        'circle2':{'x1':125,'x2':425,'y1':125,'y2':425,'r':150},
        'circle3':{'x1':75,'x2':475,'y1':75,'y2':475,'r':200},
        'circle4':{'x1':0,'x2':550,'y1':0,'y2':550,'r':275},
    }
    color = {
        'red':'rgba(247, 32, 32, 1)',
        'yellow':'rgba(172, 247, 32)',
        'blue':'rgba(2, 69, 255)'
    }
    node_pos = []

    for n in node:
        x = None
        y = None
      
        # circle 1 (inside) centroid fixed
        if n['name'] == centroid:
            if n['color'] == 'red':
                n['rgba'] = color['red']
            elif n['color'] == 'yellow':
                n['rgba'] = color['yellow']
            else:
                n['rgba'] = color['blue']

            x = xc
            y = yc

        # circle 2
        elif n['color'] == 'red':
            n['rgba'] = color['red']
            x1 = circle_coordinates['circle2']['x1']
            x2 = circle_coordinates['circle2']['x2']
            y1 = circle_coordinates['circle2']['y1']
            y2 = circle_coordinates['circle2']['y2']

            while True:
                while True:
                    x = random.randint(x1,x2) 
                    y = random.randint(y1,y2)
                    d = math.sqrt((x - xc)**2  + (y - yc)**2)

                    # if point outside circle1
                    if d-node_size > circle_coordinates['circle1']['r']:
                        break
              
                d = math.sqrt((x - xc)**2  + (y - yc)**2)
                # if point inside circle2
                if d + node_size < circle_coordinates['circle2']['r']:
                    # check node intersect
                    intersect = False
                    for c2 in node_pos:
                        c1c2 = math.sqrt((x - c2['x'])**2 + (y- c2['y'])**2)
                        if c1c2 < 20*2: # 20 = r1+r2
                            intersect = True
                    if not intersect:
                        node_pos.append({'x':x, 'y':y})
                        break
        # circle 3
        elif n['color'] == 'yellow':
            n['rgba'] = color['yellow']
            x1 = circle_coordinates['circle3']['x1']
            x2 = circle_coordinates['circle3']['x2']
            y1 = circle_coordinates['circle3']['y1']
            y2 = circle_coordinates['circle3']['y2']

            while True:
                while True:
                    x = random.randint(x1,x2) 
                    y = random.randint(y1,y2)
                    d = math.sqrt((x - xc)**2  + (y - yc)**2)

                    # if point outside circle1
                    if d-node_size > circle_coordinates['circle2']['r']:
                        break
              
                d = math.sqrt((x - xc)**2  + (y - yc)**2)
                # if point inside circle2
                if d + node_size < circle_coordinates['circle3']['r']:
                     # check node intersect
                    intersect = False
                    for c2 in node_pos:
                        c1c2 = math.sqrt((x - c2['x'])**2 + (y- c2['y'])**2)
                        if c1c2 < 20*2: # 20 = r1+r2
                            intersect = True
                    if not intersect:
                        node_pos.append({'x':x, 'y':y})
                        break

         # circle 4 (outside)
        elif n['color'] == 'blue':
            n['rgba'] = color['blue']
            x1 = circle_coordinates['circle4']['x1']
            x2 = circle_coordinates['circle4']['x2']
            y1 = circle_coordinates['circle4']['y1']
            y2 = circle_coordinates['circle4']['y2']

            while True:
                while True:
                    x = random.randint(x1,x2) 
                    y = random.randint(y1,y2)
                    d = math.sqrt((x - xc)**2  + (y - yc)**2)

                    # if point outside circle1
                    if d-node_size > circle_coordinates['circle3']['r']:
                        break
              
                d = math.sqrt((x - xc)**2  + (y - yc)**2)
                # if point inside circle2
                if d + node_size*2 < circle_coordinates['circle4']['r']:
                     # check node intersect
                    intersect = False
                    for c2 in node_pos:
                        c1c2 = math.sqrt((x - c2['x'])**2 + (y- c2['y'])**2)
                        if c1c2 < 20*2: # 20 = r1+r2
                            intersect = True
                    if not intersect:
                        node_pos.append({'x':x, 'y':y})
                        break
        n['x'] = x
        n['y'] = y
        n['fixed'] = True

    return node
      
def centroid_shotest_path(diseases, symptoms, centroid):
    sp_path = dict()
    lenght, path = nx.single_source_dijkstra(G, centroid, weight='cost')
  
    for s in symptoms:
        if s in path:
            sp_path[s] = path[s]
    for d in diseases:
        if d in path:
            sp_path[d] = path[d]
   
    return sp_path, path, lenght

def create_graph_sp(disease, path, centroid, pathcost):
    node = [] # [{name: node}]
    edge = [] # [{source: node1, target: node2}]
    node_index = dict()
    temp_path = [] # [[path1], [n]]
    index_id = 0

    # Store node info
    # iterate disease list
    for d in path:
        # check if disease have path to current symptom list.
        temp_path.append(path[d])
        # iterate node from source to target and store to node list.
        for p in path[d]:
            if p not in node_index:
                color= None
                                        
                # color
                if G.node[p]['tag'] == 'DS' or G.node[p]['tag'] == 'DT':
                    color = 'red'
                elif G.node[p]['tag'] == 'ST':
                    color = 'yellow'
                else :
                    color = 'blue'
                                            
                node_index[p] = index_id
                node.append({'name': p , 'color':color, 'cost':pathcost[p]})
                index_id += 1

    d_list = list(disease)

    # Link between disease
    for d1 in range(len(d_list)):
        for d2 in range(d1+1, len(d_list)):
            getpath, distance = get2node_path(d_list[d1], d_list[d2])
            temp_path.append(getpath)
            # add node
            for n in getpath:
                if n not in node_index:
                    color= None
                    if G.node[n]['tag'] == 'DS' or G.node[n]['tag'] == 'DT':
                        color = 'red'
                    elif G.node[n]['tag'] == 'ST':
                        color = 'yellow'
                    else :
                        color = 'blue'
                        
                    node_index[n] = index_id
                    node.append({'name': n , 'color':color , 'cost':pathcost[p]})
                    index_id += 1

    # Set postition (x, y)
    node = node_position(node, centroid)
 
    # Store edge info
    check_edge = [] # for check if edge already exist.
    # iterate path
    for p in temp_path:
        for source in range(len(p)):
            for target in range(source + 1, len(p)):
                pair = sorted([p[source], p[target]])
                if pair not in check_edge:
                    line_color = None
                    # line from red node to yellow node.
                    if node[node_index[p[source]]]['color'] == 'red' and node[node_index[p[target]]]['color'] == 'yellow' \
                        or node[node_index[p[source]]]['color'] == 'yellow' and node[node_index[p[target]]]['color'] == 'red':
                        line_color = 'red'
                    # line from red node to blue node.
                    elif node[node_index[p[source]]]['color'] == 'red' and node[node_index[p[target]]]['color'] == 'blue' \
                        or node[node_index[p[source]]]['color'] == 'blue' and node[node_index[p[target]]]['color'] == 'red':
                        line_color = 'deepSkyBlue'
                    # line from yellow node to blue node.
                    elif node[node_index[p[source]]]['color'] == 'yellow' and node[node_index[p[target]]]['color'] == 'blue' \
                        or node[node_index[p[source]]]['color'] == 'blue' and node[node_index[p[target]]]['color'] == 'yellow':
                        line_color = 'yellow'
                    else:
                        line_color = 'white'
                    edge.append({'source' : node_index[p[source]], 'target' :  node_index[p[target]], 'color':line_color})
                    check_edge.append(pair)
    
    return node, edge

def document_content(node, graph_location):
    G = nx.read_gpickle(graph_location)
    try:
        doc = G.node[node]['document']
        if "'s" in doc:
            doc = doc.replace("'s", "")
        text_file = 'static/PDF/'+doc
        return text_file
    except:
        return None

def node_symptoms_graph(node):

    lenght, path = nx.single_source_dijkstra(G, node, weight='cost')
    closest_symptoms = dict()
    limit = 10

    # store first closest 10 symptoms
    for p in path:
        if G.node[p]['tag'] == 'ST':
            closest_symptoms[p] = path[p]
        if len(closest_symptoms) >= limit:
            break

    #D3 Graph variable
    # Node variable
    graph_node = []
    node_index=dict()
    index_id = 0
    #  closest_symptoms = {'s':['n1','n2']}
    for c in closest_symptoms:

        #  closest_symptoms[c] = ['n1','n2']
        for cvalue in closest_symptoms[c]:

            if cvalue not in node_index:
                color= None
                if G.node[cvalue]['tag'] == 'DS' or G.node[cvalue]['tag'] == 'DT':
                    color = 'red'
                elif G.node[cvalue]['tag'] == 'ST':
                    color = 'yellow'
                else :
                    color = 'blue'
                node_index[cvalue] = index_id
                graph_node.append({'name': cvalue , 'color':color, 'cost':lenght[p]})
                index_id += 1

    #   set node postition (x, y)
    centroid = node
    graph_node = node_position(graph_node, centroid)

    # Edge variable
    graph_edge = []
    check_edge = [] # for check if edge already exist.
    # iterate path
    for c in closest_symptoms:
        p = closest_symptoms[c]
   
        for source in range(len(p)):
            for target in range(source + 1, len(p)):
                pair = sorted([p[source], p[target]])
                if pair not in check_edge:
                    line_color = None
                    # line from red node to yellow node.
                    if graph_node[node_index[p[source]]]['color'] == 'red' and graph_node[node_index[p[target]]]['color'] == 'yellow' \
                        or graph_node[node_index[p[source]]]['color'] == 'yellow' and graph_node[node_index[p[target]]]['color'] == 'red':
                        line_color = 'red'
                    # line from red node to blue node.
                    elif graph_node[node_index[p[source]]]['color'] == 'red' and graph_node[node_index[p[target]]]['color'] == 'blue' \
                        or graph_node[node_index[p[source]]]['color'] == 'blue' and graph_node[node_index[p[target]]]['color'] == 'red':
                        line_color = 'deepSkyBlue'
                    # line from yellow node to blue node.
                    elif graph_node[node_index[p[source]]]['color'] == 'yellow' and graph_node[node_index[p[target]]]['color'] == 'blue' \
                        or graph_node[node_index[p[source]]]['color'] == 'blue' and graph_node[node_index[p[target]]]['color'] == 'yellow':
                        line_color = 'yellow'
                    else:
                        line_color = 'white'
                    graph_edge.append({'source' : node_index[p[source]], 'target' :  node_index[p[target]], 'color':line_color})
                    check_edge.append(pair)
                    
    return graph_node, graph_edge

# display more nodes in range of distance from slider bar/ plus distance
def nodes_in_distance(centroid,main_nodes, org_nodes, org_edges, cost):
    node = [] # [ {name: node, 'color': 'blue', 'rgba': 'rgba(2, 69, 255)', 'x': 423, 'y': 437, 'fixed': True} ]
    edge = [] # [ {source: node1, target: node2} ]
    node_index = dict()
    index_id = 0

    #keep main nodes name in list
    except_nodes = []
    for mn in main_nodes:
        except_nodes.append(mn['name'])

    #check if there are have been adjust cost that higher than current cost.
    have_higher_cost = False 
    for orn in org_nodes:
        if orn['name'] not in except_nodes:
            if orn['cost'] > cost:
                have_higher_cost = True
                break
    if have_higher_cost:
        # Graph Nodes
        for orn in org_nodes:
            distance = orn['cost']
            if distance < cost+1 or orn['name'] in except_nodes:
                node.append(orn)
                node_index[orn['name']] = index_id
                index_id += 1

        nodes_amount = len(node_index)
        node_r = 6
        if nodes_amount > 60 and nodes_amount < 90:
            node_r = 5
        elif nodes_amount >= 90 and nodes_amount < 110:
            node_r = 4
        elif nodes_amount >= 110 and nodes_amount < 140:
            node_r = 3
        elif nodes_amount >= 140 and nodes_amount < 170:
            node_r = 2
        elif nodes_amount >= 170:
            node_r = 1

        # Graph Edges
        for e in org_edges:
            source_name = org_nodes[e['source']]['name']
            target_name = org_nodes[e['target']]['name']
            if source_name in node_index and target_name in node_index:
                source_id = node_index[source_name]
                target_id = node_index[target_name]
                line_color = None

                # line from red node to yellow node.
                if node[source_id]['color']  == 'red' and node[target_id]['color']  == 'yellow' \
                    or node[source_id]['color']  == 'yellow' and node[target_id]['color'] == 'red':
                    line_color = 'red'
                # line from red node to blue node.
                elif node[source_id]['color']  == 'red' and node[target_id]['color'] == 'blue' \
                    or node[source_id]['color']  == 'blue' and node[target_id]['color'] == 'red':
                    line_color = 'deepSkyBlue'
                # line from yellow node to blue node.
                elif node[source_id]['color']  == 'yellow' and node[target_id]['color'] == 'blue' \
                    or node[source_id]['color']  == 'blue' and node[target_id]['color'] == 'yellow':
                    line_color = 'yellow'
                else:
                    line_color = 'white'

                edge.append({'source' :  node_index[source_name], 'target' :  node_index[target_name], 'color': line_color})
    
    #first calculate in this cost
    else:
        lenght, path = nx.single_source_dijkstra(G, centroid, weight='cost', cutoff=cost)
        neigbors_amount = len(lenght)
        print("distance :", cost, " neighbors : ", neigbors_amount)

        # pos of nodes in main graph, after increase slider distance these nodes still on old position
        except_pos = []
        for orn in org_nodes:
            x = orn['x']
            y = orn['y']
            except_pos.append({'x':x, 'y':y})

        # Graph Nodes
        for p in path:
            if p not in node_index:
                color= None
                                        
                # color
                if G.node[p]['tag'] == 'DS' or G.node[p]['tag'] == 'DT':
                    color = 'red'
                elif G.node[p]['tag'] == 'ST':
                    color = 'yellow'
                else:
                    color = 'blue'
                                            
                node_index[p] = index_id
                node.append({'name': p , 'color':color, 'cost':lenght[p]})
                index_id += 1

        # check nodes amount for set nodes radius
        nodes_list = []
        for n in org_nodes:
            if n['name'] not in nodes_list:
                nodes_list.append(n['name'])
        for n in node_index:
            if n not in nodes_list:
                nodes_list.append(n)
                
        nodes_amount = len(nodes_list)
        node_r = 6
        if nodes_amount > 60 and nodes_amount < 90:
            node_r = 5
        elif nodes_amount >= 90 and nodes_amount < 110:
            node_r = 4
        elif nodes_amount >= 110 and nodes_amount < 140:
            node_r = 3
        elif nodes_amount >= 140 and nodes_amount < 170:
            node_r = 2
        elif nodes_amount >= 170:
            node_r = 1

        # Set postition (x, y)
        node = node_position_intersect(node, centroid, except_pos, node_r)

        # add initial nodes
        for orn in org_nodes:
            # if node from neighbors calculation duplicate with orignal node, set original pos(x, y) to that node.
            if orn['name'] in node_index:
                i = node_index[orn['name']]
                node[i]['x'] = orn['x']
                node[i]['y'] = orn['y']

            # add original node with original position
            else:
                node_index[orn['name']] = index_id
                node.append(orn)
                index_id += 1
        # Graph Edges
        check_edge = [] # for check if edge already exist.
        # iterate path
        for p in path:
            for source in range(len(path[p])):
                for target in range(source + 1, len(path[p])):
                    pair = sorted([path[p][source], path[p][target]])
                    if pair not in check_edge:
                        line_color = None
                        # line from red node to yellow node.
                        if node[node_index[path[p][source]]]['color'] == 'red' and node[node_index[path[p][target]]]['color'] == 'yellow' \
                            or node[node_index[path[p][source]]]['color'] == 'yellow' and node[node_index[path[p][target]]]['color'] == 'red':
                            line_color = 'red'
                        # line from red node to blue node.
                        elif node[node_index[path[p][source]]]['color'] == 'red' and node[node_index[path[p][target]]]['color'] == 'blue' \
                            or node[node_index[path[p][source]]]['color'] == 'blue' and node[node_index[path[p][target]]]['color'] == 'red':
                            line_color = 'deepSkyBlue'
                        # line from yellow node to blue node.
                        elif node[node_index[path[p][source]]]['color'] == 'yellow' and node[node_index[path[p][target]]]['color'] == 'blue' \
                            or node[node_index[path[p][source]]]['color'] == 'blue' and node[node_index[path[p][target]]]['color'] == 'yellow':
                            line_color = 'yellow'
                        else:
                            line_color = 'white'
                        edge.append({'source' : node_index[path[p][source]], 'target' :  node_index[path[p][target]], 'color':line_color})
                        check_edge.append(pair)

        # add original edges if not aready added
        for ore in org_edges:
            pair = sorted([org_nodes[ore['source']]['name'], org_nodes[ore['target']]['name']])
            if pair not in check_edge:
                # node_index['name'] = id
                # org_nodes['name'] = 'dengue_fever'
                # ore['source'] = node index
                # --> node_index[org_nodes[id]['name']]
                source_id = node_index[org_nodes[ore['source']]['name']]
                target_id = node_index[org_nodes[ore['target']]['name']]
                line_color = None
                # line from red node to yellow node.
                if node[source_id]['color'] == 'red' and node[target_id]['color'] == 'yellow' \
                    or node[source_id]['color'] == 'yellow' and node[target_id]['color'] == 'red':
                    line_color = 'red'
                # line from red node to blue node.
                elif node[source_id]['color'] == 'red' and node[target_id]['color'] == 'blue' \
                    or node[source_id]['color'] == 'blue' and node[target_id]['color'] == 'red':
                    line_color = 'deepSkyBlue'
                # line from yellow node to blue node.
                elif node[source_id]['color'] == 'yellow' and node[target_id]['color'] == 'blue' \
                    or node[source_id]['color'] == 'blue' and node[target_id]['color'] == 'yellow':
                    line_color = 'yellow'
                else:
                    line_color = 'white'
                        
                edge.append({'source' : source_id, 'target' :  target_id, 'color': line_color})
                check_edge.append(pair)
        print("done")
    return node, edge, node_r

# reduce nodes in range of distance from slider bar / minus distance
def nodes_out_distance(centroid,main_nodes, org_nodes, org_edges, cost, current_nodesize):

    node = []
    edge = []
    node_index = dict()
    node_id = 0
    
    # keep main nodes
    except_nodes = []
    for mn in main_nodes:
        except_nodes.append(mn['name'])

    # Graph nodes
    # remove nodes that out of range
    for n in org_nodes:
        distance = n['cost']
        if distance < cost or n['name'] in except_nodes:
            node.append(n)
            node_index[n['name']] = node_id
            node_id += 1

     
     # check nodes amount for set nodes radius
    nodes_amount = len(node)
    node_r = current_nodesize
    if nodes_amount > 60 and nodes_amount < 90:
        node_r = 5
    elif nodes_amount >= 90 and nodes_amount < 110:
        node_r = 4
    elif nodes_amount >= 110 and nodes_amount < 140:
        node_r = 3
    elif nodes_amount >= 140 and nodes_amount < 170:
        node_r = 2
    elif nodes_amount >= 170:
        node_r = 1
    else:
        node_r = 6
   
    # Graph edges
    for e in org_edges:
        source_name = org_nodes[e['source']]['name']
        target_name = org_nodes[e['target']]['name']

        if source_name in node_index and target_name in node_index:
            source_id = node_index[source_name]
            target_id = node_index[target_name]
            line_color = None

            # line from red node to yellow node.
            if node[source_id]['color']  == 'red' and node[target_id]['color']  == 'yellow' \
                or node[source_id]['color']  == 'yellow' and node[target_id]['color'] == 'red':
                line_color = 'red'
            # line from red node to blue node.
            elif node[source_id]['color']  == 'red' and node[target_id]['color'] == 'blue' \
                or node[source_id]['color']  == 'blue' and node[target_id]['color'] == 'red':
                line_color = 'deepSkyBlue'
            # line from yellow node to blue node.
            elif node[source_id]['color']  == 'yellow' and node[target_id]['color'] == 'blue' \
                or node[source_id]['color']  == 'blue' and node[target_id]['color'] == 'yellow':
                line_color = 'yellow'
            else:
                line_color = 'white'

            edge.append({'source' :  node_index[source_name], 'target' :  node_index[target_name], 'color': line_color})
        
    return node, edge, node_r

# symptoms graph in range of distance from slider bar / plus distance
def symptoms_in_distance(centroid,main_nodes, org_nodes, org_edges, cost):
    node = [] # [ {name: node, 'color': 'blue', 'rgba': 'rgba(2, 69, 255)', 'x': 423, 'y': 437, 'fixed': True} ]
    edge = [] # [ {source: node1, target: node2} ]
    node_index = dict()
    index_id = 0

    #keep main nodes name in list
    except_nodes = []
    for mn in main_nodes:
        except_nodes.append(mn['name'])

    #check if there are have been adjust cost that higher than current cost.
    have_higher_cost = False 
    for orn in org_nodes:
        if orn['name'] not in except_nodes:
            if orn['cost'] > cost:
                have_higher_cost = True
                break
    if have_higher_cost:
        # Graph Nodes
        for orn in org_nodes:
            distance = orn['cost']
            if distance < cost+1 or orn['name'] in except_nodes:
                node.append(orn)
                node_index[orn['name']] = index_id
                index_id += 1
        
        # check nodes amount for set nodes radius
        nodes_amount = len(node_index)
        node_r = 6
        if nodes_amount > 60 and nodes_amount < 90:
            node_r = 5
        elif nodes_amount >= 90 and nodes_amount < 110:
            node_r = 4
        elif nodes_amount >= 110 and nodes_amount < 140:
            node_r = 3
        elif nodes_amount >= 140 and nodes_amount < 170:
            node_r = 2
        elif nodes_amount >= 170:
            node_r = 1

        # Graph Edges
        for e in org_edges:
            source_name = org_nodes[e['source']]['name']
            target_name = org_nodes[e['target']]['name']
            if source_name in node_index and target_name in node_index:
                source_id = node_index[source_name]
                target_id = node_index[target_name]
                line_color = None

                # line from red node to yellow node.
                if node[source_id]['color']  == 'red' and node[target_id]['color']  == 'yellow' \
                    or node[source_id]['color']  == 'yellow' and node[target_id]['color'] == 'red':
                    line_color = 'red'
                # line from red node to blue node.
                elif node[source_id]['color']  == 'red' and node[target_id]['color'] == 'blue' \
                    or node[source_id]['color']  == 'blue' and node[target_id]['color'] == 'red':
                    line_color = 'deepSkyBlue'
                # line from yellow node to blue node.
                elif node[source_id]['color']  == 'yellow' and node[target_id]['color'] == 'blue' \
                    or node[source_id]['color']  == 'blue' and node[target_id]['color'] == 'yellow':
                    line_color = 'yellow'
                else:
                    line_color = 'white'

                edge.append({'source' :  node_index[source_name], 'target' :  node_index[target_name], 'color': line_color})
    
    #first calculate in this cost
    else:
        lenght, path = nx.single_source_dijkstra(G, centroid, weight='cost', cutoff=cost)
        neigbors_amount = len(lenght)
        print("distance :", cost, " neighbors : ", neigbors_amount)
        
        # pos of nodes in main graph, after increase slider distance these nodes still on old position
        except_pos = []
        for orn in org_nodes:
            x = orn['x']
            y = orn['y']
            except_pos.append({'x':x, 'y':y})

        # Graph Nodes
        for p in path:
            if p not in node_index:
                color= None
                                        
                # color
                if G.node[p]['tag'] == 'DS' or G.node[p]['tag'] == 'DT':
                    color = 'red'
                elif G.node[p]['tag'] == 'ST':
                    color = 'yellow'
                else:
                    color = 'blue'
                                            
                node_index[p] = index_id
                node.append({'name': p , 'color':color, 'cost':lenght[p]})
                index_id += 1
                
        # check nodes amount for set nodes radius
        nodes_list = []
        for n in org_nodes:
            if n['name'] not in nodes_list:
                nodes_list.append(n['name'])
        for n in node_index:
            if n not in nodes_list:
                nodes_list.append(n)
                
        nodes_amount = len(nodes_list)
        node_r = 6
        if nodes_amount > 60 and nodes_amount < 90:
            node_r = 5
        elif nodes_amount >= 90 and nodes_amount < 110:
            node_r = 4
        elif nodes_amount >= 110 and nodes_amount < 140:
            node_r = 3
        elif nodes_amount >= 140 and nodes_amount < 170:
            node_r = 2
        elif nodes_amount >= 170:
            node_r = 1

        # Set postition (x, y)
        node = node_position_intersect(node, centroid, except_pos,node_r)

        # add initial nodes
        for orn in org_nodes:
            # if node from neighbors calculation duplicate with orignal node, set original pos(x, y) to that node.
            if orn['name'] in node_index:
                i = node_index[orn['name']]
                node[i]['x'] = orn['x']
                node[i]['y'] = orn['y']

            # add original node with original position
            else:
                node_index[orn['name']] = index_id
                node.append(orn)
                index_id += 1
        # Graph Edges
        check_edge = [] # for check if edge already exist.
        # iterate path
        for p in path:
            for source in range(len(path[p])):
                for target in range(source + 1, len(path[p])):
                    pair = sorted([path[p][source], path[p][target]])
                    if pair not in check_edge:
                        line_color = None
                        # line from red node to yellow node.
                        if node[node_index[path[p][source]]]['color'] == 'red' and node[node_index[path[p][target]]]['color'] == 'yellow' \
                            or node[node_index[path[p][source]]]['color'] == 'yellow' and node[node_index[path[p][target]]]['color'] == 'red':
                            line_color = 'red'
                        # line from red node to blue node.
                        elif node[node_index[path[p][source]]]['color'] == 'red' and node[node_index[path[p][target]]]['color'] == 'blue' \
                            or node[node_index[path[p][source]]]['color'] == 'blue' and node[node_index[path[p][target]]]['color'] == 'red':
                            line_color = 'deepSkyBlue'
                        # line from yellow node to blue node.
                        elif node[node_index[path[p][source]]]['color'] == 'yellow' and node[node_index[path[p][target]]]['color'] == 'blue' \
                            or node[node_index[path[p][source]]]['color'] == 'blue' and node[node_index[path[p][target]]]['color'] == 'yellow':
                            line_color = 'yellow'
                        else:
                            line_color = 'white'
                        edge.append({'source' : node_index[path[p][source]], 'target' :  node_index[path[p][target]], 'color':line_color})
                        check_edge.append(pair)

        # add original edges if not aready added
        for ore in org_edges:
            pair = sorted([org_nodes[ore['source']]['name'], org_nodes[ore['target']]['name']])
            if pair not in check_edge:
                # node_index['name'] = id
                # org_nodes['name'] = 'dengue_fever'
                # ore['source'] = node index
                # --> node_index[org_nodes[id]['name']]
                source_id = node_index[org_nodes[ore['source']]['name']]
                target_id = node_index[org_nodes[ore['target']]['name']]
                line_color = None
                # line from red node to yellow node.
                if node[source_id]['color'] == 'red' and node[target_id]['color'] == 'yellow' \
                    or node[source_id]['color'] == 'yellow' and node[target_id]['color'] == 'red':
                    line_color = 'red'
                # line from red node to blue node.
                elif node[source_id]['color'] == 'red' and node[target_id]['color'] == 'blue' \
                    or node[source_id]['color'] == 'blue' and node[target_id]['color'] == 'red':
                    line_color = 'deepSkyBlue'
                # line from yellow node to blue node.
                elif node[source_id]['color'] == 'yellow' and node[target_id]['color'] == 'blue' \
                    or node[source_id]['color'] == 'blue' and node[target_id]['color'] == 'yellow':
                    line_color = 'yellow'
                else:
                    line_color = 'white'
                        
                edge.append({'source' : source_id, 'target' :  target_id, 'color': line_color})
                check_edge.append(pair)
        print("done")
    return node, edge, node_r

# reduce symptoms graph corresponding to range of distance from slider bar / minus distance
def symptoms_out_distance(centroid,main_nodes, org_nodes, org_edges, cost, current_nodesize):
    node = []
    edge = []
    node_index = dict()
    node_id = 0
    
    # keep main nodes
    except_nodes = []
    for mn in main_nodes:
        except_nodes.append(mn['name'])

    # Graph nodes
    # remove nodes that out of range
    for n in org_nodes:
        distance = n['cost']
        if distance < cost or n['name'] in except_nodes:
            node.append(n)
            node_index[n['name']] = node_id
            node_id += 1

    # check nodes amount for set nodes radius
    nodes_amount = len(node)
    node_r = current_nodesize
    if nodes_amount > 60 and nodes_amount < 90:
        node_r = 5
    elif nodes_amount >= 90 and nodes_amount < 110:
        node_r = 4
    elif nodes_amount >= 110 and nodes_amount < 140:
        node_r = 3
    elif nodes_amount >= 140 and nodes_amount < 170:
        node_r = 2
    elif nodes_amount >= 170:
        node_r = 1
    else:
        node_r = 6

    # Graph edges
    for e in org_edges:
        source_name = org_nodes[e['source']]['name']
        target_name = org_nodes[e['target']]['name']

        if source_name in node_index and target_name in node_index:
            source_id = node_index[source_name]
            target_id = node_index[target_name]
            line_color = None

            # line from red node to yellow node.
            if node[source_id]['color']  == 'red' and node[target_id]['color']  == 'yellow' \
                or node[source_id]['color']  == 'yellow' and node[target_id]['color'] == 'red':
                line_color = 'red'
            # line from red node to blue node.
            elif node[source_id]['color']  == 'red' and node[target_id]['color'] == 'blue' \
                or node[source_id]['color']  == 'blue' and node[target_id]['color'] == 'red':
                line_color = 'deepSkyBlue'
            # line from yellow node to blue node.
            elif node[source_id]['color']  == 'yellow' and node[target_id]['color'] == 'blue' \
                or node[source_id]['color']  == 'blue' and node[target_id]['color'] == 'yellow':
                line_color = 'yellow'
            else:
                line_color = 'white'

            edge.append({'source' :  node_index[source_name], 'target' :  node_index[target_name], 'color': line_color})
        
    return node, edge, node_r

# set nodes position without check nodes overlap
def node_position_intersect(node, centroid, except_pos, node_r):
    xc = 275
    yc = 275
    node_size = 10
    circle_coordinates = {
        'circle1':{'x1':225,'x2':325,'y1':225,'y2':325,'r':50},
        'circle2':{'x1':125,'x2':425,'y1':125,'y2':425,'r':150},
        'circle3':{'x1':75,'x2':475,'y1':75,'y2':475,'r':200},
        'circle4':{'x1':0,'x2':550,'y1':0,'y2':550,'r':275},
    }
    color = {
        'red':'rgba(247, 32, 32, 1)',
        'yellow':'rgba(172, 247, 32)',
        'blue':'rgba(2, 69, 255)'
    }
    node_pos = except_pos

    for n in node:
        x = None
        y = None
      
        # circle 1 (inside) centroid fixed
        if n['name'] == centroid:
            if n['color'] == 'red':
                n['rgba'] = color['red']
            elif n['color'] == 'yellow':
                n['rgba'] = color['yellow']
            else:
                n['rgba'] = color['blue']

            x = xc
            y = yc

        # circle 2
        elif n['color'] == 'red':
            n['rgba'] = color['red']
            x1 = circle_coordinates['circle2']['x1']
            x2 = circle_coordinates['circle2']['x2']
            y1 = circle_coordinates['circle2']['y1']
            y2 = circle_coordinates['circle2']['y2']

            while True:
                while True:
                    x = random.randint(x1,x2) 
                    y = random.randint(y1,y2)
                    d = math.sqrt((x - xc)**2  + (y - yc)**2)

                    # if point outside circle1
                    if d-node_size > circle_coordinates['circle1']['r']:
                        break
              
                d = math.sqrt((x - xc)**2  + (y - yc)**2)
                # if point inside circle2
                if d + node_size < circle_coordinates['circle2']['r']:
                    # check node intersect
                    intersect = False
                    for c2 in node_pos:
                        c1c2 = math.sqrt((x - c2['x'])**2 + (y- c2['y'])**2)
                        interval = node_r * 2 * 2 + 3 # 2 node size(radius * 2) + interval between nodes
                        if c1c2 < interval: # 20 = r1+r2
                            intersect = True
                    if not intersect:
                    #if True:
                        node_pos.append({'x':x, 'y':y})
                        break
        # circle 3
        elif n['color'] == 'yellow':
            n['rgba'] = color['yellow']
            x1 = circle_coordinates['circle3']['x1']
            x2 = circle_coordinates['circle3']['x2']
            y1 = circle_coordinates['circle3']['y1']
            y2 = circle_coordinates['circle3']['y2']

            while True:
                while True:
                    x = random.randint(x1,x2) 
                    y = random.randint(y1,y2)
                    d = math.sqrt((x - xc)**2  + (y - yc)**2)

                    # if point outside circle2
                    if d-node_size > circle_coordinates['circle2']['r']:
                        break
              
                d = math.sqrt((x - xc)**2  + (y - yc)**2)
                # if point inside circle3
                if d + node_size < circle_coordinates['circle3']['r']:
                     # check node intersect
                    intersect = False
                    for c2 in node_pos:
                        c1c2 = math.sqrt((x - c2['x'])**2 + (y- c2['y'])**2)
                        interval = node_r * 2 * 2 + 3 # 2 node size(radius * 2) + interval between nodes
                        if c1c2 < interval: # 20 = r1+r2
                            intersect = True
                    if not intersect:
                    #if True:
                        node_pos.append({'x':x, 'y':y})
                        break

         # circle 4 (outside)
        elif n['color'] == 'blue':
            n['rgba'] = color['blue']
            x1 = circle_coordinates['circle4']['x1']
            x2 = circle_coordinates['circle4']['x2']
            y1 = circle_coordinates['circle4']['y1']
            y2 = circle_coordinates['circle4']['y2']

            while True:
                while True:
                    x = random.randint(x1,x2) 
                    y = random.randint(y1,y2)
                    d = math.sqrt((x - xc)**2  + (y - yc)**2)

                    # if point outside circle3
                    if d-node_size > circle_coordinates['circle3']['r']:
                        break
              
                d = math.sqrt((x - xc)**2  + (y - yc)**2)
                # if point inside circle4
                if d + node_size*2 < circle_coordinates['circle4']['r']:
                     # check node intersect
                    intersect = False
                    for c2 in node_pos:
                        c1c2 = math.sqrt((x - c2['x'])**2 + (y- c2['y'])**2)
                        interval = node_r * 2 * 2 + 3 # 2 node size(radius * 2) + interval between nodes
                        if c1c2 < interval: # 20 = r1+r2
                            intersect = True
                    if not intersect:
                    #if True:
                        node_pos.append({'x':x, 'y':y})
                        break
        n['x'] = x
        n['y'] = y
        n['fixed'] = True

    return node

# display direct connected nodes
def get_direct_connected_nodes(selectednode, nodes, edges):
    direct_nodes = []
    direct_edges = []
    node_index = dict()
    node_id = 0

    for e in edges:
        if nodes[e['source']]['name'] == selectednode or nodes[e['target']]['name'] == selectednode:
            if nodes[e['source']]['name'] not in node_index:
                direct_nodes.append(nodes[e['source']])
                node_index[nodes[e['source']]['name']] = node_id
                node_id += 1
            if nodes[e['target']]['name'] not in node_index:
                direct_nodes.append(nodes[e['target']])
                node_index[nodes[e['target']]['name']] = node_id
                node_id += 1

            line_color = None
            # line from red node to yellow node.
            if nodes[e['source']]['color']  == 'red' and nodes[e['target']]['color']  == 'yellow' \
                or nodes[e['source']]['color']  == 'yellow' and nodes[e['target']]['color'] == 'red':
                line_color = 'red'
            # line from red node to blue node.
            elif nodes[e['source']]['color']  == 'red' and nodes[e['target']]['color'] == 'blue' \
                or nodes[e['source']]['color']  == 'blue' and nodes[e['target']]['color'] == 'red':
                line_color = 'deepSkyBlue'
            # line from yellow node to blue node.
            elif nodes[e['source']]['color']  == 'yellow' and nodes[e['target']]['color'] == 'blue' \
                or nodes[e['source']]['color']  == 'blue' and nodes[e['target']]['color'] == 'yellow':
                line_color = 'yellow'
            else:
                line_color = 'white'


            direct_edges.append({'source' :  node_index[nodes[e['source']]['name']], 'target' :  node_index[nodes[e['target']]['name']], 'color': line_color})

    return direct_nodes, direct_edges

# get closest nodes to select node
def get_closest_nodes(selectnode, existnodes):
    
    closestnodes = dict()
    lenght, path = nx.single_source_dijkstra(G, selectnode, weight='cost')
    except_nodes = []

    for en in existnodes:
        except_nodes.append(en['name'])

    limit = 10
    for n in lenght:
        if n not in except_nodes:
            distance = float(format(lenght[n] , '.2f'))
            closestnodes[n] = [distance, G.node[n]['tag']]
            if len(closestnodes) == 10:
                break
    
    return closestnodes

# symptoms frequencies
def get_node_occur(keywords, centroid):
    symptoms = dict()
    for k in keywords:
        symptoms[k] = [G.node[k]['occur'], float(format(get2node_path(k, centroid)[1], '.2f'))]

    return symptoms

# get graph info
def graph_info():
    graph_info = dict()
    graph_info['nodes'] = len(G)
    graph_info['edges'] = G.number_of_edges()
    nodes_type = dict()
    for n in G.nodes:
        if G.node[n]['tag'] in nodes_type:
            nodes_type[G.node[n]['tag']] += 1
        else:
            nodes_type[G.node[n]['tag']] = 1
    
    return graph_info, nodes_type

def get_graph_file():
    graph_file = dict()
    server_path = '/var/www/webroot/ROOT/graph/*.gpickle'
    local_path = "graph/*.gpickle"
    for file in glob.glob(server_path):
        filename = os.path.basename(file)
        file = file.replace('\\', '/')
        graph_file[filename] = file
    if not graph_file:
        for file in glob.glob(local_path):
            filename = os.path.basename(file)
            file = file.replace('\\', '/')
            graph_file[filename] = file

    return graph_file

def set_graph_location(gpath):
    global G
    print(G)
    print(gpath)
    G = nx.read_gpickle(gpath)
    print(nx.info(G))
    graphname = os.path.basename(gpath)
    return graphname

def clear_graph():
    global G
    G = None

import pretextprocess as pt
import creategraph as cg

def create_document_graph(inputdoc, graphname, tag):
    outputfilepath = 'pretext/'+graphname
    pt.import_pdf_file(inputdoc, outputfilepath, tag)
    cg.create_graph(outputfilepath+'/', 'graph/'+graphname+'.gpickle')
    new_graph = 'graph/'+graphname+'.gpickle'
    return new_graph

def _encode_type(file):

    rawdata = open(file, 'rb').read()
    FileCode = chardet.detect(rawdata)

    return FileCode['encoding']

def add_document_graph(graph_path, new_graph_name, file):
    word_count = dict()
    word_tag = dict()
    link_count = dict()
    link_dict = dict()
    G = nx.read_gpickle(graph_path)
    for n in G.nodes:
        node_attribute = G.node[n]
        count = node_attribute['occur']
        tag = node_attribute['tag']
        word_count[n] = count
        word_tag[n] = tag
    
    for link in G.edges:
        link_sort = sorted(link)
        link_key = link_sort[0] + "|" + link_sort[1]
        count = G.edges[link]['count']
        link_count[link_key] = count

    file_text = file.readlines()
    for line in file_text:
        word_list = line.decode('utf-8').split()
        for w in word_list:
            word, tag = w.split('|')
            if word in word_count:
                word_count[word] += 1
            else:
                word_count[word] = 1
                word_tag[word] = tag
        
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
    new_graph_path = graph_path
    if new_graph_name:
        new_graph_path = 'graph/'+new_graph_name+'.gpickle'
    _write_graph_to_gpickle_format(new_graph_path, word_count, word_tag, link_count, link_dict, link_cost)
    return new_graph_path
            

