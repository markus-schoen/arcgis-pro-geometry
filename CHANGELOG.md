# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0]

Restructuring release. The toolbox tools behave the same, but the repository layout, the import path and several
long-standing defects changed.

### Fixed

- **All twelve toolbox tools were broken.** `Toolbox.tbx` resolves its tool scripts relative to itself
  (`src/arcgis_pro_geometry/<tool>.py`), but the scripts had been moved to `scripts/`. They are back at the path the
  toolbox expects, and a unit test now verifies every path stored in the toolbox.
- **Numerate sorted by object id instead of by coordinate.** `row[xy_index + 1 % 2]` always evaluated to
  `row[xy_index + 1]`, because `%` binds tighter than `+`. For the four `top_*` / `bottom_*` options that is the object
  id column, so features sharing a y value were ordered by object id instead of by x.
- **Rotate ignored two of its five rotation methods.** `extent middle point` and `point feature` are offered in the tool
  dialog but were never evaluated — the tool silently fell back to the *Rotation - x* / *Rotation - y* parameters. Both
  are implemented now, including a clear error when the required optional layer is missing.
- **Points Along Feature produced a duplicated end point.** The loop ran one step past the end of the line, and
  `positionAlongLine()` clamps to the end point. The end point is now only part of the result when *Include endpoint* is
  set.
- **Inner Circle never released its temporary feature class** — it called `arcpy.DeleteField_management()` with a single
  argument instead of `arcpy.Delete_management()`.
- **Inner Circle checked the wrong geometry when converging.** The stop condition read `shape.pointCount` from the
  enclosing loop variable instead of the polygon currently being shrunk.
- **Circle From Three Points picked the wrong radius after a collinear triple.** The group counter only advanced on
  success, so every following circle took its radius from a shifted point.
- **Distance Lines wrote its output without a coordinate system**, and its "coordinate system is defined" check could
  never trigger, because arcpy returns a spatial reference named `Unknown` rather than `None`.
- `pyproject.toml` declared the non-existent build backend `setuptools.backends.legacy:build`.

### Changed

- **Layout.** The `Geometry` class moved to `src/arcgis_pro_geometry/geometry.py`, the tool scripts sit next to it, and
  the package exposes a public API: `from arcgis_pro_geometry import Geometry`.
- **Errors are exceptions.** Invalid input raises `GeometryError` instead of calling `exit()`. The message still goes to
  `arcpy.AddError()`, so it shows up in the ArcGIS Pro message pane as before.
- **`Geometry` no longer changes global arcpy state on import.** `arcpy.env.overwriteOutput` is set by the toolbox
  scripts, which is where it belongs — the class stays safe to use from any script or notebook.
- **`shape_type` and `spatial_reference` read from the feature description** instead of loading every geometry of the
  feature class first. This is noticeably faster on large inputs and works for empty feature classes.
- **`__exit__` releases the cached geometries** instead of deleting the instance attributes, so the object stays usable.
- The repeated map handling of the twelve tool scripts moved into a shared `_toolbox` module.
- The sorting logic of `numerate()` and the ranking logic of `distance_lines()` are exposed as
  `Geometry.sort_features()` and `Geometry.rank_by_length()` — pure functions that are unit tested without arcpy.
- Integration tests write to a throwaway file geodatabase instead of a `results_test.gdb` inside the repository.

### Added

- Unit tests that run without an ArcGIS Pro license: every toolbox script is executed end to end against a mocked
  arcpy, plus coverage for the sorting, ranking, rotation and circle math.
- GitHub Actions CI: ruff linting and the unit tests on Python 3.9 and 3.11.
- Ruff configuration, `CHANGELOG.md` and `CONTRIBUTING.md`.

### Removed

- `results_test.gdb` (test output), the committed `.idea/` project files and personal scratch files
  (`ipython.bat`, `ipyton_points_along_feature.ipy`, `run_pytest.bat`).
- `pytest.ini` — the configuration lives in `pyproject.toml` now.

### Migration

- `from arcgis_pro_geometry.Geometry import Geometry` → `from arcgis_pro_geometry import Geometry`
- Code that relied on a `SystemExit` from invalid input has to catch `GeometryError` instead.
- Scripts that relied on `import`ing `Geometry` to set `arcpy.env.overwriteOutput` have to set it themselves.
- The reference results for **Points Along Feature** in `data/_testdata/results.gdb` still contain the duplicated end
  point. Regenerate that dataset with ArcGIS Pro and drop the `xfail` marker in
  `tests/integration/test_points_along_feature.py`.

## [1.5.0]

### Added

- **Points Along Feature** tool: creates points along a polyline or polygon feature at a chosen distance. One multipoint
  is created per feature.

## [1.4.0]

### Added

- **Extent** tool: creates the extents for the input feature class.

## [1.3.0]

### Changed

- `boundary()`, `convex_hull()` and `hull_rectangle()` copy the fields of the original input feature.

## [1.2.2]

### Fixed

- `inner_circle()` now creates circles for circle polygons as well.

## [1.2.1]

### Changed

- Removed the example commands from `Geometry.py`.

## [1.2.0]

### Added

- **Hull Rectangle** tool: creates the minimal bounding rectangle for the input feature class.

## [1.1.0]

### Added

- **Polyline To Polygon** tool: creates a polygon feature class from a polyline feature class.

## [1.0.2]

### Fixed

- Check whether the project has an active map before adding data to it.
- `inner_circle()` reports through `arcpy.AddMessage()` instead of `arcpy.AddError()`.
- Output feature classes get a spatial reference.

## [1.0.1]

### Fixed

- Guard the recursive part of `inner_circle()` with try/except and report the exception message.
- Changed the default `accuracy` from 0.1 to 0.01, in the method and in the toolbox.

## [1.0.0]

### Added

- First release: **Boundary**, **Circle From Three Points**, **Convex Hull**, **Cut**, **Distance Lines**,
  **Inner Circle** and **Numerate**, with complete toolbox metadata.

[2.0.0]: https://github.com/markus-schoen/arcgis-pro-geometry/compare/v1.5.0...v2.0.0
[1.5.0]: https://github.com/markus-schoen/arcgis-pro-geometry/compare/v1.4.0...v1.5.0
[1.4.0]: https://github.com/markus-schoen/arcgis-pro-geometry/compare/v1.3.0...v1.4.0
[1.3.0]: https://github.com/markus-schoen/arcgis-pro-geometry/compare/v1.2.2...v1.3.0
[1.2.2]: https://github.com/markus-schoen/arcgis-pro-geometry/compare/v1.2.1...v1.2.2
[1.2.1]: https://github.com/markus-schoen/arcgis-pro-geometry/compare/v1.2.0...v1.2.1
[1.2.0]: https://github.com/markus-schoen/arcgis-pro-geometry/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/markus-schoen/arcgis-pro-geometry/compare/v1.0.2...v1.1.0
[1.0.2]: https://github.com/markus-schoen/arcgis-pro-geometry/compare/v1.0.1...v1.0.2
[1.0.1]: https://github.com/markus-schoen/arcgis-pro-geometry/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/markus-schoen/arcgis-pro-geometry/releases/tag/v1.0.0
