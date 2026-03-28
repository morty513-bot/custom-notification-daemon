# Custom notification daemon

My custom notification daemon script. Just for fun. Designed for running on Wayland sway Ubuntu machine.

## Setup

### 1. System packages

The file `apt-packages.txt` contains the apt packages required for this project.
I'm not bothering yet with version pinning.
These can be installed with the command,

```bash
sudo xargs -a apt-packages.txt apt install -y
```

### 2. (Optional) Virtual environment setup

If creating a virtual environment, use the `--system-site-packages` flag,
and only do so after installing the apt packages, so that the venv can use them:

```bash
python -m venv --system-site-packages .venv
```

NOTE TO SELF: make sure to use the apt-installed Python binary, not the nix-installed one, otherwise `--system-site-packagaes` won't do what you want it to. Therefore use `/usr/bin/python3 -m venv --system-site-packages .venv`.

Then activate it:

```bash
source ./.venv/bin/activate
```

### 3. pip requirements

Then the Python requirements can be installed with the `requirements.txt` file,

```bash
pip install -r requirements.txt
```
