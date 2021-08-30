from ruamel.yaml import YAML

from gitlabci_lint.autoformatter.autoformatter import reorder
from gitlabci_lint.tests.autoformatter.utils import get_dumped_yaml

yaml = YAML()


def test_reorder__flat_full_match__consistently_reordered():
    yaml_str = """\
    first_name: Art
    occupation: Architect  # This is an occupation comment
    about: Art Vandelay is a fictional character that George invents...
    """
    data = yaml.load(yaml_str)
    ordering = {"occupation": True, "about": True, "first_name": True}
    modified = reorder(data, ordering)
    assert modified is True

    assert get_dumped_yaml(data) == (
        "occupation: Architect      # This is an occupation comment\n"
        "about: Art Vandelay is a fictional character that George invents...\n"
        "first_name: Art\n"
    )


def test_reorder__no_modification_required__modified_false():
    yaml_str = """\
    first_name: Art
    occupation: Architect
    """
    data = yaml.load(yaml_str)
    ordering = {
        "first_name": True,
        "occupation": True,
    }
    modified = reorder(data, ordering)
    assert modified is False


def test_reorder__no_match__modified_false():
    yaml_str = """\
    first_name: Art
    occupation: Architect
    """
    data = yaml.load(yaml_str)
    ordering = {"unknown": True}
    modified = reorder(data, ordering)
    assert modified is False


def test_reorder__nested_reordering_only__top_level_order_unaltered_nested_is_altered():
    yaml_str = """\
     first_name: Art
     occupation: Architect  # This is an occupation comment
     message:
       info: some_ingo
       warning: some_warning
     """
    data = yaml.load(yaml_str)
    ordering = {
        "message": {
            "warning": True,
            "info": True,
        },
    }
    modified = reorder(data, ordering)
    assert modified is True

    assert get_dumped_yaml(data) == (
        "first_name: Art\n"
        "occupation: Architect       # This is an occupation comment\n"
        "message:\n"
        "  warning: some_warning\n"
        "  info: some_ingo\n"
    )


def test_reorder__mixed_reordering__consistently_reordered():
    yaml_str = """\
     first_name: Art
     last_name: Foo
     occupation: Architect  # This is an occupation comment
     message:
       info: some_ingo
       warning: some_warning
     """
    data = yaml.load(yaml_str)
    ordering = {
        "message": {
            True: True,
            "warning": True,
        },
        "occupation": True,
    }
    modified = reorder(data, ordering)
    assert modified is True

    assert get_dumped_yaml(data) == (
        "message:\n"
        "  warning: some_warning\n"
        "  info: some_ingo\n"
        "occupation: Architect       # This is an occupation comment\n"
        "first_name: Art\n"
        "last_name: Foo\n"
    )
