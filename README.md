# physoce-obs

Python tools for working with specific publicly-available oceanographic datasets

## Contents

* mlml.py module - Moss Landing Marine Labs public data
* lobo.py module - MBARI LOBO mooring data
* nerr.py module - National Estuarine Research Reserve data
* elkhorn.py module - Elkhorn Slough Reserve GIS data
* noaatide.py module - NOAA CO-OPS tide gauge data
* nasa.py module - NASA Ocean Color

## Requirements

In addition to numpy, scipy, matplotlib and standard Python packages, some functions or options may require:
* [physoce-py](https://github.com/physoce/physoce-py)
* [pandas](http://pandas.pydata.org/)
* [xarray](http://xarray.pydata.org/)

## Installation

To install using pip, run the following the terminal/command prompt:

`pip install git+https://github.com/physoce/physoce-obs`

## Importing modules

Python code to import module and see the functions available in that module:

```python
from physoce_obs import nerr
help(nerr)
```
