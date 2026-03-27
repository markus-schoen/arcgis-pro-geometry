# SCRIPT --------------------------------------------------------------------------------------------------------------
# Test boundary method
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

dataset_name = 'boundary'
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
        ('Point', 'true'),
        ('Line', 'true'),
        ('Polygon', 'true')
    ]
)
def test_boundary(fc_name, expected):
    # https://pro.arcgis.com/en/pro-app/latest/tool-reference/data-management/feature-compare.htm
    fc = os.path.join(gdb_data, fc_name)

    fc_boundary_name = f'{fc_name}_boundary'
    fc_boundary = os.path.join(dataset_results, fc_boundary_name)
    fc_boundary_test = os.path.join(dataset_results_test, fc_boundary_name)

    try:
        geom = Geometry(fc)
        geom.boundary(fc_boundary_test)

        result = arcpy.FeatureCompare_management(
            in_base_features=fc_boundary,
            in_test_features=fc_boundary_test,
            sort_field='OBJECTID',
            continue_compare='CONTINUE_COMPARE'
        )

        assert result.getOutput(1) == expected

    finally:
        # Clean up
        arcpy.Delete_management(fc_boundary_test)
# ---------------------------------------------------------------------------------------------------------------------


# PREPARATION ---------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------


# MAIN PROGRAM --------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    pass
# ---------------------------------------------------------------------------------------------------------------------
