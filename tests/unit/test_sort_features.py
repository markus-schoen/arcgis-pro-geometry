# SCRIPT --------------------------------------------------------------------------------------------------------------
# Unit tests for Geometry.sort_features().
#
# sort_features() holds the pure sorting logic of Geometry.numerate(). It uses plain Python only, so these tests run
# without an ArcGIS Pro license. conftest.py mocks arcpy so the geometry module can be imported.
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

from arcgis_pro_geometry import Geometry, GeometryError

# ---------------------------------------------------------------------------------------------------------------------


# MARKERS -------------------------------------------------------------------------------------------------------------
pytestmark = pytest.mark.unit
# ---------------------------------------------------------------------------------------------------------------------


# GENERAL INFORMATION -------------------------------------------------------------------------------------------------
__author__ = 'Markus Schön'
__copyright__ = 'Copyright 2021 by Markus Schön'
__license__ = 'Apache License, Version 2.0'
# ---------------------------------------------------------------------------------------------------------------------


# VARIABLES -----------------------------------------------------------------------------------------------------------
# Four points on a 2x2 grid, given as (x, y, object id):
#
#   y=1   1 --- 2        (0, 1) has oid 1, (1, 1) has oid 2
#   y=0   3 --- 4        (0, 0) has oid 3, (1, 0) has oid 4
#         x=0   x=1
GRID = [
    (0.0, 1.0, 1),
    (1.0, 1.0, 2),
    (0.0, 0.0, 3),
    (1.0, 0.0, 4),
]
# ---------------------------------------------------------------------------------------------------------------------


# FUNCTIONS -----------------------------------------------------------------------------------------------------------
def oids(rows):
    """Reduce sorted rows to their object ids."""
    return [row[2] for row in rows]


@pytest.mark.parametrize('sort_by, expected_oids', [
    # Top to bottom, ties left to right
    ('top_left', [1, 2, 3, 4]),
    # Top to bottom, ties right to left
    ('top_right', [2, 1, 4, 3]),
    # Bottom to top, ties left to right
    ('bottom_left', [3, 4, 1, 2]),
    # Bottom to top, ties right to left
    ('bottom_right', [4, 3, 2, 1]),
    # Right to left, ties top to bottom
    ('right_top', [2, 4, 1, 3]),
    # Right to left, ties bottom to top
    ('right_bottom', [4, 2, 3, 1]),
    # Left to right, ties top to bottom
    ('left_top', [1, 3, 2, 4]),
    # Left to right, ties bottom to top
    ('left_bottom', [3, 1, 4, 2]),
])
def test_sort_features(sort_by, expected_oids):
    assert oids(Geometry.sort_features(GRID, sort_by)) == expected_oids


@pytest.mark.parametrize('sort_by', ['top_left', 'top_right', 'bottom_left', 'bottom_right'])
def test_sort_features_breaks_y_ties_by_x(sort_by):
    """
    Regression test: the secondary sort axis of the y based options has to be x.

    The former implementation used 'row[xy_index + 1 % 2]'. Because '%' binds tighter than '+', that expression always
    evaluated to 'row[xy_index + 1]' - which is the object id instead of the x coordinate for every y based option.
    Points sharing a y value were therefore ordered by object id.
    """

    # Same y for every point, so only the secondary axis decides. The object id order is deliberately the reverse of
    # the x order, so a fallback to the object id is visible.
    rows = [(2.0, 5.0, 1), (0.0, 5.0, 2), (1.0, 5.0, 3)]

    sorted_x = [row[0] for row in Geometry.sort_features(rows, sort_by)]

    if sort_by.endswith('_left'):
        assert sorted_x == [0.0, 1.0, 2.0]
    else:
        assert sorted_x == [2.0, 1.0, 0.0]


@pytest.mark.parametrize('sort_by', ['right_top', 'right_bottom', 'left_top', 'left_bottom'])
def test_sort_features_breaks_x_ties_by_y(sort_by):
    """The secondary sort axis of the x based options has to be y."""

    rows = [(5.0, 2.0, 1), (5.0, 0.0, 2), (5.0, 1.0, 3)]

    sorted_y = [row[1] for row in Geometry.sort_features(rows, sort_by)]

    if sort_by.endswith('_top'):
        assert sorted_y == [2.0, 1.0, 0.0]
    else:
        assert sorted_y == [0.0, 1.0, 2.0]


def test_sort_features_keeps_input_untouched():
    """The input rows must not be reordered in place."""

    rows = list(GRID)
    Geometry.sort_features(rows, 'bottom_right')

    assert rows == GRID


def test_sort_features_rejects_unknown_option():
    with pytest.raises(GeometryError):
        Geometry.sort_features(GRID, 'diagonal')


def test_sort_options_are_complete():
    """Every option named in the numerate() docstring has to exist."""

    expected = {
        'top_left', 'top_right', 'bottom_left', 'bottom_right',
        'right_top', 'right_bottom', 'left_top', 'left_bottom',
    }

    assert set(Geometry.SORT_OPTIONS) == expected
# ---------------------------------------------------------------------------------------------------------------------
