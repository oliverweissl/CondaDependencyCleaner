import logging
import os
import re
import shlex
import subprocess
from subprocess import CompletedProcess
from tempfile import TemporaryDirectory
from typing import Any

from conda.env.env import Environment, from_file
from tqdm import tqdm


def _call(command: str) -> CompletedProcess[str]:
    """
    A wrapper around subprocess.run() for convenience.

    :param command: The command (arguments) to parse.
    :return: The completed process.
    """
    return subprocess.run(command, shell=True, capture_output=True, text=True)


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
    export_filename = _normalize_export_filename(new_filename or env.filename)
    quoted_channels = " -c ".join(shlex.quote(channel) for channel in channels)

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
        status = _call(f"conda env create -f {shlex.quote(file_path)} --quiet")
        if status.returncode != 0:
            raise Exception(
                f"Returncode {status.returncode}: Failed to create conda environment, with error {status.stderr}"
            )

        pip_fallback: list[str] = []
        failed_conda_installs: list[str] = []
        logging.info("Converting pip dependencies. This can take a bit.")
        for pd in tqdm(pip_deps):
            dep_components = re.split(r"(==|>=|<=)", pd, maxsplit=1)
            package = dep_components[0]
            version = dep_components[2] if len(dep_components) == 3 else ""
            conda_spec = f"{package}={version}" if version else package
            # If the package is available on the channels provided, then try to insall it.
            if (
                _call(
                    f"conda search -c {quoted_channels} {shlex.quote(package)} --skip-flexible-search"
                ).returncode
                == 0
            ):
                install_status = _call(
                    f"conda install -n {shlex.quote(tmp_env_object.name)} -y -c {quoted_channels} {shlex.quote(conda_spec)}"
                )
                if install_status.returncode != 0:
                    failed_conda_installs.append(package)
            else:
                pip_fallback.append(pd)

        if len(failed_conda_installs) > 0:
            logging.warning(
                f"Failed to install packages over conda: {', '.join(failed_conda_installs)}"
            )
        logging.info("Finalizing converted environment.")
        if len(pip_fallback) > 0:
            quoted_pip_deps = " ".join(shlex.quote(dep) for dep in pip_fallback)
            pip_install_status = _call(
                f"conda run -n {shlex.quote(tmp_env_object.name)} pip install {quoted_pip_deps}"
            )
            if pip_install_status.returncode != 0:
                raise Exception(
                    "Failed to install fallback pip dependencies "
                    f"into temporary env '{tmp_env_object.name}': {pip_install_status.stderr}"
                )

        export_status = _call(
            f"conda export -n {shlex.quote(tmp_env_object.name)} -f {shlex.quote(export_filename)}"
        )
        if export_status.returncode != 0:
            raise Exception(
                f"Failed to export converted environment to '{export_filename}': {export_status.stderr}"
            )

        remove_status = _call(f"conda remove -n {shlex.quote(tmp_env_object.name)} --all -y")
        if remove_status.returncode != 0:
            logging.warning(
                f"Failed to remove temporary env '{tmp_env_object.name}': {remove_status.stderr}"
            )


def _normalize_export_filename(filename: str) -> str:
    """
    Ensure the output filename matches a conda-supported export pattern.

    :param filename: The requested output filename.
    :return: A supported filename, defaulting to the YAML exporter when no suffix is provided.
    """
    if filename.endswith((".yml", ".yaml", ".json", ".txt")):
        return filename
    return f"{filename}.yml"
