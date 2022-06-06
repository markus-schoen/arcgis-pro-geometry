# SCRIPT --------------------------------------------------------------------------------------------------------------
# Create circles and centroids for every three points of a point feature layer/class.
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
# Thanks to all developers who created the used modules.
# Thanks to FelixIP and BERA from gis.stackexchange.com for the inspiration:
# - https://gis.stackexchange.com/questions/286439/need-tool-for-arcmap-to-draw-circle-touching-three-points
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
out_fc_circle_name = arcpy.GetParameterAsText(2)
out_fc_circle_centroid_name = arcpy.GetParameterAsText(3)
# ---------------------------------------------------------------------------------------------------------------------


# PATHS ---------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------


# CLASSES -------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------


# FUNCTIONS -----------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------


# PREPARATION ---------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------


# MAIN PROGRAM --------------------------------------------------------------------------------------------------------
out_fc_circle = os.path.join(out_fc_gdb, out_fc_circle_name)
out_fc_circle_centroid = os.path.join(out_fc_gdb, out_fc_circle_centroid_name) if out_fc_circle_centroid_name else None

# Create convex hull feature class
with Geometry(fc) as fc_geom:
    fc_geom.circle_from_three_points(out_fc_circle, out_fc_circle_centroid)

# Add convex hull to content
project = arcpy.mp.ArcGISProject("CURRENT")
active_map = project.activeMap

if active_map:
    active_map.addDataFromPath(out_fc_circle)
    if out_fc_circle_centroid:
        active_map.addDataFromPath(out_fc_circle_centroid)
# ---------------------------------------------------------------------------------------------------------------------
