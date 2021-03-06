# SCRIPT --------------------------------------------------------------------------------------------------------------
# Numerate all features by it's coordinates.
# To store the results, this method creates a short integer field. The lowest value is 1.
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
# ---------------------------------------------------------------------------------------------------------------------


# GENERAL INFORMATION -------------------------------------------------------------------------------------------------
__author__ = 'Markus Schön'
__copyright__ = 'Copyright 2021 by Markus Schön'
__license__ = 'Apache License, Version 2.0'
# ---------------------------------------------------------------------------------------------------------------------


# VARIABLES -----------------------------------------------------------------------------------------------------------
point_fc = arcpy.GetParameterAsText(0)
sort_by = arcpy.GetParameterAsText(1)
id_field_name = arcpy.GetParameterAsText(2)
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
with Geometry(point_fc) as point_fc_geom:
    point_fc_geom.numerate(sort_by=sort_by, field_name=id_field_name)
# ---------------------------------------------------------------------------------------------------------------------
