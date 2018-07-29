from util import *
import os
import pickle
import random
import queue
from copy import deepcopy
import json

class SIR_model():

    def __init__(self):
        self.population = self.loading_population()
        self.lining_neighbor, self.lining_list = self.loading_lining()
        self.G = self.loading_graph()
        self.mos = self.loading_mos()

    

    def loading_lining(self):
        if (os.path.isfile('./lining_list.pkl') and os.path.isfile('./lining_neighbor.pkl')):
            return pickle.load(open('./lining_neighbor.pkl','rb')), \
                   pickle.load(open('./lining_list.pkl','rb'))
        else:
            lining_neighbor = dict()
            with open('./neighbor.txt',encoding='utf8') as f:
                for line in f.readlines():
                    line = line.strip().split(',')
                    key = line[0].replace(u'\ufeff', '')
                    value = line[1:]
                    lining_neighbor[key] = value
            lining_list = list(lining_neighbor.keys())
            pickle.dump(lining_neighbor, open('./lining_neighbor.pkl','wb'))
            pickle.dump(lining_list, open('./lining_list.pkl','wb'))
            return lining_neighbor, lining_list                            
    def loading_population(self):
        if (os.path.isfile('./population.pkl')):
            return pickle.load(open('./population.pkl','rb'))
        else:
            population = population_filter('北區')
            pickle.dump(population, open('./population.pkl','wb'))
            return population
    def loading_graph(self):
        if (os.path.isfile('./graph.pkl')):
            return pickle.load(open('./graph.pkl','rb'))
        else:
            G = create_graph(self.population, self.lining_list, self.lining_neighbor)
            pickle.dump(G, open('./graph.pkl','wb'))
            return G
    def loading_mos(self):
        if (os.path.isfile('./mos.pkl')):
            return pickle.load(open('./mos.pkl','rb'))
        else:
        #mos_dict = dict()
        #for lining in self.lining_list:
        #    date_dict = dict()
        #    for i in range(365):
        #        date_dict[i] = random.randint(100,300)
        #    mos_dict[lining] = date_dict
            mos_dict = create_mos(self.lining_list)
            pickle.dump(mos_dict, open('./mos.pkl','wb'))
        return mos_dict

    
    def simulation(self):
        first_day_mos_rate = 0.1
        effect_rate = 0.6
        queue_dict = dict()
        for day in range(213):
            if day == 0:
                for lining in self.lining_list:
                    #mos_information_update
                    total_mos = int(self.mos[lining][day])
                    ill_mos = int(total_mos * first_day_mos_rate)
                    health_mos = total_mos - ill_mos
                    queue_tmp = queue.Queue()
                    queue_tmp.put(ill_mos)
                    self.G.nodes[lining]['health_mos'] = health_mos
                    self.G.nodes[lining]['ill_mos'] = ill_mos
                    queue_dict[lining] = queue_tmp
                    #mos_contact_update
                    neighbor = [x for x in self.G.neighbors(lining)]
                    effect_people = list()
                    for mor_index in range(ill_mos):
                        selection = random.choices(neighbor, k=3)
                        effect_people += selection
                    effect_people = list(set(effect_people))
                    for people in effect_people:
                        if random.random() < 0.6:
                            self.G.nodes[people]['status'] = 'E_1'
            else:
                #status update
                for node in self.G:
                    if node not in self.lining_list:
                        status_str = self.G.nodes[node]['status'].split('_')
                        status = status_str[0]                        
                        delay = self.G.nodes[node]['delay']
                        #E update
                        if status == 'E':
                            status_day = int(status_str[1])
                            if status_day == delay:
                                if random.random() < 0.4669:
                                    self.G.nodes[node]['status'] = 'I_1'
                                else:
                                    self.G.nodes[node]['status'] = 'R'
                            else:
                                self.G.nodes[node]['status'] = 'E_' + str(status_day+1)
                        elif status == 'I':
                            status_day = int(status_str[1])
                            if status_day == 7:
                                self.G.nodes[node]['status'] = 'R'
                            else:
                                self.G.nodes[node]['status'] = 'I_' + str(status_day+1)
                            
                for lining in self.lining_list:                    
                    #mos_information_update
                    total_mos = int(self.mos[lining][day])
                    ill_mos = self.G.nodes[lining]['ill_mos']
                    health_mos = total_mos - ill_mos
                    if day > 20:
                        ill_mos = ill_mos - queue_dict[lining].get()
                    #mos_contact_update
                    neighbor = [x for x in self.G.neighbors(lining)]
                    effect_people = list()
                    for mor_index in range(ill_mos):
                        selection = random.choices(neighbor, k=3)
                        effect_people += selection
                    effect_people = list(set(effect_people))
                    for people in effect_people:
                        if self.G.nodes[people]['status'] == 'S':
                            if random.random() < 0.6: 
                                self.G.nodes[people]['status'] = 'E_1'
                    #mos_ill_by_people
                    count = 0
                    for mor_index in range(health_mos):
                        selection = random.choices(neighbor, k=3)
                        for nei in neighbor:
                            if self.G.nodes[nei]['status'].split('_')[0] == 'I':
                                count +=1
                                break
                    #mos_information_update_after_contact
                    ill_mos += count
                    health_mos = total_mos - ill_mos
                    self.G.nodes[lining]['health_mos'] = health_mos
                    self.G.nodes[lining]['ill_mos'] = ill_mos                    
                    queue_dict[lining].put(count)
            E_count = 0
            I_count = 0
            R_count = 0
            S_count = 0
            for node in self.G:
                if node not in self.lining_list:
                    status_str = self.G.nodes[node]['status'].split('_')
                    status = status_str[0]
                    if status == 'E':
                        E_count +=1
                    elif status == 'I':
                        I_count +=1
                    elif status == 'R':
                        R_count +=1
                    elif status == 'S':
                        S_count +=1
            print ('Day:', day, ' S:', S_count, ' E:', E_count,' I:', I_count, ' R:', R_count)
                
                
                                
                                
                            
                
                    


if __name__ == '__main__':
    model = SIR_model()
    #print(json.dumps(model.mos,indent = 4))
    model.simulation()
            
