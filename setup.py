from setuptools import setup, find_packages

# for PyPi
with open("README.md", "r", encoding="utf-8") as f:
    description = f.read()

setup(
    name="gud_vcs",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "questionary==2.0.1",
        "termcolor==2.4.0"
    ],
    include_package_data=True,
    package_data={
        'gud': [
            'defaults/config',
            'defaults/gudignore',
            "tutorial/checklist.json",
            "tutorial/tutorial/notes.txt",
            "tutorial/tutorial/README.md",
            "tutorial/tutorial/project/main.py",
            "tutorial/tutorial/project/vars.py",
        ],
    },
    entry_points={
        "console_scripts": [
            "gud = gud:main"
        ]
    },
    long_description=description,
    long_description_content_type="text/markdown"
)