# arcgis-pro-geometry
This is a collection of geometry tools for ArcGIS Pro. The tools are written with Python, mainly based on arcpy. Each tool has been documented and can be directly used through the toolbox 'Toolbox.tbx'.


Within the toolbox 'Toolbox.tbx' you find several tools to edit and calculate geometries:
- Boundary: Create a boundary feature class for polyline or polygon feature (layer/classes).
- Circle from three points: Create circles for every three points from a point feature (layer/class).
- Convex hull: Create convex hulls for any feature (layer/class).
- Cut: Create a cut feature class for polygon feature (layer/classes).
- Distance lines: Create distance lines from point features to any feature (layer/class).
- Inner circle: Create inner circle for any polygon feature (layer/class).
- Numerate: Sort any feature and create a field for the sort range.


**Why the project is useful?**<br>
These tools expands the possibilities in dealing with geometries.


**How can users get started with the project?**<br>
After downloading the entire repo, the toolbox 'Toolbox.tbx' can be directly used within ArcGIS Pro.
You can use the class 'Geometry' from the script '.script\Geometry.py' in other scripts as well.


**Where can users get help for their project?**<br>
- ArcGIS Pro - Every tool within the toolbox has edited metadata. You can read the metadata through the info buttons.
- Class Geometry - Every script is documented.


**Requirements?**<br>
- ArcGIS Pro 2.8.1+
- Frameworks:
    - arcpy
    - numpy
    - os
    - sys


**Licensing?**<br>
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
