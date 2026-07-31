# Contributing

Thanks for taking a look at this project. This page describes how to set it up, how the tests are organised and what to
keep in mind when changing a tool.

## Setup

The library targets the Python environment that ships with ArcGIS Pro. For the unit tests and the linter, any Python
3.9+ works — `arcpy` is mocked there.

```bash
git clone https://github.com/markus-schoen/arcgis-pro-geometry.git
cd arcgis-pro-geometry
pip install -e ".[dev]"
```

To use the package inside ArcGIS Pro, install it into a *clone* of the ArcGIS Pro environment — the default
`arcgispro-py3` environment is read-only:

```
conda activate arcgispro-py3-clone
pip install --no-deps -e .
```

## Tests

| Command | What it runs | Needs ArcGIS Pro |
| --- | --- | --- |
| `pytest tests/unit` | Pure Python logic and all twelve tool scripts against a mocked arcpy | no |
| `pytest tests/integration` | The real geometry methods, compared against `data/_testdata/results.gdb` | yes |
| `pytest` | Both — the integration tests skip themselves when `arcpy` is missing | no |
| `ruff check .` | Code style | no |

The integration tests write their output into a throwaway file geodatabase created by the `results_gdb` fixture in
`tests/integration/conftest.py`. They never write into the repository.

### Changing what a tool produces

The integration tests compare against the reference results in `data/_testdata/results.gdb`. When a fix deliberately
changes the output of a method, regenerate the affected dataset with ArcGIS Pro and commit it together with the change,
so the reference stays the source of truth.

## Code layout

- `src/arcgis_pro_geometry/geometry.py` — the `Geometry` class. All geometry logic belongs here.
- `src/arcgis_pro_geometry/_toolbox.py` — helpers shared by the script tools (map handling, output paths, dissolve).
- `src/arcgis_pro_geometry/<tool>.py` — one entry script per toolbox tool. It reads the tool parameters, calls one
  `Geometry` method and adds the result to the map. Keep the logic out of these files.

**The script paths are fixed by the toolbox.** `Toolbox.tbx` stores them relative to itself, so renaming or moving a
tool script breaks its tool in ArcGIS Pro without any warning. `tests/unit/test_toolbox_scripts.py` guards against
this — if you have to move a script, repoint the tool in ArcGIS Pro and commit the updated `Toolbox.tbx`.

Scripts with a leading underscore (`_convex_hull.py`, `_extent.py`, `_hull_rectangle.py`) are deprecated: ArcGIS Pro 3.x
ships native tools for them. They are kept because the toolbox still references them.

## Style

- `ruff check .` has to pass. The configuration lives in `pyproject.toml`, line length is 120.
- Keep the section banners — they are the house style of this project.
- Document every public method with a docstring in the existing `:param:` / `:rtype:` / `:return:` format.
- The `Geometry` class must not touch `arcpy.env` or `arcpy.mp`. That belongs in the tool scripts, so the class stays
  usable from any script or notebook.
- Raise `GeometryError` for invalid input, after reporting the message with `arcpy.AddError()`.

## Commits and branches

- `main` is the release branch, `develop` is where work lands first.
- Prefix commit subjects with their kind, as in the existing history: `newfeature:`, `bugfix:`, `refactoring:`.
- Add an entry to `CHANGELOG.md` for anything user visible.
- Releases are tagged `vMAJOR.MINOR.PATCH`; keep the version in `pyproject.toml` and `__init__.py` in sync.
