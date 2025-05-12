from conda.env.env import Environment, from_file
from conda.exports import linked
from conda.models.dist import Dist

from .utility import Dependency, get_dependency_graph, to_yaml_patch


def clean_environment_from_file(
    environment_file_path: str,
    new_file_name: str | None,
    exclude_versions: bool,
    exclude_builds: bool,
) -> None:
    """
    Clean a conda environment from its yaml file.

    :param environment_file_path: The path to the .yaml file.
    :param new_file_name: An optional new name for the yaml file.
    :param exclude_versions: Whether to remove the versions of the dependencies (Note if the version is removed the build will be removed aswell).
    :param exclude_builds: Whether to remove the builds of the dependencies.
    """
    env: Environment = from_file(environment_file_path)
    package_cache: list[Dist] = linked(env.prefix)
    # Generate directed graph from distributions.
    graph = get_dependency_graph(packages=package_cache, env_path=env.prefix)
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
        pip_deps = [d.split("=")[0] for d in pip_deps] if exclude_versions else pip_deps
        conda_dependencies += [{"pip": pip_deps}]

    env_dict = env.to_dict()
    env_dict["dependencies"] = conda_dependencies

    path = new_file_name or env.filename
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
