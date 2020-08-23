# python\_polar\_projections
Polar projections for 2020 JPL internship.

Contact: zade.akras@yale.edu

## Requirements

- A pressure grid 'pressure\_grid.txt' to provide pressure levels and the corresponding pressure. 
By default the pressure level should come first in the pair, though this can be changed by switching the 0 and 1 in line 26 (in the pressure\_grid.update statement).

- A .dat file ('Tp\_2014dec11\_results.dat') containg the temperature values for each latitude/longitude/pressure triplet.
The file string can be modified at line 30 if needed. The script is designed to handle the output of /home/zakras/projects/texes\_vs\_time/idl/output\_txt\_texes\_temperatures\_2014dec11.pro, which gives a .dat file with a latitude in column 1, a longitude in column 2, followed by a series of temperature values in column 1 and the corresponding error in column 2. The script is written to ignore the errors, so those aren't necessary. Each latitude/longitude pair has np many values (np = number of pressure levels), with the ith value corresponding to the temperature at the ith pressure level. After np many rows comes the next latitude/longitude pair.

## Usage

Before running the script, a handful of variables need to be changed immediately following the import statements. These variables are commented and should be self-explanatory.

The script outputs two files. The default is two .png files (one for North, one for South) titled "date\_N.png" for North and "date\_S.png" for South. These can be changed at lines 210 and 268, in the plt.savefig commands.

The default colormap is 'inferno.' I found this colormap to use colors intuitive to heat, and it should work in black and white. The colormap can be changed in the contourf statements, such as in line 191.

The number of contour levels for the South is set to a default value of 20, since this was close to the maximum for the 2014dec11 data before the contourf function started breaking. For some dates this will be too high, and for others you will be able to go higher. This number can be adjusted in line 247, as the fourth parameter of the contourf function. To set it at the same number of contour levels as the North (this almost certainly won't work), use contour\_levels in place of a number. If you get an error, it's probably because there were too many contour levels for the South. The North output should be unaffected.
