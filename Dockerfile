FROM python:3.12-slim

# 必要なツールとライブラリをインストール
RUN apt-get update && apt-get install -y \
    make \
    graphviz \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

# Pythonパッケージのインストール
# nb test on cli (https://github.com/treebeardtech/nbmake)
# formatter for .py
# formatter for .ipynb
RUN pip install --no-cache-dir \
    jupyter \
    numpy \
    networkx \
    matplotlib \
    ipykernel \ 
    qiskit \
    qiskit_aer \
    pytest \
    nbmake \
    black \
    nbqa \
    pylatexenc

# Jupyter Notebookの設定ファイルをコピー
COPY jupyter_notebook_config.py /root/.jupyter/

# Jupyter Notebookのポートを公開
EXPOSE 8888

# コンテナ起動時にJupyter Notebookを起動
CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root"]
