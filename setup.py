# Some parts of this file Copyright (c) 2016 the Pybind Development Team,
# and are subject to the licensing terms of that project see LICENSE.pybind_python_example
import sys
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
import setuptools
import subprocess
import os


def read(filename):
    path = os.path.join(os.path.dirname(__file__), filename)
    contents = open(path).read()
    return contents


def llvm_config(arg):
    llvm_home = os.environ['LLVM_HOME']
    llvm_config = os.path.join(llvm_home, 'bin', 'llvm-config')
    res = subprocess.check_output([llvm_config, arg]).split()
    if sys.version_info.major >= 3:
        return [p.decode('utf-8') for p in res]
    return res

LLVM_CFLAGS  = llvm_config('--cflags')
LLVM_LIBS    = [ lib[2:] for lib in llvm_config('--libs') ]

def clang_libraries():
    libraries = [
        'clangAST',
        'clangAnalysis',
        'clangBasic',
        'clangDriver',
        'clangEdit',
        'clangFrontend',
        'clangFormat',
        'clangFrontendTool',
        'clangLex',
        'clangParse',
        'clangSema',
        'clangEdit',
        'clangASTMatchers',
        'clangRewrite',
        'clangRewriteFrontend',
        'clangStaticAnalyzerFrontend',
        'clangStaticAnalyzerCheckers',
        'clangStaticAnalyzerCore',
        'clangSerialization',
        'clangToolingCore',
        'clangTooling',
    ]
    libraries = ['-l' + lib for lib in libraries ]
    return ['-Wl,--start-group'] + libraries + ['-Wl,--end-group']

class get_pybind_include(object):
    """Helper class to determine the pybind11 include path
    The purpose of this class is to postpone importing pybind11
    until it is actually installed, so that the ``get_include()``
    method can be invoked. """

    def __init__(self, user=False):
        self.user = user

    def __str__(self):
        import pybind11
        return pybind11.get_include(self.user)


ext_modules = [
    Extension(
        '_clast',
        [
            'src/modulemain.cpp',
            'src/toolmain.cpp'
        ],
        extra_compile_args=LLVM_CFLAGS,
        libraries=LLVM_LIBS ,
        extra_link_args=clang_libraries(),
        library_dirs=[
            os.path.join(os.environ['LLVM_HOME'], 'lib')
        ],
        include_dirs=[
            # Path to pybind11 headers
            get_pybind_include(),
            get_pybind_include(user=True),
            os.path.join(os.environ['LLVM_HOME'], 'include')
        ],
        language='c++'
    ),
]


def has_flag(compiler, flagname):
    """Return a boolean indicating whether a flag name is supported on
    the specified compiler.
    """
    import tempfile
    with tempfile.NamedTemporaryFile('w', suffix='.cpp') as f:
        f.write('int main (int argc, char **argv) { return 0; }')
        try:
            compiler.compile([f.name], extra_postargs=[flagname])
        except setuptools.distutils.errors.CompileError:
            return False
    return True


def cpp_flag(compiler):
    """Return the -std=c++[11/14] compiler flag.
    The c++14 is prefered over c++11 (when it is available).
    """
    if has_flag(compiler, '-std=c++14'):
        return '-std=c++14'
    elif has_flag(compiler, '-std=c++11'):
        return '-std=c++11'
    else:
        raise RuntimeError('Unsupported compiler -- at least C++11 support '
                           'is needed!')


class BuildExt(build_ext):
    """A custom build extension for adding compiler-specific options."""
    c_opts = {
        'msvc': ['/EHsc'],
        'unix': [],
    }

    if sys.platform == 'darwin':
        c_opts['unix'] += ['-stdlib=libc++', '-mmacosx-version-min=10.7']

    def build_extensions(self):
        ct = self.compiler.compiler_type
        opts = self.c_opts.get(ct, [])
        if ct == 'unix':
            opts.append(cpp_flag(self.compiler))
            if has_flag(self.compiler, '-fvisibility=hidden'):
                opts.append('-fvisibility=hidden')
        for ext in self.extensions:
            ext.extra_compile_args = opts
        build_ext.build_extensions(self)


setup(
    name         = "clast",
    version      = "0.0.1",
    description  = "Generate pybind11 bindings for the unstable interface of the Clang AST Matchers library",
    long_description = read('README.rst'),
    author       = "Andrew Walker",
    author_email = "walker.ab@gmail.com",
    url          = "http://github.com/AndrewWalker/clast",
    license      = "MIT",
    setup_requires  = ['glud>=0.3'],
    install_requires= ['pybind11>=1.7'],
    packages     = {'clast': 'clast'}, 
    cmdclass     = {'build_ext': BuildExt},
    ext_modules  = ext_modules,
    classifiers  = [
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Operating System :: POSIX :: Linux',
        'Topic :: Software Development :: Code Generators',
    ],
    zip_safe=False
)

