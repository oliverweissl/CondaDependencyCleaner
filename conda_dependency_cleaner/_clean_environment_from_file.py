from dataclasses import dataclass, field

from conda import exports as ce
from conda.env.env import Environment, from_file
from conda.models.dist import Dist

from ._get_dependeny_graph import get_dependency_graph
from ._to_yaml_patch import to_yaml_patch


@dataclass
class _Dependency:
    full_name: str
    exclude_version: bool
    exclude_build: bool

    name: str = field(init=False)
    version: str = field(init=False)
    build: str = field(init=False)

    def __post_init__(self) -> None:
        """After init process the full name."""
        self.name, rest = self.full_name.split("==")
        self.version, self.build = rest.split("=")

    def __repr__(self) -> str:
        """
        Define the representation of the Dependency.

        :return: Return the name.
        """
        v = "" if self.exclude_version else f"=={self.version}"
        b = "" if (self.exclude_build or self.exclude_version) else f"={self.build}"
        return f"{self.name}{v}{b}"


def clean_environment_from_file(
    environment_file_path: str,
    new_file_name: str | None,
    exclude_version: bool,
    exclude_build: bool,
) -> None:
    """
    Clean a conda environment from its yaml file.

    :param environment_file_path: The path to the .yaml file.
    :param new_file_name: An optional new name for the yaml file.
    :param exclude_version: Whether to remove the versions of the dependencies (Note if the version is removed the build will be removed aswell).
    :param exclude_build: Whether to remove the builds of the dependencies.
    """
    env: Environment = from_file(environment_file_path)
    package_cache: list[Dist] = ce.linked(env.prefix)

    # Generate directed graph from distributions.
    graph = get_dependency_graph(packages=package_cache, env_path=env.prefix)
    # Extract all packages without ingoing dependencies.
    roots = [k for k, v in graph.in_degree if v < 1]
    filtered_dependencies = [
        str(_Dependency(d, exclude_version, exclude_build))
        for d in env.dependencies["conda"]
        if any((n == d.split("==")[0] for n in roots))
    ]

    env_dict = env.to_dict()
    env_dict["dependencies"] = filtered_dependencies

    path = new_file_name or env.filename
    with open(path, "wb") as stream:
        to_yaml_patch(stream=stream, obj=env_dict)
