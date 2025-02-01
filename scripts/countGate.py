# Description: QASMファイルから1量子ビットゲートと2量子ビットゲートの数をカウントするスクリプト
# Usage: python countGate.py

import re

# QASMファイルを読み込む
qasm_file = "qft_without_swaps/qft_no_swaps_nativegates_quantinuum_tket_8.qasm"

# 1量子ビットゲートのリスト
one_qubit_gates = {"rz", "rx"}
# 2量子ビットゲートのリスト
two_qubit_gates = {"rzz"}


def count_gates(file_path):
    one_qubit_count = 0
    two_qubit_count = 0

    # ファイルを読み込む
    with open(file_path, "r") as file:
        lines = file.readlines()

    for line in lines:
        line = line.strip()
        # コメントや空行をスキップ
        if (
            not line
            or line.startswith("//")
            or line.startswith("OPENQASM")
            or line.startswith("include")
        ):
            continue

        # 2量子ビットゲートを先にチェックしてカウント
        for gate in two_qubit_gates:
            if re.match(f"^{gate}\\(", line):
                two_qubit_count += 1
                break

        # 1量子ビットゲートをカウント
        for gate in one_qubit_gates:
            if re.match(f"^{gate}\\(", line):
                one_qubit_count += 1
                break

    total_timesteps = one_qubit_count + 3 * two_qubit_count

    return one_qubit_count, two_qubit_count, total_timesteps


# ゲートのカウントを取得
one_qubit_count, two_qubit_count, total_timesteps = count_gates(qasm_file)

# 結果を出力
print(f"1量子ビットゲートの数: {one_qubit_count}")
print(f"2量子ビットゲートの数: {two_qubit_count}")
print(f"ゲート実行にかかるタイムステップ数: {total_timesteps}")
