from setuptools import setup

setup(name='pyschedule',
      version='0.1.2',
      description='A python package to formulate and solve resource-constrained scheduling problems: flow- and job-shop, travelling salesman, vehicle routing and all kind of combinations',
      url='https://github.com/timnon/pyschedule',
      author='Tim Nonner',
      author_email='tim@nonner.de',
      license='Apache 2.0',
      packages=['pyschedule'],
      package_dir={'':'src'},
      install_requires=['pulp'])

