from setuptools import setup, find_packages

setup(
    name="llm_student",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        # List your project's dependencies here.
        # Examples:
        # 'numpy>=1.18.1',
        # 'pandas==1.0.3',
    ],
    # Include additional metadata about your project
    author="Austin Lipe",
    author_email="your.email@example.com",
    description="Cheat on your Homework",
    # Add more fields as needed
)
