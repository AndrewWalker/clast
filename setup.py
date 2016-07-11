# Some parts of this file Copyright (c) 2016 the Pybind Development Team,
# and are subject to the licensing terms of that project see LICENSE.pybind_python_example
import sys
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
import setuptools
import subprocess
import os
import glob

def llvm_config(arg):
    llvm_home = os.environ['LLVM_HOME']
    llvm_config = os.path.join(llvm_home, 'bin', 'llvm-config')
    res = subprocess.check_output([llvm_config, arg]).split()
    if sys.version_info.major >= 3:
        return [p.decode('utf-8') for p in res]
    return res


def read(filename):
    path = os.path.join(os.path.dirname(__file__), filename)
    contents = open(path).read()
    return contents


CLANG_VERSION = llvm_config('--version')[0].replace('.', '')

# Rely on the llvm flags being compatible with the flags from Python
# In cases where compilation fails, consider examining the verbose logs
# of the build
LLVM_CFLAGS  = [ f for f in llvm_config('--cflags') ] 

# Rely on the dynamic library version of LLVM being present 
# If your version of LLVM is not compiled in this way, you can
# try using llvm_config('--libs'), and adding any omitted libraries
LLVM_LIBS    = ['LLVM'] 

def clang_libraries():
    # Note that this list of libraries is drawn from Eli Bendersky's
    # excellent LLVM-Clang-Samples repository [1]
    # 
    # [1] https://github.com/eliben/llvm-clang-samples
    libraries = [
        'clangAST',
        'clangAnalysis',
        'clangBasic',
        'clangDriver',
        'clangDynamicASTMatchers', 
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
        glob.glob('src/*.cpp') + glob.glob('src/%s/*.cpp' % CLANG_VERSION),
        extra_compile_args=LLVM_CFLAGS,
        libraries=LLVM_LIBS ,
        extra_link_args=clang_libraries(),
        library_dirs=[
            os.path.join(os.environ['LLVM_HOME'], 'lib')
        ],
        include_dirs=[
            'src',
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
            opts.append('-std=c++11')
            opts.append('-O0')
            if has_flag(self.compiler, '-fvisibility=hidden'):
                opts.append('-fvisibility=hidden')
        for ext in self.extensions:
            ext.extra_compile_args += opts
        build_ext.build_extensions(self)


setup(
    name         = "clast",
    version      = "0.0.1rc0",
    description  = "Python bindings for the unstable interface of the Clang AST Matchers library",
    long_description = read('README.rst'),
    author       = "Andrew Walker",
    author_email = "walker.ab@gmail.com",
    url          = "http://github.com/AndrewWalker/clast",
    license      = "MIT",
    install_requires= [
        'pybind11>=1.7'
    ],
    packages     = {'clast': 'clast'}, 
    cmdclass     = {'build_ext': BuildExt},
    ext_modules  = ext_modules,
    classifiers  = [
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Operating System :: POSIX :: Linux',
        'Topic :: Software Development :: Code Generators',
    ],
    zip_safe=False
)

