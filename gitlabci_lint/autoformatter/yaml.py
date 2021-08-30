from io import StringIO

from ruamel.yaml import YAML, CommentedMap

yaml = YAML()
yaml.indent(mapping=2, sequence=4, offset=2)
yaml.width = 1_000_000  # High to avoid that it add line-breaks


def read_yaml_from_file(filepath: str) -> CommentedMap:
    with open(filepath, "r") as fin:
        return yaml.load(fin)


def dump_yaml_to_file(filepath: str, data: CommentedMap) -> CommentedMap:
    with open(filepath, "w") as fout:
        return yaml.dump(data, stream=fout)


def read_yaml_from_file_safe(filepath: str):
    with open(filepath, "r") as fin:
        return load_safe_yaml(fin)


def load_safe_yaml(filepath_or_str):
    return YAML(typ="safe").load(filepath_or_str)


def dump_yaml_to_str(data: CommentedMap) -> str:
    dumped_str = StringIO()
    yaml.dump(data, stream=dumped_str)
    return dumped_str.getvalue()
