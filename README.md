- # Uranus-Viewmol

  ## Uranus-Titania.py

  Uranus-Titania is the current final version of the program, which processes .xyz files in the cluster. However, if everything is working, you usually don't call Uranus-Titania [directly](#to_dtbpy).

  ### Use

  `python3 Uranus-Titania.py [name_of_xyz_file] (-args)`

  #### Args frequently used

  - `-c` lets you customize the process, to run only what you want.
  - `-away` send all process to the cluster, so you can shut down your computer and the whole calculation will continue.
  - `-n [name]` lets you to put the name directly and thus disable every input.

  ### What it can do:

  | Output files               | Used for                                                     |
  | -------------------------- | :----------------------------------------------------------- |
  | geom.xyz                   | Optimized geometry                                           |
  | Homo/Lumo cub files        | yes                                                          |
  | mos.in                     | A hundred or so calculated orbital densities                 |
  | mos_cut.in                 | Twenty orbitals densities around the homo/lumo               |
  | freq.in                    | Vibration vector matrix in a wide range of wavelengths       |
  | exspectrum/convolution.csv | Exited orbitals informations (energy, occupancy, wavelength) |
  | panama_files               | First exited orbitals calculated densities                   |

  I believe this program is also flexible, and new operations can be added in the `launch_job()` function.

  ### What it can't do

  - Use turbomole files already calculated, or start from a previous calculation. Actually, it can do that, but not in `-away` mode, which is the mode used for every long calculation.
  - In `-away` mode, if an operation fails-but-not-too-much, the program will try to continue anyway, thus creating weird results. This is not the case in normal mode, the mode that nobody will use, which happens to have a nice gui.
  - It can't process molecules with an impair number of electrons. Actually, it will do it, but it will fail.

  ## to_dtb.py

  `to_dtb.py` can be put anywhere *in the cluster*.

  It is used for :

  - Starting the process of .xyz files that are in `z_calc/to_be_made/`  with `to_dtb.py -p [NUMBER OF FILES TO BE PROCESSED]`
  - Sorting the processed files into `xDatabase/` with `to_dtb.py -s`

  ## retrieve.py

  `retrieve.py` can be put anywhere *in your local computer*.

  It is used for:

  - Retrieving final files that were processed in the cluster with `retrieve.py -r`. It will get every file from your remote `xDatabase/` and put them in a temporary folder, then create the needed file tree in `static/data/`
  - Sending waiting files in `files_from_users` to the cluster, with `retrieve.py -s [NUMBER OF FILE TO SENT]`. It will put these files in `xDatabase/to_be_made`

  ## Hard-code

  - The location of my modified program of `PANAMA` is hard-coded in `Uranus-Titania.py`. The normal version of panama doesn't work for some processes, so my modified version should be downloaded. 
  - The location of `spyctrum` is hard-coded.
  - `/home/barres/` is hard-coded in Uranus-Titania.py, need to be replaced with current user of the cluster.
  - The first variables of `retrieve.py` and `to-dtb.py` are hard-coded paths, they must be changed according to the instructions that are near them.
  - `scp frontale:` is hard-coded in `retrieve.py`, it must be changed to the ssh address.

  # Neptune-draw

  | Arguments    | Effects                                      |
  | ------------ | -------------------------------------------- |
  | `-yz`, `-xz` | Change visible axis, which are by default xy |
  | `-fx`        | Flip the x axis                              |
  | -s           | Save the picture in a `pics/` folder         |
  | -wh          | Give input for length and height             |

  ## Neptune-draw.py

  Draw distances of the`coord` files in the current directory, color them by quartiles.

  | Arguments        | Effects                                                      |
  | ---------------- | ------------------------------------------------------------ |
  | -showv           | Show values                                                  |
  | -diff [MAIN DIR] | Plot the difference of distance between the two `coord` files, found in the directories given in input. |
  | -p               | Show atom labels                                             |

  ## Neptune-draw+.py

  Draw the molecule structure with double and simple bonds, from the Gaussian output file.

  ## Neptune-draw-gimic.py

  Draw from the `OUTPUT.OUT` and `coord` file generated respectively from `gimicall.py` and turbomole.

  Show properties corresponding to the `-iwant` parameter:

  | -iwant [int] | Property                                       |
  | ------------ | ---------------------------------------------- |
  | 0            | Induced current (sum of positive and negative) |
  | 1            | Positive contribution                          |
  | 2            | Negative contribution                          |

  # Utilities

  ## triangle.py

  Find the center of each triangle of points given in input, and repeat the operation for each cycle given.

  Then, write these coordinates to the `coord` file, as `q` phantom atoms.

  ## truc.py

  Create the first 50 structures from the Gaussian output, by calling `Neptune-draw+.py`.

  ## Neptune.py

  Automatize the process of:

  | Argument | Effect                                     |
  | -------- | ------------------------------------------ |
  | -o       | Basic optimization                         |
  | -x       | escf calculation                           |
  | -ox      | Optimisation of first excited state        |
  | -p       | Electronic density of the first excitation |

  ## gimicall.py

  ### Need

  - An `input.txt` file in which is written every atom bond that has to be examined, one bond per line.
  - Change the fixpoint of `gimic.inp` to an hydrogen atom so that it can't fail during the process.

  It will write every output in the `OUTPUT.OUT` file, appending to it.
