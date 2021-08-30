import argparse
import sys

from gitlabci_lint.autoformatter.autoformatter import ORDERING, reorder
from gitlabci_lint.autoformatter.custom_reader import (
    read_yaml_file_custom,
    restore_tl_key_comments_or_lb,
)
from gitlabci_lint.autoformatter.yaml import (
    yaml,
    read_yaml_from_file_safe,
    dump_yaml_to_file,
    dump_yaml_to_str,
    load_safe_yaml,
)


def process_file(filepath: str):
    safe_initial_content = read_yaml_from_file_safe(filepath)

    custom_content, top_level_comments = read_yaml_file_custom(filepath)
    yaml_data = yaml.load(custom_content)
    reorder(yaml_data, ORDERING)
    restore_tl_key_comments_or_lb(data=yaml_data, tl_key_comments=top_level_comments)

    yaml_data_strio = dump_yaml_to_str(yaml_data)
    safe_new_content = load_safe_yaml(yaml_data_strio)

    # This should only be doing reformatting, actual content should never change
    if safe_new_content != safe_initial_content:
        raise Exception("Actual content changed! Reformatting failed")

    content_altered = True  # TODO
    if content_altered:
        dump_yaml_to_file(filepath + "_new.yaml", data=yaml_data)


# def main():
#     parser = argparse.ArgumentParser()
#     parser.add_argument("instancefiles", nargs="+", help="JSON or YAML files to check.")
#
#     args = parser.parse_args()
#
#     order_modified = run_autoformatter(args, ORDERING)
#
#     if order_modified:
#         # pre-commit modifying files should end as a failure
#         # by convention
#         sys.exit(1)
#     else:
#         sys.exit(0)
