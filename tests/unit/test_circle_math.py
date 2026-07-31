# SCRIPT --------------------------------------------------------------------------------------------------------------
# Unit tests for the circle-center formula used in Geometry.circle_from_three_points().
#
# The formula is extracted here as a standalone function so it can be tested with plain
# (x, y) values — no arcpy objects, no ArcGIS Pro license required.
# Only numpy is needed (available via the standard anaconda/arcgispro environment).
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
import math

import numpy as np
import pytest

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
def _circle_center(p1, p2, p3):
    """
    Calculate the circle center for three (x, y) points.

    This reproduces the formula from Geometry.circle_from_three_points() so it can be
    tested without arcpy objects. Returns (x, y) of the center, or None if the points
    are collinear (no unique circle exists).

    :param tuple p1: First point as (x, y).
    :param tuple p2: Second point as (x, y).
    :param tuple p3: Third point as (x, y).
    :rtype: tuple or None
    :return: (x, y) of the circle center, or None for collinear points.
    """

    class _Pt:
        def __init__(self, x, y):
            self.X = x
            self.Y = y

    pts = [_Pt(*p) for p in (p1, p2, p3)]

    matrix = [[p.X, p.Y, 1] for p in pts]
    det_a = np.linalg.det(matrix)

    if abs(det_a) < 1e-10:
        return None

    matrix = [[(p.X ** 2 + p.Y ** 2) / 2, p.Y, 1] for p in pts]
    x = np.linalg.det(matrix) / det_a

    matrix = [[p.X, (p.X ** 2 + p.Y ** 2) / 2, 1] for p in pts]
    y = np.linalg.det(matrix) / det_a

    return x, y


def _radius(center, point):
    """Euclidean distance from center to point."""
    return math.sqrt((center[0] - point[0]) ** 2 + (center[1] - point[1]) ** 2)
# ---------------------------------------------------------------------------------------------------------------------


# TESTS ---------------------------------------------------------------------------------------------------------------
@pytest.mark.parametrize('p1, p2, p3, expected_center', [
    # Unit circle centered at origin
    ((1.0, 0.0), (-1.0, 0.0), (0.0, 1.0), (0.0, 0.0)),
    # Circle at (2, 3) with radius 1
    ((3.0, 3.0), (1.0, 3.0), (2.0, 4.0), (2.0, 3.0)),
    # Circle at (5, -2) with radius 3
    ((8.0, -2.0), (2.0, -2.0), (5.0, 1.0), (5.0, -2.0)),
    # Circle at (0, 0) with radius 5
    ((5.0, 0.0), (-5.0, 0.0), (0.0, 5.0), (0.0, 0.0)),
])
def test_circle_center(p1, p2, p3, expected_center):
    center = _circle_center(p1, p2, p3)

    assert center is not None
    assert center == pytest.approx(expected_center, abs=1e-10)


@pytest.mark.parametrize('p1, p2, p3, expected_center', [
    ((1.0, 0.0), (-1.0, 0.0), (0.0, 1.0), (0.0, 0.0)),
    ((3.0, 3.0), (1.0, 3.0), (2.0, 4.0), (2.0, 3.0)),
    ((8.0, -2.0), (2.0, -2.0), (5.0, 1.0), (5.0, -2.0)),
])
def test_circle_all_points_equidistant(p1, p2, p3, expected_center):
    """All three input points must lie on the calculated circle (equal distance to center)."""
    center = _circle_center(p1, p2, p3)

    r1 = _radius(center, p1)
    r2 = _radius(center, p2)
    r3 = _radius(center, p3)

    assert r1 == pytest.approx(r2, abs=1e-10)
    assert r2 == pytest.approx(r3, abs=1e-10)


@pytest.mark.parametrize('p1, p2, p3', [
    # Points on a horizontal line
    ((0.0, 0.0), (1.0, 0.0), (2.0, 0.0)),
    # Points on a vertical line
    ((0.0, 0.0), (0.0, 1.0), (0.0, 2.0)),
    # Points on a diagonal
    ((0.0, 0.0), (1.0, 1.0), (2.0, 2.0)),
])
def test_circle_collinear_returns_none(p1, p2, p3):
    """Collinear points have no unique circumscribed circle — must return None."""
    assert _circle_center(p1, p2, p3) is None
# ---------------------------------------------------------------------------------------------------------------------


# MAIN PROGRAM --------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    pass
# ---------------------------------------------------------------------------------------------------------------------
