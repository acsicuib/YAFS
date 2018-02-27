# encoding: utf-8
from setuptools import setup, find_packages


setup(
    name='yafs',
    version='0.1',
    author='Isaac Lera, Carlos Guerrero',
    author_email='isaac.lera at uib.es; carlos.guerrero at uib.es',
    description='Yet Another Fog Simulator for Python.',
    long_description='\n\n'.join(
        open(f, 'rb').read().decode('utf-8')
        for f in ['README.md', 'CHANGES.txt', 'AUTHORS.txt']),
    url='https://yafs.readthedocs.io',
    license='MIT License',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    include_package_data=True,
    install_requires=['simpy','pandas','networkx','tinydb'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Scientific/Engineering',
    ],
)