=====
Clast
=====

Clast is a Python wrapper of the unstable interface of the Clang AST Matchers
library. 

Existing tools in this space make good use of libclang to build rapid
prototypes for exploring the Clang AST, however, several important tools
(for example code rewriting) are not available from libclang. 

|license| |build| 

Usage
=====

DynTypedMatcher
---------------

Example of creating a dynamically typed AST node matcher using the dynamic
parser and dumping the node.

.. code:: python

	import sys
	from clast import *

	class MyMatchCallback(MatchCallback):
	    def __init__(self, *args, **kwargs):
		super(MyMatchCallback, self).__init__()

	    def run(self, result):
		cls = result.GetNode('cls').get(CXXRecordDecl)
		cls.dump()

	if __name__ == "__main__":
	    callback = MyMatchCallback()
	    m = parseMatcherExpression('cxxRecordDecl().bind("cls")')
	    finder = MatchFinder()
	    finder.addDynamicMatcher(m, callback)
	    matchString('class X;', finder, '-std=c++11', 'input.cpp')

Installation
============

To install Clast, you'll need to:

1. Install a c++11 compliant compiler
2. Install a compatible version of Clang and LLVM 
3. Set some environment variables
4. Install the pybind11 package
5. Install Clast

Ubuntu 14.04 (Trusty)
---------------------

To compile under Ubuntu 14.04 (Trusty), you'll need to get an updated version of LLVM:

.. code:: console

    wget -O - http://llvm.org/apt/llvm-snapshot.gpg.key | sudo apt-key add -
    echo "deb http://llvm.org/apt/trusty/ llvm-toolchain-trusty-3.8 main" | sudo tee -a /etc/apt/sources.list
    sudo apt-get update -qq
    sudo apt-get install -y clang-3.8 libclang-common-3.8-dev libclang-3.8-dev llvm-3.8-dev liblldb-3.8-dev python-clang-3.8

Then, set your environment variables:

.. code:: console

    export LLVM_HOME=/usr/lib/llvm-3.8
    export LD_LIBRARY_PATH=$LLVM_HOME/lib

Finally, install pybind11 and Clast. It is strongly recommended that clast be
installed with the verbose flag on to show compilation progress

.. code:: console

    pip install pybind11
    pip install -v clast

Updating the Bindings
---------------------

Given the breadth of the Clang AST matchers API, it isn't feasible to attempt
to maintain hand rolled bindings, instead Clast bootstraps itself using the
libclang library, and generates the pybind11 wrappers as required.

In cases where the bindings are stale, or do not compile correctly, you can try
to rebuild the them using the included clastgen.py script.  

It is hoped that future revisions of Clast will rapidly become self-hosting
(one version of Clast will be able to build successive versions).


Limitations
===========

- Clast does not support all versions of Clang - focus is on the stable and development
  branches of the Clang compiler (currently 3.8 and 3.9).
- Clast relies on the C++ reference counting scheme to collect memory in
  preference to using the Python reference counting.  This is in part a
  technical limitation of the Clang AST Nodes having private destructors, but is also in
  part by design because Clast scripts are intended to facilitate prototyping, not act
  as a replacement for the AST Matchers API. 
- Clast installs are quite slow and memory intensive, ensure that you have at least 2Gb or RAM
  free, compile times are on the order of 30 seconds.
- Clast has not been tested on Windows - it's likely that small changes would allow it to function
  on that platform.
- Clast will not compile if you do not have the development headers for Clang and LLVM installed.
- Out of the box, Clast will fail to link if LLVM has not been configured to
  generate a shared library.  Future work may include overcoming this issue.
- Clast is known to not work correctly if Clang and LLVM have been compiled
  with the -fno-rtti option.  This means that (at least some) of the Ubuntu
  binaries from `llvm.org`_ cannot be used with Clast.
- Clast disables pybinds C++14 support - future work will involve improving tests to use platforms 
  that ship with C++14 compilers and standard libraries by default.  This will help reduce the 
  size of binaries produced.
- Compiling Clang bindings is on the order of 10 times slower with
  optimisations enabled.  By default Clast builds bindings with optimisations
  disabled - this is considered an acceptable, given that the primary goal of
  the project is to facilitate rapid prototying. Furthermore, Clast code should
  be easy to translate to equivalent C++ constructs if performance does become
  and issue.
- Some issues have been observed with older Python releases, it is strongly
  recommended that you use an up-to-date version of Python (2.7.11)

Acknowledgements
================

This project builds on the excellent work of the LLVM team and the University of
Illinois at Urbana-Champaign, but is in no way affiliated with either.

Some parts of clasts setup.py were derived from the BSD licensed pybind
`python_example`_, Copyright (c) 2016 the Pybind Development Team, All rights
reserved. 

The need for a tool to make the Clang AST matchers library available from
Python was inspired by Christian Schafmeister's work on `clasp`_

.. _pybind11: https://github.com/pybind/pybind11
.. _llvm.org: https://llvm.org
.. _clasp: https://github.com/drmeister/clasp
.. _python_example: https://github.com/pybind/python_example

.. |license| image:: https://img.shields.io/badge/license-MIT-blue.svg
   :target: https://raw.githubusercontent.com/andrewwalker/glud/master/LICENSE
   :alt: MIT License

.. |build| image:: https://travis-ci.org/AndrewWalker/clast.svg?branch=master
   :target: https://travis-ci.org/AndrewWalker/clast
   :alt: Continuous Integration


