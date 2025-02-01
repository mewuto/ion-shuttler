from graph_basics import GraphCreator, create_starting_config
from graph_utils import create_idc_dictionary


def test_graph3311():
    graph_creator = GraphCreator(3, 3, 1, 1)

    assert graph_creator.entry == (2, 0)
    assert graph_creator.exit == (2, 2)
    assert graph_creator.processing_zone == (3, 3)
    assert graph_creator.parking_node == (4, 3)
    assert graph_creator.parking_edge == ((3, 3), (4, 3))
    assert graph_creator.exit_edge == ((2, 2), (3, 3))
    assert graph_creator.entry_edge == ((2, 0), (3, 3))
    assert graph_creator.path_to_pz == [((2, 2), (3, 3))]
    assert graph_creator.path_from_pz == [((3, 3), (2, 0))]

    G = graph_creator.get_graph()
    assert len(G.nodes) == 11
    assert len(G.edges) == 15

    G.idc_dict = create_idc_dictionary(G)
    assert len(G.edges) == len(G.idc_dict)

    n_of_chains = 4
    n_of_registers = create_starting_config(G, n_of_chains, seed=0)
    assert (
        n_of_chains == n_of_registers
    ), "Number of chains and number of registers do not match"

    print("Nodes in the graph:")
    assert G.nodes[(2, 2)].get("node_type") == "junction_node"
    assert G.nodes[(3, 3)].get("node_type") == "processing_zone_node"
    assert G.nodes[(4, 3)].get("node_type") == "parking_node"

    print("Edges in the graph:")
    assert G.edges[((2, 1), (2, 2))].get("edge_type") == "trap"
    assert G.edges[((2, 2), (3, 3))].get("edge_type") == "exit"
    assert G.edges[((3, 3), (4, 3))].get("edge_type") == "parking_edge"
