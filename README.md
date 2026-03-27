# arcgis-pro-geometry
This is a collection of geometry tools for ArcGIS Pro. The tools are written with Python, mainly based on arcpy. Each tool has been documented and can be directly used through the toolbox 'Toolbox.tbx'.


Within the toolbox 'Toolbox.tbx' you find several tools to edit and calculate geometries:
- Boundary: Create a boundary feature class for polyline or polygon feature (layer/classes).
- Circle from three points: Create circles for every three points from a point feature (layer/class).
- Convex hull: Create convex hulls for any feature (layer/class).
- Cut: Create a cut feature class for polygon feature (layer/classes).
- Distance lines: Create distance lines from point features to any feature (layer/class).
- Extent: Create an extent feature class for any feature (layer/class).
- Hull Rectangle: Create minimal rectangles that enclose the input feature (layer/class).
- Inner circle: Create maximum inner circles and associated centroids for any polygon feature (layer/class).
- Numerate: Sort any feature and create a field for the sort range.
- Points Along Feature: Create points along a polyline or polygon feature (layer/class) for a selected distance.
- Polyline To Polygon: Create a polygon feature class from a polyline feature (layer/class).
- Rotate: Rotate a feature class by different rotation methods (layer/class).


**Why the project is useful?**<br>
These tools expand the possibilities in dealing with geometries in ArcGIS Pro.


**How can users get started with the project?**<br>
After downloading the entire repo, the toolbox 'Toolbox.tbx' can be directly used within ArcGIS Pro.
You can also use the `Geometry` class from `src/arcgis_pro_geometry/Geometry.py` in your own scripts:

```python
from arcgis_pro_geometry.Geometry import Geometry

with Geometry(feature_layer) as geom:
    geom.boundary(output_path)
```


**Where can users get help for their project?**<br>
- ArcGIS Pro — Every tool within the toolbox has edited metadata. You can read the metadata through the info buttons.
- Class Geometry — Every method is documented with docstrings.


**Project structure**<br>
```
arcgis-pro-geometry/
├── data/
│   ├── _testdata/      # Test geodatabases (input, expected results, test results)
│   └── layer/          # Layer files (.lyrx)
├── src/
│   └── arcgis_pro_geometry/
│       ├── Geometry.py         # Main Geometry class (library)
│       ├── boundary.py         # ArcGIS toolbox script: Boundary
│       ├── circle_from_three_points.py
│       ├── cut.py
│       ├── distance_line.py
│       ├── inner_circle.py
│       ├── numerate.py
│       ├── points_along_feature.py
│       ├── polyline_to_polygon.py
│       └── rotate.py
├── tests/
│   └── unit/           # Unit tests (require ArcGIS Pro)
├── Toolbox.tbx         # ArcGIS Pro toolbox
└── pyproject.toml
```


**Requirements**<br>
- ArcGIS Pro 3.5 or 3.6
- Provided by ArcGIS Pro installation:
    - arcpy
    - numpy


**Licensing**<br>
Copyright 2021 by Markus Schön

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
