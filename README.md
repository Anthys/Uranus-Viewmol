# Uranus-Viewmol

## Uranus-Titania

Uranus-Titania is the current final version of the programm.


### Use

`python3 Uranus-Titania.py [name_of_xyz_file] (-args)`

#### Args frequently used

- `-c` lets you customize the process, to run only what you want.
- `-away` send all process to the cluster, so you can shut down your computer and the whole calculation will continue.
- `-n [name]` lets you to put the name and thus disable any input


### What it can do:

File|Use
---|--- 
 geom.xyz | Optimized geometry
 Homo/Lumo cub files | yes 
 mos.in | A hundred or so calculated orbital density 
 mos_cut.in | Twenty orbitals around the homo/lumo 
 freq.in | Vibration vector matrice of a wide range of wavelength 
 exspectrum/convolution.csv | Exited orbitals informations (energy, occupancy, wavelength) 
 panama_files | First exited orbitals calculated densities 
 
I believe this programm is also highly modulable, and new operations can be added in the `launch()` function.

### What it can't do

- Use turbomole files already calculated, or start from a previous calculation. Actually, it can do that, but not in `-away` mode, which is the mode used for every long calculation.

- In `-away` mode, if an operation fails-but-not-too-much, the programm will try to continue anyway, thus creating weird results. This is not the case in normal mode, the mode that nobody will use, which has a nice gui btw.

- It can't process molecules with an impair number of electrons. Actually, it will do it, but it will fail.
