import networkx as nx
import random
import matplotlib.pyplot as plt
from time import sleep


def ttc_algorithm(preference_dict: dict):
    result_cycles_list = []

    while preference_dict != {}:

        g = nx.DiGraph()

        nodes_list = []
        for key in preference_dict:
            nodes_list.append(key)

        nodes_list.sort()

        for elem in nodes_list:
            g.add_node(elem)

        for key in preference_dict:
            g.add_edge(key, preference_dict[key][0])

        cycles = nx.simple_cycles(g)
        cycles_list = list(cycles)

        # color_map_pre = ["deepskyblue" for pref in preferences_list]
        # for cycle in cycles_list:
        #     for edge_num in cycle:
        #         color_map_pre[edge_num] = "yellow"

        # color_map = [color_map_pre[i] for i in range(len(color_map_pre)) if preferences_list[i] != []]

        # nx.draw_networkx(g, node_color=color_map)
        # plt.show()

        print(cycles_list)
        result_cycles_list.append(cycles_list)
        for cycle in cycles_list:
            for edge_num in cycle:
                preference_dict.pop(edge_num, None)
                for key in preference_dict:
                    if edge_num in preference_dict[key]:
                        preference_dict[key].remove(edge_num)

    return result_cycles_list


if __name__ == "__main__":
    num_gifts = 5
    preferences = {}
    for i in range(num_gifts):
        preferences[i] = random.sample(list(range(num_gifts)), num_gifts)
    print(preferences)
    print(ttc_algorithm(preference_dict=preferences))
