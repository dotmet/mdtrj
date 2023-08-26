from setuptools import setup, find_packages

__version__ = "0.0.1"

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name="MDTrj",
    version=__version__,
    author="Even Wong",
    author_email="evenwong@stu.cdut.edu.cn",
    url="https://github.com/dotmet/mdtrj",
    description="A trajectory parser",
    long_description_content_type='text/markdown',
    long_description=long_description,
    extras_require={},
    packages = find_packages(),
    zip_safe=False,
    python_requires=">=3.1",
    install_requires = [
    'matplotlib',
    'numpy',
    'scipy',
    'numba',
    'gsd',
    'memory_profiler',
    'seaborn',
    'fresnel',
    'pillow',
    'tqdm',
    ],
)
