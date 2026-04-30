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
        components = tuple(filter(None, self.full_name.split("=")))
        self.name = components[0]
        self.version = components[1] if len(components) > 1 else ""
        self.build = components[2] if len(components) > 2 else ""

    def __repr__(self) -> str:
        """
        Define the representation of the Dependency.

        :return: Return the name.
        """
        v = "" if (self.exclude_version or not self.version) else f"=={self.version}"
        b = (
            ""
            if (self.exclude_build or self.exclude_version or not self.build)
            else f"={self.build}"
        )
        return f"{self.name}{v}{b}"
