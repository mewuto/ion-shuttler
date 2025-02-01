import pytest
import networkx as nx

from graph_basics import GraphCreator
from graph_utils import (
    get_edge_from_site,
    get_sites_from_edge,
    get_ion_chains,
    get_idx_from_idc,
    get_idc_from_idx,
    create_idc_dictionary,
    move_ion,
    rollback_graph,
)


@pytest.mark.parametrize(
    "G, expected_dict",
    [
        # 3311
        (
            GraphCreator(3, 3, 1, 1).get_graph(),
            {
                0: ((0, 0), (1, 0)),
                1: ((0, 0), (0, 1)),
                2: ((0, 1), (1, 1)),
                3: ((0, 1), (0, 2)),
                4: ((0, 2), (1, 2)),
                5: ((1, 0), (2, 0)),
                6: ((1, 0), (1, 1)),
                7: ((1, 1), (2, 1)),
                8: ((1, 1), (1, 2)),
                9: ((1, 2), (2, 2)),
                10: ((2, 0), (2, 1)),
                11: ((2, 0), (3, 3.0)),
                12: ((2, 1), (2, 2)),
                13: ((2, 2), (3, 3.0)),
                14: ((3, 3.0), (4, 3)),
            },
        ),
    ],
)
def test_create_idc_dictionary(
    G: nx.Graph,
    expected_dict: dict[int, tuple[tuple[int, int], tuple[int, int]]],
):
    """
    Test for `create_idc_dictionary` function with multiple graphs.
    """
    got = create_idc_dictionary(G)
    assert len(G.edges) == len(got)
    assert got == expected_dict


@pytest.mark.parametrize(
    "graph_fixture, idc, expected_idx",
    [
        # 3311
        ("graph3311", ((0, 0), (1, 0)), 0),
        ("graph3311", ((3, 3.0), (4, 3)), 14),
    ],
)
def test_get_idx_from_idc(
    graph_fixture,
    idc: tuple[tuple[int, int], tuple[int, int]],
    expected_idx: int,
    request,
):
    """
    Test for `get_idx_from_idc` function.
    """
    graph_creator: GraphCreator = request.getfixturevalue(graph_fixture)
    G = graph_creator.get_graph()
    assert get_idx_from_idc(G.idc_dict, idc) == expected_idx


@pytest.mark.parametrize(
    "graph_fixture, idx, expected_idc",
    [
        # 3311
        ("graph3311", 0, ((0, 0), (1, 0))),
        ("graph3311", 14, ((3, 3.0), (4, 3))),
    ],
)
def test_get_idc_from_idx(
    graph_fixture,
    idx: int,
    expected_idc: tuple[tuple[int, int], tuple[int, int]],
    request,
):
    """
    Test for `get_idc_from_idx` function.
    """
    graph_creator: GraphCreator = request.getfixturevalue(graph_fixture)
    G = graph_creator.get_graph()
    assert get_idc_from_idx(G.idc_dict, idx) == expected_idc


@pytest.mark.parametrize(
    "graph_fixture, expected_ion_chains",
    [
        # 3311
        ("graph3311", {0: ((0, 0), (0, 1)), 1: ((0, 1), (1, 1))}),
    ],
)
def test_get_ion_chains(
    graph_fixture,
    expected_ion_chains: dict[int, tuple[tuple[int, int], tuple[int, int]]],
    request,
):
    """
    Test for `get_ion_chains` function with multiple graphs.
    """
    graph_creator: GraphCreator = request.getfixturevalue(graph_fixture)
    G = graph_creator.get_graph()
    got = get_ion_chains(G)
    assert len(got) == 2
    assert got == expected_ion_chains


@pytest.mark.parametrize(
    "graph_fixture, site, expected_edge",
    [
        # 3311
        ("graph3311", ((0, 0), (0, 1)), ((0, 0), (0, 1))),
        # 3322
        ("graph3322", ((0, 0), (0, 1)), ((0, 0), (0, 2))),
        ("graph3322", ((0, 0), (1, 0)), ((0, 0), (2, 0))),
        ("graph3322", ((1, 0), (2, 0)), ((0, 0), (2, 0))),
        ("graph3322", ((0, 1), (0, 2)), ((0, 0), (0, 2))),
        # 2233
        ("graph2233", ((1, 0), (2, 0)), ((0, 0), (3, 0))),
        ("graph2233", ((3, 1), (3, 2)), ((3, 0), (3, 3))),
    ],
)
def test_get_edge_from_site(
    graph_fixture,
    site: tuple[tuple[int, int], tuple[int, int]],
    expected_edge: tuple[tuple[int, int], tuple[int, int]],
    request,
):
    """
    Test for `get_edge_from_site` function with multiple graphs.
    """
    graph_creator: GraphCreator = request.getfixturevalue(graph_fixture)
    G = graph_creator.get_graph()
    got = get_edge_from_site(
        G,
        site,
        graph_creator.ion_chain_size_vertical,
        graph_creator.ion_chain_size_horizontal,
    )
    assert got == expected_edge


@pytest.mark.parametrize(
    "graph_fixture, edge, expected_sites",
    [
        # 3311
        ("graph3311", ((0, 0), (1, 0)), [((0, 0), (1, 0))]),
        ("graph3311", ((1, 0), (1, 1)), [((1, 0), (1, 1))]),
        # 3322
        ("graph3322", ((0, 0), (0, 2)), [((0, 0), (0, 1)), ((0, 1), (0, 2))]),
        ("graph3322", ((0, 0), (2, 0)), [((0, 0), (1, 0)), ((1, 0), (2, 0))]),
    ],
)
def test_get_sites_from_edge(
    graph_fixture,
    edge: tuple[tuple[int, int], tuple[int, int]],
    expected_sites: tuple[tuple[int, int], tuple[int, int]],
    request,
):
    """
    Test for `get_sites_from_edge` function with multiple graphs.
    """
    graph_creator: GraphCreator = request.getfixturevalue(graph_fixture)
    G = graph_creator.get_graph()
    got = get_sites_from_edge(
        G,
        edge,
        graph_creator.ion_chain_size_vertical,
        graph_creator.ion_chain_size_horizontal,
    )
    assert got == expected_sites


@pytest.mark.parametrize(
    "graph_fixture, graph_fixture_rollback",
    [
        # 3311
        ("graph3311", "graph3311"),
        ("graph3311", "graph3311"),
    ],
)
def test_rollback_graph(graph_fixture, graph_fixture_rollback, request):
    """
    Test for `rollback_graph` function with multiple graphs.
    """
    graph_creator: GraphCreator = request.getfixturevalue(graph_fixture)
    G = graph_creator.get_graph()
    move_ion(G, 0, ((0, 0), (0, 1)), ((0, 1), (0, 2)))
    move_ion(G, 1, ((0, 1), (1, 1)), ((1, 1), (1, 2)))

    graph_creator_rollback: GraphCreator = request.getfixturevalue(
        graph_fixture_rollback
    )
    G_rollback = graph_creator_rollback.get_graph()

    G = rollback_graph(G, G_rollback)

    # assert G == G_rollback
    print("edges", G.edges)
    assert G.edges == G_rollback.edges
    assert G.nodes == G_rollback.nodes
    assert G.idc_dict == G_rollback.idc_dict
    assert G.junction_nodes == G_rollback.junction_nodes
