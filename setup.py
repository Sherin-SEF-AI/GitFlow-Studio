from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="gitflow-studio",
    version="1.0.1",
    author="Sherin Joseph Roy",
    author_email="sherin.joseph2217@gmail.com",
    description="A comprehensive Git workflow management CLI tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Sherin-SEF-AI/GitFlow-Studio",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Version Control :: Git",
    ],
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "gitflow-studio=studio.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "studio": ["resources/*"],
    },
) 