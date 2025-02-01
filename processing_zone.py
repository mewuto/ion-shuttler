import networkx as nx
from graph_basics import update_distance_map
from graph_utils import (
    get_ion_chains,
)
from compilation import get_front_layer, remove_node, manual_copy_dag, update_sequence
from move_from_pz import move_from_pz


def process_pz(
    G: nx.Graph,
    used_junctions: dict[int, tuple[int, int]],
    timestep: int,
    max_chains_in_parking: int,
    dag_dep,
    flat_seq,
    seq,
    parking_edge: tuple[tuple[int, int], tuple[int, int]],
    init_seq_len: int,
    show_plot_move: bool = False,
):
    """
    プロセッシングゾーンの処理を行う
    """
    parking_ions: list[int] = G.edges[parking_edge]["ions"]
    out_from_pz_ions: list[int] = []
    if len(parking_ions) == 0:
        # ion nothing but distance is changed
        dag_dep = manual_copy_dag(dag_dep)
        distance_map = update_distance_map(get_ion_chains(G), G.dist_dict)
        gate_ids, next_node = update_sequence(dag_dep, distance_map)
        seq = [tuple(gate) for gate in gate_ids]
        flat_seq = [item for sublist in seq for item in sublist]
        return dag_dep, seq, flat_seq, next_node, timestep

    # キャパより多い場合，いらないイオンを出す
    if len(parking_ions) > max_chains_in_parking:
        # parking_ionsの中で，flat_seqの先頭から順で最も遅く出現するイオンをunnessecary_ionとして選ぶ
        unnecessary_ion = find_unnecessary_ion(parking_ions, flat_seq)
        if unnecessary_ion == -1:
            print("おかしい")

        out_from_pz_ions.append(unnecessary_ion)
        # print("move_from_pz", "out_from_pz_ions", out_from_pz_ions)
        move_from_pz(G, out_from_pz_ions, used_junctions, show_plot_move=show_plot_move)

    # ゲート処理
    # remove dag nodes in front layer as possible from dag by using current parking ions
    flag_dag_node_removed = True
    while flag_dag_node_removed:
        flag_dag_node_removed = False
        front_layer = get_front_layer(dag_dep)
        # front_layerのイオンがparking_ionsに含まれているか確認し，含まれていれば，そのノード（ゲート）を実行し，seqから削除する

        ###################################
        # TODO:これはまとめて削除する方
        ###################################
        # for dagNode in front_layer:
        #     # print("dag", dagNode.qindices)
        #     # print("parking_ions", parking_ions)
        #     qubit_indices = dagNode.qindices
        #     # Check whether qubit_indices(list) is completely contained in parking_ions(list)
        #     if all(qubit in parking_ions for qubit in qubit_indices):
        #         # print("qubit_indices", qubit_indices, "parking_ions", parking_ions)
        #         # print("before")
        #         # for node in dag_dep.get_nodes():
        #         #     print(f"Node ID: {node.node_id}, Qubits: {node.qargs}")
        #         if len(qubit_indices) > 1:
        #             # timestep += 3
        #             timestep += 1
        #         else:
        #             timestep += 1
        #             # timestep += 1

        #         remove_node(dag_dep, dagNode)
        #         # print("after")
        #         # for node in dag_dep.get_nodes():
        #         #     print(f"Node ID: {node.node_id}, Qubits: {node.qargs}")
        #         flag_dag_node_removed = True

        ###########################################
        # フロントレイヤーから1つのゲートだけ処理
        ###########################################
        for dagNode in front_layer:
            qubit_indices = dagNode.qindices
            if all(qubit in parking_ions for qubit in qubit_indices):
                # タイムステップをインクリメント
                if len(qubit_indices) > 1:  # 2量子ビットゲート
                    timestep += 3
                else:  # 1量子ビットゲート
                    timestep += 1

                # ゲートを実行して削除
                print(
                    f"time step: {timestep}, execution of gate ({init_seq_len-len(seq)+1}/{init_seq_len}) on qubit(s) {qubit_indices}"
                )
                remove_node(dag_dep, dagNode)
                flag_dag_node_removed = False
                break  # 1つのゲートを処理したらループを抜ける

    dag_dep = manual_copy_dag(dag_dep)
    distance_map = update_distance_map(get_ion_chains(G), G.dist_dict)
    gate_ids, next_node = update_sequence(dag_dep, distance_map)
    seq = [tuple(gate) for gate in gate_ids]
    flat_seq = [item for sublist in seq for item in sublist]
    # dag_drawer(dag_dep)

    return dag_dep, seq, flat_seq, next_node, timestep


def find_unnecessary_ion(parking_ions: list, flat_seq: list) -> int:
    # Create a set of ions in flat_seq for quick lookup
    flat_seq_set = set(flat_seq)

    # Filter out ions that are in flat_seq
    filtered_parking_ions = [ion for ion in parking_ions if ion not in flat_seq_set]

    # If there are ions not in flat_seq, return one of them
    if filtered_parking_ions:
        return filtered_parking_ions[0]

    # If all ions are in flat_seq, find the one that appears last
    last_occurrence = {ion: idx for idx, ion in enumerate(flat_seq)}
    unnecessary_ion = max(parking_ions, key=lambda ion: last_occurrence.get(ion, -1))

    return unnecessary_ion
