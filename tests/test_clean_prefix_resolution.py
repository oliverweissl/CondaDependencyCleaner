from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import networkx as nx
import pytest
from conda.exceptions import EnvironmentNameNotFound

from conda_dependency_cleaner._clean_environment_from_file import (
    clean_environment_from_file,
)


def test_clean_uses_explicit_prefix(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """
    If the environment file defines a prefix, the cleaner should use it directly.

    :param tmp_path: Temporary output directory for the generated environment file.
    :param monkeypatch: Pytest fixture for replacing imported collaborators.
    """
    env = _make_env(name="test-env", prefix="/explicit/prefix")
    linked = Mock(return_value=[])

    monkeypatch.setattr(
        "conda_dependency_cleaner._clean_environment_from_file.from_file",
        lambda filename: env,
    )
    monkeypatch.setattr(
        "conda_dependency_cleaner._clean_environment_from_file.linked",
        linked,
    )
    monkeypatch.setattr(
        "conda_dependency_cleaner._clean_environment_from_file.get_dependency_graph",
        lambda packages, env_path: nx.DiGraph(),
    )
    monkeypatch.setattr(
        "conda_dependency_cleaner._clean_environment_from_file.to_yaml_patch",
        lambda stream, obj: stream.write(b""),
    )

    clean_environment_from_file(
        filename="ignored.yml",
        new_filename=str(tmp_path / "cleaned.yml"),
        exclude_versions=False,
        exclude_builds=False,
    )

    linked.assert_called_once_with("/explicit/prefix")


def test_clean_does_not_lookup_env_dirs_when_prefix_is_present(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """
    A defined prefix must take precedence over any name-based env-dir lookup.

    :param tmp_path: Temporary output directory for the generated environment file.
    :param monkeypatch: Pytest fixture for replacing imported collaborators.
    """
    env = _make_env(name="named-env", prefix="/explicit/prefix")
    linked = Mock(return_value=[])

    monkeypatch.setattr(
        "conda_dependency_cleaner._clean_environment_from_file.from_file",
        lambda filename: env,
    )
    monkeypatch.setattr(
        "conda_dependency_cleaner._clean_environment_from_file.linked",
        linked,
    )
    monkeypatch.setattr(
        "conda_dependency_cleaner._clean_environment_from_file.get_dependency_graph",
        lambda packages, env_path: nx.DiGraph(),
    )
    monkeypatch.setattr(
        "conda_dependency_cleaner._clean_environment_from_file.to_yaml_patch",
        lambda stream, obj: stream.write(b""),
    )
    monkeypatch.setattr(
        Path,
        "exists",
        lambda path: pytest.fail("Path.exists() should not be consulted when prefix is present."),
    )

    clean_environment_from_file(
        filename="ignored.yml",
        new_filename=str(tmp_path / "cleaned.yml"),
        exclude_versions=False,
        exclude_builds=False,
    )

    linked.assert_called_once_with("/explicit/prefix")


def test_clean_resolves_prefix_from_base_envs_dir(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """
    If no prefix is present, the cleaner should resolve it from the conda base envs dir.

    :param tmp_path: Temporary output directory for the generated environment file.
    :param monkeypatch: Pytest fixture for replacing imported collaborators.
    """
    env = _make_env(name="resolved-env", prefix=None)
    linked = Mock(return_value=[])
    expected_prefix = "/base/envs/resolved-env"

    monkeypatch.setattr(
        "conda_dependency_cleaner._clean_environment_from_file.from_file",
        lambda filename: env,
    )
    monkeypatch.setattr(
        "conda_dependency_cleaner._clean_environment_from_file.linked",
        linked,
    )
    monkeypatch.setattr(
        "conda_dependency_cleaner._clean_environment_from_file.get_dependency_graph",
        lambda packages, env_path: nx.DiGraph(),
    )
    monkeypatch.setattr(
        "conda_dependency_cleaner._clean_environment_from_file.to_yaml_patch",
        lambda stream, obj: stream.write(b""),
    )
    monkeypatch.setenv("CONDA_EXE", "/base/bin/conda")
    monkeypatch.setattr(
        Path,
        "exists",
        lambda path: str(path) == expected_prefix,
    )

    clean_environment_from_file(
        filename="ignored.yml",
        new_filename=str(tmp_path / "cleaned.yml"),
        exclude_versions=False,
        exclude_builds=False,
    )

    linked.assert_called_once_with(expected_prefix)


def test_clean_resolves_prefix_from_root_prefix_when_conda_exe_is_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """
    If CONDA_EXE is unavailable, the cleaner should fall back to the conda root prefix.

    :param tmp_path: Temporary output directory for the generated environment file.
    :param monkeypatch: Pytest fixture for replacing imported collaborators.
    """
    env = _make_env(name="resolved-env", prefix=None)
    linked = Mock(return_value=[])
    expected_prefix = "/root-prefix/envs/resolved-env"

    monkeypatch.delenv("CONDA_EXE", raising=False)
    monkeypatch.setattr(
        "conda_dependency_cleaner._clean_environment_from_file.from_file",
        lambda filename: env,
    )
    monkeypatch.setattr(
        "conda_dependency_cleaner._clean_environment_from_file.linked",
        linked,
    )
    monkeypatch.setattr(
        "conda_dependency_cleaner._clean_environment_from_file.get_dependency_graph",
        lambda packages, env_path: nx.DiGraph(),
    )
    monkeypatch.setattr(
        "conda_dependency_cleaner._clean_environment_from_file.to_yaml_patch",
        lambda stream, obj: stream.write(b""),
    )
    monkeypatch.setattr(
        "conda_dependency_cleaner._clean_environment_from_file.context",
        SimpleNamespace(root_prefix="/root-prefix"),
    )
    monkeypatch.setattr(
        Path,
        "exists",
        lambda path: str(path) == expected_prefix,
    )

    clean_environment_from_file(
        filename="ignored.yml",
        new_filename=str(tmp_path / "cleaned.yml"),
        exclude_versions=False,
        exclude_builds=False,
    )

    linked.assert_called_once_with(expected_prefix)


def test_clean_raises_when_name_and_prefix_are_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """
    An environment file without name and prefix cannot be resolved.

    :param tmp_path: Temporary output directory for the generated environment file.
    :param monkeypatch: Pytest fixture for replacing imported collaborators.
    """
    env = _make_env(name=None, prefix=None)

    monkeypatch.setattr(
        "conda_dependency_cleaner._clean_environment_from_file.from_file",
        lambda filename: env,
    )

    with pytest.raises(ValueError, match="Environment must have a 'name' or 'prefix' defined."):
        clean_environment_from_file(
            filename="ignored.yml",
            new_filename=str(tmp_path / "cleaned.yml"),
            exclude_versions=False,
            exclude_builds=False,
        )


def test_clean_raises_when_named_env_is_not_found(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """
    If a named environment is not present in the resolved envs directory, the cleaner should raise.

    :param tmp_path: Temporary output directory for the generated environment file.
    :param monkeypatch: Pytest fixture for replacing imported collaborators.
    """
    env = _make_env(name="missing-env", prefix=None)

    monkeypatch.setattr(
        "conda_dependency_cleaner._clean_environment_from_file.from_file",
        lambda filename: env,
    )
    monkeypatch.setenv("CONDA_EXE", "/base/bin/conda")
    monkeypatch.setattr(Path, "exists", lambda path: False)

    with pytest.raises(
        EnvironmentNameNotFound,
        match="Conda env 'missing-env' not found. Activate it or add 'prefix:' to the yaml.",
    ):
        clean_environment_from_file(
            filename="ignored.yml",
            new_filename=str(tmp_path / "cleaned.yml"),
            exclude_versions=False,
            exclude_builds=False,
        )


def _make_env(name: str | None, prefix: str | None) -> SimpleNamespace:
    """
    Create the minimal environment stub needed by the cleaner.

    :param name: The environment name to expose on the stub.
    :param prefix: The environment prefix to expose on the stub.
    :return: A minimal object implementing the attributes used by the cleaner.
    """
    return SimpleNamespace(
        name=name,
        prefix=prefix,
        filename="ignored.yml",
        dependencies={},
        to_dict=lambda: {"name": name, "dependencies": []},
    )
