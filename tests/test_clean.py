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
        test_env_file = f"{os.path.dirname(os.path.realpath(__file__))}/test_env.yml"
        env: Environment = from_file(test_env_file)
        # Create the test environment
        subprocess.run(["conda", "env", "create", "-f", test_env_file])

        base_env_file = f"{temp_dir}/test.yml"
        subprocess.run(["conda", "env", "export", "-n", env.name ,"-f", base_env_file])
        base_env: Environment = from_file(base_env_file)
        subprocess.run(["conda", "env", "remove", "-p", base_env.prefix, "-y"])


        # Clean the environment
        clean_env_file = f"{temp_dir}/test_clean.yml"
        subprocess.run(["clean-yaml", base_env_file, "-nf", clean_env_file])
        cleaned_env: Environment = from_file(clean_env_file)
        cleaned_env.name += "Clean"  # Change name

        with open(clean_env_file, "wb") as stream:
            to_yaml_patch(stream, cleaned_env.to_dict())

        # Create and remove cleaned environment
        subprocess.run(["conda", "env", "create", "-f", clean_env_file])
        subprocess.run(["conda", "env", "remove", "-p", cleaned_env.prefix, "-y"])

