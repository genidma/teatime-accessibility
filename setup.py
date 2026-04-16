from setuptools import setup, find_packages

setup(
    name="teatime-accessibility",
    version="1.3.6",
    packages=find_packages(where="bin"),
    package_dir={"": "bin"},
    scripts=["bin/teatime.py"],
)