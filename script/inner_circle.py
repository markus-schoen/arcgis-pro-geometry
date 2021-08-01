# SCRIPT --------------------------------------------------------------------------------------------------------------
# Create maximum inner circles and associated centroids for polygons.
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
__version__ = '1.0.0'
__copyright__ = 'Copyright 2021 by Markus Schön'
__license__ = 'Apache License, Version 2.0'
# ---------------------------------------------------------------------------------------------------------------------


# VARIABLES -----------------------------------------------------------------------------------------------------------
fc = arcpy.GetParameterAsText(0)
out_fc_gdb = arcpy.GetParameterAsText(1)
out_fc_circle_name = arcpy.GetParameterAsText(2)
out_fc_circle_centroid_name = arcpy.GetParameterAsText(3)
accuracy = arcpy.GetParameter(4)
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

# Create boundary
with Geometry(fc) as fc_geom:
    fc_geom.inner_circle(out_fc_circle, out_fc_circle_centroid, accuracy)

# Add boundary to content
project = arcpy.mp.ArcGISProject("CURRENT")
active_map = project.activeMap
active_map.addDataFromPath(out_fc_circle)
if out_fc_circle_centroid:
    active_map.addDataFromPath(out_fc_circle_centroid)
# ---------------------------------------------------------------------------------------------------------------------
