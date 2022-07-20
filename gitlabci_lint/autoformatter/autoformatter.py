from ruamel.yaml import CommentedMap

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
            assert reordering_value, reordering_value
            deeper_modified = reorder(
                data=data[dkey], ordering=reordering_value, level=level + 1
            )
            modified = modified or deeper_modified

        if do_reorder_key:
            reordering_pos = present_ordering_keys.index(dkey)
            curr_pos = list(data.keys()).index(dkey)
            if reordering_pos == curr_pos:
                continue

            print(f"reorder {dkey} from {curr_pos} to {reordering_pos}")
            popped_data = data.pop(dkey)
            data.insert(reordering_pos, dkey, popped_data)
            modified = True

    return modified
