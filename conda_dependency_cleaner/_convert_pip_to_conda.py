import logging
import os
import re
import subprocess
from subprocess import CompletedProcess
from tempfile import TemporaryDirectory
from typing import Any

from conda.env.env import Environment, from_file
from tqdm import tqdm


def _call(command: str) -> CompletedProcess:
    """
    A wrapper around subprocess.run() for convenience.

    :param command: The command (arguments) to parse.
    :return: The completed process.
    """
    return subprocess.run(command, shell=True, stdout=subprocess.DEVNULL)


def convert_pip_to_conda(
    filename: str, new_filename: str | None, channels: list[str], **_: Any
) -> None:
    """
    Convert pip dependencies to conda dependencies if possible.

    :param filename: The conda environment file used for conversion.
    :param new_filename: The new file name for the converted conda environment.
    :param channels: The channels targeted for the conda dependencies.
    :param _: Other unused kwargs.
    :raises Exception: If something went wrong in the conversion.
    """
    env: Environment = from_file(filename)
    conda_deps: list[str] = env.dependencies.get("conda", [])
    pip_deps: list[str] = env.dependencies.get("pip", [])

    with TemporaryDirectory() as tmpdir:
        file_path = os.path.join(tmpdir, "tmp_env.yml")
        tmp_env_object = Environment(
            name=env.name + "_tmp",
            filename=file_path,
            channels=channels,
            dependencies=conda_deps,
        )
        tmp_env_object.save()

        logging.info("Creating temporary environment.")
        status = _call(f"conda env create -f {file_path} --quiet")
        if status.returncode != 0:
            raise Exception(
                f"Returncode {status.returncode}: Failed to create conda environment, with error {status.stderr}"
            )

        pip_fallback: list[str] = []
        failed_conda_installs: list[str] = []
        logging.info("Converting pip dependencies. This can take a bit.")
        for pd in tqdm(pip_deps):
            package, _, version = re.split(r"(==|>=|<=)", pd)
            # If the package is available on the channels provided, then try to insall it.
            if (
                _call(
                    f"conda search -c {' -c '.join(channels)} {package} --skip-flexible-search"
                ).returncode
                == 0
            ):
                install_status = _call(
                    f"conda install -n {tmp_env_object.name} -y -c {' -c '.join(channels)} {package}={version}"
                )
                if install_status.returncode != 0:
                    failed_conda_installs.append(package)
            else:
                pip_fallback.append(pd)

        if len(failed_conda_installs) > 0:
            logging.warning(
                "Failed to install packages over conda: {" ".join(failed_conda_installs)}"
            )
        logging.info("Finalizing converted environment.")
        if len(pip_fallback) > 0:
            _call("conda init")
            _call(f"conda activate {tmp_env_object.name}")
            _call(f"pip install {' '.join(pip_fallback)}")

        _call(f"conda export -n {tmp_env_object.name} -f {new_filename or env.filename}")
        _call(f"conda remove -n {tmp_env_object.name} --all")
