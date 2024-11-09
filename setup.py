#!/usr/bin/python3

from setuptools import setup

setup(
    name="byog",
    version="1.0",
    packages=["byog"],
    entry_points={"console_scripts": ["byog = byog.cli:main"]},
)
