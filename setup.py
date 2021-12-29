from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as f:
    README = f.read()

with open('LICENSE', 'r', encoding='utf-8') as f:
    LICENSE = f.read()

setup(name="graphworks",
      version="0.2.0",
      description="Graph theoretic classes and helper functions.",
      long_description_content_type="text/markdown",
      long_description=README,
      packages=find_packages(),
      install_requires=['numpy ==1.21.5', 'graphviz ==0.19.1'],
      author="Nathan Gilbert",
      author_email="me@nathangilbert.com",
      url="https://github.com/nathan-gilbert/graphworks",
      license=LICENSE,
      classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Mathematics"
      ],
      include_package_data=True,
      package_data={'': ['data/*.json']},
      zip_safe=False)
