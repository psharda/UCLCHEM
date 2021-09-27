# UCLCHEM v2.0.3
UCLCHEM is a gas-grain chemical code written in Fortran 95. It propagates the abundances of chemical species through a network of user-defined reactions according to the physical conditions of the gas. Included in the repository is MakeRates, a python script to combine a species list, UMIST reaction file and user-defined reaction file into a consistent network with all files required by UCLCHEM.

**************************************************************
Usage Instructions
**************************************************************

Full documentation is available from the website: [uclchem.github.io](https://uclchem.github.io)

To build UCLCHEM, edit the Makefile in uclchem/src to use a compiler available on your machine. Then use "make" to create the executable.
- The Makefile also contains the choice of physics module.
- Building requires odes.f90 and network.f90 which are outputs of Makerates.
- uclchem/Makerates/ contains the Makerates python script to produce a network from the files in uclchem/Makerates/inputFiles

To run UCLCHEM, create an input file with the desired parameters. Any variable in defaultparameters.f90 can be set, any that are not will take the value given in defaultparameters.f90.
A full explanation of each parameter is given in defaultparameters.f90 and an example input file is given in example.inp
Call uclchem with the filename as an argument: "./uclchem example.inp"

**************************************************************
Python
**************************************************************
"Make python" builds a python module from the source code and wrap.f90. The whole module can be found in Python/uclchem/ and as long as that directory is in your path, you can ```import uclchem``` in any python script. The functions available in this module can be found in our documentation's [Python API](https://uclchem.github.io/docs/pythonapi) page.

Currently, the wrapper must be recompiled for different physics modules.

**************************************************************
Change Log
**************************************************************
**Three phases**
Following Garrod & Pauly 2011 and Ruaud et al. 2016, we've added three phase chemistry to UCLCHEM. By default, it's turned off but a flag in Makerates/MakeRates.py will switch it on.

**Improved Python**
Our Python module is much improved, we still compile the fortran source code for an efficient chemical model but we've written easy to use Python functions for the user to call it through. We've also increased the documentation on this feature.

**New Analysis**
The analysis script in Python/ is now more accurate, calling UCLCHEM to calculate the rates as needed.


*************************************************************
Contributing
*************************************************************
This is an open source science code for the community and we are happy to accept pull requests. We are also happy to work with you to produce a physics module if none of the ones available in the repository suit the modelling work you wish to do. If you are contributing ,please try to work with our current code style. We have the following general guidelines:

- camelCase variable and subroutines names that are self-explanatory where possible 

- CAPITALIZED fortran built in functions to make code structure apparent.
