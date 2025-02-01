import networkx as nx
from itertools import pairwise


def get_shortest_path(
    G: nx.Graph, src: tuple[int, int], tar: tuple[int, int], ion_penalty: float = 10.0
) -> list[tuple[tuple[int, int], tuple[int, int]]]:
    """
    outbound edgeを避け、さらにイオンが存在するエッジにペナルティを付けて
    srcからtarまでの最短経路を計算する。

    Args:
        G (nx.Graph): グラフオブジェクト
        src (tuple[int, int]): 出発ノード
        tar (tuple[int, int]): 目的ノード
        ion_penalty (float): イオンが存在するエッジに加算する重みの倍率

    Returns:
        list[tuple[tuple[int, int], tuple[int, int]]]: 最短経路のエッジリスト
    """

    def edge_weight(u, v, edge_attr_dict):
        # outbound edge の重みを高くする
        weight = 1
        if edge_attr_dict["edge_type"] == "first_entry_connection":
            weight = 1e8

        # イオンが存在するエッジにペナルティを加算
        # if "ions" in edge_attr_dict and edge_attr_dict["ions"]:
        #     weight *= ion_penalty

        return weight

    # 最短経路を計算
    node_path = nx.shortest_path(G, src, tar, weight=edge_weight)
    return list(pairwise(node_path))


def find_path(
    G: nx.Graph,
    edge: list[tuple[int, int], tuple[int, int]],
    targetNode: tuple[int, int],
) -> list[list[tuple[int, int], tuple[int, int]]]:
    node1, node2 = edge[0], edge[1]
    path1 = get_shortest_path(G, node1, targetNode)
    path2 = get_shortest_path(G, node2, targetNode)

    # 長さが短い方を選択
    if len(path1) < len(path2):
        return path1
    else:
        return path2
