"""
Setup configuration for Red Hat Catalog Image Reporter
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name="rh-report",
    version="1.0.0",
    description="CLI tool to query and report Red Hat Catalog container images",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Tu Nombre",
    author_email="tu@email.com",
    url="https://github.com/tuusuario/rh-report",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "pandas>=2.0.0",
        "openpyxl>=3.1.0",
        "requests>=2.31.0",
        "tqdm>=4.66.0",
        "click>=8.1.0",
        "urllib3>=2.0.0",
    ],
    entry_points={
        "console_scripts": [
            "rh-report=rh_report.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords="redhat container images catalog openshift",
    project_urls={
        "Bug Reports": "https://github.com/tuusuario/rh-report/issues",
        "Source": "https://github.com/tuusuario/rh-report",
    },
)
