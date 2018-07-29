import pandas as pd
import pickle
import networkx as nx
import random
import numpy as np

def connect(age):
    if (age == '0歲' or age == '1歲' or age == '2歲' or age == '3歲' or \
       age == '4歲' or age == '5歲-9歲' or age == '65歲-69-歲' or \
       age =='70歲以上' ):
        return False
    else:
        return True


def population_filter(area):
    population = pd.read_csv('./file_188Ｗ.csv', engine='python', encoding='utf8', delimiter=',')
    
    population.columns = ['index', 'sex', 'total_area', 'age']
    population.set_index('index', inplace=True)
    population['first_area'] = population['total_area'].str.rpartition('-')[0]
    population['second_area'] = population['total_area'].str.rpartition('-')[2]
    
    return (population[ population['first_area']==area])

def create_graph(population, lining_list, lining_neighbor):
    population = population.reset_index(drop=True)
    G = nx.Graph()
    G.add_nodes_from(lining_list, ill_mos = 0, health_mos = 0)
    for index, row in population.iterrows():
        G.add_node(str(index), status = 'S', delay = random.randint(4,8))
        G.add_edge(str(index), row['second_area'])
        if connect(row['age']):
            if random.random() > 0.7:
                source_area = row['second_area']
                neighbor = lining_neighbor[source_area]
                G.add_edge(str(index), random.choice(neighbor))
    return G
    #print (G.number_of_edges())
    #print (list(G.neighbors('1')))
    #print (G.nodes['1'])
    #print (G.nodes['嘉芳里'])

def create_mos(lining_list):
    mos_dict = dict()
    mos_count = pd.read_csv('./mos_data.csv', encoding='utf8')
    #print (mos_count)
    for lining in lining_list:
        mos_count[lining] = mos_count[lining].replace(0,np.nan)
        mos_sum = mos_count[lining].sum()
        mos_unique = mos_count[lining].count()
        avg = mos_sum / mos_unique
        mos_count[lining] = mos_count[lining].fillna(avg)
        tmp_dict = dict()
        for index, row in mos_count[lining].iteritems():
            if index >= 0 and index <= 213:
                tmp_dict[index] = row
        mos_dict[lining] = tmp_dict    
    return mos_dict

        

if __name__ == '__main__':
    #population = population_filter('新營區')
    #create_graph(pickle.load(open('./population.pkl','rb')), \
    #             pickle.load(open('./lining_list.pkl','rb')), \
    #             pickle.load(open('./lining_neighbor.pkl','rb')))
    mos_dict = create_mos(pickle.load(open('./lining_list.pkl','rb')))
    #print (mos_dict['力行里'])
