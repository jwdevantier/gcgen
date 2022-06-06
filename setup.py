import os
from setuptools import setup, find_packages
from pathlib import Path


PKG_ROOT = Path(__file__).parent


README = (PKG_ROOT / "README.md").read_text()


version = os.getenv("GITHUB_REF", "refs/tags/0.0.1").split("/")[-1]
print(f"Building version: {version}")

setup(
    name="gcgen",
    description="generate code in any language or format",
    long_description=README,
    long_description_content_type="text/markdown",
    classifiers=["Framework :: Pytest"],
    version=version,
    author="Jesper Wendel Devantier",
    author_email="jwd@defmacro.it",
    url="https://github.com/jwdevantier/codegen",
    packages=find_packages(exclude=["tests"]),
    install_requires=[],
    entry_points={"console_scripts": ["gcgen = gcgen.__main__:main"]},
    license="MIT",
    options={"bdist_wheel": {"universal": True}},
)
