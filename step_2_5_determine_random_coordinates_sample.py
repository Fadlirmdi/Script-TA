# -*- coding: utf-8 -*-
"""Step 2/5 - Determine random coordinates sample.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1exeJKHxF_xnpJCpjRLumtqUFwxu1LMvT

# **File used**

**SHP Files**
*   R1.shp/shx
*   R2.shp/shx
*   R3_iv.shp/shx

**semua file di: Tugas Akhir -> Data -> Raw Data -> Shapefile Region**

*-----------------------------------------*

**Random Grid Method**
*   random_grid_regions_1
*   random_grid_regions_2
*   random_grid_regions_3

**semua file di: Tugas Akhir -> Data -> Raw Data -> Random Coordinates -> Random Grid Method**

*-----------------------------------------*

**Random Uniform Method**
*   random_uniform_regions_1
*   random_uniform_regions_2
*   random_uniform_regions_3

**semua file di: Tugas Akhir -> Data -> Raw Data -> Random Coordinates -> Random Uniform Method**

*-----------------------------------------*

**DSS Coordinates**
*   sorted_coordinates_1
*   sorted_coordinates_2
*   sorted_coordinates_3

**semua file di: Tugas Akhir -> Data -> Raw Data -> DSS_Coordinates**

*------------------------------------------------------------------------------------------------------------------------------------------------------------------------*

# **Must Running**

----------------------------------------
"""

pip install geopandas shapely pandas

pip install fiona

pip install pandas matplotlib cartopy pyproj

import geopandas as gpd
import random
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import cartopy.crs as ccrs
import pyproj
import os
import numpy as np
import time
import fiona

from shapely.geometry import Point
from fiona.drvsupport import supported_drivers

"""# **Generated missing attribute SHP file**

----------------------------------------
"""

supported_drivers['ESRI Shapefile'] = 'rw'

# Input file
input_shapefile = '/content/SHP/R3_iv.shp'
output_folder = '/content/Output_SHP'
output_shapefile = os.path.join(output_folder, 'Region_3_new.shp')

# Buat output folder
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Buat atribut ilang di SHP file
with fiona.Env(SHAPE_RESTORE_SHX=True):
    with fiona.open(input_shapefile, 'r') as src:
        meta = src.meta
        with fiona.open(output_shapefile, 'w', **meta) as dst:
            for feature in src:
                dst.write(feature)

print("SHX file ada didalem foler 'Output_SHP'")

"""# **Random Grid Method**

----------------------------------------
"""

def generate_hexagonal_grid_coordinates(region_polygon, num_points):
    grid_coordinates = []
    min_x, min_y, max_x, max_y = region_polygon.bounds
    max_attempts = 10

    for attempt in range(max_attempts):
        grid_size = np.sqrt((max_x - min_x) * (max_y - min_y) / (num_points * np.sqrt(10)/2)) / (attempt + 1)
        hex_height = grid_size * np.sqrt(3)

        potential_points = []
        for i, x in enumerate(np.arange(min_x, max_x, grid_size)):
            for j, y in enumerate(np.arange(min_y, max_y, hex_height)):
                y_offset = 0 if i % 2 == 0 else hex_height / 2
                point = Point(x, y + y_offset)
                if region_polygon.contains(point):
                    potential_points.append((x, y + y_offset))

        if len(potential_points) >= num_points:
            grid_coordinates = np.random.choice(len(potential_points), num_points, replace=False)
            grid_coordinates = [potential_points[i] for i in grid_coordinates]
            break

    while len(grid_coordinates) < num_points:
        random_x = np.random.uniform(min_x, max_x)
        random_y = np.random.uniform(min_y, max_y)
        point = Point(random_x, random_y)
        if region_polygon.contains(point):
            grid_coordinates.append((random_x, random_y))

    grid_coordinates = [(round(coord[0], 2), round(coord[1], 2)) for coord in grid_coordinates]
    return grid_coordinates

#_______________________________________________________________________________________________________________________________________#

def process_shapefile(shp_file, points_per_region, output_filename):
    regions = gpd.read_file(shp_file)
    np.random.seed(int(time.time()))

    all_grid_coordinates = []
    for index, region in regions.iterrows():
        print(f"Region SHP {index + 1}/{len(regions)}, generating {points_per_region[index]} points")
        region_polygon = region['geometry']
        grid_coordinates = generate_hexagonal_grid_coordinates(region_polygon, points_per_region[index])
        all_grid_coordinates.extend(grid_coordinates)

    df = pd.DataFrame(all_grid_coordinates, columns=['Longitude', 'Latitude'])
    df.to_excel(output_filename, index=False)
    print("Exported to", output_filename)
    print(f"Total data points: {len(df)}\n")

#_______________________________________________________________________________________________________________________________________#

# SHP file dir, Generate point per wilayah, Output
shapefiles = [
    ('/content/SHP/R1.shp', [120, 21], 'random_grid_regions_1.xlsx'),
    ('/content/SHP/R2.shp', [230], 'random_grid_regions_2.xlsx'),
    ('/content/SHP/R3_iv.shp', [870, 80, 61], 'random_grid_regions_3.xlsx')
]

# Proses tiap SHP file
for shp_file, points_per_region, output_filename in shapefiles:
    process_shapefile(shp_file, points_per_region, output_filename)

# Ubah ke radius mars
mars_radius = 3396200
mars_crs = pyproj.CRS(proj='eqc', R=mars_radius, lon_0=0)

#_______________________________________________________________________________________________________________________________________#

# Proses plot tiap region
def process_and_plot_region(file_path, title, legend_location='lower right', marker_size=15):
    # Read the Excel file
    data = pd.read_excel(file_path)

    # Konversi Latitude Longitude
    data['Latitude'] = pd.to_numeric(data['Latitude'], errors='coerce')
    data['Longitude'] = pd.to_numeric(data['Longitude'], errors='coerce')
    data = data.dropna(subset=['Latitude', 'Longitude'])

    print(f"Latitude range for {title}: ", data['Latitude'].min(), " to ", data['Latitude'].max())
    print(f"Longitude range for {title}: ", data['Longitude'].min(), " to ", data['Longitude'].max())

    # Plotting
    fig = plt.figure(figsize=(10, 7))
    ax = plt.axes(projection=ccrs.PlateCarree())

    # Koordinat grid
    gl = ax.gridlines(draw_labels=True, crs=ccrs.PlateCarree())
    gl.top_labels = False
    gl.right_labels = False

    # Plot
    sns.scatterplot(data=data, x='Longitude', y='Latitude', color='red', label="Koordinat DSS (Random Method)", s=marker_size, ax=ax, transform=ccrs.PlateCarree())

    plt.title(title)
    plt.legend(loc=legend_location)
    plt.show()

#_______________________________________________________________________________________________________________________________________#

# Dir file
regions = [
    ('/content/random_grid_regions_1.xlsx', 'Random Grid Method - Region 1'),
    ('/content/random_grid_regions_2.xlsx', 'Random Grid Method - Region 2'),
    ('/content/random_grid_regions_3.xlsx', 'Random Grid Method - Region 3', 'lower left', 7)
]

# Prosses tiap file
for file_path, title, *opts in regions:
    process_and_plot_region(file_path, title, *opts)

"""# **Random Uniform Method**

----------------------------------------
"""

# Function to generate random coordinates within a region
def generate_random_coordinates_in_region(region_polygon, num_points):
    random_coordinates = []
    min_x, min_y, max_x, max_y = region_polygon.bounds

    while len(random_coordinates) < num_points:
        # Generate a random point
        random_x = random.uniform(min_x, max_x)
        random_y = random.uniform(min_y, max_y)
        point = Point(random_x, random_y)

        # Ensure the point is within the region shp
        if region_polygon.contains(point):
            random_x = (random_x + 360) % 360
            random_coordinates.append((round(random_x, 2), round(random_y, 2)))

    return random_coordinates

# Function to process shapefile and generate random coordinates
def process_shapefile(file_path, points_per_region, output_filename):
    regions = gpd.read_file(file_path)
    assert len(regions) == len(points_per_region), f"The shapefile should contain exactly {len(points_per_region)} regions."

    all_random_coordinates = []
    for index, region in regions.iterrows():
        num_points = points_per_region[index]
        print(f"Region SHP {index + 1}/{len(regions)}, total {num_points} coordinate(s)")
        region_polygon = region['geometry']
        random_coordinates = generate_random_coordinates_in_region(region_polygon, num_points)
        all_random_coordinates.extend(random_coordinates)

    # Create a DataFrame
    df = pd.DataFrame(all_random_coordinates, columns=['Longitude', 'Latitude'])

    # Export to Excel without CRS information
    df.to_excel(output_filename, index=False, header=True)
    print(f"Exported to {output_filename}")
    print(f"Total data: {len(df)}\n")

# Define the input shapefiles, points per region, and output filenames
shapefiles_info = [
    ('/content/SHP/R1.shp', [120, 21], 'random_uniform_regions_1.xlsx'),
    ('/content/SHP/R2.shp', [230], 'random_uniform_regions_2.xlsx'),
    ('/content/SHP/R3_iv.shp', [870, 80, 61], 'random_uniform_regions_3.xlsx')
]

# Process each shapefile
for file_path, points_per_region, output_filename in shapefiles_info:
    process_shapefile(file_path, points_per_region, output_filename)

# Ubah ke radius mars
mars_radius = 3396200
mars_crs = pyproj.CRS(proj='eqc', R=mars_radius, lon_0=0)

#_______________________________________________________________________________________________________________________________________#

# Proses plot tiap region
def process_and_plot_region(file_path, title, legend_location='lower right', marker_size=15):
    # Read the Excel file
    data = pd.read_excel(file_path)

    # Konversi Latitude Longitude
    data['Latitude'] = pd.to_numeric(data['Latitude'], errors='coerce')
    data['Longitude'] = pd.to_numeric(data['Longitude'], errors='coerce')
    data = data.dropna(subset=['Latitude', 'Longitude'])

    print(f"Latitude range for {title}: ", data['Latitude'].min(), " to ", data['Latitude'].max())
    print(f"Longitude range for {title}: ", data['Longitude'].min(), " to ", data['Longitude'].max())

    # Plotting
    fig = plt.figure(figsize=(10, 7))
    ax = plt.axes(projection=ccrs.PlateCarree())

    # Koordinat grid
    gl = ax.gridlines(draw_labels=True, crs=ccrs.PlateCarree())
    gl.top_labels = False
    gl.right_labels = False

    # Plot
    sns.scatterplot(data=data, x='Longitude', y='Latitude', color='red', label="Koordinat DSS (Random Method)", s=marker_size, ax=ax, transform=ccrs.PlateCarree())

    plt.title(title)
    plt.legend(loc=legend_location)
    plt.show()

#_______________________________________________________________________________________________________________________________________#

# Dir file
regions = [
    ('/content/random_uniform_regions_1.xlsx', 'Random Uniform Method - Region 1'),
    ('/content/random_uniform_regions_2.xlsx', 'Random Uniform Method - Region 2'),
    ('/content/random_uniform_regions_3.xlsx', 'Random Uniform Method - Region 3', 'lower left', 7)
]

# Prosses tiap file
for file_path, title, *opts in regions:
    process_and_plot_region(file_path, title, *opts)

"""# **Displaying Random Method Over Actual DSS Coordinate**

----------------------------------------

## **Random Grid Method Over Actual DSS**

----------------------------------------
"""

# Ubah ke radius mars
mars_radius = 3396200
mars_crs = pyproj.CRS(proj='eqc', R=mars_radius, lon_0=0)

#_______________________________________________________________________________________________________________________________________#

# Dir
actual_data_files = [
    '/content/DSS/sorted_coordinates_1_p1.xlsx',
    '/content/DSS/sorted_coordinates_2_p1.xlsx',
    '/content/DSS/sorted_coordinates_3_p1.xlsx']

random_data_files = [
    '/content/random_grid_regions_1.xlsx',
    '/content/random_grid_regions_2.xlsx',
    '/content/random_grid_regions_3.xlsx']

# Ax size
point_sizes = [15, 15, 7]

#_______________________________________________________________________________________________________________________________________#

# Perulangan tiap wilayah
for i, (actual_data_file, random_data_file, point_size) in enumerate(zip(actual_data_files, random_data_files, point_sizes)):

    actual_data = pd.read_excel(actual_data_file)
    actual_data['Latitude'] = pd.to_numeric(actual_data['Latitude'], errors='coerce')
    actual_data['Longitude_360'] = pd.to_numeric(actual_data['Longitude_360'], errors='coerce')
    actual_data = actual_data.dropna(subset=['Latitude', 'Longitude_360'])

    random_data = pd.read_excel(random_data_file)
    random_data['Latitude'] = pd.to_numeric(random_data['Latitude'], errors='coerce')
    random_data['Longitude'] = pd.to_numeric(random_data['Longitude'], errors='coerce')
    random_data = random_data.dropna(subset=['Latitude', 'Longitude'])

    print(f"Actual Data - Region {i+1} Latitude range: ", actual_data['Latitude'].min(), " to ", actual_data['Latitude'].max())
    print(f"Actual Data - Region {i+1} Longitude range: ", actual_data['Longitude_360'].min(), " to ", actual_data['Longitude_360'].max())
    print(f"Random Data - Region {i+1} Latitude range: ", random_data['Latitude'].min(), " to ", random_data['Latitude'].max())
    print(f"Random Data - Region {i+1} Longitude range: ", random_data['Longitude'].min(), " to ", random_data['Longitude'].max())

    # Cartopy
    fig = plt.figure(figsize=(10, 6))
    ax = plt.axes(projection=ccrs.PlateCarree())

    # Peta Grid
    gl = ax.gridlines(draw_labels=True, crs=ccrs.PlateCarree())
    gl.top_labels = False
    gl.right_labels = False

    # Scatter Plot DSS
    sns.scatterplot(data=actual_data, x='Longitude_360', y='Latitude', color='red', s=point_size, ax=ax, label='Koordinat DSS asli', transform=ccrs.PlateCarree())

    # Scatter Plot Random
    sns.scatterplot(data=random_data, x='Longitude', y='Latitude', color='blue', s=point_size, ax=ax, label='Koordinat Random Grid Method', transform=ccrs.PlateCarree())

    # Title
    plt.title(f'Koordinat DSS Asli and Random Grid - Region {i + 1}')
    plt.legend()
    plt.show()

"""## **Random Uniform Method Over Actual DSS**

----------------------------------------
"""

# Ubah ke radius mars
mars_radius = 3396200
mars_crs = pyproj.CRS(proj='eqc', R=mars_radius, lon_0=0)

#_______________________________________________________________________________________________________________________________________#

# Dir
actual_data_files = [
    '/content/DSS/sorted_coordinates_1_p1.xlsx',
    '/content/DSS/sorted_coordinates_2_p1.xlsx',
    '/content/DSS/sorted_coordinates_3_p1.xlsx']

random_data_files = [
    '/content/random_uniform_regions_1.xlsx',
    '/content/random_uniform_regions_2.xlsx',
    '/content/random_uniform_regions_3.xlsx']

# Ax size
point_sizes = [15, 15, 7]

#_______________________________________________________________________________________________________________________________________#

# Perulangan tiap wilayah
for i, (actual_data_file, random_data_file, point_size) in enumerate(zip(actual_data_files, random_data_files, point_sizes)):

    actual_data = pd.read_excel(actual_data_file)
    actual_data['Latitude'] = pd.to_numeric(actual_data['Latitude'], errors='coerce')
    actual_data['Longitude_360'] = pd.to_numeric(actual_data['Longitude_360'], errors='coerce')
    actual_data = actual_data.dropna(subset=['Latitude', 'Longitude_360'])

    random_data = pd.read_excel(random_data_file)
    random_data['Latitude'] = pd.to_numeric(random_data['Latitude'], errors='coerce')
    random_data['Longitude'] = pd.to_numeric(random_data['Longitude'], errors='coerce')
    random_data = random_data.dropna(subset=['Latitude', 'Longitude'])

    print(f"Actual Data - Region {i+1} Latitude range: ", actual_data['Latitude'].min(), " to ", actual_data['Latitude'].max())
    print(f"Actual Data - Region {i+1} Longitude range: ", actual_data['Longitude_360'].min(), " to ", actual_data['Longitude_360'].max())
    print(f"Random Data - Region {i+1} Latitude range: ", random_data['Latitude'].min(), " to ", random_data['Latitude'].max())
    print(f"Random Data - Region {i+1} Longitude range: ", random_data['Longitude'].min(), " to ", random_data['Longitude'].max())

    # Cartopy
    fig = plt.figure(figsize=(10, 6))
    ax = plt.axes(projection=ccrs.PlateCarree())

    # Peta Grid
    gl = ax.gridlines(draw_labels=True, crs=ccrs.PlateCarree())
    gl.top_labels = False
    gl.right_labels = False

    # Scatter Plot DSS
    sns.scatterplot(data=actual_data, x='Longitude_360', y='Latitude', color='red', s=point_size, ax=ax, label='Koordinat DSS asli', transform=ccrs.PlateCarree())

    # Scatter Plot Random
    sns.scatterplot(data=random_data, x='Longitude', y='Latitude', color='green', s=point_size, ax=ax, label='Koordinat Random Uniform Method', transform=ccrs.PlateCarree())

    # Title
    plt.title(f'Koordinat DSS Asli and Random Uniform - Region {i + 1}')
    plt.legend()
    plt.show()

"""## **2 Random Method Over Actual DSS**

----------------------------------------
"""

# Ubah ke radius mars
mars_radius = 3396200
mars_crs = pyproj.CRS(proj='eqc', R=mars_radius, lon_0=0)

#_______________________________________________________________________________________________________________________________________#

# Dir
actual_data_files = [
    '/content/Coordinates/sorted_coordinates_1.xlsx',
    '/content/Coordinates/sorted_coordinates_2.xlsx',
    '/content/Coordinates/sorted_coordinates_3.xlsx']

random_data_files = [
    '/content/Coordinates/random_grid_regions_1_p1.xlsx',
    '/content/Coordinates/random_grid_regions_2_p1.xlsx',
    '/content/Coordinates/random_grid_regions_3_p1.xlsx']

random_data_files_2 = [
    '/content/Coordinates/random_uniform_regions_1_p1.xlsx',
    '/content/Coordinates/random_uniform_regions_2_p1.xlsx',
    '/content/Coordinates/random_uniform_regions_3_p1.xlsx']

# Ax size
point_sizes = [20, 20, 10]

#_______________________________________________________________________________________________________________________________________#

# Perulangan tiap wilayah
for i, (actual_data_file, random_data_file, random_data_files_2, point_size) in enumerate(zip(actual_data_files, random_data_files, random_data_files_2, point_sizes)):

    actual_data = pd.read_excel(actual_data_file)
    actual_data['Latitude'] = pd.to_numeric(actual_data['Latitude'], errors='coerce')
    actual_data['Longitude'] = pd.to_numeric(actual_data['Longitude'], errors='coerce')
    actual_data = actual_data.dropna(subset=['Latitude', 'Longitude'])

    random_data = pd.read_excel(random_data_file)
    random_data['Latitude'] = pd.to_numeric(random_data['Latitude'], errors='coerce')
    random_data['Longitude'] = pd.to_numeric(random_data['Longitude'], errors='coerce')
    random_data = random_data.dropna(subset=['Latitude', 'Longitude'])

    random_data2 = pd.read_excel(random_data_files_2)
    random_data2['Latitude'] = pd.to_numeric(random_data2['Latitude'], errors='coerce')
    random_data2['Longitude'] = pd.to_numeric(random_data2['Longitude'], errors='coerce')
    random_data2 = random_data2.dropna(subset=['Latitude', 'Longitude'])

    print(f"Actual Data - Region {i+1} Latitude range: ", actual_data['Latitude'].min(), " to ", actual_data['Latitude'].max())
    print(f"Actual Data - Region {i+1} Longitude range: ", actual_data['Longitude_360'].min(), " to ", actual_data['Longitude_360'].max())
    print(f"Random Data - Region {i+1} Latitude range: ", random_data['Latitude'].min(), " to ", random_data['Latitude'].max())
    print(f"Random Data - Region {i+1} Longitude range: ", random_data['Longitude'].min(), " to ", random_data['Longitude'].max())
    print(f"Random Data - Region {i+1} Latitude range: ", random_data2['Latitude'].min(), " to ", random_data2['Latitude'].max())
    print(f"Random Data - Region {i+1} Longitude range: ", random_data2['Longitude'].min(), " to ", random_data2['Longitude'].max())

    # Cartopy
    fig = plt.figure(figsize=(10, 6), dpi=500, facecolor='none')
    ax = plt.axes(projection=ccrs.PlateCarree())

    # Peta Grid
    gl = ax.gridlines(draw_labels=True, crs=ccrs.PlateCarree())
    gl.top_labels = False
    gl.right_labels = False

    # Scatter Plot DSS
    sns.scatterplot(
        data=actual_data,
        x='Longitude_360',
        y='Latitude',
        color='blue',
        s=point_size,
        alpha=1,
        ax=ax,
        label='Koordinat DSS asli',
        transform=ccrs.PlateCarree()
    )

    # Scatter Plot Random
    sns.scatterplot(
        data=random_data,
        x='Longitude',
        y='Latitude',
        color='red',
        s=point_size,
        alpha=1,
        ax=ax,
        label='Koordinat Random Grid Method',
        transform=ccrs.PlateCarree()
    )

    # Scatter Plot Random
    sns.scatterplot(
        data=random_data2,
        x='Longitude',
        y='Latitude',
        color='green',
        s=point_size,
        alpha=1,
        ax=ax,
        label='Koordinat Random Uniform Method',
        transform=ccrs.PlateCarree()
    )

    max_lat = max(actual_data['Latitude'].max(), random_data['Latitude'].max(), random_data2['Latitude'].max())
    plt.ylim(None, max_lat * 1.2)

    # Title
    plt.title(f'Koordinat DSS Asli and Kedua Random Method - Wilayah {i + 1}')
    plt.legend(loc='best')

    plt.savefig(f'region_{i+1}_plot.png', dpi=500, transparent=True)
    plt.show()

"""# **Displaying All Over Coordinates**

----------------------------------------
"""

mars_radius = 3396200 # Radius Mars (m)
mars_crs = pyproj.CRS(proj='eqc', R=mars_radius, lon_0=0)

# Lokasi File
file_path = '/content/longitude_latitude.xlsx'
data = pd.read_excel(file_path)

# Baca kolom di file
data['Latitude'] = pd.to_numeric(data['Latitude'], errors='coerce')
data['Longitude'] = pd.to_numeric(data['Longitude'], errors='coerce')

data = data.dropna(subset=['Latitude', 'Longitude'])

print("Latitude range: ", data['Latitude'].min(), " to ", data['Latitude'].max())
print("Longitude range: ", data['Longitude'].min(), " to ", data['Longitude'].max())

# Plot
fig = plt.figure(figsize=(15, 10))
ax = plt.axes(projection=ccrs.PlateCarree())

# Grid Plot
gl = ax.gridlines(draw_labels=True, crs=ccrs.PlateCarree())
gl.top_labels = False
gl.right_labels = False

# Scatter Plot
sns.scatterplot(data=data, x='Longitude', y='Latitude', color='red', s=2, ax=ax, transform=ccrs.PlateCarree())

plt.title('All 1 degree coordinates')
plt.show()