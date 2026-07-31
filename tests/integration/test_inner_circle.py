# SCRIPT --------------------------------------------------------------------------------------------------------------
# Integration test: inner_circle method
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

dataset_name = 'inner_circle'
dataset_results = os.path.join(folder_testdata, 'results.gdb', dataset_name)
# ---------------------------------------------------------------------------------------------------------------------


# FUNCTIONS -----------------------------------------------------------------------------------------------------------
def test_inner_circle(results_gdb):
    # https://pro.arcgis.com/en/pro-app/latest/tool-reference/data-management/feature-compare.htm

    polygon_name = 'Polygon'
    polygon = os.path.join(gdb_data, polygon_name)

    inner_circle_name = f'{polygon_name}_inner_circles'
    inner_circle_centroids_name = f'{polygon_name}_inner_circle_centroids'
    inner_circle = os.path.join(dataset_results, inner_circle_name)
    inner_circle_centroids = os.path.join(dataset_results, inner_circle_centroids_name)

    inner_circle_test = os.path.join(results_gdb, inner_circle_name)
    inner_circle_test_centroids = os.path.join(results_gdb, inner_circle_centroids_name)

    try:
        geom = Geometry(polygon)
        geom.inner_circle(inner_circle_test, inner_circle_test_centroids)

        result = arcpy.FeatureCompare_management(
            inner_circle, inner_circle_test, 'OBJECTID', continue_compare='CONTINUE_COMPARE'
        )

        assert result.getOutput(1) == 'true'

        result = arcpy.FeatureCompare_management(
            inner_circle_centroids, inner_circle_test_centroids, 'OBJECTID', continue_compare='CONTINUE_COMPARE'
        )

        assert result.getOutput(1) == 'true'

    finally:
        arcpy.Delete_management(inner_circle_test)
        arcpy.Delete_management(inner_circle_test_centroids)
# ---------------------------------------------------------------------------------------------------------------------


# MAIN PROGRAM --------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    pass
# ---------------------------------------------------------------------------------------------------------------------
