import networkx as nx
import random
import matplotlib.pyplot as plt
from time import sleep


def ttc_algorithm(preferences_list: list):
    result_cycles_list = []

    while preferences_list != [[] for i in range(len(preferences_list))]:

        g = nx.DiGraph()

        for i in range(len(preferences_list)):
            if preferences_list[i]:
                g.add_node(i)

        for i in range(len(preferences_list)):
            if preferences_list[i]:
                g.add_edge(i, preferences_list[i][0])

        cycles = nx.simple_cycles(g)
        cycles_list = list(cycles)

        color_map_pre = ["deepskyblue" for pref in preferences_list]
        for cycle in cycles_list:
            for edge_num in cycle:
                color_map_pre[edge_num] = "yellow"

        color_map = [color_map_pre[i] for i in range(len(color_map_pre)) if preferences_list[i] != []]

        nx.draw_networkx(g, node_color=color_map)
        plt.show()

        print(cycles_list)
        result_cycles_list.append(cycles_list)
        for cycle in cycles_list:
            for edge_num in cycle:
                preferences_list[edge_num].clear()
                for pref in preferences_list:
                    if edge_num in pref:
                        pref.remove(edge_num)

    return result_cycles_list


if __name__ == "__main__":
    num_gifts = 30
    preferences = [random.sample(list(range(num_gifts)), num_gifts) for i in range(num_gifts)]
    print(preferences)
    print(ttc_algorithm(preferences_list=preferences))
