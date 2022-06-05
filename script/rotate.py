# SCRIPT --------------------------------------------------------------------------------------------------------------
# Rotate a feature class/layer.
# ---------------------------------------------------------------------------------------------------------------------


# LICENSE -------------------------------------------------------------------------------------------------------------
# Copyright 2021 by Markus Schön
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
# ---------------------------------------------------------------------------------------------------------------------


# CREDITS -------------------------------------------------------------------------------------------------------------
# Thanks to Curtis Price for the rotation inspiration:
# - https://github.com/usgs/arcgis-sample/blob/master/scripts/RotateFeatureClass.py
# ---------------------------------------------------------------------------------------------------------------------


# ---------------------------------------------------------------------------------------------------------------------
# TODO /
# ---------------------------------------------------------------------------------------------------------------------


# MODULES -------------------------------------------------------------------------------------------------------------
import arcpy
from Geometry import Geometry
import os
# ---------------------------------------------------------------------------------------------------------------------


# GENERAL INFORMATION -------------------------------------------------------------------------------------------------
__author__ = 'Markus Schön'
__copyright__ = 'Copyright 2021 by Markus Schön'
__license__ = 'Apache License, Version 2.0'
# ---------------------------------------------------------------------------------------------------------------------


# VARIABLES -----------------------------------------------------------------------------------------------------------
fc = arcpy.GetParameterAsText(0)
out_fc_gdb = arcpy.GetParameterAsText(1)
out_fc_name = arcpy.GetParameterAsText(2)
rotation_angle = arcpy.GetParameter(3)
rotation_method = arcpy.GetParameterAsText(4)
# Hint: rotation_method in
# ['coordinates', 'extent_middle_point', 'point feature', 'in_feature_centroid', 'in_feature_true_centroid']
feature_layer = arcpy.GetParameterAsText(5)
point_feature_layer = arcpy.GetParameterAsText(6)
rotation_x = arcpy.GetParameter(7)
rotation_y = arcpy.GetParameter(8)
# ---------------------------------------------------------------------------------------------------------------------


# PATHS ---------------------------------------------------------------------------------------------------------------
out_fc = os.path.join(out_fc_gdb, out_fc_name)
# ---------------------------------------------------------------------------------------------------------------------


# CLASSES -------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------


# FUNCTIONS -----------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------


# PREPARATION ---------------------------------------------------------------------------------------------------------
arcpy.env.overwriteOutput = True
# ---------------------------------------------------------------------------------------------------------------------


# MAIN PROGRAM --------------------------------------------------------------------------------------------------------
# Set rotation type
if rotation_method in ['in_feature_centroid', 'in_feature_true_centroid']:
    # Use centroids for rotation
    rotation_type = rotation_method
else:
    # Use selected xy data for rotation
    rotation_type = 'xy'

# Rotate
with Geometry(fc) as fc_geom:
    out_fc = fc_geom.rotate_fc(out_fc, rotation_angle, rotation_type, rotation_x, rotation_y)

# Add out_fc to the current active map
if out_fc:
    project = arcpy.mp.ArcGISProject("CURRENT")
    active_map = project.activeMap

    if active_map:
        # Remove fc from active, if out_fc == fc
        lyrs = active_map.listLayers(out_fc_name)
        for lyr in lyrs:
            active_map.removeLayer(lyr)

        # Add out_fc to active map
        in_layer_out_fc = active_map.addDataFromPath(out_fc)
# ---------------------------------------------------------------------------------------------------------------------
