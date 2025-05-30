from setuptools import setup, find_packages

setup(
    name="generate-tests",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "google-generativeai",
        "requests"
    ],
    entry_points={
        "console_scripts": [
            "generate-tests=generate_tests.cli:main"
        ],
    },
)
