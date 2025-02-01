# without_swapsの方のファイルを使うので、今は使っていない
# Description: 任意の量子ビット数に対するQFT回路を生成し、QASMファイルとして出力するスクリプト
# Usage: python gen_qft.py

from math import pi
from qiskit import transpile, QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit.qasm2 import dumps
from qiskit_ibm_runtime.fake_provider import FakeManilaV2


def qft(n):
    """n量子ビットに対するQFT回路を作成"""
    qc = QuantumCircuit(n)

    for qubit in range(n):
        qc.h(qubit)
        for other_qubit in range(qubit + 1, n):
            angle = pi / (2 ** (other_qubit - qubit))
            qc.cp(angle, other_qubit, qubit)  # 制御U1ゲートを適用
    # qc.barrier()

    # 量子ビットの並びを反転
    # for i in range(n // 2):
    #     qc.swap(i, n - i - 1)

    return qc


# 量子ビット数を設定
n_qubits = 4  # 任意の量子ビット数
qc = qft(n_qubits)

# シミュレータバックエンドの取得
# backend = Aer.get_backend('qasm_simulator')
# backend = AerSimulator()
backend = FakeManilaV2()

print(qc.draw(output="text"))  # 回路の確認
# 回路をネイティブゲートセットにトランスパイル
# basis_gates = ['rz', 'rx', 'cx']
# transpiled_qc = transpile(qc, backend=backend, optimization_level=3)
# print(transpiled_qc.draw(output='text'))  # ネイティブゲートの確認

# QASMファイルとして出力
# qasm_str =  dumps(transpiled_qc)
qasm_str = dumps(qc)

# ファイルに保存
with open("transpiled_qft.qasm", "w") as f:
    f.write(qasm_str)

print("QASMファイルに出力しました: transpiled_qft.qasm")
