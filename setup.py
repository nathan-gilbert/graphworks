from setuptools import setup

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    # pylint: disable=redefined-builtin
    license = f.read()

setup(name="graphworks",
      version="0.1.0",
      description="A graph theory package.",
      package=['graphworks'],
      author="Nathan Gilbert",
      author_email="me@nathangilbert.com",
      url="https://github.com/nathan-gilbert/graphworks",
      zip_safe=False)
