from typing import Dict

from ruamel.yaml import CommentedMap


def read_yaml_file_custom(filepath: str):
    with open(filepath, "r") as fin:
        custom_content, top_level_comments = read_yaml_stream_custom(fin.readlines())
    return custom_content, top_level_comments


def read_yaml_stream_custom(yaml_stream):
    top_level_comments = {}
    file_content = []

    comments_block = []
    for line in yaml_stream:
        line_is_empty = not line.strip(" \n")

        if line_is_empty and not comments_block:
            # drops empty lines outside of comments block
            continue

        if line.startswith(" ") or line_is_empty:
            # Line is indented, assume it is a key or indented-comment
            file_content.extend(comments_block)
            comments_block = []
            if not line_is_empty:
                file_content.append(line)
            continue

        is_top_level_key = (
            ":" in line and "#" not in line.split(":")[0]
        )  # Account for inline comment on the key
        if is_top_level_key:
            key = line.split(":")[0]
            if comments_block:
                top_level_comments[key] = "".join(comments_block).strip("\n")
            comments_block = []
            file_content.append(line)
        elif line.startswith("#"):
            comments_block.append(line)
        else:
            # Occurs for instance with multi-line strings (using "|" in yaml)
            file_content.append(line)
    return "".join(file_content), top_level_comments


def restore_tl_key_comments_or_lb(
    data: CommentedMap, tl_key_comments: Dict[str, str]
) -> None:
    LB = "\n"  # line break
    yaml_contain_header_comment = data.ca.comment and data.ca.comment[1]
    for key_idx, key in enumerate(data.keys()):
        tl_comment = tl_key_comments.get(key, "")
        tl_comment = (
            tl_comment
            if key_idx == 0 and not yaml_contain_header_comment
            else LB + tl_comment
        )
        data.yaml_set_comment_before_after_key(
            key=key,
            before=tl_comment,
        )

    # Comments get prepended by "# " automatically by the lib
    # so we fix that back...
    for key, com_tokens_lists in data.ca.items.items():
        for com_tokens in com_tokens_lists:
            if com_tokens:
                for ct in com_tokens:
                    if ct.value.startswith("# #"):
                        ct.value = ct.value[2:]
