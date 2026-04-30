from pathlib import Path

import networkx as nx
import pytest
from conda.env.env import from_file

from conda_dependency_cleaner._clean_environment_from_file import (
    clean_environment_from_file,
)

ROOT_DEPENDENCIES = ("brotli", "matplotlib", "unicodedata2")


@pytest.mark.parametrize(
    "args, expected_env_file",
    [
        ({}, "clean_test_env.yml"),
        ({"exclude_builds": True}, "clean_test_env_no_builds.yml"),
        ({"exclude_versions": True}, "clean_test_env_no_versions.yml"),
    ],
)
def test_clean_yaml(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    args: dict[str, bool],
    expected_env_file: str,
) -> None:
    """
    Test cleaning an environment file without depending on a writable local conda setup.

    The cleaner only needs the parsed environment and the dependency graph roots.
    Mock the graph lookup so the test stays deterministic across machines and CI.

    :param tmp_path: Temporary output directory for the generated environment file.
    :param monkeypatch: Pytest fixture for replacing imported collaborators.
    :param args: Cleaner flags to apply for the parameterized case.
    :param expected_env_file: Fixture file describing the expected cleaned output.
    """
    test_files = Path(__file__).parent / "files"
    source_env_file = test_files / "test_env.yml"
    cleaned_env_file = tmp_path / "cleaned_env.yml"
    expected_env_file_path = test_files / expected_env_file
    source_env = from_file(str(source_env_file))
    source_env.prefix = "/explicit/test-prefix"

    monkeypatch.setattr(
        "conda_dependency_cleaner._clean_environment_from_file.linked",
        lambda prefix: [],
    )
    monkeypatch.setattr(
        "conda_dependency_cleaner._clean_environment_from_file.get_dependency_graph",
        lambda packages, env_path: _build_dependency_graph(),
    )
    monkeypatch.setattr(
        "conda_dependency_cleaner._clean_environment_from_file.from_file",
        lambda filename: source_env,
    )

    clean_environment_from_file(
        filename=str(source_env_file),
        new_filename=str(cleaned_env_file),
        exclude_versions=args.get("exclude_versions", False),
        exclude_builds=args.get("exclude_builds", False),
    )

    assert cleaned_env_file.exists(), f"{cleaned_env_file} was not created!"

    cleaned_env = from_file(str(cleaned_env_file))
    expected_clean_env = from_file(str(expected_env_file_path))

    assert cleaned_env.channels == expected_clean_env.channels
    assert cleaned_env.dependencies == expected_clean_env.dependencies


def _build_dependency_graph() -> nx.DiGraph:
    """
    Create a minimal graph whose roots represent the direct dependencies to keep.

    :return: A graph whose root nodes match the dependencies expected to remain.
    """
    graph = nx.DiGraph()
    graph.add_nodes_from(ROOT_DEPENDENCIES)
    graph.add_edge("matplotlib", "numpy-base")
    graph.add_edge("brotli", "libbrotlicommon")
    graph.add_edge("unicodedata2", "python")
    return graph
