from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="dj",
    version="1.0.0",
    author="Maximiliano Alarcon",
    author_email="",
    description="Librería Python para manejo de documentos tributarios chilenos",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/maximiliano-alarcon/dj",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Office/Business :: Financial",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
        "lxml>=4.6.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.900",
        ],
    },
    keywords="sii documentos tributarios chile dte facturacion electronica",
    project_urls={
        "Bug Tracker": "https://github.com/maximiliano-alarcon/dj/issues",
        "Documentation": "https://dj.readthedocs.io",
        "Source Code": "https://github.com/maximiliano-alarcon/dj",
    },
)
