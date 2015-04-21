from setuptools import setup, find_packages

setup(name='pyschedule',
      version='0.1.3.1',
      description='A python package to formulate and solve resource-constrained scheduling problems: flow- and job-shop, travelling salesman, vehicle routing and all kind of combinations',
      url='https://github.com/timnon/pyschedule',
      author='Tim Nonner',
      author_email='tim@nonner.de',
      license='Apache 2.0',
      packages=['pyschedule','pyschedule.solvers','pyschedule.plotters'],
      package_data={'': ['pyschedule.mod']},
      package_dir={'':'src'},
      include_package_data=True,
      install_requires=['pulp'])


