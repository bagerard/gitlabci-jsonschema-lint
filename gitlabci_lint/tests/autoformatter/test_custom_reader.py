import os
import textwrap
from io import StringIO

from ruamel.yaml import YAML

from gitlabci_lint.autoformatter.custom_reader import (
    read_yaml_file_custom,
    read_yaml_stream_custom,
    restore_tl_key_comments_or_lb,
)
from gitlabci_lint.tests import TESTS_DIR
from gitlabci_lint.tests.autoformatter.utils import get_dumped_yaml

yaml = YAML()


VALID_SAMPLE_GITLABCI = os.path.join(TESTS_DIR, "sample_valid_gitlabci.yml")


def YamlString(triple_quoted_str):
    s = textwrap.dedent(triple_quoted_str)
    return StringIO(s)


# read_yaml_file_custom
def test_read_yaml_file_custom():
    new_content, top_level_comments = read_yaml_file_custom(VALID_SAMPLE_GITLABCI)
    assert isinstance(new_content, str)
    assert top_level_comments == {}


# read_yaml_stream_custom
def test_read_yaml_stream_custom__top_level_blank_lines__removed():
    yaml_str = YamlString(
        """\

    key1:
      - value1


    key2:
      - value2
    """
    )
    new_content, top_level_comments = read_yaml_stream_custom(yaml_str.readlines())
    expected_content = YamlString(
        """\
    key1:
      - value1
    key2:
      - value2
    """
    )
    assert new_content == expected_content.getvalue()
    assert not top_level_comments


def test_read_yaml_stream_custom__top_level_comments_simple__collected():
    yaml_str = YamlString(
        """\
    # key1-comment
    key1:
      - value1
    # key2-comment
    key2:
      subkey2: value2
    """
    )
    new_content, top_level_comments = read_yaml_stream_custom(yaml_str.readlines())
    expected_content = YamlString(
        """\
    key1:
      - value1
    key2:
      subkey2: value2
    """
    )
    assert new_content == expected_content.getvalue()
    assert top_level_comments == {"key1": "# key1-comment", "key2": "# key2-comment"}


def test_read_yaml_stream_custom__top_level_comments_multiline__collected():
    yaml_str = YamlString(
        """\
    key1:
      - value1
    # key2-comment-line1
    # key2-comment-line2
    key2:
      - value2
    """
    )
    new_content, top_level_comments = read_yaml_stream_custom(yaml_str.readlines())
    expected_content = YamlString(
        """\
    key1:
      - value1
    key2:
      - value2
    """
    )
    assert new_content == expected_content.getvalue()
    assert top_level_comments == {"key2": "# key2-comment-line1\n# key2-comment-line2"}


def test_read_yaml_stream_custom__header_and_first_key_comment__header_remain_first_key_com_collected():
    yaml_str = YamlString(
        """\
    # header

    # key1-comment
    key1:
      - value1
    """
    )
    new_content, top_level_comments = read_yaml_stream_custom(yaml_str.readlines())
    expected_content = YamlString(
        """\
    # header
    key1:
      - value1
    """
    )
    assert new_content == expected_content.getvalue()
    assert top_level_comments == {"key1": "# key1-comment"}


def test_read_yaml_stream_custom__indented_comment__ignored():
    yaml_str = YamlString(
        """\
    key1:
      - value1
      # - value2
    # key2-comment
    key2:
      - value2
    """
    )
    new_content, top_level_comments = read_yaml_stream_custom(yaml_str.readlines())
    expected_content = YamlString(
        """\
    key1:
      - value1
      # - value2
    key2:
      - value2
    """
    )
    assert new_content == expected_content.getvalue()
    assert top_level_comments == {"key2": "# key2-comment"}


def test_read_yaml_stream_custom__whole_section_commented__ignored():
    yaml_str = YamlString(
        """\
    key1:
      - value1

    # key2-comment
    #key2:
    #  - value2

    # key3-comment
    key3: value3
    """
    )
    new_content, top_level_comments = read_yaml_stream_custom(yaml_str.readlines())
    expected_content = YamlString(
        """\
    key1:
      - value1
    # key2-comment
    #key2:
    #  - value2
    key3: value3
    """
    )
    assert new_content == expected_content.getvalue()
    assert top_level_comments == {"key3": "# key3-comment"}


def test_read_yaml_stream_custom__key_with_inline_comment__recognized_and_kept():
    yaml_str = YamlString(
        """\
    # key1-comment
    key1:
      - value1
    # key2-comment
    key2: # some_comment
        subkey2: value2
    """
    )
    new_content, top_level_comments = read_yaml_stream_custom(yaml_str.readlines())
    expected_content = YamlString(
        """\
    key1:
      - value1
    key2: # some_comment
        subkey2: value2
    """
    )
    assert new_content == expected_content.getvalue()
    assert top_level_comments == {"key1": "# key1-comment", "key2": "# key2-comment"}


def test_read_yaml_stream_custom__long_string_cut__ignored():
    yaml_str = YamlString(
        """\
    # key1-comment
    key1:
      subkey1: some_subkey1_string|
    some_more_subkey1_string
    # key2-comment
    key2: # some_comment
        subkey2: value2
    """
    )
    new_content, top_level_comments = read_yaml_stream_custom(yaml_str.readlines())
    expected_content = YamlString(
        """\
    key1:
      subkey1: some_subkey1_string|
    some_more_subkey1_string
    key2: # some_comment
        subkey2: value2
    """
    )
    assert new_content == expected_content.getvalue()
    assert top_level_comments == {"key1": "# key1-comment", "key2": "# key2-comment"}


def test_read_yaml_stream_custom__fancy_top_level_section__recognized():
    yaml_str = YamlString(
        """\
    ##########
    # section1
    ##########
    key1:
      - value1

    ##########
    # section2
    ##########
    key2:
        subkey2: value2
    """
    )
    new_content, top_level_comments = read_yaml_stream_custom(yaml_str.readlines())
    expected_content = YamlString(
        """\
    key1:
      - value1
    key2:
        subkey2: value2
    """
    )
    assert new_content == expected_content.getvalue()
    assert top_level_comments == {
        "key1": "##########\n# section1\n##########",
        "key2": "##########\n# section2\n##########",
    }


# restore_tl_key_comments_or_lb
def test_restore_tl_key_comments_or_lb__simple_case__comment_restored():
    yaml_str = """\
    first_name: Art
    """
    data = yaml.load(yaml_str)
    restore_tl_key_comments_or_lb(
        data, tl_key_comments={"first_name": "# some_comments"}
    )
    expected_content = YamlString(
        """\
    # some_comments
    first_name: Art
    """
    )
    assert get_dumped_yaml(data) == expected_content.getvalue()


def test_restore_tl_key_comments_or_lb__fancy_section__comment_restored():
    yaml_str = """\
    first_name: Art
    """
    data = yaml.load(yaml_str)
    restore_tl_key_comments_or_lb(
        data, tl_key_comments={"first_name": "##########\n# section1\n##########"}
    )
    expected_content = YamlString(
        """\
    ##########
    # section1
    ##########
    first_name: Art
    """
    )
    assert get_dumped_yaml(data) == expected_content.getvalue()


def test_restore_tl_key_comments_or_lb__header__comment_restored_and_lb_between_header_and_comment():
    yaml_str = YamlString(
        """\
    # header
    first_name: Art
    """
    )
    data = yaml.load(yaml_str)
    restore_tl_key_comments_or_lb(
        data, tl_key_comments={"first_name": "# some_comments"}
    )
    expected_content = YamlString(
        """\
    # header

    # some_comments
    first_name: Art
    """
    )
    assert get_dumped_yaml(data) == expected_content.getvalue()


def test_restore_tl_key_comments_or_lb__first_key_no_comment_no_header__no_lb_added():
    yaml_str = YamlString(
        """\
    first_name: Art
    """
    )
    data = yaml.load(yaml_str)
    restore_tl_key_comments_or_lb(data, tl_key_comments={})
    assert get_dumped_yaml(data) == yaml_str.getvalue()
