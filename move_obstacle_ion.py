import networkx as nx
import random
import copy
from graph_utils import (
    get_ion_chains,
    get_idx_from_idc,
    move_ion,
)
from find_path import get_shortest_path
from plot import plot_state


def move_as_push_obstacle_ions(
    G: nx.Graph,
    ion: int,
    next_edge: list[tuple[int, int], tuple[int, int]],
    used_junctions: dict[int, tuple[int, int]],
    show_plot_move: bool = False,
):
    """
    Only in Memory zone, (prior) ion push obstacle ions on next edge
    """
    prev_G = copy.deepcopy(G)
    prev_used_junctions = copy.deepcopy(used_junctions)

    ion_edge = get_ion_chains(G)[ion]
    common_node = set(ion_edge).intersection(set(next_edge))
    single_common_node = next(iter(common_node))

    # イオンは移動済みでなく、さらに、使用予定のジャンクションノードが未使用である場合、True
    if ion not in used_junctions and single_common_node not in used_junctions.values():
        used_junctions[ion] = single_common_node
        move_ion(G, ion, ion_edge, next_edge)
    else:
        return used_junctions, prev_G

    # イオンの移動(上)に伴って、1サイト内に2つのイオンが存在している場合があるため以下の処理を行う
    prev_edge = ion_edge
    prev_ion = ion
    current_edge = get_ion_chains(G)[prev_ion]
    # print("prev_edge", prev_edge)
    # print("prev_ion", prev_ion)
    # print("current_edge", current_edge)

    while len(G.edges[current_edge]["ions"]) > 1:
        # 隣のエッジを探し，prev_edgeではない方向に進む
        # 基本的にイオンがない方に進むが，進めない場合はイオンがあっても進み，current_edgeなどを更新する

        # 移動させるイオンの決定
        on_site_ions: list[int] = G.edges[current_edge]["ions"]
        moving_ion = next((x for x in on_site_ions if x != prev_ion), None)
        # print("moving_ion", moving_ion)

        if moving_ion in used_junctions:
            print("rollback", "3")
            # move_ion(G, prev_ion, current_edge, prev_edge)
            # used_junctions.pop(prev_ion)
            # G = rollback_graph(G, prev_G)
            return prev_used_junctions, prev_G

        # 移動候補リスト
        adjacent_edges = list(
            nx.edge_boundary(G, nbunch1=[current_edge[0], current_edge[1]], data=True)
        )
        min_cost = float("inf")
        next_edge = None
        for ad_edge in adjacent_edges:
            # print("ad_edge", ad_edge)
            # 戻る方向には進まない
            if get_idx_from_idc(G.idc_dict, ad_edge[:2]) == get_idx_from_idc(
                G.idc_dict, prev_edge
            ):
                # not go back(swap)
                continue

            common_node = set(ad_edge[:2]).intersection(set(current_edge))
            single_common_node = next(iter(common_node))

            if single_common_node in used_junctions.values():
                continue

            if ad_edge[2]["edge_type"] == "trap" and len(ad_edge[2]["ions"]) == 0:
                # TODO:
                path = get_shortest_path(G, ad_edge[0], (0, 0))
                cost = sum(
                    G.edges[edge]["weight"] if "weight" in G.edges[edge] else 1
                    for edge in path
                )
                if cost < min_cost:
                    min_cost = cost
                    next_edge = ad_edge
                break

            next_edge = None

        if not next_edge:
            # adjacents are fully occupied with other ions
            candidates = []
            for ad in adjacent_edges:
                # print("ad", ad)
                # 戻る方向には進まない
                if get_idx_from_idc(G.idc_dict, ad[:2]) == get_idx_from_idc(
                    G.idc_dict, prev_edge
                ):
                    continue
                common_node = set(ad[:2]).intersection(set(current_edge))
                single_common_node = next(iter(common_node))
                if single_common_node in used_junctions.values():
                    continue
                if ad[2]["edge_type"] == "trap":
                    # トラップだったら候補ではある
                    candidates.append(ad)

            if not candidates:
                # 進めるエッジがない場合　ロールバックする
                print("rollback", "2")
                # G = rollback_graph(G, prev_G)
                return prev_used_junctions, prev_G

            # print("candidates", candidates)
            next_edge = random.choice(candidates)

        if not next_edge:
            # 進めるエッジがない場合
            assert False, "not find next edge"

        # print("next_edge", next_edge)
        # 移動
        # print("bugfix2", current_edge, next_edge)
        move_ion(G, moving_ion, current_edge, next_edge[:2])
        common_node = set(current_edge).intersection(set(next_edge[:2]))
        single_common_node = next(iter(common_node))
        used_junctions[moving_ion] = single_common_node
        plot_state(G, ("Move obstacle", moving_ion), show_plot=show_plot_move)
        # 更新
        prev_edge = current_edge
        prev_ion = moving_ion
        current_edge = next_edge[:2]

    return used_junctions, G
