import logging
import os
from pathlib import Path
from typing import Any

from conda.base.context import context
from conda.env.env import Environment, from_file
from conda.exceptions import EnvironmentNameNotFound
from conda.exports import linked
from conda.models.dist import Dist

from .utility import Dependency, get_dependency_graph, to_yaml_patch


def clean_environment_from_file(
    filename: str,
    new_filename: str | None,
    exclude_versions: bool,
    exclude_builds: bool,
    **_: Any,
) -> None:
    """
    Clean a conda environment from its yaml file.

    :param filename: The path to the .yaml file.
    :param new_filename: An optional new name for the yaml file.
    :param exclude_versions: Whether to remove the versions of the dependencies (Note if the version is removed the build will be removed aswell).
    :param exclude_builds: Whether to remove the builds of the dependencies.
    :param _: Other unused kwargs.
    :raises ValueError: If no name or prefix is provided in the environment.
    :raises EnvironmentNameNotFound: If a conda environment is not found by name.
    """
    logging.info("Cleaning conda environment.")
    env: Environment = from_file(filename)

    prefix = env.prefix
    if env.prefix is None:  # If no prefix is defined do manual search of environment.
        if env.name is None:
            raise ValueError("Environment must have a 'name' or 'prefix' defined.")

        conda_exe = os.environ.get("CONDA_EXE")
        base_prefix = (
            Path(conda_exe).parent.parent if conda_exe is not None else Path(context.root_prefix)
        )
        candidate = base_prefix / "envs" / env.name
        if candidate.exists():
            prefix = str(candidate)
        else:
            raise EnvironmentNameNotFound(
                f"Conda env '{env.name}' not found. Activate it or add 'prefix:' to the yaml."
            )

    package_cache: list[Dist] = linked(prefix)
    # Generate directed graph from distributions.
    graph = get_dependency_graph(packages=package_cache, env_path=prefix)
    # Extract all packages that are roots (i.e. have no packages depend on them).
    roots = [k for k, v in graph.in_degree if v < 1]
    # Get filtered dependencies for conda and pip
    conda_dependencies = _get_filtered_dependencies(
        env.dependencies.get("conda"), roots, exclude_versions, exclude_builds
    )

    # For now we can only filter conda packages
    # TODO: maybe incorporate filtering for pip
    pip_deps: list[str] | None = env.dependencies.get("pip")
    if pip_deps is not None:
        pip_deps = (
            [d.split("=")[0] for d in pip_deps] if exclude_versions else [str(d) for d in pip_deps]
        )
        conda_dependencies += [{"pip": pip_deps}]

    env_dict = env.to_dict()
    env_dict["dependencies"] = conda_dependencies

    logging.info("Finalizing cleaned environment.")
    path = new_filename or env.filename
    with open(path, "wb") as stream:
        to_yaml_patch(stream=stream, obj=env_dict)


def _get_filtered_dependencies(
    dependencies: list[str] | None, roots: list[str], ev: bool, eb: bool
) -> list[str]:
    """
    Get a list of filtered dependencies.

    :param dependencies: The dependencies to filter.
    :param roots: The root dependencies.
    :param ev: Exclude version from dependency representation.
    :param eb: Exclude build from dependency representation.
    :return: The filtered list.
    """
    if dependencies is None:
        return []
    dependencies = [Dependency(d, ev, eb) for d in dependencies]
    return [repr(d) for d in dependencies if any((n == d.name for n in roots))]
