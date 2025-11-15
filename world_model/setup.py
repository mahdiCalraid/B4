from setuptools import setup, find_packages

setup(
    name="world_model",
    version="0.1.0",
    description="O3-lite world model system - waterfall of agents for event extraction",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.10",
    install_requires=[
        line.strip()
        for line in open("requirements.txt")
        if line.strip() and not line.startswith("#")
    ],
    entry_points={
        "console_scripts": [
            "wm-ingest=ingestion.cli:main",
            "wm-api=api.server:run_server",
        ],
    },
)