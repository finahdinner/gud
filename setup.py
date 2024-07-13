from setuptools import setup, find_packages

with open("README.md", "r") as f:
    description = f.read()

setup(
    name="gud",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "questionary==2.0.1",
    ],
    entry_points={
        "console_scripts": [
            "gud = gud:main"
        ]
    },
    long_description=description,
    long_description_content_type="text/markdown"
)