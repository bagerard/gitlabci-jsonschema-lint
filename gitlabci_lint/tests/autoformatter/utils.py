from io import StringIO

from ruamel.yaml import YAML, CommentedMap

yaml = YAML()


def get_dumped_yaml(data: CommentedMap) -> str:
    dumped_str = StringIO()
    yaml.dump(data, stream=dumped_str)
    return dumped_str.getvalue()
