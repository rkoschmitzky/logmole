from setuptools import setup, find_packages

version = __import__("src").__version__

classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "Intended Audience :: System Administrators",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python",
    "Programming Language :: Python :: 2",
    "Programming Language :: Python :: 2.6",
    "Programming Language :: Python :: 2.7",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: Utilities",
    "Topic :: System :: Logging",
    "Topic :: System :: Monitoring",
    "Topic :: Text Processing :: Filters"
]


setup(
    name="logmole",
    version=version,
    author='Rico Koschmitzky',
    author_email='contact@ricokoschmitzky.com',
    packages=find_packages("src"),
    package_dir={"": "src"},
    url='https://github.com/rkoschmitzky/logmole',
    license='LICENSE.md',
    description='An Extendable and Versatile Logparsing System',
    long_description=open('README.md').read(),
    test_suite="tests"
)