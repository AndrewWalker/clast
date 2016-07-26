import sys
import os
import subprocess


def clang_version():
    """Get a string that describes the version of the clang compiler 
    """
    llvm_home = os.environ['LLVM_HOME']
    binary = os.path.join(llvm_home, 'bin', 'clang')
    res = subprocess.check_output([binary, '--version']).splitlines()[0]
    if sys.version_info.major >= 3:
        return res.decode('utf-8')
    return res


def llvm_config(arg):
    """Run the llvm_config tool 
    """
    llvm_home = os.environ['LLVM_HOME']
    llvm_config = os.path.join(llvm_home, 'bin', 'llvm-config')
    res = subprocess.check_output([llvm_config, arg]).split()
    if sys.version_info.major >= 3:
        return [p.decode('utf-8') for p in res]
    return res


