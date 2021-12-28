from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as f:
    README = f.read()

with open('LICENSE', 'r', encoding='utf-8') as f:
    # pylint: disable=redefined-builtin
    LICENSE = f.read()

setup(name="graphworks",
      version="0.1.1",
      description="Graph theoretic classes and helper functions.",
      long_description_content_type="text/markdown",
      long_description=README,
      packages=find_packages(),
      install_requires=['numpy', 'graphviz'],
      author="Nathan Gilbert",
      author_email="me@nathangilbert.com",
      url="https://github.com/nathan-gilbert/graphworks",
      license=LICENSE,
      classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent"
      ],
      include_package_data=True,
      package_data={'': ['data/*.json']},
      zip_safe=False)
