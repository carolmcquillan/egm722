import geopandas as gpd
from mpl_toolkits.axes_grid1 import make_axes_locatable
from cartopy.feature import ShapelyFeature
import cartopy.crs as ccrs
import os
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
import matplotlib.pyplot as plt


# try to print the results to the screen using the format method demonstrated in the workbook
plt.ion() # make the plotting interactive


myCRS = ccrs.UTM(29)  # create a Universal Transverse Mercator reference system to transform our data.

# load the necessary data here and transform to a UTM projection
counties = gpd.read_file(os.path.abspath('c:/Carol_PG_CERT_GIS/egm722_Practicals/egm722/week2/data_files/Counties.shp'))
wards = gpd.read_file(os.path.abspath('c:/Carol_PG_CERT_GIS/egm722_Practicals/egm722/week3/data_files/NI_Wards.shp'))
counties.to_crs(epsg=2157)
wards.to_crs(epsg=2157)
# your analysis goes here...

join = gpd.sjoin(counties, wards, how='inner', lsuffix='left', rsuffix='right')

joinedData= join.groupby(['CountyName'])['Population'].sum()
print(joinedData)


# below here, you may need to modify the script somewhat to create your map.
# create a crs using ccrs.UTM() that corresponds to our CRS
myCRS = ccrs.UTM(29)
# create a figure of size 10x10 (representing the page size in inches

fig, ax = plt.subplots(1, 1, figsize=(10, 10), subplot_kw=dict(projection=myCRS))



# add gridlines below
gridlines = ax.gridlines(draw_labels=True,
                         xlocs=[-8, -7.5, -7, -6.5, -6, -5.5],
                         ylocs=[54, 54.5, 55, 55.5],
                         linewidth = 0.5, color = 'gray', alpha = 0.5, linestyle='--')

gridlines.right_labels = False
gridlines.bottom_labels = False
gridlines.left_labels = True
gridlines.top_labels = True

# to make a nice colorbar that stays in line with our map, use these lines:
divider = make_axes_locatable(ax)
cax = divider.append_axes("right", size="5%", pad=0.1, axes_class=plt.Axes)


# plot the ward data into our axis, using
ward_plot = Wards.plot(column='Population', ax=ax, vmin=1000, vmax=8000, cmap='viridis',
                       legend=True, cax=cax, legend_kwds={'label': 'Resident Population'})




county_outline = ShapelyFeature(counties['geometry'], # first argument is the geometry
                            myCRS, # second argument is the CRS
                            edgecolor='lightblue', # set the edgecolor to be mediumblue
                            facecolor='lightblue', # set the facecolor to be mediumblue
                            linewidth=1) # set the outline width to be 1 pt


ax.add_feature(county_outlines)
county_handles = [mpatches.Rectangle((0, 0), 1, 1, facecolor='none', edgecolor='r')]

ax.legend(county_handles, ['County Boundaries'], fontsize=12, loc='upper left', framealpha=1)

# save the figure
fig.savefig('sample_map22.png', dpi=300, bbox_inches='tight')


