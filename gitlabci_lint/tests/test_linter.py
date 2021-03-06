import os
from collections import namedtuple

from gitlabci_lint.linter import lint_it, run_check
from gitlabci_lint.tests import TESTS_DIR


VALID_SAMPLE_GITLABCI = os.path.join(TESTS_DIR, "sample_valid_gitlabci.yml")
INVALID_SAMPLE_GITLABCI = os.path.join(TESTS_DIR, "sample_invalid_gitlabci.yml")

args_tuple = namedtuple("args", "instancefiles")


def test_lint_it_valid():
    schema = {
        "type": "object",
        "properties": {
            "price": {"type": "number"},
            "name": {"type": "string"},
        },
    }
    doc = {"name": "Eggs", "price": 34.99}
    assert not lint_it(doc, schema)


def test_lint_it_invalid():
    schema = {
        "type": "object",
        "properties": {
            "price": {"type": "number"},
            "firstname": {"type": "string"},
            "lastname": {"type": "string"},
        },
        "required": ["price", "firstname", "lastname"],
    }
    doc = {"name": "Eggs", "price": 34.99}
    errors = lint_it(doc, schema)
    assert errors == [
        ("<root>", "'firstname' is a required property"),
        ("<root>", "'lastname' is a required property"),
    ]


def test_run_check_valid():
    args = args_tuple(instancefiles=[VALID_SAMPLE_GITLABCI])
    success, messages = run_check(args)
    assert success is True
    assert messages == ["ok -- validation done"]


def test_run_check_invalid():
    args = args_tuple(instancefiles=[INVALID_SAMPLE_GITLABCI])
    success, messages = run_check(args)
    assert success is False
    assert messages == [
        "Schema validation errors were encountered.",
        "  "
        f"\x1b[0;33m{INVALID_SAMPLE_GITLABCI}::test.artifacts: "
        "\x1b[0m['not supposed to be a list'] is not of type 'object'",
        "  "
        f"\x1b[0;33m{INVALID_SAMPLE_GITLABCI}::test.script: "
        "\x1b[0m{'some_key': 'wont work'} is not valid under any of the given schemas",
    ]
