# SCRIPT --------------------------------------------------------------------------------------------------------------
# Integration test: numerate method
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

dataset_name = 'numerate'
dataset_results = os.path.join(folder_testdata, 'results.gdb', dataset_name)
# ---------------------------------------------------------------------------------------------------------------------


# FUNCTIONS -----------------------------------------------------------------------------------------------------------
def test_numerate(results_gdb):
    # https://pro.arcgis.com/en/pro-app/latest/tool-reference/data-management/feature-compare.htm

    point_name = 'Point'
    point = os.path.join(gdb_data, point_name)

    point_numerate_name = f'{point_name}_numerate'
    point_numerate = os.path.join(dataset_results, point_numerate_name)
    point_numerate_test = os.path.join(results_gdb, point_numerate_name)

    try:
        arcpy.CopyFeatures_management(point, point_numerate_test)
        geom = Geometry(point_numerate_test)
        geom.numerate('top_left', 'id_top_left')
        geom.numerate('top_right', 'id_top_right')
        geom.numerate('bottom_left', 'id_bottom_left')
        geom.numerate('bottom_right', 'id_bottom_right')
        geom.numerate('left_top', 'id_left_top')
        geom.numerate('left_bottom', 'id_left_bottom')
        geom.numerate('right_top', 'id_right_top')
        geom.numerate('right_bottom', 'id_right_bottom')

        result = arcpy.FeatureCompare_management(
            point_numerate, point_numerate_test, 'OBJECTID', continue_compare='CONTINUE_COMPARE'
        )

        assert result.getOutput(1) == 'true'

    finally:
        arcpy.Delete_management(point_numerate_test)
# ---------------------------------------------------------------------------------------------------------------------


# MAIN PROGRAM --------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    pass
# ---------------------------------------------------------------------------------------------------------------------
