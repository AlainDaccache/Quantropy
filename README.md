# Quantropy


## Installation
Requirements:
* Python 3.10 or higher


```
# Ensure you have python installed
python --version
python -m pip install --upgrade pip

# Create environment, name it env
python -m venv env

# Activate environment

# In Linux
source env/bin/activate

# In Windows
env\Scripts\activate

# Install the dependencies (f Python 3.10.12)
python -m pip install -r requirements.txt

# Otherwise automatic dependency evaluation. TODO find stable ranges.
python -m pip install numpy pandas scipy jupyter matplotlib \
                        mkdocs mkdocs-material mkdocstrings[python] mkdocs-with-pdf
```
## Usage

### Jupyter Notebook

To run Jupyter, simply command line `jupyter notebook`. will output in the log a URL that you can copy paste. It comes with a token so make sure you copy paste
the entire URL. In my case, it is `http://localhost:8888/tree?token=a136012c6477b5dd56b5deed5bf6ffa14e48a9040118acef`.

### Documentation

To run Mkdocs, simply command line `mkdocs serve`
