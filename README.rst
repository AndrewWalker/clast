=====
Clast
=====

Overview
========

Clast is a tool to generate `pybind11`_ bindings for the unstable interface of
the Clang AST Matchers library. 

Existing tools in this space make good use of libclang to build rapid
prototypes for exploring the Clang AST, however, several important tools
(for example code rewriting) are not available from libclang. 

**Clast is currently being bootstrapped - expect rapid change while the
prototype evolves into something more suitable for use in production**

|license| 

Prerequisites
=============

Install a recent version of Clang and the python libclang bindings. On Ubuntu
you can install pre-built binaries from the llvm repositories:

.. code:: console

    wget -O - http://llvm.org/apt/llvm-snapshot.gpg.key | sudo apt-key add -
    echo "deb http://llvm.org/apt/trusty/ llvm-toolchain-trusty-3.8 main" | sudo tee -a /etc/apt/sources.list
    sudo apt-get update -qq
    sudo apt-get install -y python-clang-3.8 libclang1-3.8

Make sure that libclang.so is on your loader path.

.. code:: console

    sudo ln -s /usr/lib/llvm-3.8/lib/libclang-3.8.so.1 /usr/local/lib/libclang-3.8.so
    sudo ln -s /usr/lib/llvm-3.8/lib/libclang.so.1 /usr/local/lib/libclang.so
    export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH


Installing
==========

You can install the latest stable version from Github

.. code:: console 

    $ pip install git+git://github.com/AndrewWalker/clast.git


Acknowledgements
================

This project is in no way affiliated with the LLVM Team or the University of
Illinois at Urbana-Champaign.

The need for a tool like Clast was inspired by Christian Schafmeister's work on `clasp`_

.. _pybind11: https://github.com/pybind/pybind11
.. _clasp: https://github.com/drmeister/clasp

.. |license| image:: https://img.shields.io/badge/license-MIT-blue.svg
   :target: https://raw.githubusercontent.com/andrewwalker/glud/master/LICENSE
   :alt: MIT License


