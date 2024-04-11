import arcpy
import numpy as np
import psycopg2

#path to local database
local_gdb = r"C:\Users\Deepika\OneDrive\Documents\ArcGIS\Projects\ArcGIS-II-Lab2\ArcGIS-II-Lab2.gdb"


# Establish SDE Connection via PGAdmin & Catalog Pane in ArcGIS Pro
db = r"C:\Users\Deepika\OneDrive\Documents\ArcGIS\Projects\ArcGIS-II-Lab2\PostgreSQL-35-gis5572(postgres)(1).sde"

# Establish database connection
conn = psycopg2.connect(host = '35.224.213.125',
                              port = '5432',
                              database = 'gis5572',
                              user = 'postgres',
                              password = 'Deepika@98',
                             )

# Create a cursor object
cur = conn.cursor()


# Fetch the results
#results = cursor.fetchall()

# Do something with the results
#cur.execute(sql)

# Close cursor and connection
conn.commit()
cur.close()
conn.close


# Calculated Interpolated IDW
with arcpy.EnvManager(mask="Clipped_dem", scratchWorkspace=r"C:\Users\Deepika\OneDrive\Documents\ArcGIS\Projects\ArcGIS-II-Lab2\ArcGIS-II-Lab2.gdb"):
    out_raster = arcpy.sa.Idw(
        in_point_features="gis5572.postgres.dem_points_in_sde",
        z_field="grid_code",
        cell_size=2160,
        power=2,
        search_radius="VARIABLE 12",
        in_barrier_polyline_features=None
    )
    out_raster.save(r"C:\Users\Deepika\OneDrive\Documents\ArcGIS\Projects\ArcGIS-II-Lab2\ArcGIS-II-Lab2.gdb\Idw_dem_poin1")

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
    out_surface_raster.save(r"C:\Users\Deepika\OneDrive\Documents\ArcGIS\Projects\ArcGIS-II-Lab2\ArcGIS-II-Lab2.gdb\Kriging_gis51")

# Spline
with arcpy.EnvManager(mask="Clipped_dem", scratchWorkspace=r"C:\Users\Deepika\OneDrive\Documents\ArcGIS\Projects\ArcGIS-II-Lab2\ArcGIS-II-Lab2.gdb"):
    out_raster = arcpy.sa.Spline(
        in_point_features="gis5572.postgres.dem_points_in_sde",
        z_field="grid_code",
        cell_size=2160,
        spline_type="REGULARIZED",
        weight=0.1,
        number_points=12
    )
    out_raster.save(r"C:\Users\Deepika\OneDrive\Documents\ArcGIS\Projects\ArcGIS-II-Lab2\ArcGIS-II-Lab2.gdb\Spline_gis551")

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

# IDW upload points to sde
import arcpy

# Define functions
def downsample_raster(input_raster, output_raster, cell_size):
    arcpy.Resample_management(input_raster, output_raster, cell_size)

def raster_to_points(input_raster, output_points):
    arcpy.RasterToPoint_conversion(input_raster, output_points, "VALUE")

def upload_points_to_sde(input_points, output_sde_connection, output_sde_feature_class):
    arcpy.FeatureClassToFeatureClass_conversion(input_points, output_sde_connection, output_sde_feature_class)

# Paths and parameters
input_raster = r"C:\Users\Deepika\OneDrive\Documents\ArcGIS\Projects\ArcGIS-II-Lab2\ArcGIS-II-Lab2.gdb\Idw_dem_poin1"
output_downsampled_raster = r'C:\Users\Deepika\OneDrive\Documents\ArcGIS\Projects\ArcGIS-II-Lab2\downIDWelevation_raster.tif'
output_points = r'C:\Users\Deepika\OneDrive\Documents\ArcGIS\Projects\ArcGIS-II-Lab2\idwelevpoints.shp'
output_sde_connection = r"C:\Users\Deepika\OneDrive\Documents\ArcGIS\Projects\ArcGIS-II-Lab2\PostgreSQL-35-gis5572(postgres)(1).sde"
output_sde_feature_class = 'idwelevationpoints_in_sde'

# Perform operations
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


# Kriging upload points to sde
import arcpy

# Define functions
def downsample_raster(input_raster, output_raster, cell_size):
    arcpy.Resample_management(input_raster, output_raster, cell_size)

def raster_to_points(input_raster, output_points):
    arcpy.RasterToPoint_conversion(input_raster, output_points, "VALUE")

def upload_points_to_sde(input_points, output_sde_connection, output_sde_feature_class):
    arcpy.FeatureClassToFeatureClass_conversion(input_points, output_sde_connection, output_sde_feature_class)

# Paths and parameters
input_raster = r"C:\Users\Deepika\OneDrive\Documents\ArcGIS\Projects\ArcGIS-II-Lab2\ArcGIS-II-Lab2.gdb\Kriging_gis51"
output_downsampled_raster = r'C:\Users\Deepika\OneDrive\Documents\ArcGIS\Projects\ArcGIS-II-Lab2\downkrigingelevation_raster.tif'
output_points = r'C:\Users\Deepika\OneDrive\Documents\ArcGIS\Projects\ArcGIS-II-Lab2\krigelevpoints.shp'
output_sde_connection = r"C:\Users\Deepika\OneDrive\Documents\ArcGIS\Projects\ArcGIS-II-Lab2\PostgreSQL-35-gis5572(postgres)(1).sde"
output_sde_feature_class = 'idwelevationpoints_in_sde'

# Perform operations
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


# Spline upload points to sde
import arcpy

# Define functions
def downsample_raster(input_raster, output_raster, cell_size):
    arcpy.Resample_management(input_raster, output_raster, cell_size)

def raster_to_points(input_raster, output_points):
    arcpy.RasterToPoint_conversion(input_raster, output_points, "VALUE")

def upload_points_to_sde(input_points, output_sde_connection, output_sde_feature_class):
    arcpy.FeatureClassToFeatureClass_conversion(input_points, output_sde_connection, output_sde_feature_class)

# Paths and parameters
input_raster = r"C:\Users\Deepika\OneDrive\Documents\ArcGIS\Projects\ArcGIS-II-Lab2\ArcGIS-II-Lab2.gdb\Spline_gis551"
output_downsampled_raster = r'C:\Users\Deepika\OneDrive\Documents\ArcGIS\Projects\ArcGIS-II-Lab2\downsplineelevation_raster.tif'
output_points = r'C:\Users\Deepika\OneDrive\Documents\ArcGIS\Projects\ArcGIS-II-Lab2\splineelevpoints.shp'
output_sde_connection = r"C:\Users\Deepika\OneDrive\Documents\ArcGIS\Projects\ArcGIS-II-Lab2\PostgreSQL-35-gis5572(postgres)(1).sde"
output_sde_feature_class = 'splineelevationpoints_in_sde'

# Perform operations
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


arcpy.ga.ExploratoryInterpolation(
    in_features="gis5572.postgres.dem_points_in_sde",
    value_field="grid_code",
    out_cv_table=r"C:\Users\Deepika\OneDrive\Documents\ArcGIS\Projects\ArcGIS-II-Lab2\ArcGIS-II-Lab2.gdb\ExploratoryInterpolation1",
    out_geostat_layer=None,
    interp_methods="SIMPLE_KRIGING;ORDINARY_KRIGING;IDW",
    comparison_method="SINGLE",
    criterion="ACCURACY",
    criteria_hierarchy="ACCURACY PERCENT #",
    weighted_criteria="ACCURACY 1",
    exclusion_criteria=None
)


