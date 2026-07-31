# SCRIPT --------------------------------------------------------------------------------------------------------------
# Unit tests for the ArcGIS Pro script tools of 'Toolbox.tbx'.
#
# Every tool script is executed end to end against a mocked arcpy that emulates just enough of the geoprocessing API
# (feature tables, data access cursors, geometry objects) to run without an ArcGIS Pro license.
#
# These tests do not verify geodata results - that is what the integration tests are for. They verify the wiring: that
# every script referenced by 'Toolbox.tbx' exists at the referenced path, imports, resolves its helpers and completes
# its Geometry call. A broken script path is exactly the kind of defect that stays invisible until someone opens the
# toolbox in ArcGIS Pro.
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
import json
import re
import runpy
import sys
from pathlib import Path
from unittest.mock import MagicMock

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


# PATHS ---------------------------------------------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]
PACKAGE = PROJECT_ROOT / 'src' / 'arcgis_pro_geometry'
TOOLBOX = PROJECT_ROOT / 'Toolbox.tbx'
# ---------------------------------------------------------------------------------------------------------------------


# VARIABLES -----------------------------------------------------------------------------------------------------------
#: script file name -> (shape type the mocked input reports, tool text parameters by index)
TOOL_SCRIPTS = {
    'boundary.py': ('Polygon', {}),
    'circle_from_three_points.py': ('Point', {}),
    'cut.py': ('Polyline', {}),
    'distance_line.py': ('Point', {}),
    'inner_circle.py': ('Polygon', {}),
    'numerate.py': ('Point', {1: 'top_left', 2: 'id'}),
    'points_along_feature.py': ('Polyline', {}),
    'polyline_to_polygon.py': ('Polyline', {}),
    'rotate.py': ('Polygon', {4: 'extent middle point'}),
    '_convex_hull.py': ('Polygon', {}),
    '_extent.py': ('Polygon', {}),
    '_hull_rectangle.py': ('Polygon', {}),
}

FEATURE_SET_JSON = json.dumps({
    'geometryType': 'esriGeometryPolyline',
    'spatialReference': {'wkid': 25832},
    'fields': [],
    'features': [{'geometry': {'paths': [[[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 0.0]]]}, 'attributes': {}}],
})

SHAPE_JSON = json.dumps({'rings': [[[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 0.0]]]})
# ---------------------------------------------------------------------------------------------------------------------


# CLASSES -------------------------------------------------------------------------------------------------------------
class FakePoint:
    """Stand-in for arcpy.Point."""

    def __init__(self, x, y):
        self.X = x
        self.Y = y


class FakeGeometry:
    """Stand-in for an arcpy geometry object - every method returns something the tool scripts can work with."""

    def __init__(self, shape_type, x=0.0, y=0.0):
        self.type = shape_type.lower()
        self.isMultipart = False
        self.pointCount = 2
        self.length = 10.0
        self.firstPoint = FakePoint(x, y)
        self.lastPoint = FakePoint(x + 10, y + 10)
        self.centroid = FakePoint(x + 5, y + 5)
        self.trueCentroid = FakePoint(x + 5, y + 5)
        self.hullRectangle = '0 0 10 0 10 10 0 10'
        self.spatialReference = MagicMock(name='SpatialReference')

    def boundary(self):
        return self

    def convexHull(self):
        return self

    def buffer(self, distance):
        return self

    def snapToLine(self, other):
        return self

    def positionAlongLine(self, position):
        return self

    def distanceTo(self, other):
        return 5.0

    def disjoint(self, other):
        return True

    def cut(self, other):
        return [self]

    @property
    def extent(self):
        extent = MagicMock(name='Extent')
        extent.XMin, extent.YMin, extent.width, extent.height = 0.0, 0.0, 10.0, 10.0
        extent.polygon = self
        return extent


class FakeTable:
    """A tiny in-memory feature table - rows are dicts of field name to value."""

    def __init__(self, row_count):
        self.field_types = {}
        self.rows = [
            {
                'OBJECTID': i + 1,
                'OID@': i + 1,
                'Shape_Length': 10.0 + i,   # distinct lengths, so the distance line ranking has something to sort
                'SHAPE@X': float(i),
                'SHAPE@Y': float(i * 2),
                'SHAPE@XY': (float(i), float(i * 2)),
                'SHAPE@JSON': SHAPE_JSON,
                'SHAPE@': FakeGeometry('polygon'),
            }
            for i in range(row_count)
        ]


class FakeCursor:
    """Stand-in for arcpy.da.SearchCursor / arcpy.da.UpdateCursor - iterator, context manager and writer in one."""

    def __init__(self, table, fields):
        self.table = table
        self.fields = [fields] if isinstance(fields, str) else list(fields)
        self._current = None

    def __iter__(self):
        for row in list(self.table.rows):
            self._current = row
            yield [row.get(field, 0.0) for field in self.fields]

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def updateRow(self, row):
        for field, value in zip(self.fields, row):
            # arcpy coerces a written value to the field type; only TEXT matters for these scripts
            if self.table.field_types.get(field) == 'TEXT' and value is not None:
                value = str(value)

            self._current[field] = value

    def deleteRow(self):
        self.table.rows.remove(self._current)
# ---------------------------------------------------------------------------------------------------------------------


# FUNCTIONS -----------------------------------------------------------------------------------------------------------
def build_arcpy_mock(shape_type, text_parameters):
    """
    Build a mocked arcpy module that answers the geoprocessing calls of the tool scripts.

    :param str shape_type: Shape type the mocked input feature class reports.
    :param dict text_parameters: Tool parameter values by index, for the parameters that need a specific value.

    :rtype: MagicMock
    :return: The mocked arcpy module.
    """

    arcpy = MagicMock(name='arcpy')

    geometries = [FakeGeometry(shape_type, i * 10.0, i * 10.0) for i in range(3)]
    tables = {}

    def table_for(name):
        return tables.setdefault(str(name), FakeTable(3))

    def copy_features(in_features, out_feature_class, *args, **kwargs):
        # arcpy.Geometry() as output means 'give me the geometries', a path means 'write a feature class'
        if not isinstance(out_feature_class, str):
            return geometries

        tables[out_feature_class] = FakeTable(len(in_features) if isinstance(in_features, list) else 3)

        return out_feature_class

    def multipart_to_singlepart(in_features, out_feature_class, *args, **kwargs):
        if not isinstance(out_feature_class, str):
            return geometries

        table_for(out_feature_class)

        return out_feature_class

    def add_field(in_table, field_name, field_type='TEXT', *args, **kwargs):
        table_for(in_table).field_types[field_name] = str(field_type).upper()

    arcpy.GetParameterAsText.side_effect = lambda index: text_parameters.get(index, 'dummy_value')
    arcpy.GetParameter.return_value = 1.0

    arcpy.CopyFeatures_management.side_effect = copy_features
    arcpy.MultipartToSinglepart_management.side_effect = multipart_to_singlepart
    arcpy.AddField_management.side_effect = add_field
    arcpy.Buffer_analysis.side_effect = lambda in_features, out_features, *a, **k: table_for(out_features)

    arcpy.da.SearchCursor.side_effect = lambda table, fields, *a, **k: FakeCursor(table_for(table), fields)
    arcpy.da.UpdateCursor.side_effect = lambda table, fields, *a, **k: FakeCursor(table_for(table), fields)

    arcpy.Describe.return_value.shapeType = shape_type
    arcpy.Describe.return_value.catalogPath = 'catalog_path'
    arcpy.Describe.return_value.spatialReference.name = 'ETRS_1989_UTM_Zone_32N'
    arcpy.Describe.return_value.spatialReference.factoryCode = 25832
    arcpy.Describe.return_value.extent.XMin = 0.0
    arcpy.Describe.return_value.extent.YMin = 0.0
    arcpy.Describe.return_value.extent.width = 10.0
    arcpy.Describe.return_value.extent.height = 10.0

    arcpy.GetCount_management.return_value.getOutput.return_value = '3'

    field = MagicMock(name='Field')
    field.name = 'id'
    arcpy.ListFields.return_value = [field]

    arcpy.FeatureSet.return_value.JSON = FEATURE_SET_JSON
    arcpy.Exists.return_value = False

    arcpy.mp.ArcGISProject.return_value.activeMap.listLayers.return_value = []

    return arcpy


def toolbox_script_references():
    """
    Read the script paths 'Toolbox.tbx' points its script tools to.

    The paths are stored as UTF-16 strings relative to the toolbox file.

    :rtype: set
    :return: Set of script paths, relative to the repository root and with forward slashes.
    """

    data = TOOLBOX.read_bytes()
    matches = re.finditer(rb'(?:[\x20-\x7e]\x00){6,}', data)

    return {
        match.group().decode('utf-16-le').replace('\\', '/')
        for match in matches
        if match.group().decode('utf-16-le').lower().endswith('.py')
    }
# ---------------------------------------------------------------------------------------------------------------------


# FIXTURES ------------------------------------------------------------------------------------------------------------
@pytest.fixture
def isolated_imports():
    """
    Run a tool script with a fresh import state and restore sys.modules afterwards.

    ArcGIS Pro starts every tool run with its own import state, and the scripts import the package at module level. The
    fixture reproduces that and keeps the mocked modules out of the other tests.
    """

    prefixes = ('arcpy', 'arcgis_pro_geometry')
    saved = {name: module for name, module in sys.modules.items() if name.split('.')[0] in prefixes}

    def run(script, arcpy_mock):
        for name in list(sys.modules):
            if name.split('.')[0] in prefixes:
                del sys.modules[name]

        sys.modules['arcpy'] = arcpy_mock
        runpy.run_path(str(PACKAGE / script), run_name='__main__')

    yield run

    for name in list(sys.modules):
        if name.split('.')[0] in prefixes:
            del sys.modules[name]

    sys.modules.update(saved)
# ---------------------------------------------------------------------------------------------------------------------


# TESTS ---------------------------------------------------------------------------------------------------------------
@pytest.mark.parametrize('script', sorted(TOOL_SCRIPTS))
def test_tool_script_runs(script, isolated_imports):
    """Every tool script has to run from top to bottom against the mocked arcpy."""

    shape_type, text_parameters = TOOL_SCRIPTS[script]

    isolated_imports(script, build_arcpy_mock(shape_type, text_parameters))


@pytest.mark.parametrize('script', sorted(TOOL_SCRIPTS))
def test_tool_script_exists(script):
    assert (PACKAGE / script).is_file()


@pytest.mark.skipif(not TOOLBOX.is_file(), reason="'Toolbox.tbx' is not part of the checkout")
def test_toolbox_script_paths_exist():
    """
    Every script path stored in 'Toolbox.tbx' has to resolve to a file.

    ArcGIS Pro resolves these paths relative to the toolbox, so moving a script silently breaks its tool. This test is
    the guard against repeating that.
    """

    missing = [reference for reference in toolbox_script_references() if not (PROJECT_ROOT / reference).is_file()]

    assert not missing, f'Toolbox.tbx references scripts that do not exist: {sorted(missing)}'


@pytest.mark.skipif(not TOOLBOX.is_file(), reason="'Toolbox.tbx' is not part of the checkout")
def test_every_toolbox_script_is_covered():
    """Every script the toolbox references has to be part of the run test above."""

    referenced = {Path(reference).name for reference in toolbox_script_references()}

    assert referenced == set(TOOL_SCRIPTS)
# ---------------------------------------------------------------------------------------------------------------------
