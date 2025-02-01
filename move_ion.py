# !pip install numpy networkx matplotlib
import networkx as nx
from graph_utils import (
    get_ion_chains,
    move_ion,
)
from plot import plot_state


def stride_move(
    G: nx.Graph,
    ion: int,
    path: list[tuple[tuple[int, int], tuple[int, int]]],
    used_junctions: dict[int, tuple[int, int]],  # ion: node
    path_to_pz: list[tuple[tuple[int, int], tuple[int, int]]],
    timestep: int,
    parking_edge: tuple[tuple[int, int], tuple[int, int]],
    processing_zone: tuple[int, int],
    show_plot_move: bool = False,
):
    """
    ジャンクションを跨ぐまでイオンを移動させる

    Parameters
    ----------
    G : nx.Graph
    ion : int イオンの番号

    """
    current_edge = get_ion_chains(G)[ion]
    for next_edge in path:
        # パスが空いていたらジャンクションを1つ超えるまでこのイオンを移動させる
        # 超えたらused_junctionsに追加し、止める

        common_node = set(current_edge).intersection(set(next_edge))
        single_common_node = next(iter(common_node))
        if ion in used_junctions or single_common_node in used_junctions.values():
            # ジャンクションが使われていたら当然stay
            return used_junctions

        if next_edge != parking_edge and len(G.edges[next_edge]["ions"]) > 0:
            # next edge にイオンがある場合は基本的にNGだが，parking_edgeはOK
            return used_junctions

        # 普通の移動
        if single_common_node in G.junction_nodes or current_edge in path_to_pz:
            # over junction in Memory zone
            move_ion(G, ion, current_edge, next_edge)
            plot_state(G, ("Timestep", timestep), show_plot=show_plot_move)
            used_junctions[ion] = single_common_node
            return used_junctions
        elif single_common_node not in G.junction_nodes:
            # first_entry_connectionにいる場合のみ逆周り可能
            if single_common_node == processing_zone:
                move_ion(G, ion, current_edge, next_edge)
                plot_state(G, ("Timestep", timestep), show_plot=show_plot_move)
                used_junctions[ion] = single_common_node
                return used_junctions
            else:
                if G.edges[current_edge]["edge_type"] == "trap":
                    print("1,1格子ではありえない in move_stride")
                    return used_junctions
            used_junctions[ion] = single_common_node
            move_ion(G, ion, current_edge, next_edge)
            plot_state(G, ("Timestep", timestep), show_plot=show_plot_move)
            return used_junctions

        current_edge = next_edge

    return used_junctions
