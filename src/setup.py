from setuptools import setup, find_packages

setup(
    name='pyschedule',
    version='0.2.26',
    description='A python package to formulate and solve resource-constrained scheduling problems',
    url='https://github.com/timnon/pyschedule',
    author='Tim Nonner',
    author_email='tim@nonner.de',
    license='Apache 2.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=['pulp']
)
