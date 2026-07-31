# SCRIPT --------------------------------------------------------------------------------------------------------------
# Integration test: rotate methods
# Requires ArcGIS Pro (arcpy). Skipped automatically if arcpy is not available.
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


# MODULES -------------------------------------------------------------------------------------------------------------
import os
from pathlib import Path

import pytest

arcpy = pytest.importorskip('arcpy')

from arcgis_pro_geometry import Geometry

# ---------------------------------------------------------------------------------------------------------------------


# MARKERS -------------------------------------------------------------------------------------------------------------
pytestmark = pytest.mark.integration
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
# ---------------------------------------------------------------------------------------------------------------------


# FUNCTIONS -----------------------------------------------------------------------------------------------------------
@pytest.mark.parametrize(
    'fc_name, expected',
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

    assert (x_center, y_center) == pytest.approx(expected, abs=1e-6)


@pytest.mark.parametrize(
    'fc_name, rotation_angle, expected',
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
    x = 32567000
    y = 5746000

    fc = os.path.join(gdb_data, fc_name)
    extent = arcpy.Describe(fc).extent
    x_center = extent.XMin + 0.5 * extent.width
    y_center = extent.YMin + 0.5 * extent.height

    geom = Geometry(fc)
    rotated = geom.rotate_xy(x, y, rotation_angle=rotation_angle, x_cnt=x_center, y_cnt=y_center)

    assert rotated == pytest.approx(expected, abs=1e-6)
# ---------------------------------------------------------------------------------------------------------------------


# MAIN PROGRAM --------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    pass
# ---------------------------------------------------------------------------------------------------------------------
