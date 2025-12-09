"""
F.A.R.F.A.N Pipeline Setup
Minimal setup for development installation
"""

from setuptools import setup, find_packages

setup(
    name="farfan-pipeline",
    version="1.0.0",
    description="Framework for Advanced Retrieval of Administrative Narratives",
    python_requires=">=3.12",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        # Core dependencies - minimal set
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "ruff>=0.1.0",
            "mypy>=1.0.0",
        ],
    },
)
