import networkx as nx
import matplotlib.pyplot as plt
import random

import pathData


def calculateDirectFlight(G, airport_one, airport_two, edgearray):
    for edge in edgearray:
        u, v, attrs = edge
        if (u == airport_one and v == airport_two) or (u == airport_two and v == airport_one):
            distance = attrs['dist']
    pd = pathData.pathData(airport_one, airport_two, distance, 0, G.nodes[airport_one]['pop'],
                           G.nodes[airport_two]['pop'])
    return distance, pd.getData("cost")


class Main:
    TotalEdgeDistance = 0
    TotalEdgeNumber = 0
    weighted_avg_sat =0
    nodeArray = [
        ('BOI', {'pop': int(476000)}),
        ('LAS', {'pop': int(2953000)}),
        ('DEN', {'pop': int(2963000)}),
        ('GRR', {'pop': int(195908)}),
        ('CMH', {'pop': int(915427)}),
        ('ATL', {'pop': int(6193000)}),
    ]
    edgeArray = [
        ('BOI', 'LAS', {'dist': int(520)}),
        ('BOI', 'DEN', {'dist': int(648)}),
        ('BOI', 'GRR', {'dist': int(1580)}),
        ('BOI', 'CMH', {'dist': int(1400)}),
        ('BOI', 'ATL', {'dist': int(1700)}),
        ('LAS', 'DEN', {'dist': int(628)}),
        ('LAS', 'GRR', {'dist': int(1560)}),
        ('LAS', 'CMH', {'dist': int(1540)}),
        ('LAS', 'ATL', {'dist': int(1745)}),
        ('DEN', 'GRR', {'dist': int(1045)}),
        ('DEN', 'CMH', {'dist': int(1150)}),
        ('DEN', 'ATL', {'dist': int(1200)}),
        ('GRR', 'CMH', {'dist': int(250)}),
        ('GRR', 'ATL', {'dist': int(650)}),
        ('CMH', 'ATL', {'dist': int(445)})
    ]
    pathDataArray = []

    def __init__(self):
        seed = random.randint(0, 2 ** 32 - 1)  # generate a random seed number
        random.seed(seed)#2383482255
        self.randomSeed = seed
        self.seed = seed
        self.TotalEdgeDistance = 0
        self.TotalEdgeNumber = 0
        self.pathDataArray = []
        self.G = nx.Graph()
        self.G.add_nodes_from(self.nodeArray)


        # Pick a random number of edges between 5 and 15
        num_edges = random.randint(5, 15)
        # Keep trying until we get a connected graph with the chosen number of edges
        while True:
            self.G.clear_edges()  # Clear any previous edges
            edgeArray_copy = self.edgeArray.copy()
            random.shuffle(edgeArray_copy)
            # Select the first num_edges from the shuffled array
            selected_edges = edgeArray_copy[:num_edges]

            # Add the selected edges to the graph
            for edge in selected_edges:
                u, v, attrs = edge
                self.G.add_edge(u, v, **attrs)
            # Check if the graph is connected
            if nx.is_connected(self.G):
                break

        self.TotalEdgeNumber = self.G.number_of_edges()
        self.TotalEdgeDistance = sum(attrs['dist'] for u, v, attrs in self.G.edges(data=True))

        pathTracker = []
        while len(pathTracker) < 15:
            while True:
                u = random.choice(self.nodeArray)
                v = random.choice(self.nodeArray)
                if u != v and (u, v) not in pathTracker and (v, u) not in pathTracker:
                    break
            pathTracker.append((u, v))
            paths = list(nx.all_simple_paths(self.G, u[0], v[0]))
            bestPath = None
            bestRatio = float('-inf')
            for path in paths:
                totalDistance = 0
                connectionCounter = 0
                for i in range(len(path) - 1):
                    nu = path[i]
                    nv = path[i + 1]
                    connectionCounter += 1
                    totalDistance = totalDistance + self.G.get_edge_data(nu, nv, 'dist')['dist']

                pd = pathData.pathData(u, v, totalDistance, connectionCounter - 1, u[1]['pop'], v[1]['pop'])
                directDist, directCost = calculateDirectFlight(self.G, u[0], v[0], self.edgeArray)
                pd.compareDirectFlight(directDist, directCost)
                pd.calculateSatisfaction()
                currentRatio = int(pd.getData("pathsatisfaction"))/int(pd.getData("cost"))
                if  currentRatio> bestRatio:
                    bestRatio = currentRatio
                    bestPath = pd
            self.pathDataArray.append(bestPath)

    def displayData(self):
    # print(*sorted(distanceTracker), sep ='\n')
        for (pd) in self.pathDataArray:
            pd.compareDirectFlight(*calculateDirectFlight(self.G, pd.AIRPORT_ONE[0], pd.AIRPORT_TWO[0], self.edgeArray))
            pd.printData()
        print("Total Edge Distance: ", self.TotalEdgeDistance)
        print("Total Edge Number: ", self.TotalEdgeNumber)
        print(f"Total Network Cost: ${sum(pd.getData('cost') for pd in self.pathDataArray):,.2f}")

        weights = [pd.getData("population") / pathData.pathData.NetworkPopulation for pd in self.pathDataArray]
        weighted_avg_sat = sum(pd.getData("pathsatisfaction") * w for pd, w in zip(self.pathDataArray, weights)) / sum(weights)
        print(f"Weighted Average Satisfaction: {weighted_avg_sat:.2f}")
        print("Random Seed: ", self.randomSeed)

    # display graph
    # print(G.nodes())
    # print(G.edges())
    def displayGraph(self):
        pos = nx.spring_layout(self.G, seed=1)
        nx.draw_networkx_edge_labels(
            self.G,
            pos,
            edge_labels=nx.get_edge_attributes(self.G, 'dist'),
            rotate=False,
            bbox=dict(boxstyle="round,pad=0.2", fc="green", alpha=0.7))

        nx.draw_networkx_nodes(
            self.G,
            pos,
            node_color="purple",
            node_size=800,
            alpha=1,
        )
        nx.draw_networkx_labels(
            self.G,
            pos,
            font_size=12,
            font_color="black",
            font_weight="bold"
        )
        nx.draw_networkx_edges(
            self.G,
            pos,
            edgelist=self.G.edges(),
            width=2,
            alpha=0.5,
            edge_color="blue",
            style="dashed"
        )
        plt.savefig("Graph.png")
    def returnWeightedSat(self):
        weights = [pd.getData("population") / pathData.pathData.NetworkPopulation for pd in self.pathDataArray]
        weighted_avg_sat = sum(pd.getData("pathsatisfaction") * w for pd, w in zip(self.pathDataArray, weights)) / sum(weights)
        return weighted_avg_sat
    def get_graph_fingerprint(self):
        """Return a hashable representation of the graph structure"""
        edges = tuple(sorted([tuple(sorted([u, v])) for u, v in self.G.edges()]))
        return edges

if __name__ == "__main__":
    main_instance = Main()
    main_instance.displayData()
    main_instance.displayGraph()

