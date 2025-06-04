import os
import subprocess
import tempfile
from typing import Any, Generator

import pytest
from conda.env.env import Environment, from_file


def _remove_conda_env(env: Environment) -> None:
    """
    Remove a conda environment from the system.

    :param env: The environment to remove.
    """
    subprocess.run(["conda", "env", "remove", "-n", env.name, "-y"])


@pytest.fixture(scope="session")
def base_env_file() -> Generator[str, Any, None]:
    """
    Create and export the base environment file once for all tests.

    :yields: The base environment file path.
    """
    test_env_file = os.path.join(os.path.dirname(__file__), "files", "test_env.yml")
    test_env = from_file(test_env_file)
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            subprocess.run(["conda", "env", "create", "--file", test_env_file])
            base_env_file = f"{tmpdir}/base_env.yml"
            subprocess.run(["conda", "env", "export", "-n", test_env.name, "--file", base_env_file])
            yield base_env_file
    finally:
        _remove_conda_env(test_env)


@pytest.fixture
def temp_dir() -> Generator[str, Any, None]:
    """
    Create a unique temporary directory for each test.

    :yields: The temporary directory path.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.mark.parametrize(
    "args, expected_env_file",
    [
        ([], "clean_test_env.yml"),
        (["--exclude-builds"], "clean_test_env_no_builds.yml"),
        (["--exclude-versions"], "clean_test_env_no_versions.yml"),
    ],
)
def test_clean_yaml(
    base_env_file: str, temp_dir: str, args: list[str], expected_env_file: str
) -> None:
    """
    Test clean-yaml script with different arguments.

    :param base_env_file: The base environment file path.
    :param temp_dir: The temporary directory path.
    :param args: The arguments to pass to the clean_yaml script.
    :param expected_env_file: The expected environment file path.
    """
    cleaned_env_file = os.path.join(temp_dir, "cleaned_env.yml")

    # Run the clean-yaml script
    result = subprocess.run(
        ["cdc", "clean", base_env_file, "-nf", cleaned_env_file] + args,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, f"cdc clean failed with exit code {result.returncode}!"
    assert os.path.exists(cleaned_env_file), f"{cleaned_env_file} was not created!"

    # Load the expected environment
    cleaned_env = from_file(cleaned_env_file)
    expected_clean_env_path = os.path.join(os.path.dirname(__file__), "files", expected_env_file)
    expected_clean_env = from_file(expected_clean_env_path)

    # Compare dependencies
    assert (
        cleaned_env.dependencies == expected_clean_env.dependencies
    ), f"Dependencies differ for {args}"
