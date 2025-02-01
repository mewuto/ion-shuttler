import networkx as nx
import copy


def sort_edge(
    edge: tuple[tuple[int, int], tuple[int, int]],
) -> tuple[tuple[int, int], tuple[int, int]]:
    """
    エッジをソートする関数。開始ノードと終了ノードを比較し、小さい方を前に持ってくる。
    """
    return tuple(sorted(edge))


# create dictionary to swap from idx to idc and vice versa
def create_idc_dictionary(
    nx_g: nx.Graph,
) -> dict[int, tuple[tuple[int, int], tuple[int, int]]]:
    """
    エッジのインデックスとエッジのIDCを対応させる辞書を生成する関数。

    :param nx_g: NetworkXのグラフオブジェクト。
    :return: エッジのインデックスをキー、エッジのIDCを値とする辞書。
    """
    edge_dict: dict[int, tuple[tuple[int, int], tuple[int, int]]] = {}
    for edge_idx, edge_idc in enumerate(nx_g.edges()):
        edge_dict[edge_idx] = tuple(sorted(edge_idc, key=sum))
    # print("create_idc_dict", edge_dict)
    return edge_dict


def create_dist_dict(
    G: nx.Graph,
    exit_node: tuple[int, int],
    processing_zone: tuple[int, int],
) -> dict[tuple[tuple[int, int], tuple[int, int]], int]:
    """
    Calculate and create a dictionary of distances from each edge to the processing zone.

    Args:
    - graph (networkx.Graph): The graph representing the memory grid.
    - idc_dict (dict): Dictionary mapping edge indices to edge identifiers.
    - graph_creator (GraphCreator): Object that contains the graph and its relevant attributes.

    Returns:
    - dist_dict (dict): Dictionary with edge indices as keys and distances to processing zone as values.
    """
    # G_without_parking = G.copy()
    # G_without_parking.remove_node(processing_zone)

    dist_dict: dict[tuple[tuple[int, int], tuple[int, int]], int] = {}
    for e in G.edges(data=True):
        edge = tuple([e[0], e[1]])
        # data = e[2]
        # if data["edge_type"] != "trap":
        #     dist_dict[edge] = 0
        #     continue

        path_length_from_node1 = nx.shortest_path_length(
            G,
            source=edge[0],
            target=processing_zone,
            weight=lambda _, __, edge_attr_dict: (
                edge_attr_dict["edge_type"] == "first_entry_connection"
            )
            * 1e8
            + 1,
        )
        # node_path = nx.shortest_path(
        #     nx_g,
        #     src,
        #     tar,
        #     lambda _, __, edge_attr_dict: (edge_attr_dict["edge_type"] == "first_entry_connection") * 1e8 + 1,
        # )
        path_length_from_node2 = nx.shortest_path_length(
            G,
            source=edge[1],
            target=processing_zone,
            weight=lambda _, __, edge_attr_dict: (
                edge_attr_dict["edge_type"] == "first_entry_connection"
            )
            * 1e8
            + 1,
        )
        distance_to_pz = min(path_length_from_node1, path_length_from_node2)

        dist_dict[edge] = distance_to_pz

    return dist_dict


def get_idx_from_idc(
    edge_dictionary: dict[int, tuple[tuple[int, int], tuple[int, int]]],
    idc: tuple[tuple[int, int], tuple[int, int]],
) -> int:
    """
    エッジのIDCからエッジのインデックスを取得する関数。

    :param edge_dictionary: エッジのインデックスとエッジのIDCを対応させる辞書。
    :param idc: エッジのIDC。
    :return: エッジのインデックス。
    """
    idc = tuple(sorted(idc, key=sum))
    return list(edge_dictionary.values()).index(idc)


def get_idc_from_idx(
    edge_dictionary: dict[int, tuple[tuple[int, int], tuple[int, int]]], idx: int
) -> tuple[tuple[int, int], tuple[int, int]]:
    """
    エッジのインデックスからエッジのIDCを取得する関数。

    :param edge_dictionary: エッジのインデックスとエッジのIDCを対応させる辞書。
    :param idx: エッジのインデックス。
    :return: エッジのIDC。
    """
    return edge_dictionary[idx]


def get_ion_chains(
    graph: nx.Graph,
) -> dict[int, tuple[tuple[int, int], tuple[int, int]]]:
    """
    グラフ内の各イオンが存在するエッジを示す辞書を生成する関数。

    :param graph: NetworkXのグラフオブジェクト。
    :return: イオンのインデックスをキー、エッジを値とする辞書。
    """
    ion_chains = {}
    sorted_ion_chains = {}

    # 各エッジを走査し、イオンが存在するエッジを辞書に追加
    for edge_start, edge_end, data in graph.edges(data=True):
        # print("get_ion_chains", (edge_start, edge_end), data)
        if "ions" in data:
            for ion in data["ions"]:
                ion_chains[ion] = (edge_start, edge_end)

    sorted_ion_chains = dict(sorted(ion_chains.items()))
    return sorted_ion_chains


def get_edge_from_site(
    G: nx.Graph,
    site: tuple[tuple[int, int], tuple[int, int]],
    vertical_size: int,
    horizontal_size: int,
) -> tuple[tuple[int, int], tuple[int, int]]:
    """
    与えられたサイトが属するエッジを返す関数。

    :param G: グラフオブジェクト
    :param site: サイト (tuple of two nodes)
    :param vertical_size: 縦方向のエッジのサイズ
    :param horizontal_size: 横方向のエッジのサイズ
    :return: サイトが属するエッジ (tuple of two nodes)
    """

    junction_nodes: list[tuple[int, int]] = G.junction_nodes

    node1, node2 = site

    if node1 in junction_nodes and node2 in junction_nodes:
        # siteが1のとき
        return site
    elif node1 in junction_nodes or node2 in junction_nodes:
        # a site touches a junciton
        if node1 in junction_nodes:
            # node1 is junction
            junction_node = node1
            other_node = node2
            yj, xj = junction_node
            yo, xo = other_node  # other node
            # yj == yo
            if xo < xj:
                return ((yj, xj - horizontal_size), junction_node)
            elif xj < xo:
                return (junction_node, (yj, xj + horizontal_size))
            # x1 == x2
            elif yo < yj:
                return ((yj - vertical_size, xj), junction_node)
            elif yj < yo:
                return (junction_node, (yj + vertical_size, xj))
            else:
                raise ValueError(f"Invalid site: {site}")
        else:
            # node2 is junction
            junction_node = node2
            other_node = node1
            yj, xj = junction_node
            yo, xo = other_node  # other node
            # yj == yo
            if xo < xj:
                return ((yj, xj - horizontal_size), junction_node)
            elif xj < xo:
                return (junction_node, (yj, xj + horizontal_size))
            # x1 == x2
            elif yo < yj:
                return ((yj - vertical_size, xj), junction_node)
            elif yj < yo:
                return (junction_node, (yj + vertical_size, xj))
            else:
                raise ValueError(f"Invalid site: {site}")
    else:
        # エッジの端点がジャンクションノードでない場合
        y1, x1 = node1
        y2, x2 = node2
        if x1 == x2:  # 縦方向のエッジ
            candidates = [
                (y, x1) for y in range(y1 - vertical_size, y1 + vertical_size + 1)
            ]
            junctions_in_range = [node for node in candidates if node in junction_nodes]
            assert len(junctions_in_range) == 2
            return tuple(junctions_in_range)
        elif y1 == y2:  # 横方向のエッジ
            candidates = [
                (y1, x) for x in range(x1 - horizontal_size, x1 + horizontal_size + 1)
            ]
            junctions_in_range = [node for node in candidates if node in junction_nodes]
            assert len(junctions_in_range) == 2
            return tuple(junctions_in_range)
        else:
            raise ValueError(f"Invalid site: {site}")


def get_sites_from_edge(
    G: nx.Graph,
    edge: tuple[tuple[int, int], tuple[int, int]],
    vertical_size: int,
    horizontal_size: int,
) -> list[tuple[tuple[int, int], tuple[int, int]]]:
    """
    エッジからそのエッジに含まれるサイトを取得する関数。

    :param G: グラフオブジェクト
    :param edge: エッジ (tuple of two nodes)
    :param vertical_size: 縦方向のエッジのサイズ
    :param horizontal_size: 横方向のエッジのサイズ
    :return: エッジに含まれるサイトのリスト [tuple of two nodes, tuple of two nodes, ...]
    """
    start_node, end_node = edge
    y1, x1 = start_node
    y2, x2 = end_node

    sites: list[tuple[tuple[int, int], tuple[int, int]]] = []

    if x1 == x2:  # 縦方向のエッジ
        y = min(y1, y2)
        for i in range(vertical_size):
            site = ((y + i, x1), (y + i + 1, x1))
            if site in G.edges:
                sites.append(site)
    elif y1 == y2:  # 横方向のエッジ
        x = min(x1, x2)
        for i in range(horizontal_size):
            site = ((y1, x + i), (y1, x + i + 1))
            if site in G.edges:
                sites.append(site)
    else:
        raise ValueError(f"無効なエッジ: {edge}")

    return sites


# Function to move an ion from one edge to another
def move_ion(
    G: nx.Graph,
    ion: int,
    current_edge: tuple[tuple[int, int], tuple[int, int]],
    new_edge: tuple[tuple[int, int], tuple[int, int]],
):
    if ion in G.edges[current_edge]["ions"]:
        G.edges[current_edge]["ions"].remove(ion)
        G.edges[new_edge]["ions"].append(ion)
    else:
        print(f"Ion {ion} not found on edge {current_edge}")


# Check the updated ion positions
# for edge in G.edges:
#     print(f"Edge {edge} has ions: {G.edges[edge]['ions']}")
# move_ion(G, 1, ((5, 6), (4, 6)), ((3, 6), (4, 6)))
# move_ion(G, 6, ((5, 6), (6, 6)), ((5, 6), (4, 6)))
# move_ion(G, 8, ((6, 4), (6, 5)), ((5, 6), (6, 6)))


def rollback_graph(G: nx.Graph, snapshot: nx.Graph):
    """
    グラフGをスナップショットの状態に復元する
    """
    G.clear()  # 現在のGをクリア
    G_copy = copy.deepcopy(G)

    # G.add_edges_from(snapshot.edges(data=True))  # エッジをスナップショットから復元
    # G.add_nodes_from(snapshot.nodes(data=True))  # ノードをスナップショットから復元
    return G_copy
