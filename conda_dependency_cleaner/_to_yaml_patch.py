from typing import Any, BinaryIO

from ruamel.yaml import YAML


def to_yaml_patch(stream: BinaryIO, obj: dict[str, Any]) -> None:
    """
    A simple yaml parser based on conda Environment.save() method.

    :param stream: The stream object.
    :param obj: The object to serialize into yaml.
    """
    parser = YAML(typ="safe", pure=True)
    parser.indent(mapping=2, offset=2, sequence=4)
    parser.default_flow_style = False
    parser.sort_base_mapping_type_on_output = False

    parser.dump(obj, stream)
