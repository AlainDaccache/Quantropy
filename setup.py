"""
To release to PyPI:

* Delete .egginfo, build, and dist folders
* Be at Quantropy level (i.e. .../Quantropy, and not .../Quantropy/matilda)
* Upgrade version in setup.cfg (i.e. from 0.0.1 to 0.0.2)

*   py -m pip install --upgrade build
*   py -m build

*   py -m pip install --user --upgrade twine
*   py -m twine upload --repository testpypi dist/*

Username: __token__
Password: API token

Go to terminal, and do
*   py -m pip install -i https://test.pypi.org/simple/ Quantropy==0.0.7         (make sure you adjust Quantropy==version)
*   py      (to open python interpreter)
*   import matilda

Now you're ready to upload it to actual PyPi


"""

import setuptools

setuptools.setup()

