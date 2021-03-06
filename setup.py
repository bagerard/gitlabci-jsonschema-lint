from setuptools import setup

INSTALL_REQUIRES = [
    "jsonschema>=3.0.0",
    "ruamel.yaml>=0.16.0",
]

VERSION = "0.0.3"

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="gitlabci-jsonschema-lint",
    version=VERSION,
    maintainer="Bastien Gerard",
    maintainer_email="bast.gerard@gmail.com",
    url="https://github.com/bagerard/gitlabci-jsonschema-lint",
    keywords="gitlab-ci linter ",
    license="MIT License",
    description="Python library to lint .gitlab-ci.yml files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=["gitlabci_lint"],
    install_requires=INSTALL_REQUIRES,
    entry_points={
        "console_scripts": [
            "gitlabci-jsonschema-linter = gitlabci_lint.linter:main",
            "gitlabci-autoformatter = gitlabci_lint.autoformatter.main:main",
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Quality Assurance",
    ],
    include_package_data=True,
)
