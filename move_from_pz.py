import networkx as nx
import random
from graph_utils import (
    get_ion_chains,
    get_idx_from_idc,
    move_ion,
)
from plot import plot_state


def move_from_pz(
    G: nx.Graph,
    out_from_pz_ions: list[int],
    used_junctions: dict[int, tuple[int, int]],
    show_plot_move: bool = False,
):
    """
    処理ゾーンからメモリゾーンにイオンを移動させる
    """
    # parking_edgeからの移動
    for out_ion in out_from_pz_ions:
        ion_edge = get_ion_chains(G)[out_ion]
        adjacent_edges = list(
            nx.edge_boundary(G, nbunch1=[ion_edge[0], ion_edge[1]], data=True)
        )

        candidates = []
        for ad_edge in adjacent_edges:
            # print("ad_edge" ,ad_edge)
            edge_type = ad_edge[2]["edge_type"]
            ions = ad_edge[2]["ions"]
            
            if not edge_type == "parking_edge" and not edge_type == "exit":
                # prevent reverse move
                candidates.append(ad_edge)

        # 絶対成功する
        # print("candidates", candidates)
        if len(candidates) != 1:
            print("mvoe from pz: 現状あり得ないかも")
        # for e in moving_edge:
        #     if len(e[2]["ions"]) >0:
        #         assert False, "Move to Memory Zone: Edge is not empty."

        next_edge = random.choice(candidates)
        if not next_edge:
            # 進めるエッジがない場合
            assert False, "not find next edge"

        common_node = set(ion_edge).intersection(set(next_edge[:2]))
        single_common_node = next(iter(common_node))
        used_junctions[out_ion] = single_common_node
        move_ion(G, out_ion, ion_edge, next_edge[:2])
        plot_state(
            G, ("Move from PZ, Ion Number is", out_ion), show_plot=show_plot_move
        )

    # path_from_pz
    prev_edge = ion_edge
    prev_ion = out_ion
    current_edge = get_ion_chains(G)[prev_ion]
   
    while len(G.edges[current_edge]["ions"]) > 1:
        # 隣のエッジを探し，prev_edgeではない方向に進む
        # 基本的にイオンがない方に進むが，進めない場合はイオンがあっても進み，current_edgeなどを更新する

        # 移動させるイオンの決定
        on_site_ions: list[int] = G.edges[current_edge]["ions"]
        moving_ion = next((x for x in on_site_ions if x != prev_ion), None)
        
        # TODO:suspicious
        if moving_ion in used_junctions:
            move_ion(G, prev_ion, current_edge, prev_edge)
            used_junctions.pop(prev_ion)
            return used_junctions
            # assert False, "絶対にダメなやつ. Must rollback"

        # 移動させる方向の決定
        adjacent_edges = list(
            nx.edge_boundary(G, nbunch1=[current_edge[0], current_edge[1]], data=True)
        )
        for ad_edge in adjacent_edges:
            # まずは空いているところを探す
            # print("ad_edge from pz", ad_edge)
            if get_idx_from_idc(G.idc_dict, ad_edge[:2]) == get_idx_from_idc(
                G.idc_dict, prev_edge
            ):
                # not go back(swap)
                continue

            if (
                ad_edge[2]["edge_type"] == "parking_edge"
                or ad_edge[2]["edge_type"] == "exit"
            ):
                # print("ad_edge[2]", ad_edge[2]["edge_type"])
                continue

            # print("through continue", ad_edge[:2], current_edge)
            common_node = set(ad_edge[:2]).intersection(set(current_edge))
            single_common_node = next(iter(common_node))
            # print("single_common_node", single_common_node, used_junctions)
            if single_common_node in used_junctions.values():
                if (
                    G.edges[current_edge]["edge_type"] == "entry"
                    or G.edges[current_edge]["edge_type"] == "first_entry_connection"
                    and G.edges[ad_edge[:2]]["edge_type"] == "trap"
                ):
                    print("怪しい")
                else:
                    continue

            if len(ad_edge[2]["ions"]) == 0:
                next_edge = ad_edge
                # print("next_edge", next_edge)
                break
            next_edge = None

        ############################
        # イオンを押し出す
        ############################
        # print("next_edge", next_edge)
        # print("current_edge", current_edge)
        # print("prev_edge", prev_edge)
        if not next_edge:
            # イオンがいて進めない場合
            candidates = []
            for ad in adjacent_edges:
                if get_idx_from_idc(G.idc_dict, ad[:2]) == get_idx_from_idc(
                    G.idc_dict, prev_edge
                ):
                    # not go back(swap)
                    continue

                common_node = set(ad[:2]).intersection(set(current_edge))
                single_common_node = next(iter(common_node))
                if single_common_node in used_junctions.values():
                    continue

                if ad[2]["edge_type"] == "parking_edge" or ad[2]["edge_type"] == "exit":
                    continue

                # trap or entry
                candidates.append(ad)

            if not candidates:
                # 進めるエッジがない場合　ロールバックする
                move_ion(G, prev_ion, current_edge, prev_edge)
                used_junctions.pop(prev_ion)
                return used_junctions

            # print("candidates", candidates)
            next_edge = random.choice(candidates)

        if not next_edge:
            # 進めるエッジがない場合
            assert False, "Move from PZ: No edge to move."

        # 移動
        move_ion(G, moving_ion, current_edge, next_edge[:2])
        common_node = set(current_edge).intersection(set(next_edge[:2]))
        single_common_node = next(iter(common_node))
        used_junctions[moving_ion] = single_common_node

        plot_state(G, ("Move from PZ", moving_ion), show_plot=show_plot_move)
        # 更新
        prev_edge = current_edge
        prev_ion = moving_ion
        current_edge = next_edge[:2]
