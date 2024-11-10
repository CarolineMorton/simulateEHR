# External imports
import os
from setuptools import find_namespace_packages, setup


with open(os.path.join("src", "VERSION")) as f:
    version = f.read().strip()

setup(
    name="simulateEHR",
    version=version,
    packages=find_namespace_packages(exclude=["tests"]),
    include_package_data=True,
    url="https://github.com/CarolineMorton/simulateEHR",
    description="Python tool for generating simulated EHR datasets",
    author="Caroline Morton",
    author_email="caroline@parakeetconsulting.com",
    python_requires=">=3.9",
    install_requires=["polars"],
)