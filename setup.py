from setuptools import setup, find_packages

setup(
    name='matchindex',
    version='0.1',
    license='MIT',
    author="Theo Walker",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url='https://github.com/manimino/matchindex',
    keywords='hashbox',
    install_requires=[],
)
