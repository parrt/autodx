from setuptools import setup, find_packages

setup(
    name='autodx',
    version='0.1',
    url='https://github.com/parrt/autodx',
    license='BSD',
#    py_modules=['.autodx', '.autodx.viz'],
    packages=find_packages(exclude=['test']),
    author='Terence Parr',
    author_email='parrt@cs.usfca.edu',
    install_requires=['graphviz'],
    description='A package for automatically computing gradients from Python code, with an emphasis on education rather than performance',
    keywords='visualization differentiation gradients',
    python_requires='>=3',
    classifiers=['License :: OSI Approved :: BSD License',
                 'Intended Audience :: Developers']
)
