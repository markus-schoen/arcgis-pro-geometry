# SCRIPT --------------------------------------------------------------------------------------------------------------
# Unit tests for Geometry.rotate_xy().
#
# rotate_xy() is a static method that uses only Python math — no arcpy calls at runtime.
# These tests run without an ArcGIS Pro license.
# conftest.py mocks arcpy so the Geometry module can be imported.
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
import pytest

from arcgis_pro_geometry import Geometry

# ---------------------------------------------------------------------------------------------------------------------


# MARKERS -------------------------------------------------------------------------------------------------------------
pytestmark = pytest.mark.unit
# ---------------------------------------------------------------------------------------------------------------------


# GENERAL INFORMATION -------------------------------------------------------------------------------------------------
__author__ = 'Markus Schön'
__copyright__ = 'Copyright 2021 by Markus Schön'
__license__ = 'Apache License, Version 2.0'
# ---------------------------------------------------------------------------------------------------------------------


# FUNCTIONS -----------------------------------------------------------------------------------------------------------
@pytest.mark.parametrize('x, y, rotation_angle, x_cnt, y_cnt, expected', [
    # No rotation — point stays in place
    (1.0, 0.0, 0, 0.0, 0.0, (1.0, 0.0)),
    # 90° clockwise: (1, 0) → (0, -1)
    (1.0, 0.0, 90, 0.0, 0.0, (0.0, -1.0)),
    # 180°: (1, 0) → (-1, 0)
    (1.0, 0.0, 180, 0.0, 0.0, (-1.0, 0.0)),
    # 270° clockwise = 90° counter-clockwise: (1, 0) → (0, 1)
    (1.0, 0.0, 270, 0.0, 0.0, (0.0, 1.0)),
    # 360° = full turn, back to start
    (1.0, 0.0, 360, 0.0, 0.0, (1.0, 0.0)),
    # Negative angle: -90° = 90° counter-clockwise: (1, 0) → (0, 1)
    (1.0, 0.0, -90, 0.0, 0.0, (0.0, 1.0)),
    # Origin always stays at origin
    (0.0, 0.0, 45, 0.0, 0.0, (0.0, 0.0)),
    # With center point: rotate (2, 0) by 90° around (1, 0) → (1, -1)
    (2.0, 0.0, 90, 1.0, 0.0, (1.0, -1.0)),
    # With center point: rotate (1, 1) by 180° around (0, 0) → (-1, -1)
    (1.0, 1.0, 180, 0.0, 0.0, (-1.0, -1.0)),
    # With center point: rotate (3, 2) by 90° around (2, 2) → (2, 1)
    (3.0, 2.0, 90, 2.0, 2.0, (2.0, 1.0)),
])
def test_rotate_xy(x, y, rotation_angle, x_cnt, y_cnt, expected):
    result = Geometry.rotate_xy(x, y, rotation_angle=rotation_angle, x_cnt=x_cnt, y_cnt=y_cnt)
    assert result == pytest.approx(expected, abs=1e-10)
# ---------------------------------------------------------------------------------------------------------------------


# MAIN PROGRAM --------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    pass
# ---------------------------------------------------------------------------------------------------------------------
