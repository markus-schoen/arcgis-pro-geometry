# SCRIPT --------------------------------------------------------------------------------------------------------------
# Unit tests for Geometry.rank_by_length().
#
# rank_by_length() holds the pure ranking logic of Geometry.distance_lines(): it maps every object id to its distance
# line combinations, shortest line first. It uses plain Python only, so these tests run without an ArcGIS Pro license.
# conftest.py mocks arcpy so the geometry module can be imported.
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
def build(pairs):
    """
    Build the two lookup dictionaries distance_lines() hands to rank_by_length().

    :param list pairs: List of (oid1, oid2, length).

    :rtype: tuple
    :return: (combination_lengths, combination_oids)
    """

    lengths = {}
    oids = {}

    for oid1, oid2, length in pairs:
        combination = f'({oid1}, {oid2})'
        lengths[combination] = length
        oids[combination] = (oid1, oid2)

    return lengths, oids


def test_ranks_by_ascending_length():
    """Every object id gets its combinations ordered from the shortest to the longest distance line."""

    lengths, oids = build([
        (1, 10, 30.0),
        (1, 11, 10.0),
        (1, 12, 20.0),
    ])

    ranking = Geometry.rank_by_length(lengths, oids, 0)

    assert ranking == {'1': ['(1, 11)', '(1, 12)', '(1, 10)']}


def test_groups_by_first_and_second_object_id():
    """oid_position selects which side of the combination is grouped."""

    lengths, oids = build([
        (1, 10, 5.0),
        (1, 11, 7.0),
        (2, 10, 3.0),
        (2, 11, 9.0),
    ])

    by_first = Geometry.rank_by_length(lengths, oids, 0)
    by_second = Geometry.rank_by_length(lengths, oids, 1)

    assert by_first == {
        '1': ['(1, 10)', '(1, 11)'],
        '2': ['(2, 10)', '(2, 11)'],
    }
    assert by_second == {
        '10': ['(2, 10)', '(1, 10)'],
        '11': ['(1, 11)', '(2, 11)'],
    }


def test_equal_lengths_keep_insertion_order():
    """
    Distance lines of an equal length keep the order in which they were written to the output feature class.

    distance_lines() looks the rank up with list.index(), so a stable order is what makes the written rank reproducible.
    """

    lengths, oids = build([
        (1, 30, 5.0),
        (1, 10, 5.0),
        (1, 20, 5.0),
    ])

    ranking = Geometry.rank_by_length(lengths, oids, 0)

    assert ranking['1'] == ['(1, 30)', '(1, 10)', '(1, 20)']


def test_rank_index_matches_the_written_attribute():
    """The rank written to the output feature class is the position inside the ranking list."""

    lengths, oids = build([
        (1, 10, 30.0),
        (1, 11, 10.0),
        (1, 12, 20.0),
    ])

    ranking = Geometry.rank_by_length(lengths, oids, 0)

    assert ranking['1'].index('(1, 11)') == 0  # shortest distance line
    assert ranking['1'].index('(1, 12)') == 1
    assert ranking['1'].index('(1, 10)') == 2  # longest distance line


def test_object_ids_are_keyed_as_strings():
    """
    The ranking is looked up with the value of the OID1/OID2 text fields, so the keys have to be strings.

    Integer keys would raise a KeyError as soon as distance_lines() reads the rank back from the feature class.
    """

    lengths, oids = build([(7, 8, 1.0)])

    ranking = Geometry.rank_by_length(lengths, oids, 0)

    assert list(ranking) == ['7']


def test_empty_input():
    assert Geometry.rank_by_length({}, {}, 0) == {}
# ---------------------------------------------------------------------------------------------------------------------
