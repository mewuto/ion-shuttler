#!/bin/bash

# Description: このスクリプトは、指定されたビット数のレジスタに対して、 ハダマードゲートを適用するQASMファイルを生成します。
# Usage: ./gen_full_register_access.sh <number_of_qubits>

# 引数チェック
if [ -z "$1" ]; then
  echo "Usage: $0 <number_of_qubits>"
  exit 1
fi

# 引数からビット数を取得
num_qubits=$1

# 出力ディレクトリとファイル名
output_dir="full_register_access"
output_file="../$output_dir/full_register_access_$num_qubits.qasm"

# 出力ディレクトリが存在しない場合は作成
if [ ! -d "$output_dir" ]; then
  mkdir -p "$output_dir"
fi

# QASMヘッダーを生成
echo "OPENQASM 2.0;" > $output_file
echo "include \"qelib1.inc\";" >> $output_file
echo "qreg q[$num_qubits];" >> $output_file
echo "" >> $output_file  # 改行を追加

# 各ビットにハダマードゲートを適用
for (( i=0; i<$num_qubits; i++ ))
do
  echo "h q[$i];" >> $output_file
done

# QASMファイルの生成完了メッセージ
echo "QASM file generated: $output_file"
