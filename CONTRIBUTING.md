## Contributing to this project

# Install development environment
To develop on your local computer, please follow these steps.

1) Install Python 3.12. There are multiple ways to install Python. The recommended way is to get it from [the Python.org download page](https://www.python.org/downloads/).
2) Create a virtual environment "venv":
```
python3.12 -m venv .venv
```
2) Activate the virtual environment
```
source .venv/bin/activate
```

3) Install dependencies:
```
pip install -e .[dev]
```

# Activate environment
You may use [direnv](https://direnv.net/) to automatically activate the environment every time you enter the directory. If not, you can use:

```
source .venv/bin/activate
```
