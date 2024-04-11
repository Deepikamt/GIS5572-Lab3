# Importing necessary libraries
import arcpy
import numpy as np
import psycopg2

# Path to local database
local_gdb = r"C:\Users\Deepika\OneDrive\Documents\ArcGIS\Projects\ArcGIS-II-Lab2\ArcGIS-II-Lab2.gdb"

# Establishing SDE Connection via PGAdmin & Catalog Pane in ArcGIS Pro
db = r"C:\Users\Deepika\OneDrive\Documents\ArcGIS\Projects\ArcGIS-II-Lab2\PostgreSQL-35-gis5572(postgres)(1).sde"

# Establishing database connection
conn = psycopg2.connect(host='35.224.213.125',
                        port='5432',
                        database='gis5572',
                        user='postgres',
                        password='****')

# Creating a cursor object
cur = conn.cursor()

# Fetching the results
# results = cursor.fetchall()

# Closing cursor and connection
conn.commit()
cur.close()
conn.close

# Calculating Interpolated IDW
with arcpy.EnvManager(mask="Clipped_dem", scratchWorkspace=r"C:\Users\Deepika\OneDrive\Documents\ArcGIS\Projects\ArcGIS-II-Lab2\ArcGIS-II-Lab2.gdb"):
    out_raster = arcpy.sa.Idw(
        in_point_features="gis5572.postgres.dem_points_in_sde",
        z_field="grid_code",
        cell_size=2160,
        power=2,
        search_radius="VARIABLE 12",
        in_barrier_polyline_features=None
    )
    out_raster.save(r"C:\Users\Deepika\OneDrive\Documents\ArcGIS\Projects\ArcGIS-II-Lab2\ArcGIS-II-Lab2.gdb\Idw_dem_point1")

# Kriging
with arcpy.EnvManager(scratchWorkspace=r"C:\Users\Deepika\OneDrive\Documents\ArcGIS\Projects\ArcGIS-II-Lab2\ArcGIS-II-Lab2.gdb"):
    out_raster_Kriging = arcpy.sa.Kriging(
        in_point_features="gis5572.postgres.dem_points_in_sde",
        z_field="grid_code",
        kriging_model="Spherical # # # #",
        cell_size=2160,
        search_radius="VARIABLE 12",
        out_variance_prediction_raster=None
    )
    out_raster_Kriging.save(r"C:\Users\Deepika\OneDrive\Documents\ArcGIS\Projects\ArcGIS-II-Lab2\ArcGIS-II-Lab2.gdb\Kriging_gis51")

# Spline
with arcpy.EnvManager(mask="Clipped_dem", scratchWorkspace=r"C:\Users\Deepika\OneDrive\Documents\ArcGIS\Projects\ArcGIS-II-Lab2\ArcGIS-II-Lab2.gdb"):
    out_raster_Spline = arcpy.sa.Spline(
        in_point_features="gis5572.postgres.dem_points_in_sde",
        z_field="grid_code",
        cell_size=2160,
        spline_type="REGULARIZED",
        weight=0.1,
        number_points=12
    )
    out_raster_Spline.save(r"C:\Users\Deepika\OneDrive\Documents\ArcGIS\Projects\ArcGIS-II-Lab2\ArcGIS-II-Lab2.gdb\Spline_gis551")

# Raster to point IDW
arcpy.conversion.RasterToPoint(
    in_raster="out_raster_IDW",
    out_point_features=r"C:\Users\Deepika\OneDrive\Documents\ArcGIS\Projects\ArcGIS-II-Lab2\ArcGIS-II-Lab2.gdb\RasterT_Idw_dem1",
    raster_field="Value"
)

# Raster to point Kriging
arcpy.conversion.RasterToPoint(
    in_raster="out_raster_Kriging",
    out_point_features=r"C:\Users\Deepika\OneDrive\Documents\ArcGIS\Projects\ArcGIS-II-Lab2\ArcGIS-II-Lab2.gdb\RasterT_dem_Kriging1",
    raster_field="Value"
)

# Raster to Point Spline
arcpy.conversion.RasterToPoint(
    in_raster="out_raster_Spline",
    out_point_features=r"C:\Users\Deepika\OneDrive\Documents\ArcGIS\Projects\ArcGIS-II-Lab2\ArcGIS-II-Lab2.gdb\RasterT_dem_spline",
    raster_field="Value"
)

# IDW upload points to SDE
import arcpy

# Defining functions
def downsample_raster(input_raster, output_raster, cell_size):
    arcpy.Resample_management(input_raster, output_raster, cell_size)

def raster_to_points(input_raster, output_points):
    arcpy.RasterToPoint_conversion(input_raster, output_points, "VALUE")

def upload_points_to_sde(input_points, output_sde_connection, output_sde_feature_class):
    arcpy.FeatureClassToFeatureClass_conversion(input_points, output_sde_connection, output_sde_feature_class)

# Paths and parameters
input_raster = r"C:\Users\Deepika\OneDrive\Documents\ArcGIS\Projects\ArcGIS-II-Lab2\ArcGIS-II-Lab2.gdb\Idw_dem_point1"
output_downsampled_raster = r'C:\Users\Deepika\OneDrive\Documents\ArcGIS\Projects\ArcGIS-II-Lab2\downIDWelevation_raster.tif'
output_points = r'C:\Users\Deepika\OneDrive\Documents\ArcGIS\Projects\ArcGIS-II-Lab2\idwelevpoints.shp'
output_sde_connection = r"C:\Users\Deepika\OneDrive\Documents\ArcGIS\Projects\ArcGIS-II-Lab2\PostgreSQL-35-gis5572(postgres)(1).sde"
output_sde_feature_class = 'idwelevationpoints_in_sde'

# Performing operations
try:
    arcpy.env.scratchWorkspace = r"C:\Users\Deepika\OneDrive\Documents\ArcGIS\Projects\ArcGIS-II-Lab2\ArcGIS-II-Lab2.gdb"
    out_raster_IDW = arcpy.sa.Idw(
        in_point_features="gis5572.postgres.dem_points_in_sde",
        z_field="grid_code",
        cell_size=2160,
        power=2,
        search_radius="VARIABLE 12",
        in_barrier_polyline_features=None
    )
    out_raster_IDW.save(output_downsampled_raster)

    downsample_raster(input_raster, output_downsampled_raster, "15000")
    raster_to_points(output_downsampled_raster, output_points)
    upload_points_to_sde(output_points, output_sde_connection, output_sde_feature_class)
    print("Points uploaded to SDE successfully!")
except arcpy.ExecuteError:
    print(arcpy.GetMessages(2))
except Exception as e:
    print("An error occurred:", e)

# Kriging upload points to SDE
import arcpy

# Defining functions
def downsample_raster(input_raster, output_raster, cell_size):
    arcpy.Resample_management(input_raster, output_raster, cell_size)

def raster_to_points(input_raster, output_points):
    arcpy.RasterToPoint_conversion(input_raster,


