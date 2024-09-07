import backend as backend
from flask import Flask, render_template, url_for, request, jsonify, session, redirect
from flask_session import Session
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = 'd8ca72807d23a1ee51e2016cbb57f36c7e8e51555a25711a'
UPLOAD_FOLDER = 'upload/'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# session config
app.config['SESSION_TYPE'] = 'filesystem'
sess = Session()
sess.init_app(app)

@app.route('/', methods=['GET','POST'])
def index():
    if request.method == 'POST':
        
        if session.get('graph'):
            # check if keywords exist in graph
            input_keyword = request.form['symptoms'].split()
            symptoms = backend.check_keyword_exist(session.get('graph'), input_keyword)

            # calculate centroid and build graph
            if symptoms:
                # calculate centroid
                disease, centroid, path, sum_path = backend.disease_hop_activate(symptoms)
                print("calculate centroid --> done")

                # first 10 candidate
                n_disease = dict()
                for k in list(disease.keys())[:10]:
                    n_disease[k] = [disease[k], sum_path[k]]
                centroid = list(n_disease)[0]

                # generate d3 graph
                sp_path, allpath, pathcost = backend.centroid_shotest_path(n_disease, symptoms, centroid)
                node,  edge= backend.create_graph_sp(n_disease, sp_path, centroid, pathcost)
                print("create graph --> done")

                # get symptoms frequency
                symptoms = backend.get_node_occur(symptoms, centroid)
                
                # session variable
                session['allpath'] = allpath
                session['pathcost'] = pathcost
                session['node'] = node
                session['edge'] = edge
                session['nodes_radius'] = node
                session['edges_radius'] = edge
                session['nodes_current'] = node
                session['edges_current'] = edge
                session['centroid'] = centroid
                session['center_node'] = centroid
                session['symptoms_graph'] = False
                return render_template('index.html', symptoms = symptoms, diseases = n_disease, node = session['node'], edge=session['edge'])
            
            # keywords not exist in graph
            else:
                graph_info, nodes_type = backend.graph_info()
                graph_file = backend.get_graph_file()
                return render_template('index.html', graph_info = graph_info, nodes_type = nodes_type, graph_file=graph_file, graph_name= session['graph_name'], invalid_keywords = True)
        
        # input keywords to empty graph
        else:
            graph_file = backend.get_graph_file()
            return render_template('index.html', graph_file=graph_file, invalid_keywords = True)
    # homepage
    else:
        if session.get('graph'):
            #session.clear()
            print('--> graph running')
            session['graph_name'] = backend.set_graph_location(session['graph'])
            graph_info, nodes_type = backend.graph_info()
            graph_file = backend.get_graph_file()
            return render_template('index.html', graph_info = graph_info, nodes_type = nodes_type, graph_file=graph_file, graph_name= session['graph_name'] )
        else:
            print('--> graph empty')
            graph_file = backend.get_graph_file()
            return render_template('index.html',  graph_file=graph_file)

# send disease pdf
@app.route('/send_document', methods=['GET','POST'])
def send_document():
    over_node = request.form['over_node']
    document = backend.document_content(over_node, session['graph'])
    
    return jsonify({'read':document})

# disease graph with symptoms node
@app.route('/node_symptoms', methods=['GET','POST'])
def node_symptoms():
   
    get_node = request.form['node']
    graph_node, graph_edge =  backend.node_symptoms_graph(get_node)

    # session variable
    session['nodes_radius'] = graph_node
    session['edges_radius'] = graph_edge
    session['center_node'] = get_node
        # symptoms graph dataset
    session['symp_nodes'] = graph_node
    session['symp_edges'] = graph_edge
    session['symptoms_graph'] = True

    session['nodes_current'] = graph_node
    session['edges_current'] = graph_edge

    return jsonify({'nodes':graph_node, 'edges':graph_edge})

# send first centroid graph --> click on centroid btn
@app.route('/centroid_graph', methods=['GET','POST'])
def centroid_graph():
    
    session['symptoms_graph'] = False
    session['nodes_radius'] = session['node']
    session['edges_radius'] = session['edge']
    session['center_node'] = session['centroid']
    
    return jsonify({'nodes':session['node'], 'edges':session['edge']})

# adjust slider to display nodes within distance.
@app.route('/nodes_radius', methods=['GET','POST'])
def nodes_radius():
    slider_cost = int(request.form['cost'])
    expression = request.form['expression'] # plus or minus
    session['node_r'] = 6
    # adjust nodes of main graph
    if not session['symptoms_graph']:
        if expression == 'plus':
            nodes_radius, edges_radius, node_r = backend.nodes_in_distance(session['center_node'], session['node'], session['nodes_radius'], session['edges_radius'], slider_cost)
            session['nodes_radius'] = nodes_radius
            session['edges_radius'] = edges_radius
            session['nodes_current'] = nodes_radius
            session['edges_current'] = edges_radius
            session['node_r'] = node_r
            return jsonify({'nodes':session['nodes_radius'], 'edges':session['edges_radius'], 'node_r':session['node_r']})
        elif expression == 'minus':
            de_nodes_radius, de_edges_radius, node_r = backend.nodes_out_distance(session['center_node'], session['node'], session['nodes_radius'],  session['edges_radius'], slider_cost, session['node_r'])
            session['nodes_current'] = de_nodes_radius
            session['edges_current'] = de_edges_radius
            session['node_r'] = node_r
            return jsonify({'nodes':de_nodes_radius, 'edges':de_edges_radius, 'node_r':session['node_r']})

    # adjust nodes of symptoms graph // after move some node to center instead centroid
    else:
        if expression == 'plus':
            nodes_radius, edges_radius, node_r = backend.symptoms_in_distance(session['center_node'], session['symp_nodes'], session['nodes_radius'], session['edges_radius'], slider_cost)
            session['nodes_radius'] = nodes_radius
            session['edges_radius'] = edges_radius
            session['nodes_current'] = nodes_radius
            session['edges_current'] = edges_radius
            session['node_r'] = node_r
            return jsonify({'nodes':session['nodes_radius'], 'edges':session['edges_radius'], 'node_r':session['node_r']})
        elif expression == 'minus':
            de_nodes_radius, de_edges_radius, node_r = backend.symptoms_out_distance(session['center_node'], session['symp_nodes'], session['nodes_radius'], session['edges_radius'], slider_cost, session['node_r'])
            session['nodes_current'] = de_nodes_radius
            session['edges_current'] = de_edges_radius
            session['node_r'] = node_r
            return jsonify({'nodes':de_nodes_radius, 'edges':de_edges_radius, 'node_r':session['node_r']})
    
# display direct connected nodes in graph
@app.route('/direct_connected_nodes', methods=['GET','POST'])
def direct_connected_nodes():
   
    selectednode = request.form['selectednode']
    nodes_radius, edges_radius = backend.get_direct_connected_nodes(selectednode, session['nodes_radius'], session['edges_radius'])

    # session variable
    session['symptoms_graph'] = False
    session['nodes_radius'] = nodes_radius
    session['edges_radius'] =  edges_radius
    session['nodes_current'] = nodes_radius
    session['edges_current'] = edges_radius
    session['center_node'] = selectednode
    return jsonify({'nodes':nodes_radius, 'edges':edges_radius})

# get closest to select node for find more condition.    
@app.route('/more_relevant', methods=['GET','POST'])
def more_relevant():
    selectednode = request.form['selectednode']
    relevantnodes = backend.get_closest_nodes(selectednode, session['nodes_radius'])
    print("more relevant nodes --> done")
    return jsonify({'relevantnodes':relevantnodes})

# send first centroid graph --> click on centroid btn
@app.route('/current_graph', methods=['GET','POST'])
def current_graph():
    
    session['symptoms_graph'] = False
    session['nodes_radius'] = session['nodes_current']
    session['edges_radius'] = session['edges_current']
    session['center_node'] = session['centroid']
    
    return jsonify({'nodes':session['nodes_current'], 'edges':session['edges_current']})

@app.route('/select_graph', methods=['GET','POST'])
def select_graph():
    session['graph'] = request.form['gpath']
    return 'set graph --> done'

@app.route('/clear_graph', methods=['GET','POST'])
def clear_graph():
    session.clear()
    backend.clear_graph()
    return 'clear graph --> done'

@app.route('/create_graph', methods=['GET','POST'])
def create_graph():
    graph_name = request.form['inputgraphname']
    documents = request.files.getlist('inputdocuments')
    tag1 = request.form['tag1']
    tag1_file = request.files.getlist('tag_file1')
    tag2 = request.form['tag2']
    tag2_file = request.files.getlist('tag_file2')
    tag_dict = {tag1:tag1_file[0], tag2:tag2_file[0]}
    
    input_path = app.config['UPLOAD_FOLDER']+'/'+graph_name+'/documents'
    input_wordlist = app.config['UPLOAD_FOLDER']+'/'+graph_name+'/wordlist'
    try:
        os.mkdir(app.config['UPLOAD_FOLDER']+'/'+graph_name)
        os.mkdir(input_path)
        os.mkdir(input_wordlist)
    except:
        pass
    # unload document
    for f in documents:
        filename = secure_filename(os.path.basename(f.filename))
        f.save(os.path.join(input_path, filename))
    # upload wordlist
    listpath = dict()
    for t in tag_dict:
        filename = secure_filename(os.path.basename(tag_dict[t].filename))
        tag_dict[t].save(os.path.join(input_wordlist, filename))
        listpath[t] = input_wordlist+'/'+filename
    
    # pretext
    new_graph = backend.create_document_graph(input_path, graph_name, listpath)
    session['graph'] = new_graph
    return 'create graph done!'

@app.route('/graph/document/add', methods=['POST'])
def graph_document_add():
    graph_document = request.files['inputDocumentGraph']
    new_graph_name = request.form['newGraphName']
    if session['graph']:
        new_graph_name = backend.add_document_graph(session['graph'], new_graph_name, graph_document)
        session['graph'] = new_graph_name
        return 'success', 200
    else:
        return 'graph not found', 400

if __name__ == "__main__":
    app.run(host='0.0.0.0', port='80', debug=True)
    
