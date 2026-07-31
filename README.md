# arcgis-pro-geometry

[![CI](https://github.com/markus-schoen/arcgis-pro-geometry/actions/workflows/ci.yml/badge.svg)](https://github.com/markus-schoen/arcgis-pro-geometry/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![ArcGIS Pro](https://img.shields.io/badge/ArcGIS%20Pro-3.5%20%7C%203.6-brightgreen.svg)](https://www.esri.com/en-us/arcgis/products/arcgis-pro/overview)

A collection of geometry tools for ArcGIS Pro, written in Python and mainly based on `arcpy`. Every tool is documented
and can be used directly through the toolbox `Toolbox.tbx` — or from your own scripts through the `Geometry` class.

## Tools

The toolbox `Toolbox.tbx` contains the following tools:

| Tool | Description |
| --- | --- |
| **Boundary** | Create a boundary feature class for polyline or polygon features. |
| **Circle From Three Points** | Create a circle for every three points of a point feature class. |
| **Convex Hull** | Create convex hulls for any feature class. *(ArcGIS Pro 3.x has a native tool for this.)* |
| **Cut** | Cut a polyline or polygon feature class by a cutting polyline. |
| **Distance Lines** | Create distance lines from point features to any feature class, ranked by length. |
| **Extent** | Create an extent feature class for any feature class. *(ArcGIS Pro 3.x has a native tool for this.)* |
| **Hull Rectangle** | Create the minimal rectangle that encloses the input features. *(ArcGIS Pro 3.x has a native tool for this.)* |
| **Inner Circle** | Create maximum inner circles and their centroids for any polygon feature class. |
| **Numerate** | Sort features by their coordinates and write the rank into a field. |
| **Points Along Feature** | Create points along a polyline or polygon at a chosen distance. |
| **Polyline To Polygon** | Create a polygon feature class from a polyline feature class, curves included. |
| **Rotate** | Rotate a feature class by five different rotation methods. |

All tools accept feature layers, so a selection in the map is respected.

## Requirements

- Windows with **ArcGIS Pro 3.5 or 3.6**
- `arcpy` and `numpy` — both ship with the ArcGIS Pro Python environment, no extra installation needed

## Getting started

### As an ArcGIS Pro toolbox

1. Download or clone the repository.
2. In ArcGIS Pro, add `Toolbox.tbx` to your project (*Catalog → Toolboxes → Add Toolbox*).
3. Run any tool. The metadata behind every ℹ️ button explains the parameters.

> **Keep the folder structure intact.** The toolbox stores the path of every tool script relative to `Toolbox.tbx`
> (`src/arcgis_pro_geometry/<tool>.py`). Moving the scripts breaks the tools.

### As a Python library

```python
from arcgis_pro_geometry import Geometry

with Geometry(r'C:\data\project.gdb\parcels') as geom:
    geom.boundary(r'C:\data\project.gdb\parcels_boundary')
    geom.inner_circle(r'C:\data\project.gdb\parcels_circle')
```

Point Python at the `src` folder — either by installing the package into your cloned ArcGIS Pro environment …

```
conda activate arcgispro-py3-clone
pip install --no-deps -e .
```

… or by adding `src` to `sys.path` before importing, as the tool scripts do.

## Project structure

```
arcgis-pro-geometry/
├── .github/workflows/          # CI: linting and unit tests
├── data/
│   ├── _testdata/              # Test geodatabases: input (data.gdb) and reference results (results.gdb)
│   └── layer/                  # Layer files (.lyrx) used by the Distance Lines tool
├── src/
│   └── arcgis_pro_geometry/
│       ├── geometry.py         # The Geometry class — all the geometry logic lives here
│       ├── _toolbox.py         # Shared helpers for the script tools
│       └── <tool>.py           # One entry script per toolbox tool
├── tests/
│   ├── unit/                   # Run without an ArcGIS Pro license (arcpy is mocked)
│   └── integration/            # Require ArcGIS Pro, compare against data/_testdata/results.gdb
├── Toolbox.tbx                 # The ArcGIS Pro toolbox
├── CHANGELOG.md
└── pyproject.toml
```

## Development

```bash
pip install -e ".[dev]"

pytest tests/unit          # no ArcGIS Pro license needed
pytest tests/integration   # needs ArcGIS Pro; skipped automatically without arcpy
ruff check .
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full workflow.

## Documentation

- **In ArcGIS Pro** — every tool carries its own metadata, readable through the info buttons of the tool dialog.
- **In code** — every method of the `Geometry` class is documented with a docstring.

## Credits

- FelixIP and BERA on [gis.stackexchange.com](https://gis.stackexchange.com/questions/286439/need-tool-for-arcmap-to-draw-circle-touching-three-points)
  for the circle-from-three-points approach.
- [Curtis Price](https://github.com/usgs/arcgis-sample/blob/master/scripts/RotateFeatureClass.py) for the rotation
  approach.

## License

Copyright 2021 by Markus Schön

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the [License](LICENSE) for the specific language governing permissions and
limitations under the License.
