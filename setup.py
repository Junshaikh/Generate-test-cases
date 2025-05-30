from setuptools import setup, find_packages

setup(
    name="generate-test-cases",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "google-generativeai",
        "requests",
        "python-dotenv"
    ],
    entry_points={
        "console_scripts": [
            "generate-tests = generate_tests.cli:main"
        ]
    },
)

