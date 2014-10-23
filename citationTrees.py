import api_utilities
import networkx as nx
import matplotlib.pyplot as plt


def make_group_tree(identifier,idtype='doi',level=0,maxlevel=2):
    '''Returns a networkX graph based on papers available in the database.

    Give a doi, or a uri if the keyword argument idtype = 'uri'

    Example:
    -------
    import citationTrees
    import api_utilities
    import networkx as nx
    import matplotlib.pyplot as plt
    
    doi = api_utilities.randdoi()
    G =  citationTrees.make_group_tree(doi)  # Use this script to make the network
    pos=nx.spring_layout(G)
    nx.draw(G,pos,node_color=[G.node[node]['color'] for node in G]) # Draw the map; colors are included as node property
    labels = {}
    for node in G:
        if G.node[node]['color']=='red':
            labels[node] = ''
        else:
            labels[node] = G.node[node]['label']
    nx.draw_networkx_labels(G, pos, labels)
    plt.show()  # Need to run if not using interactive matplotlib
    '''

    G = nx.Graph()

    if idtype=='doi':
        if not api_utilities.in_database(identifier):
            return G #no more to add to graph
        else:
            d =  api_utilities.citations(identifier)

    else:
        if not api_utilities.in_database_from_uri(identifier):
            return G #no more to add to graph
        else:
            d = api_utilities.citations_from_uri(identifier)

    # Add root node
    try:
        label = d['bibliographic']['title'][0:10]
    except KeyError:
        label = 'no title'

    G.add_node(d['uri'],color='blue',label=label)

    # Check for citations
    try:
        d['citation_groups']
    except KeyError:
        return G 

    # Add branches
    for grp in d['citation_groups']:
        G.add_node((d['uri'], grp['id']),text_before=grp['context']['text_before'],text_after=grp['context']['text_after'],color='red')
        G.add_edge(d['uri'],(d['uri'], grp['id']),label=grp['id'])

    for ref in d['references']:
        try:
            label = ref['bibliographic']['title'][0:10]
        except KeyError:
            label = 'no title'

        G.add_node(ref['uri'],color='blue',label=label)
        for i in ref['citation_groups']:
            G.add_edge((d['uri'],i),ref['uri'])
     
    # Add second level when reference is cited 2 or more times
    if level!=maxlevel:
        for ref in d['references']:
            if len(ref['citation_groups']) >= 2:
                uri = ref['uri']
                newG = make_group_tree(uri,idtype='uri',level=level+1,maxlevel=maxlevel)
                G=nx.compose(G,newG)
        
    return G
