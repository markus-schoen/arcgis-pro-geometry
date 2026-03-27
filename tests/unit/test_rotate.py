# SCRIPT --------------------------------------------------------------------------------------------------------------
# Scrip description
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

dataset_name = 'rotate'
dataset_results = os.path.join(folder_testdata, 'results.gdb', dataset_name)
dataset_results_test = os.path.join(folder_testdata, 'results_test.gdb', dataset_name)
# ---------------------------------------------------------------------------------------------------------------------


# VARIABLES -----------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------


# CLASSES -------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------


# FUNCTIONS -----------------------------------------------------------------------------------------------------------
@pytest.mark.parametrize(
    "fc_name, expected",
    [
        ('Point', (32567113.48335, 5746147.131572414)),
        ('Line', (32567113.48335, 5746147.131572414)),
        ('Polygon', (32567113.48335, 5746147.131572414)),
    ]
)
def test_rotate_extent(fc_name, expected):
    fc = os.path.join(gdb_data, fc_name)

    extent = arcpy.Describe(fc).extent
    x_center = extent.XMin + 0.5 * extent.width
    y_center = extent.YMin + 0.5 * extent.height

    assert (x_center, y_center) == expected


@pytest.mark.parametrize(
    "fc_name, rotation_angle, expected",
    [
        ('Polygon', -30, (32567088.7696722, 5745962.970218004)),
        ('Polygon', 20, (32566956.521921936, 5746047.686711164)),
        ('Polygon', 45, (32566929.200771082, 5746123.338686171)),
        ('Polygon', 90, (32566966.351777587, 5746260.614922415)),
        ('Polygon', 127.4, (32567065.526922736, 5746326.648567188)),
        ('Polygon', 420, (32566929.32199559, 5746171.845250214))
    ]
)
def test_rotate_xy(fc_name, rotation_angle, expected):
    # xy coordinates, to be rotated
    x = 32567000
    y = 5746000

    # Get fc extent centroid as rotation point
    fc = os.path.join(gdb_data, fc_name)
    extent = arcpy.Describe(fc).extent
    x_center = extent.XMin + 0.5 * extent.width
    y_center = extent.YMin + 0.5 * extent.height
    # x_center = 32567113.48335
    # y_center = 5746147.131572414

    geom = Geometry(fc)
    assert geom.rotate_xy(x, y, rotation_angle=rotation_angle, x_cnt=x_center, y_cnt=y_center) == expected


'''
def test_rotate_polygon_xy_90():
    # https://pro.arcgis.com/en/pro-app/latest/tool-reference/data-management/feature-compare.htm

    polygon_name = 'polygon_rot_xy_90'
    polygon_rot = os.path.join(dataset_results, polygon_name)
    polygon_rot_test = os.path.join(dataset_results_test, polygon_name)

    extent = arcpy.Describe(polygon).extent
    x_center = extent.XMin + 0.5 * extent.width
    y_center = extent.YMin + 0.5 * extent.height

    geom = Geometry(polygon)
    rotation_angle = 90
    geom.rotate_fc(
        polygon_rot_test, rotation_value='xy', rotation_angle=rotation_angle, rotation_x=x_center, rotation_y=y_center
    )

    result = arcpy.FeatureCompare_management(
        polygon_rot, polygon_rot_test, 'OBJECTID', omit_field='Shape_Area', continue_compare='CONTINUE_COMPARE'
    )

    assert result.getOutput(1) == 'true'

    arcpy.Delete_management(polygon_rot_test)
'''
# ---------------------------------------------------------------------------------------------------------------------


# PREPARATION ---------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------


# MAIN PROGRAM --------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------
