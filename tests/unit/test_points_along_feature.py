# SCRIPT --------------------------------------------------------------------------------------------------------------
# Test points_along_feature method
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
import pytest

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

dataset_name = 'points_along_feature'
dataset_results = os.path.join(folder_testdata, 'results.gdb', dataset_name)
dataset_results_test = os.path.join(folder_testdata, 'results_test.gdb', dataset_name)
# ---------------------------------------------------------------------------------------------------------------------


# VARIABLES -----------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------


# CLASSES -------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------


# FUNCTIONS -----------------------------------------------------------------------------------------------------------
@pytest.mark.parametrize(
    "fc_name,distance,include_endpoint,expected",
    [
        ('Line', 0.5, False, 'true'),
        ('Polygon', 0.5, False, 'true')
    ]
)
def test_points_along_feature(fc_name, distance, include_endpoint, expected):
    # https://pro.arcgis.com/en/pro-app/latest/tool-reference/data-management/feature-compare.htm

    fc = os.path.join(gdb_data, fc_name)

    fc_points_along_feature_name = f'{fc_name}_points_multipoint'
    fc_points_along_feature = os.path.join(dataset_results, fc_points_along_feature_name)
    fc_points_along_feature_test = os.path.join(dataset_results_test, fc_points_along_feature_name)

    geom = Geometry(fc)
    geom.points_along_feature(fc_points_along_feature_test, distance=distance, include_endpoint=include_endpoint)

    result = arcpy.FeatureCompare_management(
        fc_points_along_feature, fc_points_along_feature_test, 'OBJECTID', continue_compare='CONTINUE_COMPARE'
    )

    assert result.getOutput(1) == expected

    arcpy.Delete_management(fc_points_along_feature_test)


'''
def test_points_along_feature_polygon(distance=0.5, include_endpoint=False):
    # https://pro.arcgis.com/en/pro-app/latest/tool-reference/data-management/feature-compare.htm

    polygon_points_along_feature = os.path.join(dataset_results, 'Polygon_points_multipoint')
    polygon_points_along_feature_test = os.path.join(dataset_results_test, 'Polygon_points_multipoint')

    geom = Geometry(polygon)
    geom.points_along_feature(polygon_points_along_feature_test, distance=distance, include_endpoint=include_endpoint)

    result = arcpy.FeatureCompare_management(
        polygon_points_along_feature, polygon_points_along_feature_test, 'OBJECTID', continue_compare='CONTINUE_COMPARE'
    )

    assert result.getOutput(1) == 'true'

    arcpy.Delete_management(polygon_points_along_feature_test)


def test_points_along_feature_line(distance=0.5, include_endpoint=False):
    # https://pro.arcgis.com/en/pro-app/latest/tool-reference/data-management/feature-compare.htm

    line_points_along_feature = os.path.join(dataset_results, 'Line_points_multipoint')
    line_points_along_feature_test = os.path.join(dataset_results_test, 'Line_points_multipoint')

    geom = Geometry(line)
    geom.points_along_feature(line_points_along_feature_test, distance=distance, include_endpoint=include_endpoint)

    result = arcpy.FeatureCompare_management(
        line_points_along_feature, line_points_along_feature_test, 'OBJECTID', continue_compare='CONTINUE_COMPARE'
    )

    assert result.getOutput(1) == 'true'

    arcpy.Delete_management(line_points_along_feature_test)
'''
# ---------------------------------------------------------------------------------------------------------------------


# PREPARATION ---------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------


# MAIN PROGRAM --------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    pass
# ---------------------------------------------------------------------------------------------------------------------
