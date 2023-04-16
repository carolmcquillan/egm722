# EGM722 - Week 4 Practical: Raster data using rasterio



#%matplotlib notebook
import os
import numpy as np
import rasterio as rio
import geopandas as gpd
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
from shapely.ops import unary_union
from shapely.geometry.polygon import Polygon
from cartopy.feature import ShapelyFeature
import matplotlib.patches as mpatches
import matplotlib.lines as mlines


def percentile_stretch(img, pmin=0., pmax=100.):
    '''
    This is where you should write a docstring.
    '''
    # here, we make sure that pmin < pmax, and that they are between 0, 100
    if not 0 <= pmin < pmax <= 100:
        raise ValueError('0 <= pmin < pmax <= 100')
    # here, we make sure that the image is only 2-dimensional
    if not img.ndim == 2:
        raise ValueError('Image can only have two dimensions (row, column)')

    minval = np.percentile(img, pmin)
    maxval = np.percentile(img, pmax)

    stretched = (img - minval) / (maxval - minval)  # stretch the image to 0, 1
    stretched[img < minval] = 0  # set anything less than minval to the new minimum, 0.
    stretched[img > maxval] = 1  # set anything greater than maxval to the new maximum, 1.

    return stretched


def img_display(img, ax, bands, stretch_args=None, **imshow_args):
    '''
    This is where you should write a docstring.
    '''
    dispimg = img.copy().astype(np.float32)  # make a copy of the original image,
    # but be sure to cast it as a floating-point image, rather than an integer

    for b in range(img.shape[0]):  # loop over each band, stretching using percentile_stretch()
        if stretch_args is None:  # if stretch_args is None, use the default values for percentile_stretch
            dispimg[b] = percentile_stretch(img[b])
        else:
            dispimg[b] = percentile_stretch(img[b], **stretch_args)

    # next, we transpose the image to re-order the indices
    dispimg = dispimg.transpose([1, 2, 0])

    # finally, we display the image
    handle = ax.imshow(dispimg[:, :, bands], **imshow_args)

    return handle, ax


# ------------------------------------------------------------------------
# read in the raster file
with rio.open('data_files/NI_Mosaic.tif') as dataset:
    img = dataset.read()
    xmin, ymin, xmax, ymax = dataset.bounds


# loading the towns/cities/outlines data to add to the map
towns = gpd.read_file(os.path.abspath('c:\Carol_PG_CERT_GIS/EGM722_Practicals/egm722/week2/data_files/Towns.shp'))
cities = gpd.read_file(os.path.abspath('c:\Carol_PG_CERT_GIS/EGM722_Practicals/egm722/week2/data_files/Towns.shp'))
counties = gpd.read_file(os.path.abspath('c:\Carol_PG_CERT_GIS/EGM722_Practicals/egm722/week2/data_files/Counties.shp'))
outlines = gpd.read_file(os.path.abspath('c:\Carol_PG_CERT_GIS/EGM722_Practicals/egm722/week2/data_files/NI_outline.shp'))


# next, create the figure and axis objects to add the map to

myCRS = ccrs.UTM(29)  # create a Universal Transverse Mercator reference system to transform our data.
myfig, ax = plt.subplots(1, 1, figsize=(10, 10), subplot_kw=dict(projection=myCRS))  # create a figure of size 10x10 (representing the page size in inches)
#ax = plt.axes(projection=myCRS)  # finally, create an axes object in the figure, using a UTM projection,
# be sure to fill in 29 above with the correct number for the UTM Zone that Northern Ireland is part of.


# now, add the satellite image to the map

my_kwargs = {'extent': [xmin, xmax, ymin, ymax],
             'transform': myCRS}

my_stretch = {'pmin': 0.1, 'pmax': 99.9}

h, ax = img_display(img, ax, [2, 1, 0], stretch_args=my_stretch, **my_kwargs)


# next, add the county outlines to the map

county_outlines = ShapelyFeature(counties['geometry'], myCRS, edgecolor='r', facecolor='none')
ax.add_feature(county_outlines)

# generate matplotlib handles to create a legend of the features we put in our map.
def generate_handles(labels, colors, edge='r', alpha=1):
    lc = len(colors)  # get the length of the color list
    handles = []
    for i in range(len(labels)):
        handles.append(mpatches.Rectangle((0, 0), 1, 1, facecolor=colors[i % lc], edgecolor=edge, alpha=alpha))
    return handles


county_handle = generate_handles(['County Boundaries'], ['none'])

# then, add the town and city points to the map, but separately
town_handle = ax.plot(towns.loc[towns['STATUS'] == 'Town'].geometry.x, towns.loc[towns['STATUS'] == 'Town'].geometry.y, 's', color='b', ms=6, transform=myCRS)
city_handle = ax.plot(towns.loc[towns['STATUS'] == 'City'].geometry.x, towns.loc[towns['STATUS'] == 'City'].geometry.y, 'd', color='mediumorchid', ms=8, transform=myCRS)


for ind, row in towns.iterrows():  # towns.iterrows() returns the index and row
    x, y = row.geometry.x, row.geometry.y  # get the x,y location for each town
    ax.text(x, y, row['TOWN_NAME'].title(), fontsize=8, transform=myCRS)  # use plt.text to place a label at x,y

# finally, try to add a transparent overlay to the map
# note: one way you could do this is to combine the individual county shapes into a single shape, then
# use a geometric operation, such as a symmetric difference, to create a hole in a rectangle.
# then, you can add the output of the symmetric difference operation to the map as a semi-transparent feature.

#First create a bounding box layer, 
map_frame = Polygon([(xmin, ymin), (xmin, ymax), (xmax, ymax), (xmax, ymin)]) # create polygon of map extent
#then union the counties a
counties_union = unary_union(counties.geometry) # create NI outline by joining geometries of counties
#and then create a map overlay poly with counties 'hole' removed and set layer transparency

mapblur = ShapelyFeature(map_frame.symmetric_difference(counties_union), myCRS, facecolor='w', alpha=0.5)

ax.add_feature(mapblur) 


# last but not least, add gridlines to the map
gridlines = ax.gridlines(draw_labels=True, # draw  labels for the grid lines
                         xlocs=[-7.5, -7, -6.5, -6], # add longitude lines at 0.5 deg intervals
                         ylocs=[54.5, 55, 55.5]) # add latitude lines at 0.5 deg intervals
gridlines.left_labels = False # turn off the left-side labels
gridlines.bottom_labels = False # turn off the bottom labels


#Create legend:
handles = county_handle + town_handle + city_handle # use '+' to concatenate (combine) lists
labels = ['County Boundaries', 'Towns', 'Cities']

leg = ax.legend(handles, labels, title='Legend', title_fontsize=14, 
                 fontsize=10, loc= 'upper left', frameon=True, framealpha=1)
# save the map
myfig.savefig('mapWeek4_tada.png', bbox_inches='tight', dpi=300)



