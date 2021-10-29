# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open("README.md") as f:
    readme = f.read()

with open("LICENSE") as f:
    project_license = f.read()

setup(
    name="RatS",
    version="0.11.5",
    description="Movie ratings synchronisation",
    long_description=readme,
    author="Sebastian Schreck",
    author_email="github@stegschreck.de",
    url="https://github.com/StegSchreck/RatS",
    license=project_license,
    packages=find_packages(exclude=("tests", "docs")),
    py_modules=["RatS"],
)
