import networkx as nx
import math
import csv
import random as rand
import sys
import matplotlib.pyplot as plt
import tkinter
import os

_DEBUG_ = True


# This method reads the graph structure from the input file
def buildG(file_, delimiter_='auto'):
    G = nx.Graph()

    # construct the weighted version of the contact graph from cgraph.dat file
    if delimiter_ == 'auto':
        filename, file_extension = os.path.splitext(file_)
        if file_extension == '.in':
            delimiter_ = ','
        elif file_extension == '.txt':
            delimiter_ = ' '
        elif file_extension == '.gml':
            try:
                return nx.read_gml(file_)
            except:
                return nx.read_gml(file_, label='id')

    reader = csv.reader(open(file_), delimiter=delimiter_)
    for line in reader:
        if line[0] != line[1]:
            if len(line) > 2:
                if float(line[2]) != 0.0:
                    # line format: u,v,w
                    G.add_edge(int(line[0]), int(line[1]), weight=float(line[2]))
            else:
                # line format: u,v
                G.add_edge(int(line[0]), int(line[1]), weight=1.0)

    return G


# This method keeps removing edges from Graph until one of the connected components of Graph splits into two
# compute the edge betweenness
def CmtyGirvanNewmanStep(G):
    if _DEBUG_:
        print("Running CmtyGirvanNewmanStep method ...")
    init_ncomp = nx.number_connected_components(G)  # no of components
    ncomp = init_ncomp
    while ncomp <= init_ncomp and init_ncomp != len(nx.nodes(G)):
        bw = nx.edge_betweenness_centrality(G, weight='weight')  # edge betweenness for G
        # find the edge with max centrality
        if len(bw.values()) > 0:
            max_ = max(bw.values())
        else:
            max_ = 0.0
        # find the edge with the highest centrality and remove all of them if there is more than one!
        for k, v in bw.items():
            if float(v) == max_:
                G.remove_edge(k[0], k[1])  # remove the central edge
        ncomp = nx.number_connected_components(G)  # recalculate the no of components


# This method compute the modularity of current split
def _GirvanNewmanGetModularity(G, deg_, m_):
    New_A = nx.adjacency_matrix(G)
    New_deg = UpdateDeg(New_A, G.nodes())
    # Let's compute the Q
    comps = nx.connected_components(G)  # list of components
    print('No of communities in decomposed G: {}'.format(nx.number_connected_components(G)))
    Mod = 0  # Modularity of a given partitionning
    for c in comps:
        EWC = 0  # no of edges within a community
        RE = 0  # no of random edges
        for u in c:
            EWC += New_deg[u]
            RE += deg_[u]  # count the probability of a random edge
        Mod += (float(EWC) - float(RE * RE) / float(2 * m_))
    Mod = Mod / float(2 * m_)
    if _DEBUG_:
        print("Modularity: {}".format(Mod))
    return Mod


def UpdateDeg(A, nodes):
    deg_dict = {}
    n = len(nodes)  # len(A) ---> some ppl get issues when trying len() on sparse matrixes!
    B = A.sum(axis=1)
    i = 0
    for node_id in list(nodes):
        deg_dict[node_id] = B[i, 0]
        i += 1
    return deg_dict


# This method runs GirvanNewman algorithm and find the best community split by maximizing modularity measure
def runGirvanNewman(G, Orig_deg, m_):
    # let's find the best split of the graph
    BestQ = 0.0
    while True:
        CmtyGirvanNewmanStep(G)
        Q = _GirvanNewmanGetModularity(G, Orig_deg, m_);
        print("Modularity of decomposed G: {}".format(Q))
        if Q > BestQ:
            BestQ = Q
            Bestcomps = list(nx.connected_components(G))  # Best Split
            graph = G.copy()
            print("Identified components: {}".format(Bestcomps))
        if G.number_of_edges() == 0:
            break
    if BestQ > 0.0:
        print("Max modularity found (Q): {} and number of communities: {}".format(BestQ, len(Bestcomps)))
        print("Graph communities: {}".format(Bestcomps))
        return graph
    else:
        print("Max modularity (Q):", BestQ)


def plotGraph(G):
    plt.figure(figsize=(12, 8))

    nx.draw_networkx(G, with_labels=True)
    plt.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)
    plt.tick_params(axis='y', which='both', right=False, left=False, labelleft=False)
    for pos in ['right', 'top', 'bottom', 'left']:
        plt.gca().spines[pos].set_visible(False)

    plt.show()


def plotNetworkGraph(G, comps):
    communities = [1] * len(G)

    currentIndex = 1
    for comp in comps:
        for node in comp:
            communities[list(G.nodes).index(node)] = currentIndex
        currentIndex += 1

    pos = nx.spring_layout(G)  # compute graph layout

    plt.figure(figsize=(12, 8))  # image is 8 x 8 inches

    plt.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)
    plt.tick_params(axis='y', which='both', right=False, left=False, labelleft=False)

    nx.draw_networkx(G, pos, node_size=200, cmap=plt.cm.RdYlBu, node_color=communities, with_labels=True)

    for pos in ['right', 'top', 'bottom', 'left']:
        plt.gca().spines[pos].set_visible(False)

    plt.show()


def generateCustomTests():
    nx.write_gml(nx.barbell_graph(10, 4), 'barbell.gml')
    nx.write_gml(nx.frucht_graph(), 'frucht.gml')
    nx.write_gml(nx.lollipop_graph(12, 5), 'lollipop.gml')
    nx.write_gml(nx.ladder_graph(8), 'ladder.gml')
    nx.write_gml(nx.krackhardt_kite_graph(), 'krackhardt_kite.gml')
    nx.write_gml(nx.sedgewick_maze_graph(), 'sedgewick_maze.gml')


def main(argv):
    generateCustomTests()

    if len(argv) < 2:
        filepath = tkinter.filedialog.askopenfilename(
            filetypes=[("Geography Markup Language", ".gml"), ("Text files", ".txt"), ("Input files", ".in"),
                       ("All files", ".*")])
        if filepath == '':
            sys.stderr.write("Please select a '.in', '.txt' or '.gml' file")
            return -1
    else:
        filepath = argv[1]

    graph_fn = filepath
    G = buildG(graph_fn)

    originalG = G.copy()

    if _DEBUG_:
        print('G nodes: {} & G no of nodes: {}'.format(G.nodes(), G.number_of_nodes()))

    n = G.number_of_nodes()  # |V|
    A = nx.adjacency_matrix(G)  # adjacenct matrix

    m_ = 0.0  # the weighted version for number of edges
    for i in range(0, n):
        for j in range(0, n):
            m_ += A[i, j]
    m_ = m_ / 2.0
    if _DEBUG_:
        print("m: {}".format(m_))

    # calculate the weighted degree for each node
    Orig_deg = UpdateDeg(A, G.nodes())

    plotGraph(G)

    # run Newman alg
    newG = runGirvanNewman(G, Orig_deg, m_)

    plotNetworkGraph(originalG, list(nx.connected_components(newG)))
    plotGraph(newG)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
