from dataclasses import dataclass, field


@dataclass
class Dependency:
    """A class representing a dependency of the conda environment."""

    full_name: str
    exclude_version: bool
    exclude_build: bool

    name: str = field(init=False)
    version: str = field(init=False)
    build: str = field(init=False)

    def __post_init__(self) -> None:
        """After init, process the full name."""
        components = self.full_name.split("=")
        self.name, self.version, *other = tuple(filter(None, components))
        self.build = other[0] if len(other) > 0 else ""

    def __repr__(self) -> str:
        """
        Define the representation of the Dependency.

        :return: Return the name.
        """
        v = "" if self.exclude_version else f"=={self.version}"
        b = "" if (self.exclude_build or self.exclude_version) else f"={self.build}"
        return f"{self.name}{v}{b}"
