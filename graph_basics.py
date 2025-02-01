import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import random


class GraphCreator:
    def __init__(
        self,
        m: int,
        n: int,
        ion_chain_size_vertical: int,
        ion_chain_size_horizontal: int,
    ):
        self.m = m
        self.n = n
        self.ion_chain_size_vertical = ion_chain_size_vertical
        self.ion_chain_size_horizontal = ion_chain_size_horizontal
        # エントリーやエグジットから PZ への接続に使用されるエッジの数
        self.num_connection_edges = self.n // 2

        self.networkx_graph: nx.Graph = self.create_graph()

    def create_graph(self) -> nx.Graph:
        self.m_extended = self.m + (self.ion_chain_size_vertical - 1) * (self.m - 1)
        self.n_extended = self.n + (self.ion_chain_size_horizontal - 1) * (self.n - 1)

        networkx_graph: nx.Graph = nx.grid_2d_graph(self.m_extended, self.n_extended)
        networkx_graph.junction_nodes: list[tuple[int, int]] = []

        self._set_trap_nodes(networkx_graph)
        self._remove_horizontal_edges(networkx_graph)
        self._remove_vertical_edges(networkx_graph)
        self._remove_horizontal_nodes(networkx_graph)
        self._set_junction_nodes(networkx_graph)
        nx.set_edge_attributes(networkx_graph, "trap", "edge_type")
        self._set_processing_zone(networkx_graph)

        return networkx_graph

    def _set_trap_nodes(self, networkx_graph: nx.Graph):
        for node in networkx_graph.nodes():
            networkx_graph.add_node(node, node_type="trap_node", color="b")

    def _remove_horizontal_edges(self, networkx_graph: nx.Graph):
        for i in range(
            0,
            self.m_extended - self.ion_chain_size_vertical,
            self.ion_chain_size_vertical,
        ):
            for k in range(1, self.ion_chain_size_vertical):
                for j in range(self.n_extended - 1):
                    networkx_graph.remove_edge((i + k, j), (i + k, j + 1))

    def _remove_vertical_edges(self, networkx_graph: nx.Graph):
        for i in range(
            0,
            self.n_extended - self.ion_chain_size_horizontal,
            self.ion_chain_size_horizontal,
        ):
            for k in range(1, self.ion_chain_size_horizontal):
                for j in range(self.m_extended - 1):
                    networkx_graph.remove_edge((j, i + k), (j + 1, i + k))

    def _remove_horizontal_nodes(self, networkx_graph: nx.Graph):
        for i in range(
            0,
            self.m_extended - self.ion_chain_size_vertical,
            self.ion_chain_size_vertical,
        ):
            for k in range(1, self.ion_chain_size_vertical):
                for j in range(
                    0,
                    self.n_extended - self.ion_chain_size_horizontal,
                    self.ion_chain_size_horizontal,
                ):
                    for s in range(1, self.ion_chain_size_horizontal):
                        networkx_graph.remove_node((i + k, j + s))

    def _remove_mid_part(self, networkx_graph: nx.Graph):
        for i in range(self.ion_chain_size_vertical):
            networkx_graph.remove_node((self.m_extended // 2, self.n_extended // 2 + i))
        for i in range(1, self.ion_chain_size_vertical):
            networkx_graph.remove_node((self.m_extended // 2, self.n_extended // 2 - i))
        for i in range(1, self.ion_chain_size_horizontal):
            networkx_graph.remove_node((self.m_extended // 2 + i, self.n_extended // 2))
        for i in range(1, self.ion_chain_size_horizontal):
            networkx_graph.remove_node((self.m_extended // 2 - i, self.n_extended // 2))

    def _set_junction_nodes(self, networkx_graph: nx.Graph):
        for i in range(0, self.m_extended, self.ion_chain_size_vertical):
            for j in range(0, self.n_extended, self.ion_chain_size_horizontal):
                networkx_graph.add_node((i, j), node_type="junction_node", color="g")
                networkx_graph.junction_nodes.append((i, j))

    def _set_processing_zone(self, networkx_graph: nx.Graph):
        # Define the key nodes
        self.exit = (self.m_extended - 1, self.n_extended - 1)
        # print("exit", self.exit)
        self.processing_zone = (
            self.m_extended + self.num_connection_edges - 1,
            self.n_extended + self.num_connection_edges - 1,
        )
        # print("processing_zone", self.processing_zone)
        self.entry = (self.m_extended - 1, 0)
        self.parking_node = (self.processing_zone[0] + 1, self.processing_zone[1])
        # print("parking_node", self.parking_node)
        self.parking_edge = (self.processing_zone, self.parking_node)
        # print("parking_edge", self.parking_edge)

        # differences
        dy_exit = self.exit[1] - self.processing_zone[1]
        dy_entry = self.processing_zone[1] - self.entry[1]

        self.path_to_pz = []
        self.path_from_pz = []

        # Add exit edges
        for i in range(self.num_connection_edges):
            exit_node = (
                self.exit[0] + (i + 1),
                self.exit[1] - (i + 1) * dy_exit / self.num_connection_edges,
            )

            if i == 0:
                networkx_graph.add_node(exit_node, node_type="exit_node", color="y")
                previous_exit_node = self.exit
                self.exit_edge = (previous_exit_node, exit_node)

            networkx_graph.add_node(
                exit_node, node_type="exit_connection_node", color="y"
            )
            networkx_graph.add_edge(
                previous_exit_node, exit_node, edge_type="exit", color="k"
            )
            self.path_to_pz.append((previous_exit_node, exit_node))
            previous_exit_node = exit_node

        # Add entry edges
        for i in range(self.num_connection_edges):
            entry_node = (
                self.entry[0] + (i + 1),
                self.entry[1] + (i + 1) * dy_entry / self.num_connection_edges,
            )

            if i == 0:
                networkx_graph.add_node(
                    entry_node, node_type="entry_node", color="orange"
                )
                previous_entry_node = self.entry
                self.entry_edge = (previous_entry_node, entry_node)

            networkx_graph.add_node(
                entry_node, node_type="entry_connection_node", color="orange"
            )
            # first entry connection is first edge after pz
            # entry is edge connected to memory grid, so last entry connection
            # if entry is one edge only -> first entry connection is the same as entry edge
            if entry_node == self.processing_zone:
                self.first_entry_connection_from_pz = (entry_node, previous_entry_node)
                networkx_graph.add_edge(
                    previous_entry_node,
                    entry_node,
                    edge_type="first_entry_connection",
                    color="k",
                )
            else:
                networkx_graph.add_edge(
                    previous_entry_node, entry_node, edge_type="entry", color="k"
                )
            self.path_from_pz.insert(0, (entry_node, previous_entry_node))

            previous_entry_node = entry_node

        assert exit_node == entry_node, "Exit and entry do not end in same node"
        assert (
            exit_node == self.processing_zone
        ), "Exit and entry do not end in processing zone"

        # Add the processing zone node
        networkx_graph.add_node(
            self.processing_zone, node_type="processing_zone_node", color="r"
        )

        # new parking edge
        networkx_graph.add_node(self.parking_node, node_type="parking_node", color="r")
        networkx_graph.add_edge(
            self.parking_edge[0],
            self.parking_edge[1],
            edge_type="parking_edge",
            color="g",
        )

    def get_graph(self):
        return self.networkx_graph


def create_starting_config(graph: nx.Graph, n_of_chains: int, seed=None):
    if seed is not None:
        random.seed(seed)
        starting_traps = []
        traps = [
            edges
            for edges in graph.edges()
            if graph.get_edge_data(edges[0], edges[1])["edge_type"] == "trap"
        ]
        n_of_traps = len(traps)
        random_starting_traps = random.sample(range(n_of_traps), (n_of_chains))
        for trap in random_starting_traps:
            starting_traps.append(traps[trap])
    else:
        starting_traps = [
            edges
            for edges in graph.edges()
            if graph.get_edge_data(edges[0], edges[1])["edge_type"] == "trap"
        ][:n_of_chains]
    number_of_registers = len(starting_traps)

    # place ions onto traps (ion0 on starting_trap0)
    for ion, idc in enumerate(starting_traps):
        graph.edges[idc]["ions"] = [ion]

    return number_of_registers


def update_distance_map(
    ion_chains: dict[int, tuple[tuple[int, int], tuple[int, int]]],
    dist_dict: dict[tuple[tuple[int, int], tuple[int, int]], int],
) -> dict[int, int]:
    """
    Create a distance map for each ion chain to the processing zone.

    Args:
    - ion_chains (dict): A dictionary where the key is the ion index and the value is the edge (as a tuple of nodes).
    - dist_dict (dict): A dictionary with edges as keys and their corresponding distances to the processing zone as values.

    Returns:
    - distance_map (dict): A dictionary where the key is the ion index and the value is the distance to the processing zone.
    """
    distance_map: dict[int, int] = {}
    for ion, edge_idc in ion_chains.items():
        distance_map[ion] = dist_dict[edge_idc]
    return distance_map
