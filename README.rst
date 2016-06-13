=====
Clast
=====

Clast is a tool to generate `pybind11`_ bindings for the unstable interface of
the Clang AST Matchers library. 

Existing tools in this space make good use of libclang to build rapid
prototypes for exploring the Clang AST, however, several important tools
(for example code rewriting) are not available from libclang. 

|license| 

Installation
============

To compile Clast, you'll need to:

1. Install Clang and LLVM
2. Set some environment variables
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

Finally, install Clast

.. code:: console

    pip install clast



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
.. _clasp: https://github.com/drmeister/clasp
.. _python_example: https://github.com/pybind/python_example

.. |license| image:: https://img.shields.io/badge/license-MIT-blue.svg
   :target: https://raw.githubusercontent.com/andrewwalker/glud/master/LICENSE
   :alt: MIT License


