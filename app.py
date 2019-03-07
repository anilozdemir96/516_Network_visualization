import pandas as pd
import numpy as np

pd.options.mode.chained_assignment = None

#institusions = ["Google", "Microsoft", "Akbank", "Garanti", "Yapi Kredi", "Unilever", "Turkcell", "Siemens", "Procter & Gamble", "Philip Morris", "Mercedes", "Coca Cola", "Bosch", "Boğaziçi Üniv", "Koç Üniv", "Tübitak", "Accenture", "(PwC)", "Deloitte", "Ford", "THY"]
institusions = [{'label': 'Google', 'value': 'Google'},
                {'label': 'Microsoft', 'value': 'Microsoft'},
                {'label': 'Akbank', 'value': 'Akbank'},
                {'label': 'Garanti', 'value': 'Garanti'},
                {'label': 'Yapi Kredi', 'value': 'Yapi Kredi'},
                {'label': 'Unilever', 'value': 'Unilever'},
                {'label': 'Turkcell', 'value': 'Turkcell'},
                {'label': 'Siemens', 'value': 'Siemens'},
                {'label': 'Procter & Gamble', 'value': 'Procter & Gamble'},
                {'label': 'Philip Morris', 'value': 'Philip Morris'},
                {'label': 'Mercedes', 'value': 'Mercedes'},
                {'label': 'Coca Cola', 'value': 'Coca Cola'},
                {'label': 'Bosch', 'value': 'Bosch'},
                {'label': 'Boğaziçi University', 'value': 'Boğaziçi Üniv'},
                {'label': 'Koç University', 'value': 'Koç Üniv'},
                {'label': 'Tübitak', 'value': 'Tübitak'},
                {'label': 'Accenture', 'value': 'Accenture'},
                {'label': '(PwC)', 'value': '(PwC)'},
                {'label': 'Deloitte', 'value': 'Deloitte'},
                {'label': 'Ford', 'value': 'Ford'},
                {'label': 'THY', 'value': 'THY'}]
#grad_years = [{'label': '2004', 'value': '2004'}, {'label': '2005', 'value': '2005'},
#              {'label': '2006', 'value': '2006'}, {'label': '2007', 'value': '2007'},
#              {'label': '2008', 'value': '2008'}, {'label': '2009', 'value': '2009'},
#              {'label': '2010', 'value': '2010'}, {'label': '2011', 'value': '2011'},
#              {'label': '2012', 'value': '2012'}, {'label': '2013', 'value': '2013'},
#              {'label': '2014', 'value': '2014'}, {'label': '2015', 'value': '2015'},
#              {'label': '2016', 'value': '2016'}, {'label': '2017', 'value': '2017'},
#              {'label': '2018', 'value': '2018'}]

df = pd.read_excel('Data/mezuniyet_sonrası_kariyer.xls', header=0)
graduation = pd.read_excel('Data/mezuniyet_derece_bilgileri.xls', header=0)
personal_df = pd.read_excel('Data/ogrencilik_donemi_kisisel_bilgiler.xls', header=0)

import json

import dash
import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objs as go

import networkx as nx

def create_network_data(edge):
    #create graph G
    G = nx.Graph()
    #G.add_nodes_from(node)
    G.add_edges_from(edge)
    #get a x,y position for each node
    pos = nx.layout.spring_layout(G)
    
    #add a pos attribute to each node
    for node in G.nodes:
        G.nodes[node]['pos'] = list(pos[node])
    
    ##from the docs, create a random geometric graph for test
    #G=nx.random_geometric_graph(200,0.125)
    pos=nx.get_node_attributes(G,'pos')
    
    
    dmin=1
    ncenter=0
    for n in pos:
        x,y=pos[n]
        d=(x-0.5)*2+(y-0.5)*2
        if d<dmin:
            ncenter=n
            dmin=d
    
    #Non-used line
    p=nx.single_source_shortest_path_length(G,ncenter)
    
    #Create Edges
    edge_trace = go.Scatter(
        x=[],
        y=[],
        line=dict(width=0.5,color='#888'),
        hoverinfo='text',
    	text=[],
        mode='lines')
    
    for edge in G.edges():
        x0, y0 = G.node[edge[0]]['pos']
        x1, y1 = G.node[edge[1]]['pos']
        edge_trace['x'] += tuple([x0, x1, None])
        edge_trace['y'] += tuple([y0, y1, None])
    
    node_trace = go.Scatter(
        x=[],
        y=[],
        text=[],
        mode='markers',
        hoverinfo='text',
        marker=dict(
            showscale=True,
            # colorscale options
            #'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
            #'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
            #'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
            colorscale='YlGnBu',
            reversescale=True,
            color=[],
            size=10,
            colorbar=dict(
                thickness=15,
                title='Node Connections',
                xanchor='left',
                titleside='right'
            ),  
            line=dict(width=2)))
    
    for node in G.nodes():
        x, y = G.node[node]['pos']
        node_trace['x'] += tuple([x])
        node_trace['y'] += tuple([y])
    
    #add color to node points
    for node, adjacencies in enumerate(G.adjacency()):
        node_trace['marker']['color']+=tuple([len(adjacencies[1])])
        node_info = 'ID: ' + str(adjacencies[0]) + '<br># of connections: '+str(len(adjacencies[1]))
        node_trace['text']+=tuple([node_info])
    
    return [edge_trace, node_trace]
################### START OF DASH APP ###################

app = dash.Dash()

# to add ability to use columns
app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
})

app.layout = html.Div([ 
                html.Div([
                    dcc.Graph(id='network_graph'),
                    html.Div([
                        dcc.Dropdown(
                                id='network_company',
                                options=institusions,
                                multi=False,
                                value="Microsoft"
                            )],
                        className='four columns'),
                    html.Div([
                        #dcc.Dropdown(
                        #        id='network_year',
                        #        options=grad_years,
                        #        multi=False,
                        #        value=["2004"]
                        #    )
                        dcc.RangeSlider(
                                id='network_year',
                                min=2004,
                                max=2018,
                                value=[2008, 2010],
                                marks={
                                    2004: {'label': '2004'},
                                    #2005: {'label': '2005'},
                                    2006: {'label': '2006'},
                                    #2007: {'label': '2007'},
                                    2008: {'label': '2008'},
                                    #2009: {'label': '2009'},
                                    2010: {'label': '2010'},
                                    #2011: {'label': '2011'},
                                    2012: {'label': '2012'},
                                    #2013: {'label': '2013'},
                                    2014: {'label': '2014'},
                                    #2015: {'label': '2015'},
                                    2016: {'label': '2016'},
                                    #2017: {'label': '2017'},
                                    2018: {'label': '2018'}
                                }
                            )
                        ],
                        className='four columns'),
                    html.Div([
                        dcc.Checklist(
                            id='filter_choice',
                            options=[
                                {'label': 'Grad. Year', 'value': 'GY'},
                                {'label': 'Program', 'value': 'PR'}
                                #,
                                #{'label': 'Lise', 'value': 'LS'}
                            ],
                            values=['GY'],
                            labelStyle={'display': 'inline-block'}
                        )
                        ],
                        className='three columns')
                    ],
                    className='eight columns'),
                    html.Div(children=[
                        html.H3('Personal Info'),
                        html.H5('Personal Id: -'),
                        html.H5('Birth Date: -'),
                        html.H5('Birthplace: -'),
                        html.H5('Prevschool: -'),
                        html.H5('Graduation Degree: -'),
                        html.H5('Graduation Program: -'),
                        html.H5('Graduation Year: -'),
                        html.H3('Institution Info'),
                        html.H5('Institution Name: -'),
                        html.H5('Institution Sector: -')],
                    className='three columns',
                    id='personal_info')
                ],
                    className='row')

@app.callback(
    dash.dependencies.Output('personal_info', 'children'),
    [dash.dependencies.Input('network_graph','clickData'),
     dash.dependencies.Input('network_company','value'),
     dash.dependencies.Input('network_year','value')])

def display_personal_data(click, company_name, years):
    #json.loads(json.dumps(click, indent=2))['points'][0]['text']
    in_text = json.loads(json.dumps(click, indent=2))
    if in_text != None:
        id_num = ''.join(list(filter(str.isdigit, in_text['points'][0]['text'][:-5])))
        
        info=personal_df[personal_df['PIDM'] == int(id_num)]
        
        birth=list(info['BIRTHDATE'])[0]
        bplace=list(info['BIRTHPLACE'])[0]
        prev_s=list(info['PREVSCHOOL'])[0]
        
        grad_year = graduation[graduation['PIDM'] == int(id_num)]['GRADYEAR'].iloc[0]
        grad_prog = graduation[graduation['PIDM'] == int(id_num)]['MAJORCODE'].iloc[0]
        grad_degree = graduation[graduation['PIDM'] == int(id_num)]['DEGREECODE'].iloc[0]
        
        employee_inst = df[df['INSTITUTION_NAME'].str.contains(company_name)]
        employee = employee_inst[employee_inst['PIDM'] == int(id_num)]
        
        institution = employee[employee.apply(lambda x: ((int(x['FROMDATE'][-2:]) <= int(str(years[0])[2:]) if pd.notnull(x['FROMDATE']) else False) & 
                                              (int(x['TODATE'][-2:]) >= int(str(years[1])[2:]) if pd.notnull(x['TODATE']) else True)) | 
                                                ((int(x['FROMDATE'][-2:]) >= int(str(years[0])[2:]) if pd.notnull(x['FROMDATE']) else False) & 
                                              (int(x['FROMDATE'][-2:]) <= int(str(years[1])[2:]) if pd.notnull(x['FROMDATE']) else False)), axis=1)]
        
        institution['FROMDATE'] = pd.to_datetime(institution.FROMDATE)
        institution = institution.sort_values(by='FROMDATE')
        
        inst_name = institution['INSTITUTION_NAME'].iloc[-1]
        
        #df[(df['PIDM'] == str(id_num) and df['FROMDATE'][-2:] >= str(years[0])[2:] and df['TODATE'][-2:] <= str(years[1])[2:])]['INSTITUTION_NAME']
       
        
        inst_sector = institution['INSTITUTION_SECTOR'].iloc[-1] #df[(df['PIDM'] == str(id_num) and df['FROMDATE'][-2:] >= str(years[0])[2:] and df['TODATE'][-2:] <= str(years[1])[2:])]['INSTITUTION_SECTOR']
            
        return [html.H3('Personal Info'),
                html.H5('Personal Id: ' + str(id_num)),
                html.H5('Birth Date: ' + str(birth)),
                html.H5('Birthplace: ' + str(bplace)),
                html.H5('Prevschool: ' + str(prev_s)),
                html.H5('Graduation Degree: ' + str(grad_degree)),
                html.H5('Graduation Program: ' + str(grad_prog)),
                html.H5('Graduation Year: ' + str(grad_year)),
                html.H3('Institution Info'),
                html.H5('Institution Name: ' + str(inst_name)),
                html.H5('Institution Sector: ' + str(inst_sector))]
    else:
        return [html.H3('Personal Info'),
                html.H5('Personal Id: -'),
                html.H5('Birth Date: -'),
                html.H5('Birthplace: -'),
                html.H5('Prevschool: -'),
                html.H5('Graduation Degree: -'),
                html.H5('Graduation Program: -'),
                html.H5('Graduation Year: -'),
                html.H3('Institution Info'),
                html.H5('Institution Name: -'),
                html.H5('Institution Sector: -')]
    

@app.callback(
    dash.dependencies.Output('network_graph', 'figure'),
    [dash.dependencies.Input('network_company','value'),
     dash.dependencies.Input('network_year','value'),
     dash.dependencies.Input('filter_choice','values')])

def display_selected_data(company_name, year, filter_choice):
    
    employees = df[df['INSTITUTION_NAME'].str.contains(company_name)]
    nodes = np.array(employees[employees.apply(lambda x: ((int(x['FROMDATE'][-2:]) <= int(str(year[0])[2:]) if pd.notnull(x['FROMDATE']) else False) & 
                  (int(x['TODATE'][-2:]) >= int(str(year[1])[2:]) if pd.notnull(x['TODATE']) else True)) | 
                    ((int(x['FROMDATE'][-2:]) >= int(str(year[0])[2:]) if pd.notnull(x['FROMDATE']) else False) & 
                  (int(x['FROMDATE'][-2:]) <= int(str(year[1])[2:]) if pd.notnull(x['FROMDATE']) else False)), axis=1)]["PIDM"])

    edges = []
    
    for i in range(0, len(nodes)):
        grad_year = graduation[graduation['PIDM'] == nodes[i]]['GRADYEAR'].iloc[0]
        grad_prog = graduation[graduation['PIDM'] == nodes[i]]['PROGRAMCODE'].iloc[0]
        
        edges.append(str(nodes[i])+","+str(nodes[i]))
        
        for j in range(i+1, len(nodes)):
            if i != j:
                grad_year_j = graduation[graduation['PIDM'] == nodes[j]]['GRADYEAR'].iloc[0]
                grad_prog_j = graduation[graduation['PIDM'] == nodes[j]]['PROGRAMCODE'].iloc[0]
                if grad_year == grad_year_j and 'GY' in filter_choice:
                    edges.append(str(nodes[i])+","+str(nodes[j]))
                    edges.append(str(nodes[j])+","+str(nodes[i]))
                if grad_prog == grad_prog_j and 'PR' in filter_choice:
                    edges.append(str(nodes[i])+","+str(nodes[j]))
                    edges.append(str(nodes[j])+","+str(nodes[i]))
                    
    edge_df = pd.DataFrame(edges, columns=["itemset"])
    edge_df['itemset'] = edge_df['itemset'].apply(lambda x: x.split(','))
    
    fig = go.Figure(data = create_network_data(edge_df["itemset"]),
                layout=go.Layout(
                titlefont=dict(size=16),
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20,l=5,r=5,t=40),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)))
    
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
