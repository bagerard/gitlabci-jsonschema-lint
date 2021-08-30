from typing import List

from ruamel.yaml import CommentedMap

from gitlabci_lint.autoformatter import yaml, read_yaml_from_file, dump_yaml_to_file

_AnyJob_ = "_AnyJob_"

ORDERING = {
    "stages": True,
    "workflow": True,
    "default": True,
    "variables": True,
    "image": True,
    "cache": True,
    _AnyJob_: {
        "extends": True,
        "stage": True,
        "image": True,
        "tags": True,
        "only": True,
        "rules": True,
        # "services": True,
        "variables": True,
        "script": True,
        "after_script": True,
        "artifacts": True,
    },
}


YAML_ROOT = 0


def reorder(data: CommentedMap, ordering: dict, level=YAML_ROOT) -> bool:
    modified = False

    merged_keys = {k for _, mdict in data.merge for k in mdict.keys()}
    present_ordering_keys = [
        k for k in ordering.keys() if k in data and k not in merged_keys
    ]
    rest_data_keys = [
        k for k in data if k not in present_ordering_keys and k not in merged_keys
    ]

    if data.merge:
        print(f"Skip merged data entirely as reordering is buggy")
        return False

    for dkey in present_ordering_keys + rest_data_keys:
        print(f"Checking {dkey}")
        do_reorder_key = False
        do_deeper_reorder = False
        reordering_value = None

        if dkey in present_ordering_keys:
            reordering_value = ordering[dkey]
            do_deeper_reorder = isinstance(reordering_value, dict)
            do_reorder_key = reordering_value is True or (
                do_deeper_reorder and True in reordering_value
            )
        else:
            is_job = (
                isinstance(data[dkey], dict)
                and "script" in data[dkey]
                and level == YAML_ROOT
            )
            if _AnyJob_ in ordering and is_job:
                reordering_value = ordering[_AnyJob_]
                do_deeper_reorder = True

        if do_deeper_reorder:
            print(f"dig in {dkey}")
            assert reordering_value, reordering_value
            deeper_modified = reorder(
                data=data[dkey], ordering=reordering_value, level=level + 1
            )
            modified = modified or deeper_modified

        if do_reorder_key:
            reordering_pos = present_ordering_keys.index(dkey)
            curr_pos = list(data.keys()).index(dkey)
            if reordering_pos == curr_pos:
                print(f"{dkey} already well positioned")
                continue

            print(f"reorder {dkey} from {curr_pos} to {reordering_pos}")
            popped_data = data.pop(dkey)
            data.insert(reordering_pos, dkey, popped_data)
            modified = True

        print(list(data.keys()))
    return modified


def run_autoformatter(filepaths: List[str], ordering: dict):
    modified = False
    for filepath in filepaths:
        yaml_data = read_yaml_from_file(filepath)
        file_modified = reorder(yaml_data, ordering)
        if file_modified:
            print("File order modified!")
            dump_yaml_to_file(filepath + "_new.yml", yaml_data)
        else:
            print("File order was fine!")

        modified = modified or file_modified
    return modified


# run_autoformatter(["/home/bgerard/dev/gitlabci-jsonschema-lint/gitlabci_lint/tests/sample_valid_gitlabci.yml"], ORDERING)
# run_autoformatter(
#     ["/home/bgerard/dev/cpwp-api/.gitlab-ci2.yml"], ORDERING
# )