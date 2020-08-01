from setuptools import find_packages
from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="receipt-scanner",
    version="3.0",
    packages=find_packages(),
    package_data={"": ["*.yml"]},
    install_requires=[
        "requests",
        "pillow",
        "pyzbar",
        "pyyaml",
        "matplotlib",
        "pandas",
        "tabulate",
        "click",
    ],
    python_requires=">=3.8",
    entry_points="""
        [console_scripts]
        rc=main:main
    """,
    author="dadyarri",
    author_email="dadyarri@gmail.com",
    description="Receipt scanner",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dadyarri/receipt-scanner",
)
