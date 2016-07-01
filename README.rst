=====
Clast
=====

Clast is a Python wrapper of the unstable interface of the Clang AST Matchers
library. 

Existing tools in this space make good use of libclang to build rapid
prototypes for exploring the Clang AST, however, several important tools
(for example code rewriting) are not available from libclang. 

|license| 

Installation
============

To install Clast, you'll need to:

1. Install a c++11 compliant compiler
1. Install a compatible version of Clang and LLVM 
2. Set some environment variables
1. Install the pybind11 package
3. Install Clast

Ubuntu 14.04 (Trusty)
---------------------

To compile under Ubuntu 14.04 (Trusty), you'll need to get an updated version of LLVM:

.. code:: console

    wget -O - http://llvm.org/apt/llvm-snapshot.gpg.key | sudo apt-key add -
    echo "deb http://llvm.org/apt/trusty/ llvm-toolchain-trusty-3.8 main" | sudo tee -a /etc/apt/sources.list
    sudo apt-get update -qq
    sudo apt-get install -y python-clang-3.8 libclang1-3.8

Then, set your environment variables:

.. code:: console

    export LLVM_HOME=/usr/lib/llvm-3.8
    export LD_LIBRARY_PATH=$LLVM_HOME/lib

Finally, install pybind11 and Clast

.. code:: console

    pip install pybind11
    pip install clast

Updating the Bindings
---------------------

Given the breadth of the Clang AST matchers API, it isn't feasible to attempt
to maintain hand rolled bindings, instead Clast bootstraps itself using the
libclang library, and generates the pybind11 wrappers as required.

In cases where the bindings are stale, or do not compile correctly, you can try
to rebuild the bindings using the clastgen.py script.


Limitations
===========

- Clast does not support all versions of Clang - focus is on the stable and development
  branches of the Clang compiler (currently 3.8 and 3.9).
- Clast will not compile if you do not have the development headers for 
- Clast is known to not work correctly if Clang and LLVM have been compiled
  with the `-fno-rtti` option.  Some of the official downloads from `llvm.org`
  have this issue.
- It is strongly recommended that you use an up-to-date version of Python
  (2.7.11)

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


