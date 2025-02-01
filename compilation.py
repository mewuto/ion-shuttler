import math

from qiskit.dagcircuit import DAGDependency
from qiskit.dagcircuit.dagnode import DAGOpNode
from qiskit import QuantumCircuit
from qiskit.converters import circuit_to_dagdependency

# This file is almost copy from Daniel's one.
# ref: https://docs.quantum.ibm.com/api/qiskit/0.24/dagcircuit


def is_qasm_file(filename: str) -> bool:
    """
    Check if the provided file is a valid QASM file.

    Args:
        filename: The name of the file to check.

    Returns:
        True if the file is a QASM file, False otherwise.
    """
    if not filename.endswith(".qasm"):
        return False

    try:
        with open(filename) as file:
            first_line = file.readline()
            return "OPENQASM" in first_line
    except OSError:
        return False


def get_front_layer(dag: DAGDependency) -> list[DAGOpNode]:
    """
    Get the front layer of the DAG.

    Args:
        dag: The DAGDependency object representing the quantum circuit.

    Returns:
        A list of DAGOpNodes in the front layer of the DAG.
    """
    front_layer = []
    for node in dag.get_nodes():
        # print(f"Node ID: {node.node_id}, Qubits: {node.qargs}")
        if not dag.direct_predecessors(node.node_id):
            front_layer.append(node)
    return front_layer


# My original function
def get_front_layer_ions(dag: DAGDependency):
    working_dag = manual_copy_dag(dag)
    front_gates = get_front_layer(working_dag)
    if not front_gates:
        return []

    front_ions = []
    for gate in front_gates:
        front_ions.extend(gate.qindices)

    return front_ions


def remove_node(dag: DAGDependency, node: DAGOpNode) -> None:
    """
    Execute a node and update the DAG (remove the node and its edges).

    Args:
        dag: The DAGDependency object.
        node: The node to be removed from the DAG.
    """
    dag._multi_graph.remove_node(node.node_id)


def find_best_gate(front_layer: list[DAGOpNode], dist_map: dict[int, int]) -> DAGOpNode:
    """
    Find the best gate to execute based on the distance map.

    Args:
        front_layer: A list of DAGOpNodes in the front layer.
        dist_map: A dictionary mapping qubit indices to distances.

    Returns:
        The DAGOpNode of the best gate to execute.
    """
    min_gate_cost = math.inf
    best_gate = None
    for gate_node in front_layer:
        # print(f"Node ID: {gate_node.node_id}, Qubits: {gate_node.qargs}, qindices: {gate_node.qindices}")
        qubit_indices = gate_node.qindices
        gate_cost = max([dist_map[qs] for qs in qubit_indices])

        if len(qubit_indices) == 2 and gate_cost == 0:
            return gate_node  # Execute 2-qubit gate if both ions are in the processing zone

        if gate_cost < min_gate_cost:
            min_gate_cost = gate_cost
            best_gate = gate_node

    return best_gate


def manual_copy_dag(dag: DAGDependency) -> DAGDependency:
    """
    Create a copy of the provided DAGDependency object.

    Args:
        dag: The original DAGDependency object.

    Returns:
        A copy of the DAGDependency object.
    """
    new_dag = DAGDependency()

    for qreg in dag.qregs.values():
        new_dag.add_qreg(qreg)

    for node in dag.get_nodes():
        new_dag.add_op_node(node.op, node.qargs, node.cargs)

    return new_dag


def update_sequence(dag: DAGDependency, distance_map: dict[int, int]):
    """
    Get the sequence of gates from the DAG and create a new sequence based on distances.

    Args:
    - dag (DAGDependency): The dependency DAG of quantum gates.
    - distance_map (dict): A dictionary that maps each ion to its distance from the processing zone.

    Returns:
    - sequence (list): List of gate sequences.
    - first_node (DAGDependencyNode): The first gate node in the sequence.
    """
    # Create a working copy of the DAG
    working_dag = manual_copy_dag(dag)
    sequence = []
    first_node = None

    while True:
        # Get the front layer of executable gates
        front_gates = get_front_layer(working_dag)
        if not front_gates:
            break

        # Find the best gate to execute based on distance map
        best_gate = find_best_gate(front_gates, distance_map)

        # Append the gate's qubit indices to the sequence
        sequence.append(best_gate.qindices)
        # Remove the selected node from the working DAG
        remove_node(working_dag, best_gate)

        # Update first_node for the first iteration
        if first_node is None:
            first_node = best_gate

    return sequence, first_node


def create_initial_sequence(
    distance_map: dict[tuple[int, int], int], filename: str
) -> tuple[list[tuple[int]], list[int], DAGDependency, DAGOpNode]:
    """
    Create the initial gate sequence from the QASM file.

    Args:
        distance_map: A dictionary mapping qubit pairs to distances.
        filename: The name of the QASM file.

    Returns:
        A tuple containing:
            - A list of tuples representing the gate sequence.
            - A flattened list of qubit indices.
            - The DAGDependency object representing the quantum circuit.
            - The next DAGOpNode to be executed.
    """
    with open(filename) as file:
        first_line = file.readline()
        # print(first_line)
    assert is_qasm_file(filename), "The file is not a valid QASM file."

    qc = QuantumCircuit.from_qasm_file(filename)
    dag_dep = circuit_to_dagdependency(qc)

    gate_ids, next_node = update_sequence(dag_dep, distance_map)
    seq = [tuple(gate) for gate in gate_ids]
    flat_seq = [item for sublist in seq for item in sublist]

    return seq, flat_seq, dag_dep, next_node
