from matplotlib import pyplot as plt
from matplotlib import ticker as mticker
from matplotlib.colors import Normalize
import matplotlib.cm as cm
import matplotlib.colors
import matplotlib.colorbar as cb
import numpy as np
import pandas as pd
import math
import cartopy.crs as ccrs


date = '2019aug20' #DATE STRING (eg '2014dec11')
i_p = 79 #PRESSURE LEVEL
contour_lines = False #True displays contour lines
contour_levels = 255 #recommend < 30 if contour_lines == True
show_gridlines = True #True displays gridlines
show_labels = False #True displays gridline labels
gridline_style = '-' # '-' for solid lines, '--' for dashed lines


with open('pressure_grid.txt') as pressure_file:
    pressure_grid = {}
    for line in pressure_file:
        item = line.split()
        pressure_grid.update({float(item[0]):float(item[1])})
        #key of each dict entry is the pressure level; value is the corresponding mbar


with open('Tp_' + date + '_results.dat') as dat_file:
    data = []
    for line in dat_file:
        item = line.split()
        if float(item[0]) == float(item[1]) == 0:
            pass #remove temperatures of 0
        else:
            data.append([float(item[0]),float(item[1])])
            #data = list of two-element lists [col1, col2]


latitudes = [i for i in range(-90, 92, 2)] #latitudes from [-90,90], increment 2
longitudes = [i for i in range(0, 361,10)] #longitudes from [0,360], increment 10

#FLAG LATITUDE/LONGITUDE PAIRS WITH NO TEMPERATURE DATA
#eventually will be removed (flag first for easier debugging)
for i in range(len(data) - 1): 
    #avoid indexing errors by stopping early, check last element manually
    if data[i][0] in latitudes and data[i][1] in longitudes and data[i+1][0] in latitudes and data[i+1][1] in longitudes:
        data[i].append('flag')
if data[len(data)-1][0] in latitudes and data[len(data)-1][1] in longitudes:
    data[len(data)-1].append('flag')


#REMOVE FLAGGED LATITUDE/LONGITUDE PAIRS
new_data = []
for l in data:
    if len(l) == 2:
        new_data.append(l)
data = new_data


#IGNORE ERRORS
new_data = []
for l in data:
    if l[0] in latitudes and l[1] in longitudes:
        new_data.append(l)
    else:
        new_data.append(l[0])
data = new_data
#data is now a list such that for index N, if N % 121 == 0 then it's a latitude/longitude pair.
#otherwise, it's a temperature corresponding to the (i-1)th pressure level
#where i is the smallest value such that (n-i) % 121 == 0


#ISOLATE PRESSURE LEVEL OF INTEREST
def isolate_pressure(i_p):
    pressure_temps = []
    count = 0
    while count < (len(data)/(121)):
        pressure_temps.append(data[(121*count + i_p + 1)])
        count += 1
    return pressure_temps #a list of temperature values at a given pressure i_p

#LATITUDE/LONGITUDE PAIRS THAT HAVE TEMPERATURE VALUES
#using the same indexing as isolate_pressure
latitude_longitude_pairs = []
for item in data:
    if type(item) == list:
        latitude_longitude_pairs.append(item)


#STACK THE ABOVE LISTS
def pressure_stack(i_p):
    stacked = np.column_stack((latitude_longitude_pairs,isolate_pressure(i_p)))
    return stacked
pressure_temps = pressure_stack(i_p)
#array with three columns: latitude, longitude, temperature at i_p


#DEFINE LISTS OF UNIQUE LATITUDES AND LONGITUDES
unique_latitudes = []
for triplet in pressure_temps:
    if triplet[0] in unique_latitudes:
        pass
    else:
        unique_latitudes.append(triplet[0])
unique_longitudes = []
for triplet in pressure_temps:
    if triplet[1] in unique_longitudes:
        pass
    else:
        unique_longitudes.append(triplet[1])


#SPLIT LATITUDES INTO NORTH AND SOUTH
north_latitudes = [lat for lat in unique_latitudes if lat > 0]
south_latitudes = [lat for lat in unique_latitudes if lat < 0]

#CREATE NORTH_LONGITUDES AND SOUTH_LONGITUDES BASED ON WHICH LONGS ACTUALLY GET SAMPLED
north_longitudes = []
for triplet in pressure_temps:
    if triplet[1] in north_longitudes:
        pass
    elif triplet[0] in north_latitudes:
        north_longitudes.append(triplet[1])
        
south_longitudes = []
for triplet in pressure_temps:
    if triplet[1] in south_longitudes:
        pass
    elif triplet[0] in south_latitudes:
        south_longitudes.append(triplet[1])


#CREATE NORTH NUMPY ARRAYS FOR NORTH AND SOUTH
north_array = np.zeros((len(north_latitudes),len(north_longitudes)))
for lat in range(0,len(north_latitudes)):
    for lon in range(0,len(north_longitudes)):
        for triplet in pressure_temps:
            if triplet[0] == north_latitudes[lat] and triplet[1] == north_longitudes[lon] and triplet[0] >= 45:
                north_array[lat,lon] = triplet[2]

south_array = np.zeros((len(south_latitudes),len(south_longitudes)))
for lat in range(0,len(south_latitudes)):
    for lon in range(0,len(south_longitudes)):
        for triplet in pressure_temps:
            if triplet[0] == south_latitudes[lat] and triplet[1] == south_longitudes[lon] and triplet[0] <= -45:
                south_array[lat,lon] = triplet[2]


#REPLACE ZEROS WITH NAN
north_array[np.where(north_array==0)] = np.nan
south_array[np.where(south_array==0)] = np.nan




########## PLOTTING NORTH ##########
latl = 0
latu = 90
lonl = 0
lonu = 360
lat0 = 90
lon0 = 0

#AXIS LABEL FORMATTING
def N_fmt_x(x,pos):
    if x>=0:
        return '%.0f'  % ((x)) +u"\N{DEGREE SIGN}"
    elif x<0:
        return '%.0f'  % ((x+360)) +u"\N{DEGREE SIGN}"
    else:
        return '%.0f'  % ((x)) +u"\N{DEGREE SIGN}"
N_formatter_x = mticker.FuncFormatter(N_fmt_x)

def N_fmt_y(y,pos):
    if y==46: #46 at edge gives cleaner fill - relabel 46 as 45
        return '%.0f'  % ((45)) +u"\N{DEGREE SIGN}"
    else:
        return '%.0f'  % ((y)) +u"\N{DEGREE SIGN}"
N_formatter_y = mticker.FuncFormatter(N_fmt_y)

#INITIALIZE PLOT
fig = plt.figure(figsize=[8,8])
ax = plt.axes(projection=ccrs.NorthPolarStereo())
ax.set_extent([lonu-180,lonl-180,45,latu], ccrs.PlateCarree())

#CONTOUR FUNCTIONS
if contour_lines == True:
    ax.contour(north_longitudes, north_latitudes, north_array, contour_levels, colors="black", transform=ccrs.PlateCarree())
cs=ax.contourf(north_longitudes, north_latitudes, north_array, contour_levels, transform=ccrs.PlateCarree(),cmap='inferno')

ax.invert_yaxis() #reflect plot vertically

if show_gridlines == True:
    gl = ax.gridlines(draw_labels=show_labels, color='gray', linestyle=gridline_style, y_inline=True,x_inline=True)
#x_inline True for inside, False for outside (outside is buggy)
    if show_labels == True:
        gl.xlocator=mticker.FixedLocator([-120,-60,0,60,120,179.9]) #180 doesn't display but 179.9 rounds up
    else:
        gl.xlocator=mticker.FixedLocator([-120,-60,0,60,120,180])
    gl.ylocator=mticker.FixedLocator([75,60,46]) #set 45 to 46 and relabel (see above) for cleaner fill
    gl.xformatter= N_formatter_x
    gl.yformatter= N_formatter_y

#COLORBAR
cbar=fig.colorbar(cs, ticks=[160,170,180,190])

#SAVE PLOT AS PNG
plt.savefig(date + '_N.png')



########## PLOTTING SOUTH ##########
latl = -90
latu = 0
lonl = 0
lonu = 360
lat0 = -90
lon0 = 180

#AXIS LABEL FORMATTING
def S_fmt_x(x,pos):
    if x>=0:
        return '%.0f'  % ((x)) +u"\N{DEGREE SIGN}"
    elif x<0:
        return '%.0f'  % ((x+360)) +u"\N{DEGREE SIGN}"
    else:
        return '%.0f'  % ((x)) +u"\N{DEGREE SIGN}"
S_formatter_x = mticker.FuncFormatter(S_fmt_x)

def S_fmt_y(y,pos):
    if y==-46: #-46 at edge gives cleaner fill - relabel -46 as -45
        return '%.0f'  % ((-45)) +u"\N{DEGREE SIGN}"
    else:
        return '%.0f'  % ((y)) +u"\N{DEGREE SIGN}"
S_formatter_y = mticker.FuncFormatter(S_fmt_y)

#INITIALIZE PLOT
fig = plt.figure(figsize=[8,8])
ax = plt.axes(projection=ccrs.SouthPolarStereo())
ax.set_extent([lonu-180,lonl-180,latl,-50], ccrs.PlateCarree())

#CONTOUR FUNCTIONS
if contour_lines == True:
    ax.contour(south_longitudes, south_latitudes, south_array, contour_levels, colors="black", transform=ccrs.PlateCarree())
cs=ax.contourf(south_longitudes, south_latitudes, south_array, 20, transform=ccrs.PlateCarree(),cmap='inferno')
#for South, contourf breaks above certain contour levels, depending on the date

ax.invert_yaxis() #reflect plot vertically
gl = ax.gridlines(draw_labels=show_labels, color='gray', linestyle=gridline_style, y_inline=True,x_inline=True)
#x_inline True for inside, False for outside (outside is buggy)

if show_labels == True:
    gl.xlocator=mticker.FixedLocator([-120,-60,0,60,120,179.9]) #180 doesn't display but 179.9 rounds up
else:
    gl.xlocator=mticker.FixedLocator([-120,-60,0,60,120,180])

gl.ylocator=mticker.FixedLocator([-75,-60,-46]) #set -45 to -46 and relabel (see above) for cleaner fill

gl.xformatter= S_formatter_x
gl.yformatter= S_formatter_y

#COLORBAR
cbar=fig.colorbar(cs, ticks=[160,170,180,190])

#SAVE PLOT AS PNG
plt.savefig(date + '_S.png')











