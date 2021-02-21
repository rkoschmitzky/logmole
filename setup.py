from setuptools import setup, find_packages


classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "Intended Audience :: System Administrators",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python",
    "Programming Language :: Python :: 2",
    "Programming Language :: Python :: 2.6",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.7",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: Utilities",
    "Topic :: System :: Logging",
    "Topic :: System :: Monitoring",
    "Topic :: Text Processing :: Filters"
]


setup(
    name="logmole",
    version="0.9.0",
    author="Rico Koschmitzky",
    author_email="contact@ricokoschmitzky.com",
    classifiers=classifiers,
    packages=find_packages("src"),
    package_dir={"": "src"},
    url='https://github.com/rkoschmitzky/logmole',
    license="MIT",
    description='An Extendable and Versatile Logparsing System',
    test_suite="tests"
)