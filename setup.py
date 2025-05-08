"""
Setup script for the facatura package.
"""

from setuptools import setup, find_packages

setup(
    name="facatura",
    version="0.1.0",
    description="Small local invoicing application intended for use in Romania",
    author="Facatura Team",
    packages=find_packages(),
    install_requires=[],
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    entry_points={
        "console_scripts": [
            "facatura=facatura.cli:main",
        ],
    },
)