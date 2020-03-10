import os

from setuptools import find_packages, setup

here = os.path.abspath(os.path.dirname(__file__))

about: dict = {}
with open(os.path.join(here, "stackoverflow_answers", "__VERSION__.py")) as f:
    exec(f.read(), about)

setup(
    name="stackoverflow_answers",
    version=about["__version__"],
    description="Code for answers I've provided on SO.",
    url="https://github.com/5uper5hoot/stackoverflow_answers",
    author="Peter Schutt",
    author_email="peter@topsport.com.au",
    license=None,
    packages=find_packages(
        include=["stackoverflow_answers", "stackoverflow_answers.*"]
    ),
    zip_safe=False,
    install_requires=[],
)