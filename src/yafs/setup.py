# encoding: utf-8
from setuptools import setup, find_packages

#python setup.py sdist upload
setup(
    name='yafs',
    version='0.3.0',
    author='Isaac Lera, Carlos Guerrero',
    author_email='isaac.lera@uib.es, carlos.guerrero@ouib.es',
    description='Yet Another Fog Simulator for Python.',
    long_description='\n\n'.join(
        open(f, 'rb').read().decode('utf-8')
        for f in ['README.md', 'CHANGELOG.md', 'AUTHORS.txt']),
    url='https://yafs.readthedocs.io',
    license='MIT License',
    #packages=find_packages(where='src',exclude=("*.tests",)),
    packages=find_packages(where='src',exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    package_dir={'': 'src'},
    include_package_data=True,

    install_requires=['simpy','pandas','networkx','numpy','tqdm'],
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
