from setuptools import find_packages, setup

setup(
    name="papercraft-open",
    version="1.0.0",
    packages=find_packages(include=["library*"]),
    entry_points={
        "console_scripts": [
            "papercraft=library.cli_main:main",
        ],
    },
)
