from setuptools import setup, find_packages

setup(
    name="api_app",  # Replace with your project name
    version="0.1.0",  # Replace with your desired version
    packages=find_packages(where='api_functions'),  # Finds all packages recursively
)