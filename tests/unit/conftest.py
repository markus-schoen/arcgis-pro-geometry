# SCRIPT --------------------------------------------------------------------------------------------------------------
# pytest configuration for unit tests.
#
# Mocks arcpy so that unit tests run without an ArcGIS Pro license.
# Unit tests only cover pure Python/math logic that does not call arcpy at runtime.
# ---------------------------------------------------------------------------------------------------------------------

import sys
from unittest.mock import MagicMock

# Mock arcpy before any test module is imported.
# If arcpy is already in sys.modules (e.g., when running with a real ArcGIS Pro installation),
# the real module is used instead of the mock.
if 'arcpy' not in sys.modules:
    sys.modules['arcpy'] = MagicMock()
