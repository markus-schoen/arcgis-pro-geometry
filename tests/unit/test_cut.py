# SCRIPT --------------------------------------------------------------------------------------------------------------
# Test cut method
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
import os
from pathlib import Path

import arcpy

from arcgis_pro_geometry.Geometry import Geometry
# ---------------------------------------------------------------------------------------------------------------------


# GENERAL INFORMATION -------------------------------------------------------------------------------------------------
__author__ = 'Markus Schön'
__copyright__ = 'Copyright 2021 by Markus Schön'
__license__ = 'Apache License, Version 2.0'
# ---------------------------------------------------------------------------------------------------------------------


# PATHS ---------------------------------------------------------------------------------------------------------------
folder_tool = Path(__file__).parents[2]
folder_testdata = os.path.join(folder_tool, 'data', '_testdata')

gdb_data = os.path.join(folder_testdata, 'data.gdb')

dataset_name = 'cut'
dataset_results = os.path.join(folder_testdata, 'results.gdb', dataset_name)
dataset_results_test = os.path.join(folder_testdata, 'results_test.gdb', dataset_name)
# ---------------------------------------------------------------------------------------------------------------------


# VARIABLES -----------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------


# CLASSES -------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------


# FUNCTIONS -----------------------------------------------------------------------------------------------------------
def test_cut_polygon():
    # https://pro.arcgis.com/en/pro-app/latest/tool-reference/data-management/feature-compare.htm

    line = os.path.join(gdb_data, 'Line')
    polygon = os.path.join(gdb_data, 'Polygon')

    polygon_cut = os.path.join(dataset_results, 'Polygon_cut')
    polygon_cut_test = os.path.join(dataset_results_test, 'Polygon_cut')

    geom = Geometry(polygon)
    geom.cut(line, polygon_cut_test)

    result = arcpy.FeatureCompare_management(
        polygon_cut, polygon_cut_test, 'OBJECTID', continue_compare='CONTINUE_COMPARE'
    )

    assert result.getOutput(1) == 'true'

    arcpy.Delete_management(polygon_cut_test)
# ---------------------------------------------------------------------------------------------------------------------


# PREPARATION ---------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------


# MAIN PROGRAM --------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    pass
# ---------------------------------------------------------------------------------------------------------------------
