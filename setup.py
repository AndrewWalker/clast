from setuptools import setup, find_packages
import os


def read(filename):
    path = os.path.join(os.path.dirname(__file__), filename)
    contents = open(path).read()
    return contents


setup(
    name         = "clast",
    version      = "0.0.1",
    description  = "Generate pybind11 bindings for the unstable interface of the Clang AST Matchers library",
    long_description = read('README.rst'),
    author       = "Andrew Walker",
    author_email = "walker.ab@gmail.com",
    url          = "http://github.com/AndrewWalker/clast",
    license      = "MIT",
    packages     = find_packages(), 
    classifiers  = [
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Operating System :: POSIX :: Linux',
        'Topic :: Software Development :: Code Generators',
    ],
    tests_require=['unittest2'],
    test_suite='unittest2.collector'
)

