import networkx as nx
from conda.exports import is_linked
from conda.models.dist import Dist
from conda.models.records import PrefixRecord


def get_dependency_graph(packages: list[Dist], env_path: str) -> nx.DiGraph:
    """
    Get a directed dependency graph from a list of packages.

    :param packages: The packages.
    :param env_path: The path to the environment.
    :return: The directed dependency graph.
    """
    graph = nx.DiGraph()
    for elem in packages:
        graph.add_node(elem.name, version=elem.version)
        prefix: PrefixRecord = is_linked(env_path, elem)
        for co_elem in prefix.combined_depends:
            graph.add_edge(elem.name, co_elem.name, version=co_elem.version)
    return graph
