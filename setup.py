
import sys
if sys.version_info[0] < 3:
    import __builtin__ as builtins
else:
    import builtins
builtins.__SCT_TOOLKIT_SETUP__ = True

from setuptools import setup, find_packages
import sct_toolkit

VERSION = sct_toolkit.__version__

setup(name='sct_toolkit',
      version=VERSION,
      description='Python analysis tools for CTA pSCT',
      author='Miles J. Winter',
      author_email='milesjwinter@gmail.com',
      packages=find_packages(),
      install_requires=['numpy','matplotlib','bokeh','h5py',
                        'sphinx','sphinx_rtd_theme'])
