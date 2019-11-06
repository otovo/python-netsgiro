import re

from setuptools import find_packages, setup


with open('netsgiro/__init__.py') as fh:
    metadata = dict(re.findall("__([a-z]+)__ = '([^']+)'", fh.read()))


with open('README.rst') as fh:
    long_description = fh.read()


setup(
    name='netsgiro',
    version=metadata['version'],
    description='File parsers for Nets AvtaleGiro and OCR Giro',
    long_description=long_description,
    url='https://netsgiro.readthedocs.io/',
    author='Otovo AS',
    author_email='jodal+netsgiro@otovo.com',
    license='Apache License, Version 2.0',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    keywords='avtalegiro ocr giro',
    packages=find_packages(exclude=['tests', 'tests.*']),
    python_requires='>=3.5',
    install_requires=['attrs >= 17.4'],
    extras_require={
        'dev': [
            'check-manifest',
            'flake8',
            'flake8-import-order',
            'hypothesis',
            'mypy',
            'pydocstyle',
            'pytest',
            'pytest-xdist',
            'sphinx',
            'sphinx_rtd_theme',
            'tox',
        ]
    },
)
