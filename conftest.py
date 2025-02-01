import pytest
import networkx as nx
from graph_basics import GraphCreator
from graph_utils import create_idc_dictionary


@pytest.fixture
def graph3311():
    """
    テスト用のシンプルなグラフを返すフィクスチャ。
    """
    graph_creator = GraphCreator(3, 3, 1, 1)
    G = graph_creator.get_graph()
    G.idc_dict = create_idc_dictionary(G)
    nx.set_edge_attributes(G, {edge: [] for edge in G.edges}, "ions")

    G.edges[((0, 0), (0, 1))]["ions"] = [0]
    G.edges[((0, 1), (1, 1))]["ions"] = [1]

    return graph_creator


@pytest.fixture
def graph3322():
    """
    テスト用のシンプルなグラフを返すフィクスチャ。
    """
    graph_creator = GraphCreator(3, 3, 2, 2)
    G = graph_creator.get_graph()
    G.idc_dict = create_idc_dictionary(G)
    nx.set_edge_attributes(G, {edge: [] for edge in G.edges}, "ions")

    G.edges[((0, 1), (0, 2))]["ions"] = [0]
    G.edges[((0, 2), (1, 2))]["ions"] = [1]
    G.edges[((1, 2), (2, 2))]["ions"] = [2]
    G.edges[((2, 2), (3, 2))]["ions"] = [3]

    return graph_creator


@pytest.fixture
def graph2233():
    """
    テスト用のシンプルなグラフを返すフィクスチャ。
    """
    graph_creator = GraphCreator(2, 2, 3, 3)
    G = graph_creator.get_graph()
    G.idc_dict = create_idc_dictionary(G)
    nx.set_edge_attributes(G, {edge: [] for edge in G.edges}, "ions")

    return graph_creator


@pytest.fixture
def graph3333_sp():
    """
    テスト用のシンプルなグラフを返すフィクスチャ。
    """
    graph_creator = GraphCreator(3, 3, 3, 3)
    G = graph_creator.get_graph()
    G.idc_dict = create_idc_dictionary(G)
    nx.set_edge_attributes(G, {edge: [] for edge in G.edges}, "ions")

    G.edges[((0, 1), (0, 2))]["ions"] = [0]
    G.edges[((0, 2), (1, 2))]["ions"] = [1]
    G.edges[((1, 2), (2, 2))]["ions"] = [2]
    G.edges[((2, 2), (3, 2))]["ions"] = [3]

    return graph_creator
