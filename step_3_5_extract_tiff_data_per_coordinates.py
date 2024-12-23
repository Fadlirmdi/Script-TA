# -*- coding: utf-8 -*-
"""Step 3/5 - Extract tiff data per coordinates.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1WV9jE3V9KgVlW1aOjHiJtkbYYABKuIGY

# **File used**

**TIF Files**


**semua file di: Data TA**

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

pip install rasterio

!pip install netCDF4

!pip install netCDF4 pandas openpyxl

pip install spiceypy

import rasterio
import pandas as pd
import numpy as np
import pandas as pd
import pyproj
import netCDF4 as nc
import matplotlib.pyplot as plt
import re
import xarray as xr
import os
import seaborn as sns
import matplotlib.ticker as mtick

from scipy.interpolate import griddata
from rasterio.transform import from_origin
from rasterio.crs import CRS
from pyproj import CRS, Transformer
from scipy.ndimage import map_coordinates

"""# **Determine All Coordinates**

----------------------------------------
"""

import pandas as pd

# Initialize lists to store longitude and latitude values
longitude_values = []
latitude_values = []

# Generate longitude and latitude values
for long in range(360, -1, -1):
    for lat in range(60, -61, -1):
        longitude_values.append(long)
        latitude_values.append(lat)

# Create a DataFrame
data = {
    'Longitude': longitude_values,
    'Latitude': latitude_values
}

df = pd.DataFrame(data)

# Write the DataFrame to an Excel file
excel_filename = 'longitude_latitude.xlsx'
df.to_excel(excel_filename, index=False)

print(f"Data has been written to {excel_filename}")

"""# **Extracting Value per-Coordinates**

----------------------------------------

## **Extracting Albedo**



----------------------------------------

### **Downloading Data**
"""

#! gdown --id 1N0zv0n3BeLoC08vHwtk5tXFGBFBv0x9S # Albedo 1
! gdown --id 1Gtx10BCNhYjH3UwYHy3hy2Ovp_ea0Uxx # Normalize file

# Fail
#! gdown --id 1gOGjHCb2rXQIwJII53JYbQ0c3p_cepLQ # Albedo 2
#! gdown --id 1kgq4RVKZZloJL4DgWkaBPcTKnLngpQds # Albedo 3

"""### **Check Data**"""

tif_file = "/content/normalized_file (1).tif"
dataset = rasterio.open(tif_file)

print(dataset.crs)

# Define CRS and transformer
crs_geographic = CRS("EPSG:4326")  # Geographic (WGS84)
crs_mars = CRS("EPSG:4034")  # Mars (Update with correct EPSG code if needed)
transformer = Transformer.from_crs(crs_geographic, crs_mars, always_xy=True)

# Load the TIFF file
tif_file = "/content/normalized_file (1).tif"
dataset = rasterio.open(tif_file)

# Print dataset bounds and no-data value
print(f"Dataset bounds: {dataset.bounds}")
print(f"No-data value: {dataset.nodata}")

# Analyze raster resolution
print(f"Raster resolution (width, height): {dataset.res}")
print(f"Raster shape (height, width): {dataset.shape}")

# Read the raster data
raster_data = dataset.read(1)

# SNS Plot
sns.set(style="darkgrid")
plt.figure(figsize=(8, 6))

# Histogram of raster values
hist = plt.hist(raster_data[raster_data != dataset.nodata].flatten(), color='orange', bins=50)
plt.title('Data Seluruh Albedo Permukaan Mars (resolusi 1 derajat koordinat)')
plt.xlabel('Nilai albedo')
plt.ylabel('Banyak data')

# Ubah titik ke koma
def indonesia_format(x, pos=None):
    return f"{x:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

formatter = mtick.FuncFormatter(indonesia_format)
plt.gca().xaxis.set_major_formatter(formatter)

#_______________________________________________________________________________________________________________________________________#

plt.suptitle('Perbandingan Nilai Albedo dari Seluruh Permukaan Mars', y=.92)
plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.show()

# Plot the raster data
plt.figure(figsize=(25, 6))
plt.imshow(raster_data, cmap='viridis')
plt.colorbar(label='Raster Values')
plt.title("Raster Data Visualization")
plt.show()

"""### **Extracting Data**"""

# Extract value dari koordinat di excel
def extract_pixel_values_from_excel(excel_file_path, tiff_file_path, image_width, image_height, output_excel_path):

    excel_data = pd.read_excel(excel_file_path)
    longitudes = excel_data['Longitude']
    latitudes = excel_data['Latitude']

    # Konversi koordinat geo ke pixel
    pixel_x = ((longitudes + 180) / 360) * image_width
    pixel_y = ((90 - latitudes) / 180) * image_height

    pixel_x = np.clip(pixel_x, 0, image_width - 1)
    pixel_y = np.clip(pixel_y, 0, image_height - 1)

    # Olah TIF file
    with rasterio.open(tiff_file_path) as src:
        pixel_values = [src.read(1)[int(y), int(x)] for x, y in zip(pixel_x, pixel_y)]

    excel_data['Extracted_Value'] = pixel_values
    excel_data.to_excel(output_excel_path, index=False)

#_______________________________________________________________________________________________________________________________________#

# Dir TIF File
tiff_file_path = '/content/normalized_file (1).tif'

# Dimensi TIF
image_width = 14400
image_height = 7200

#_______________________________________________________________________________________________________________________________________#

# Input Output File
input_output_files = [
    ("/content/Coordinates/random_grid_regions_1_p10.xlsx", "/content/output_rg_extracted_1.xlsx"),
    ("/content/Coordinates/random_grid_regions_2_p10.xlsx", "/content/output_rg_extracted_2.xlsx"),
    ("/content/Coordinates/random_grid_regions_3_p10.xlsx", "/content/output_rg_extracted_3.xlsx"),

    ("/content/Coordinates/random_uniform_regions_1_p10.xlsx", "/content/output_ru_extracted_1.xlsx"),
    ("/content/Coordinates/random_uniform_regions_2_p10.xlsx", "/content/output_ru_extracted_2.xlsx"),
    ("/content/Coordinates/random_uniform_regions_3_p10.xlsx", "/content/output_ru_extracted_3.xlsx"),

    ("/content/Coordinates/sorted_coordinates_1.xlsx", "/content/output_dss_extracted_1.xlsx"),
    ("/content/Coordinates/sorted_coordinates_2.xlsx", "/content/output_dss_extracted_2.xlsx"),
    ("/content/Coordinates/sorted_coordinates_3.xlsx", "/content/output_dss_extracted_3.xlsx"),
]

# Simpan file output
for input_file, output_file in input_output_files:
    extract_pixel_values_from_excel(input_file, tiff_file_path, image_width, image_height, output_file)

"""**Buang Null Value**"""

output_directory = "/content/"
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

# Input file
input_excel_files = [
    "/content/output_dss_extracted_1.xlsx",
    "/content/output_dss_extracted_2.xlsx",
    "/content/output_dss_extracted_3.xlsx"
]

#_______________________________________________________________________________________________________________________________________#

# Nilai yang ingin di buang
threshold = 0

#_______________________________________________________________________________________________________________________________________#

# Ulangi ke seluruh file
for i, input_excel_file in enumerate(input_excel_files, start=1):
    df = pd.read_excel(input_excel_file)

    missing_values_mask = np.isclose(df['Extracted_Value'], threshold)

    valid_indices = df.index[~missing_values_mask]
    valid_values = df.loc[~missing_values_mask, 'Extracted_Value']
    missing_indices = df.index[missing_values_mask]

    interpolated_values = np.interp(missing_indices, valid_indices, valid_values)

    df.loc[missing_indices, 'Extracted_Value'] = interpolated_values

    output_excel_file = os.path.join(output_directory, f"DSS_albedo_region_{i}.xlsx")
    df.to_excel(output_excel_file, index=False)

"""## **Extracting DCI (Dust Cover Index)**



----------------------------------------

### **Downloading Data**
"""

#! gdown --id 1zvFWl1tITm70jZANDAEL2V_vC9XHrK3P  # MOLA

! gdown --id 1TRGxspXh9ZmeZiArVFsIdrPz5QhNCJQf  # MOLA upscaling

#! gdown --id 17aoDXGmZ5PmmhBSnctp5nb3a45QkjGNB # Shifted

"""### **Check Data**"""

tif_file = "/content/dci_lo_ice_dust_16ppd_mola_R11.tif"
dataset = rasterio.open(tif_file)

print(dataset.crs)

# Define CRS and transformer
crs_geographic = CRS("EPSG:4326")  # Geographic (WGS84)
crs_mars = CRS("EPSG:4034")  # Mars (Update with correct EPSG code if needed)
transformer = Transformer.from_crs(crs_geographic, crs_mars, always_xy=True)

# Load the TIFF file
tif_file = "/content/dci_lo_ice_dust_16ppd_mola_R11.tif"
dataset = rasterio.open(tif_file)

# Print dataset bounds and no-data value
print(f"Dataset bounds: {dataset.bounds}")
print(f"No-data value: {dataset.nodata}")

# Analyze raster resolution
print(f"Raster resolution (width, height): {dataset.res}")
print(f"Raster shape (height, width): {dataset.shape}")

# Read the raster data
raster_data = dataset.read(1)

# SNS Plot
sns.set(style="darkgrid")
plt.figure(figsize=(8, 6))

# Histogram of raster values
hist = plt.hist(raster_data[raster_data != dataset.nodata].flatten(), color='orange', bins=50)
plt.title('Data Seluruh DCI Permukaan Mars (resolusi 1 derajat koordinat)')
plt.xlabel('Nilai DCI')
plt.ylabel('Banyak data')

# Ubah titik ke koma
def indonesia_format(x, pos=None):
    return f"{x:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

formatter = mtick.FuncFormatter(indonesia_format)
plt.gca().xaxis.set_major_formatter(formatter)

#_______________________________________________________________________________________________________________________________________#

plt.suptitle('Perbandingan Nilai Dust Cover Index (DCI) dari Seluruh Permukaan Mars', y=.92)
plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.show()

# Plot the raster data
plt.figure(figsize=(25, 6))
plt.imshow(raster_data, cmap='viridis')
plt.colorbar(label='Raster Values')
plt.title("Raster Data Visualization")
plt.show()

"""
### **Extracting Data**"""

# Extract value dari koordinat di excel
def extract_pixel_values_spline(excel_file_path, tiff_file_path, image_width, image_height, output_excel_path):
    # Load the Excel data
    excel_data = pd.read_excel(excel_file_path)
    longitudes = excel_data['Longitude']
    latitudes = excel_data['Latitude']

    # Convert geographic coordinates to pixel coordinates
    pixel_x = ((longitudes + 180) / 360) * image_width
    pixel_y = ((90 - latitudes) / 180) * image_height

    pixel_x = np.clip(pixel_x, 0, image_width - 1)
    pixel_y = np.clip(pixel_y, 0, image_height - 1)

    # Load the TIFF file and read the band
    with rasterio.open(tiff_file_path) as src:
        band = src.read(1)

        # Prepare the grid for interpolation
        x = np.arange(image_width)
        y = np.arange(image_height)
        x_grid, y_grid = np.meshgrid(x, y, indexing='ij')

        # Use map_coordinates for spline interpolation (order=3 for cubic spline)
        pixel_values = map_coordinates(band, [pixel_y, pixel_x], order=3, mode='nearest', cval=np.nan, prefilter=True)

    # Add the extracted values to the Excel data and save the output
    excel_data['Extracted_Value'] = pixel_values
    excel_data.to_excel(output_excel_path, index=False)

#_______________________________________________________________________________________________________________________________________#

# Dir TIF File
tiff_file_path = '/content/dci_lo_ice_dust_16ppd_mola_R11.tif'

# Dimensi TIF
image_width = 9600
image_height = 4800

#_______________________________________________________________________________________________________________________________________#

# Input Output File
input_output_files = [
    ("/content/Coordinates/random_grid_regions_1_p10.xlsx", "/content/output_rg_extracted_1.xlsx"),
    ("/content/Coordinates/random_grid_regions_2_p10.xlsx", "/content/output_rg_extracted_2.xlsx"),
    ("/content/Coordinates/random_grid_regions_3_p10.xlsx", "/content/output_rg_extracted_3.xlsx"),

    ("/content/Coordinates/random_uniform_regions_1_p10.xlsx", "/content/output_ru_extracted_1.xlsx"),
    ("/content/Coordinates/random_uniform_regions_2_p10.xlsx", "/content/output_ru_extracted_2.xlsx"),
    ("/content/Coordinates/random_uniform_regions_3_p10.xlsx", "/content/output_ru_extracted_3.xlsx"),

    ("/content/Coordinates/sorted_coordinates_1.xlsx", "/content/output_dss_extracted_1.xlsx"),
    ("/content/Coordinates/sorted_coordinates_2.xlsx", "/content/output_dss_extracted_2.xlsx"),
    ("/content/Coordinates/sorted_coordinates_3.xlsx", "/content/output_dss_extracted_3.xlsx"),
]

# Simpan file output
for input_file, output_file in input_output_files:
    extract_pixel_values_spline(input_file, tiff_file_path, image_width, image_height, output_file)

output_directory = "/content/"
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

# Input file
input_excel_files = [
    "/content/output_dss_extracted_1.xlsx",
    "/content/output_dss_extracted_2.xlsx",
    "/content/output_dss_extracted_3.xlsx"
]

#_______________________________________________________________________________________________________________________________________#

# Nilai yang ingin di buang
threshold = 0

#_______________________________________________________________________________________________________________________________________#

# Ulangi ke seluruh file
for i, input_excel_file in enumerate(input_excel_files, start=1):
    df = pd.read_excel(input_excel_file)

    missing_values_mask = np.isclose(df['Extracted_Value'], threshold)

    valid_indices = df.index[~missing_values_mask]
    valid_values = df.loc[~missing_values_mask, 'Extracted_Value']
    missing_indices = df.index[missing_values_mask]

    interpolated_values = np.interp(missing_indices, valid_indices, valid_values)

    df.loc[missing_indices, 'Extracted_Value'] = interpolated_values

    output_excel_file = os.path.join(output_directory, f"DSS_DCI_region_{i}.xlsx")
    df.to_excel(output_excel_file, index=False)

"""## **Extracting Water Vapour**




----------------------------------------

### **Downloading Data**
"""

# Water Vapour ls191 - ls209 -> Fall Seasons
#! gdown --id 1PNfMEWRUtaRRYbc6slDn8oyltYQRm7pc

# Water Vapour ls286 - ls305 -> Winter Seasons
#! gdown --id 1mBmQnFYNUh3eHpjpETaUE-g2zZ8tikQb

# Water Vapour ls11 - ls25 -> Spring Seasons
#! gdown --id 1uz1TW6xWzctV6IcsoSaMVQlcu5GfBJGM

# Water Vapour ls108 - ls122 -> Summer Seasons
#! gdown --id 1H9_GBwt1R3oUsU7Axk_N9hP9y7L2ZWfI


# Average Water Vapour all seasons
! gdown --id 1XNoi9XWqaaK0E19GancNTRU0kASLNNm5

"""### **Checking Var**"""

file_path = '/content/openmars_vap_my24_ls191_my24_ls209.nc'
dataset = nc.Dataset(file_path, 'r')
variables = dataset.variables.keys()

print("Variable didalem NC:")
for var in variables:
    print(var)

namaVar = dataset.variables['vapcol']
print(namaVar.dimensions)
print(namaVar.shape)
dataset.close()

"""### **Extracting Data**"""

# Load NC file
nc_file = "/content/average_vapcol (1).nc"
dataset = nc.Dataset(nc_file, 'r')

# Extract sesuai variable
lon = dataset.variables['lon'][:]
lat = dataset.variables['lat'][:]
vapcol = dataset.variables['vapcol']

#_______________________________________________________________________________________________________________________________________#

# Load/save file excel
input_files = [
    "/content/Coordinates/random_grid_regions_1_p10.xlsx",
    "/content/Coordinates/random_grid_regions_2_p10.xlsx",
    "/content/Coordinates/random_grid_regions_3_p10.xlsx",

    "/content/Coordinates/random_uniform_regions_1_p10.xlsx",
    "/content/Coordinates/random_uniform_regions_2_p10.xlsx",
    "/content/Coordinates/random_uniform_regions_3_p10.xlsx",

    "/content/Coordinates/sorted_coordinates_1.xlsx",
    "/content/Coordinates/sorted_coordinates_2.xlsx",
    "/content/Coordinates/sorted_coordinates_3.xlsx"
]
output_files = [
    "random_grid_WaterVap_all_region_1.xlsx",
    "random_grid_WaterVap_all_region_2.xlsx",
    "random_grid_WaterVap_all_region_3.xlsx",

    "random_uniform_WaterVap_all_region_1.xlsx",
    "random_uniform_WaterVap_all_region_2.xlsx",
    "random_uniform_WaterVap_all_region_3.xlsx",

    "DSS_WaterVap_all_region_1.xlsx",
    "DSS_WaterVap_all_region_2.xlsx",
    "DSS_WaterVap_all_region_3.xlsx"
]

#_______________________________________________________________________________________________________________________________________#

# Extract file
def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx

time_index = 0

#_______________________________________________________________________________________________________________________________________#

# Proses ekstrak
for input_file, output_file in zip(input_files, output_files):
    df = pd.read_excel(input_file)
    extracted_values = []

    # Ekstrak per koordinat
    for index, row in df.iterrows():
        lon_value = row['Longitude']
        lat_value = row['Latitude']

        lon_idx = find_nearest(lon, lon_value)
        lat_idx = find_nearest(lat, lat_value)

        value = vapcol[time_index, lat_idx, lon_idx]
        extracted_values.append(value)

    df['extracted_value'] = extracted_values
    df.to_excel(output_file, index=False)

dataset.close()

# NC file
nc_file = "/content/average_vapcol (1).nc"
dataset = nc.Dataset(nc_file, 'r')

# Extrak var
lon = dataset.variables['lon'][:]
lat = dataset.variables['lat'][:]
vapcol = dataset.variables['vapcol'][:]

# Ekstrak dari awal var "time"
time_index = 0
vapcol_data = vapcol[time_index, :, :]
flattened_vapcol = vapcol_data.flatten()

# SNS Plot
sns.set(style="darkgrid")
plt.figure(figsize=(8, 6))

# Plot histogram
plt.figure(figsize=(10, 6))
sns.histplot(flattened_vapcol, bins=30, color='orange')
plt.title('Data Seluruh Water Vapour (WV) Permukaan Mars (resolusi 1 derajat koordinat)')
plt.xlabel('Nilai Water Vapour (kg/m$^{-2}$)')
plt.ylabel('Banyak data')

# Ubah titik ke koma
def indonesia_format(x, pos=None):
    return f"{x:,.3f}".replace(',', 'X').replace('.', ',').replace('X', '.')

formatter = mtick.FuncFormatter(indonesia_format)
plt.gca().xaxis.set_major_formatter(formatter)

#_______________________________________________________________________________________________________________________________________#

plt.suptitle('Perbandingan Nilai Water Vapour (WV) dari Seluruh Permukaan Mars', y=.92)
plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.show()

# tutup
dataset.close()

"""### **Combine all nc file**"""

# Semua file NC
data_path = "/content/nc"
files = os.path.join(data_path, "*.nc")

# Load file NC
dataset = xr.open_mfdataset(files, combine='by_coords')

# Calculate Nilai Rata2
vapcol_mean = dataset['vapcol']

# Save
vapcol_mean.to_netcdf("average_vapcol.nc")

"""## **Extracting Slope (Degree)**



----------------------------------------

### **Downloading Data**
"""

# Slope region 1
#! gdown --id 1adRPbLkmaZh8qLKSB9td_pvQvRqxC_5c

# Slope region 2
#! gdown --id 1_LtVbakrdooNGE2zfuwPGxn1uFMrPqP4

# Slope region 3
#! gdown --id 1lGVlIZyzAt36HfEg5xXJFMLvjj3j3vtV

# Slope full map
! gdown --id 12PAtvCUDHNoikcRfEsT-8xlg5BIRHtEY

"""### **Check Data**"""

tif_file = "/content/slopedss-all.tif"
dataset = rasterio.open(tif_file)

print(dataset.crs)

# Define CRS and transformer
crs_geographic = CRS("EPSG:4326")  # Geographic (WGS84)
crs_mars = CRS("EPSG:4034")  # Mars (Update with correct EPSG code if needed)
transformer = Transformer.from_crs(crs_geographic, crs_mars, always_xy=True)

# Load the TIFF file
tif_file = "/content/slopedss-all.tif"
dataset = rasterio.open(tif_file)

# Print dataset bounds and no-data value
print(f"Dataset bounds: {dataset.bounds}")
print(f"No-data value: {dataset.nodata}")

# Analyze raster resolution
print(f"Raster resolution (width, height): {dataset.res}")
print(f"Raster shape (height, width): {dataset.shape}")

# Read the raster data
raster_data = dataset.read(1)

# SNS Plot
sns.set(style="darkgrid")
plt.figure(figsize=(8, 6))

# Histogram of raster values
hist = plt.hist(raster_data[raster_data != dataset.nodata].flatten(), color='orange', bins=50)
plt.title('Data Seluruh Kemiringan Lereng (Slope) Permukaan Mars (resolusi 1 derajat koordinat)')
plt.xlabel('Nilai Slope (° derajat)')
plt.ylabel('Banyak data')

# Ubah titik ke koma
def indonesia_format(x, pos=None):
    return f"{x:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

formatter = mtick.FuncFormatter(indonesia_format)
plt.gca().xaxis.set_major_formatter(formatter)

#_______________________________________________________________________________________________________________________________________#

plt.suptitle('Perbandingan Nilai Kemiringan Lereng (Slope) dari Seluruh Permukaan Mars', y=.92)
plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.show()

# Plot the raster data
plt.figure(figsize=(25, 6))
plt.imshow(raster_data, cmap='viridis')
plt.colorbar(label='Raster Values')
plt.title("Raster Data Visualization")
plt.show()

"""### **Extracting Data**"""

# Extract value dari koordinat di excel
def extract_pixel_values_from_excel(excel_file_path, tiff_file_path, image_width, image_height, output_excel_path):

    excel_data = pd.read_excel(excel_file_path)
    longitudes = excel_data['Longitude']
    latitudes = excel_data['Latitude']

    # Konversi koordinat geo ke pixel
    pixel_x = ((longitudes + 180) / 360) * image_width
    pixel_y = ((90 - latitudes) / 180) * image_height

    pixel_x = np.clip(pixel_x, 0, image_width - 1)
    pixel_y = np.clip(pixel_y, 0, image_height - 1)

    # Olah TIF file
    with rasterio.open(tiff_file_path) as src:
        pixel_values = [src.read(1)[int(y), int(x)] for x, y in zip(pixel_x, pixel_y)]

    excel_data['Extracted_Value'] = pixel_values
    excel_data.to_excel(output_excel_path, index=False)

#_______________________________________________________________________________________________________________________________________#

# Dir TIF File
tiff_file_path = '/content/slopedss-all.tif'

# Dimensi TIF
image_width = 24724
image_height = 4752

#_______________________________________________________________________________________________________________________________________#

# Input Output File
input_output_files = [
    ("/content/Coordinates/random_grid_regions_1_p1.xlsx", "/content/output_rg_extracted_1.xlsx"),
    ("/content/Coordinates/random_grid_regions_2_p1.xlsx", "/content/output_rg_extracted_2.xlsx"),
    ("/content/Coordinates/random_grid_regions_3_p1.xlsx", "/content/output_rg_extracted_3.xlsx"),

    ("/content/Coordinates/random_uniform_regions_1_p1.xlsx", "/content/output_ru_extracted_1.xlsx"),
    ("/content/Coordinates/random_uniform_regions_2_p1.xlsx", "/content/output_ru_extracted_2.xlsx"),
    ("/content/Coordinates/random_uniform_regions_3_p1.xlsx", "/content/output_ru_extracted_3.xlsx"),

    ("/content/Coordinates/sorted_coordinates_1.xlsx", "/content/output_dss_extracted_1.xlsx"),
    ("/content/Coordinates/sorted_coordinates_2.xlsx", "/content/output_dss_extracted_2.xlsx"),
    ("/content/Coordinates/sorted_coordinates_3.xlsx", "/content/output_dss_extracted_3.xlsx"),
]

# Simpan file output
for input_file, output_file in input_output_files:
    extract_pixel_values_from_excel(input_file, tiff_file_path, image_width, image_height, output_file)

output_directory = "/content/"
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

# Input file
input_excel_files = [
    "/content/output_dss_extracted_1.xlsx",
    "/content/output_dss_extracted_2.xlsx",
    "/content/output_dss_extracted_3.xlsx"
]

#_______________________________________________________________________________________________________________________________________#

# Nilai yang ingin di buang
threshold = 0

#_______________________________________________________________________________________________________________________________________#

# Ulangi ke seluruh file
for i, input_excel_file in enumerate(input_excel_files, start=1):
    df = pd.read_excel(input_excel_file)

    missing_values_mask = np.isclose(df['Extracted_Value'], threshold)

    valid_indices = df.index[~missing_values_mask]
    valid_values = df.loc[~missing_values_mask, 'Extracted_Value']
    missing_indices = df.index[missing_values_mask]

    interpolated_values = np.interp(missing_indices, valid_indices, valid_values)

    df.loc[missing_indices, 'Extracted_Value'] = interpolated_values

    output_excel_file = os.path.join(output_directory, f"DSS_slope_region_{i}.xlsx")
    df.to_excel(output_excel_file, index=False)

"""## **Extracting Inertia Thermal Day/Night**


----------------------------------------

### **Downloading & Checking Data**
"""

# IMG Data
! gdown --id 1KE3trmrAosrWgRszB0DN2oZul4EfTGw- # Night Thermal Data
! gdown --id 1RShEM8b7bM2nT5ex-3oHDUJ0MOJPMh4E # Day Thermal Data

# LBL Data
! gdown --id 1_AEmM-O8FALq28oySeVHGl8aQqIHsKdw #LBL Night
! gdown --id 1kPzZ-biWsZpT4oqg1zqvBh8TEkqRb5_w #LBL Day

def parse_lbl_file(lbl_file_path):
    metadata = {}
    with open(lbl_file_path, 'r') as file:
        for line in file:
            if '=' in line:
                key, value = line.split('=', 1)
                metadata[key.strip()] = value.strip().replace('"', '')
    return metadata

lbl_path = '/content/global_ti_night_2007.lbl'
metadata = parse_lbl_file(lbl_path)
print(metadata)

"""### **Thermal Inertia Night**"""

# Define paths to the image file and Excel files
img_path = '/content/global_ti_night_2007.img'

excel_paths = [
    "/content/Coordinates/random_grid_regions_1_p10.xlsx",
    "/content/Coordinates/random_grid_regions_2_p10.xlsx",
    "/content/Coordinates/random_grid_regions_3_p10.xlsx",

    "/content/Coordinates/random_uniform_regions_1_p10.xlsx",
    "/content/Coordinates/random_uniform_regions_2_p10.xlsx",
    "/content/Coordinates/random_uniform_regions_3_p10.xlsx",

    "/content/Coordinates/sorted_coordinates_1.xlsx",
    "/content/Coordinates/sorted_coordinates_2.xlsx",
    "/content/Coordinates/sorted_coordinates_3.xlsx"
]
output_excel_paths = [
    '/content/random_grid_TI_night_region_1.xlsx',
    '/content/random_grid_TI_night_region_2.xlsx',
    '/content/random_grid_TI_night_region_3.xlsx',

    '/content/random_uniform_TI_night_region_1.xlsx',
    '/content/random_uniform_TI_night_region_2.xlsx',
    '/content/random_uniform_TI_night_region_3.xlsx',

    '/content/DSS_TI_night_region_1.xlsx',
    '/content/DSS_TI_night_region_2.xlsx',
    '/content/DSS_TI_night_region_3.xlsx'
]

# Function to read image data
def read_image_data(img_path, lines, line_samples, sample_type):
    dtype_map = {
        'MSB_INTEGER': '>i2',  # Big-endian 16-bit integer
    }

    dtype = dtype_map[sample_type]

    # Read the image data
    data = np.fromfile(img_path, dtype=dtype)

    # Reshape the data according to the image dimensions
    data = data.reshape((lines, line_samples))

    return data

# Metadata (parsed from the LBL file)
metadata = {
    'LINES': '3600',
    'LINE_SAMPLES': '7200',
    'SAMPLE_TYPE': 'MSB_INTEGER',
    'MAP_RESOLUTION': '20.0 <pix/deg>',
    'SAMPLE_PROJECTION_OFFSET': '3600.5',
    'LINE_PROJECTION_OFFSET': '1800.5',
}

lines = int(metadata['LINES'])
line_samples = int(metadata['LINE_SAMPLES'])
sample_type = metadata['SAMPLE_TYPE']

# Read the image
image_data = read_image_data(img_path, lines, line_samples, sample_type)

# Adjust longitude for 0-360 range
def adjust_longitude(lon):
    if lon > 180:
        lon -= 360
    return lon

# Convert coordinates to pixel indices
def convert_coordinates_to_indices(lat, lon, metadata):
    # Adjust longitude if necessary
    lon = adjust_longitude(lon)

    # Read projection metadata
    map_resolution = float(metadata['MAP_RESOLUTION'].split()[0])  # pixels per degree
    sample_projection_offset = float(metadata['SAMPLE_PROJECTION_OFFSET'])
    line_projection_offset = float(metadata['LINE_PROJECTION_OFFSET'])

    # Convert latitude and longitude to indices
    line_index = line_projection_offset - (lat * map_resolution)
    sample_index = (lon * map_resolution) + sample_projection_offset

    # Round indices to integers
    line_index = int(round(line_index))
    sample_index = int(round(sample_index))

    return line_index, sample_index

# Iterate over the rows in the DataFrame and extract values
def extract_values_from_image(df, image_data, metadata):
    extracted_data = []

    for _, row in df.iterrows():
        lat = row['Latitude']
        lon = row['Longitude']

        # Convert coordinates to image indices
        line_idx, sample_idx = convert_coordinates_to_indices(lat, lon, metadata)

        # Check if indices are within bounds
        if 0 <= line_idx < image_data.shape[0] and 0 <= sample_idx < image_data.shape[1]:
            # Extract the value
            value = image_data[line_idx, sample_idx]
            extracted_data.append({'Latitude': lat, 'Longitude': lon, 'Value': value})
        else:
            # Handle out-of-bounds indices
            extracted_data.append({'Latitude': lat, 'Longitude': lon, 'Value': None})
            print(f"Coordinates out of bounds: ({lat}, {lon}) -> Indexes: ({line_idx}, {sample_idx})")

    return extracted_data

# Process each input Excel file and save the results to separate output files
for i, excel_path in enumerate(excel_paths):
    # Read the Excel file into a DataFrame
    df = pd.read_excel(excel_path)

    # Extract values from the image
    extracted_data = extract_values_from_image(df, image_data, metadata)

    # Create a DataFrame from the extracted data
    output_df = pd.DataFrame(extracted_data)

    # Save the DataFrame to an Excel file
    output_excel_path = output_excel_paths[i]
    output_df.to_excel(output_excel_path, index=False)

    print(f"Extracted values from {excel_path} have been saved to {output_excel_path}.")

"""### **Thermal Inertia Day**"""

# Define paths to the image file and Excel files
img_path = '/content/global_ti_day_2007.img'

excel_paths = [
    "/content/Coordinates/random_grid_regions_1_p10.xlsx",
    "/content/Coordinates/random_grid_regions_2_p10.xlsx",
    "/content/Coordinates/random_grid_regions_3_p10.xlsx",

    "/content/Coordinates/random_uniform_regions_1_p10.xlsx",
    "/content/Coordinates/random_uniform_regions_2_p10.xlsx",
    "/content/Coordinates/random_uniform_regions_3_p10.xlsx",

    "/content/Coordinates/sorted_coordinates_1.xlsx",
    "/content/Coordinates/sorted_coordinates_2.xlsx",
    "/content/Coordinates/sorted_coordinates_3.xlsx"
]
output_excel_paths = [
    '/content/random_grid_TI_day_region_1.xlsx',
    '/content/random_grid_TI_day_region_2.xlsx',
    '/content/random_grid_TI_day_region_3.xlsx',

    '/content/random_uniform_TI_day_region_1.xlsx',
    '/content/random_uniform_TI_day_region_2.xlsx',
    '/content/random_uniform_TI_day_region_3.xlsx',

    '/content/DSS_TI_day_region_1.xlsx',
    '/content/DSS_TI_day_region_2.xlsx',
    '/content/DSS_TI_day_region_3.xlsx'
]

# Function to read image data
def read_image_data(img_path, lines, line_samples, sample_type):
    dtype_map = {
        'MSB_INTEGER': '>i2',  # Big-endian 16-bit integer
    }

    dtype = dtype_map[sample_type]

    # Read the image data
    data = np.fromfile(img_path, dtype=dtype)

    # Reshape the data according to the image dimensions
    data = data.reshape((lines, line_samples))

    return data

# Metadata (parsed from the LBL file)
metadata = {
    'LINES': '3600',
    'LINE_SAMPLES': '7200',
    'SAMPLE_TYPE': 'MSB_INTEGER',
    'MAP_RESOLUTION': '20.0 <pix/deg>',
    'SAMPLE_PROJECTION_OFFSET': '3600.5',
    'LINE_PROJECTION_OFFSET': '1800.5',
}

lines = int(metadata['LINES'])
line_samples = int(metadata['LINE_SAMPLES'])
sample_type = metadata['SAMPLE_TYPE']

# Read the image
image_data = read_image_data(img_path, lines, line_samples, sample_type)

# Adjust longitude for 0-360 range
def adjust_longitude(lon):
    if lon > 180:
        lon -= 360
    return lon

# Convert coordinates to pixel indices
def convert_coordinates_to_indices(lat, lon, metadata):
    # Adjust longitude if necessary
    lon = adjust_longitude(lon)

    # Read projection metadata
    map_resolution = float(metadata['MAP_RESOLUTION'].split()[0])  # pixels per degree
    sample_projection_offset = float(metadata['SAMPLE_PROJECTION_OFFSET'])
    line_projection_offset = float(metadata['LINE_PROJECTION_OFFSET'])

    # Convert latitude and longitude to indices
    line_index = line_projection_offset - (lat * map_resolution)
    sample_index = (lon * map_resolution) + sample_projection_offset

    # Round indices to integers
    line_index = int(round(line_index))
    sample_index = int(round(sample_index))

    return line_index, sample_index

# Iterate over the rows in the DataFrame and extract values
def extract_values_from_image(df, image_data, metadata):
    extracted_data = []

    for _, row in df.iterrows():
        lat = row['Latitude']
        lon = row['Longitude']

        # Convert coordinates to image indices
        line_idx, sample_idx = convert_coordinates_to_indices(lat, lon, metadata)

        # Check if indices are within bounds
        if 0 <= line_idx < image_data.shape[0] and 0 <= sample_idx < image_data.shape[1]:
            # Extract the value
            value = image_data[line_idx, sample_idx]
            extracted_data.append({'Latitude': lat, 'Longitude': lon, 'Value': value})
        else:
            # Handle out-of-bounds indices
            extracted_data.append({'Latitude': lat, 'Longitude': lon, 'Value': None})
            print(f"Coordinates out of bounds: ({lat}, {lon}) -> Indexes: ({line_idx}, {sample_idx})")

    return extracted_data

# Process each input Excel file and save the results to separate output files
for i, excel_path in enumerate(excel_paths):
    # Read the Excel file into a DataFrame
    df = pd.read_excel(excel_path)

    # Extract values from the image
    extracted_data = extract_values_from_image(df, image_data, metadata)

    # Create a DataFrame from the extracted data
    output_df = pd.DataFrame(extracted_data)

    # Save the DataFrame to an Excel file
    output_excel_path = output_excel_paths[i]
    output_df.to_excel(output_excel_path, index=False)

    print(f"Extracted values from {excel_path} have been saved to {output_excel_path}.")

"""### Extract all"""

# Input file
img_path = '/content/global_ti_night_2007.img'

# Metadata file
metadata = {
    'LINES': '3600',
    'LINE_SAMPLES': '7200',
    'SAMPLE_TYPE': 'MSB_INTEGER',
}

# baca data dan Konversi data
def read_image_data(img_path, lines, line_samples, sample_type):
    dtype_map = {
        'MSB_INTEGER': '>i2',
    }
    dtype = dtype_map[sample_type]
    data = np.fromfile(img_path, dtype=dtype)
    data = data.astype(np.int16)
    data = data.reshape((lines, line_samples))

    return data

lines = int(metadata['LINES'])
line_samples = int(metadata['LINE_SAMPLES'])
sample_type = metadata['SAMPLE_TYPE']

image_data = read_image_data(img_path, lines, line_samples, sample_type)
all_values = image_data.flatten()

# SNS Plot
sns.set(style="darkgrid")
plt.figure(figsize=(8, 6))
sns.histplot(all_values, bins=350, color='orange', edgecolor='#eaeaf2', linewidth=1)

plt.title('Data Seluruh Thermal Inertia (TI) Malam Hari Permukaan Mars (resolusi 1 derajat koordinat)')
plt.xlabel('Inersia Termal ($\mathrm{J} \, \mathrm{m}^{-2} \mathrm{K}^{-1} \mathrm{s}^{-1/2}$)')
plt.ylabel('Banyak data')
plt.xlim(0, 600)

# Ubah titik ke koma
def indonesia_format(x, pos=None):
    return f"{x:,.0f}".replace(',', 'X').replace('.', ',').replace('X', '.')

formatter = mtick.FuncFormatter(indonesia_format)
plt.gca().xaxis.set_major_formatter(formatter)

plt.suptitle('Perbandingan Nilai Thermal Inertia (TI) Malam Hari dari Seluruh Permukaan Mars', y=.92)
plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.show()

# Input file
img_path = '/content/global_ti_day_2007.img'

# Metadata file
metadata = {
    'LINES': '3600',
    'LINE_SAMPLES': '7200',
    'SAMPLE_TYPE': 'MSB_INTEGER',
}

# baca data dan Konversi data
def read_image_data(img_path, lines, line_samples, sample_type):
    dtype_map = {
        'MSB_INTEGER': '>i2',
    }
    dtype = dtype_map[sample_type]
    data = np.fromfile(img_path, dtype=dtype)
    data = data.astype(np.int16)
    data = data.reshape((lines, line_samples))

    return data

lines = int(metadata['LINES'])
line_samples = int(metadata['LINE_SAMPLES'])
sample_type = metadata['SAMPLE_TYPE']

image_data = read_image_data(img_path, lines, line_samples, sample_type)
all_values = image_data.flatten()

# SNS Plot
sns.set(style="darkgrid")
plt.figure(figsize=(8, 6))
sns.histplot(all_values, bins=350, color='orange', edgecolor='#eaeaf2', linewidth=1)

plt.title('Data Seluruh Thermal Inertia (TI) Siang Hari Permukaan Mars (resolusi 1 derajat koordinat)')
plt.xlabel('Inersia Termal ($\mathrm{J} \, \mathrm{m}^{-2} \mathrm{K}^{-1} \mathrm{s}^{-1/2}$)')
plt.ylabel('Banyak data')
plt.xlim(0, 700)

# Ubah titik ke koma
def indonesia_format(x, pos=None):
    return f"{x:,.0f}".replace(',', 'X').replace('.', ',').replace('X', '.')

formatter = mtick.FuncFormatter(indonesia_format)
plt.gca().xaxis.set_major_formatter(formatter)

plt.suptitle('Perbandingan Nilai Thermal Inertia (TI) Siang Hari dari Seluruh Permukaan Mars', y=.92)
plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.show()