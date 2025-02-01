import json
import networkx as nx
from pathlib import Path
from graph_basics import GraphCreator, create_starting_config, update_distance_map
from graph_utils import (
    create_idc_dictionary,
    create_dist_dict,
    get_ion_chains,
    get_idx_from_idc,
)

from compilation import create_initial_sequence
from find_path import find_path
from plot import plot_state
from move_obstacle_ion import move_as_push_obstacle_ions
from processing_zone import process_pz
from move_ion import stride_move


def run_simulation(
    G: nx.Graph,
    graph_creator: GraphCreator,
    seq,
    flat_seq,
    dag_dep,
    next_node,
    init_seq_len: int,
):
    """
    シミュレーションを実行する
    """
    show_plot_move = False
    max_chains_in_parking = 3
    used_junctions: dict[int, tuple[int, int]] = {}  # ion: node
    timestep = 0
    plot_state(G, ("Timestep", timestep), show_plot=show_plot_move)
    timestep_buffer = 0

    while len(seq) > 0:
        # print("seq", seq)
        # print("flat_seq", flat_seq)
        # print(f"Next Node ID: {next_node.node_id}, qindices: {next_node.qindices}")
        unique_seq = get_unique_flat_seq(flat_seq)
        # print("unique_seq", unique_seq)
        move_list = get_move_list(
            G, graph_creator.path_to_pz, next_node.qindices[0], unique_seq
        )
        # print("move_list", move_list)

        used_junctions = {}

        for ion in move_list:
            current_edge = get_ion_chains(G)[ion]
            path = find_path(G, current_edge, graph_creator.parking_node)
            if not path:
                continue

            if ion in used_junctions:
                continue

            if get_idx_from_idc(G.idc_dict, current_edge) == get_idx_from_idc(
                G.idc_dict, graph_creator.path_from_pz[0]
            ):
                # pzから帰る時の逆走防止
                path = find_path(
                    G, current_edge, (graph_creator.m - 1, graph_creator.n - 1)
                )

            next_edge = path[0]
            if (
                len(G.edges[next_edge]["ions"]) > 0
                and G.edges[next_edge]["edge_type"] == "trap"
            ):
                # メモリゾーン上の動く予定のないイオンに邪魔されている
                used_junctions, G = move_as_push_obstacle_ions(
                    G, ion, next_edge, used_junctions, show_plot_move
                )
            else:
                used_junctions = stride_move(
                    G,
                    ion,
                    path,
                    used_junctions,
                    graph_creator.path_to_pz,
                    timestep,
                    graph_creator.parking_edge,
                    graph_creator.processing_zone,
                    show_plot_move=show_plot_move,
                )

            # plot_state(G, ("bugfix", ion), show_plot=show_plot_move)

        # front_layerに合わせてPZを処理
        dag_dep, seq, flat_seq, next_node, timestep_new = process_pz(
            G,
            used_junctions,
            timestep,
            max_chains_in_parking,
            dag_dep,
            move_list,
            seq,
            graph_creator.parking_edge,
            init_seq_len,
            show_plot_move=show_plot_move,
        )

        # 処理ゾーンでの処理タイムステップで過剰に使ったタイムステップの一部は移動と並列して行えるので，通常移動の移動の時にtimestep_bufferから1引ければ，インクリメントする必要がない
        timestep_buffer = timestep_new - timestep

        if timestep == timestep_new:
            # ゲートの処理が行われなかった場合
            timestep_buffer -= 1
            if timestep_buffer < 0:
                timestep += 1
        else:
            timestep = timestep_new

        # plot_state(G, ("Timestep", timestep), show_plot=True)

        if len(seq) == 0:
            print("\nFull Sequence executed in %s time steps" % timestep)
            break


def get_unique_flat_seq(sequence: list):
    unique_sequence = []
    for seq_elem in sequence:
        if seq_elem not in unique_sequence:
            unique_sequence.append(seq_elem)

    return unique_sequence


def get_move_list(
    G: nx.Graph,
    path_to_pz: list[list[tuple[int, int], tuple[int, int]]],
    prior_ion: int,
    unique_seq: list,
):
    move_list = []

    reversed_path_to_pz = list(reversed(path_to_pz))
    # 逆順にしたリストをループして、各エッジ上にあるイオンを取得
    for edge in reversed_path_to_pz:
        ions_on_edge = G.edges[edge]["ions"]
        move_list.extend(ions_on_edge)

    if prior_ion not in move_list:
        move_list.append(prior_ion)

    for seq_elem in unique_seq:
        if seq_elem not in move_list and seq_elem != prior_ion:
            move_list.append(seq_elem)

    return move_list


def main():
    # JSONファイルの読み込み
    config_file = "cases/full_register_access_6.json"
    with Path(config_file).open("r") as f:
        config = json.load(f)

    # 変数の設定
    arch = config["arch"]
    max_timesteps = config["max_timesteps"]
    num_ion_chains = config["num_ion_chains"]
    filename = config["qu_alg"]

    # グラフ生成
    m, n, v, h = arch
    ion_chain_size_vertical = v
    ion_chain_size_horizontal = h
    graph_creator = GraphCreator(
        m, n, ion_chain_size_vertical, ion_chain_size_horizontal
    )
    G = graph_creator.get_graph()
    nx.set_edge_attributes(G, {edge: [] for edge in G.edges}, "ions")
    n_of_registers = create_starting_config(G, num_ion_chains, seed=0)
    G.idc_dict = create_idc_dictionary(G)
    # print("idc_dict", G.idc_dict)
    G.dist_dict = create_dist_dict(G, graph_creator.exit, graph_creator.processing_zone)
    # print("dist_dict", G.dist_dict)
    ion_chains = get_ion_chains(G)

    distance_map = update_distance_map(ion_chains, G.dist_dict)
    seq, flat_seq, dag_dep, next_node = create_initial_sequence(distance_map, filename)
    init_seq_len = len(seq)

    timestep = 0
    labels = ("timestep %s" % timestep, None)

    # シミュレーション実行
    run_simulation(G, graph_creator, seq, flat_seq, dag_dep, next_node, init_seq_len)


if __name__ == "__main__":
    main()
