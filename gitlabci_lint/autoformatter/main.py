import argparse
import sys

from gitlabci_lint.autoformatter.autoformatter import ORDERING, reorder
from gitlabci_lint.autoformatter.custom_reader import (
    read_yaml_file_custom,
    restore_tl_key_comments_or_lb,
)
from gitlabci_lint.autoformatter.yaml import (
    yaml,
    dump_yaml_to_file,
    dump_yaml_to_str,
    load_safe_yaml,
    read_file_content,
)


def _autoformat_file(filepath: str):
    custom_content, top_level_comments = read_yaml_file_custom(filepath)
    yaml_data = yaml.load(custom_content)
    reorder(yaml_data, ORDERING)
    restore_tl_key_comments_or_lb(data=yaml_data, tl_key_comments=top_level_comments)
    return yaml_data


def process_file(filepath: str) -> bool:
    initial_content = read_file_content(filepath)

    new_yaml_data = _autoformat_file(filepath)
    new_content = dump_yaml_to_str(new_yaml_data)

    # This should only be doing reformatting, actual content should never change
    if load_safe_yaml(initial_content) != load_safe_yaml(new_content):
        raise Exception("Actual content changed! Reformatting failed")

    file_modified = new_content != initial_content
    if file_modified:
        dump_yaml_to_file(filepath + "_new.yaml", data=new_yaml_data)

    return file_modified


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "instancefiles", nargs="+", help="YAML gitlab-ci.yml files to check"
    )

    args = parser.parse_args()

    any_file_modified = False
    for instancefile in args.instancefiles:
        print(f"Processing {instancefile}...")
        curr_file_modified = process_file(instancefile)
        if curr_file_modified:
            print(f"Modification were applied")
        else:
            print(f"No modification were required")
        any_file_modified = any_file_modified or curr_file_modified

    if any_file_modified:
        # pre-commit modifying files should end as a failure
        # by convention
        sys.exit(1)
    else:
        sys.exit(0)
