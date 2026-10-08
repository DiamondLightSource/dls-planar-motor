[![CI](https://github.com/DiamondLightSource/dls-planar-motor/actions/workflows/ci.yml/badge.svg)](https://github.com/DiamondLightSource/dls-planar-motor/actions/workflows/ci.yml)
[![Coverage](https://codecov.io/gh/DiamondLightSource/dls-planar-motor/branch/main/graph/badge.svg)](https://codecov.io/gh/DiamondLightSource/dls-planar-motor)
[![PyPI](https://img.shields.io/pypi/v/dls-planar-motor.svg)](https://pypi.org/project/dls-planar-motor)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://www.apache.org/licenses/LICENSE-2.0)

# dls_planar_motor

Python driver for Planar Motor

This module uses asyncua python library to creat a client which connects to UPC AI server on a PLC device.
This is an alternative way of comunication with the PLC that bypasses the EPICS layer.
Additionally the module uses fastAPI python library to creat a simple API that can be used by other devices.

What            | Where
:---:           | :---:
Source          | <https://github.com/DiamondLightSource/dls-planar-motor>
PyPI            | `pip install dls-planar-motor`
Releases        | <https://github.com/DiamondLightSource/dls-planar-motor/releases>

This is a command line service. 
To check the version call:
```
python -m dls_planar_motor --version
```

To bring the fast API up and expose a banch of get and set functions to a localhost call:
```
python -m dls_planar_motor --serve
```
