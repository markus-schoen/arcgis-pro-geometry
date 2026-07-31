# SCRIPT --------------------------------------------------------------------------------------------------------------
# pytest configuration for the integration tests.
#
# The integration tests compare freshly calculated geometries against the reference results in
# 'data/_testdata/results.gdb'. They need a real ArcGIS Pro installation (arcpy) and are skipped without one.
#
# Every test writes its output into a throwaway file geodatabase created below, so a test run never touches the
# repository and never leaves anything behind.
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

# ---------------------------------------------------------------------------------------------------------------------


# GENERAL INFORMATION -------------------------------------------------------------------------------------------------
__author__ = 'Markus Schön'
__copyright__ = 'Copyright 2021 by Markus Schön'
__license__ = 'Apache License, Version 2.0'
# ---------------------------------------------------------------------------------------------------------------------


# PATHS ---------------------------------------------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]
FOLDER_TESTDATA = PROJECT_ROOT / 'data' / '_testdata'

#: Input feature classes
GDB_DATA = str(FOLDER_TESTDATA / 'data.gdb')

#: Reference results every test compares against
GDB_RESULTS = str(FOLDER_TESTDATA / 'results.gdb')
# ---------------------------------------------------------------------------------------------------------------------


# FIXTURES ------------------------------------------------------------------------------------------------------------
@pytest.fixture(scope='session')
def results_gdb(tmp_path_factory):
    """
    Create a throwaway file geodatabase for the test output.

    :rtype: str
    :return: Path of the file geodatabase.
    """

    arcpy = pytest.importorskip('arcpy')

    folder = str(tmp_path_factory.mktemp('arcgis_pro_geometry'))
    gdb_name = 'results_test.gdb'

    arcpy.CreateFileGDB_management(folder, gdb_name)

    return os.path.join(folder, gdb_name)
# ---------------------------------------------------------------------------------------------------------------------
