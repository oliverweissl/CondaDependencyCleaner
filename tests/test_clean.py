import subprocess
from unittest.mock import Mock
import tempfile
import os
from conda.env.env import Environment, from_file
from conda_dependency_cleaner.utility import to_yaml_patch


def test_clean(mocker: Mock) -> None:
    """
    Test the environment cleaner script.

    :param mocker: The mock object.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        initial_env_file = f"{os.path.dirname(os.path.realpath(__file__))}/test_env.yml"
        clean_env_file = f"{os.path.dirname(os.path.realpath(__file__))}/clean_test_env.yml"
        clean_env: Environment = from_file(clean_env_file)

        # Create the test environment
        base_env_file = f"{temp_dir}/test.yml"
        base_env = _conda_operations(initial_env_file, base_env_file)

        # Clean the environment
        cleaned_env_file = f"{temp_dir}/test_clean.yml"
        subprocess.run(["clean-yaml", base_env_file, "-nf", cleaned_env_file])
        _remove_conda_env(base_env)

        cleaned_env = _conda_operations(cleaned_env_file, cleaned_env_file)
        _remove_conda_env(cleaned_env)

    assert cleaned_env.dependencies == clean_env.dependencies, "Error: Dependencies are different."


def _conda_operations(initial_env: str, new_env: str) -> Environment:
    """
    Create a conda environment based on a environment file, then export it to a new file.


    :param initial_env: The environment file.
    :param new_env: The new environment file.
    :return: The environment loaded as a python object.
    """
    env = from_file(initial_env)
    subprocess.run(["conda", "env", "create", "-f", initial_env])
    subprocess.run(["conda", "env", "export", "-n", env.name, "-f", new_env])
    return env


def _remove_conda_env(env: Environment) -> None:
    """
    Remove a conda environment from the system.

    :param env: The environment to remove.
    """
    subprocess.run(["conda", "env", "remove", "-n", env.name, "-y"])
