# SCRIPT --------------------------------------------------------------------------------------------------------------
# This script creates a feature class with distance lines between two feature classes, for a currently opened ArcGIS Pro
# project. Moreover, the script sets the *.lyrx-file and and the definition query.
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


# CREDITS -------------------------------------------------------------------------------------------------------------
# Thanks to all developers who created the used modules.
# ---------------------------------------------------------------------------------------------------------------------


# ---------------------------------------------------------------------------------------------------------------------
# TODO /
# ---------------------------------------------------------------------------------------------------------------------


# MODULES -------------------------------------------------------------------------------------------------------------
import arcpy
from Geometry import Geometry
import os
import sys
# ---------------------------------------------------------------------------------------------------------------------


# GENERAL INFORMATION -------------------------------------------------------------------------------------------------
__author__ = 'Markus Schön'
__copyright__ = 'Copyright 2021 by Markus Schön'
__license__ = 'Apache License, Version 2.0'
# ---------------------------------------------------------------------------------------------------------------------


# FUNCTIONS -----------------------------------------------------------------------------------------------------------
def make_int(x):
    return int(x) if x else None
# ---------------------------------------------------------------------------------------------------------------------


# CLASSES -------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------


# VARIABLES -----------------------------------------------------------------------------------------------------------
point_fc = arcpy.GetParameterAsText(0)
distance_fc = arcpy.GetParameterAsText(1)
out_fc_gdb = arcpy.GetParameterAsText(2)
out_fc_name = arcpy.GetParameterAsText(3)
overwrite = arcpy.GetParameter(4)
content_number_shortest_distance_from_point_fc = make_int(arcpy.GetParameter(5))
content_number_longest_distance_from_point_fc = make_int(arcpy.GetParameter(6))
content_number_shortest_distance_from_distance_fc = make_int(arcpy.GetParameter(7))
content_number_longest_distance_from_distance_fc = make_int(arcpy.GetParameter(8))
content_lyr_display_name = arcpy.GetParameterAsText(9)
content_lyr_unit = arcpy.GetParameter(10)


# In fc - ids
point_fc_ids = None
distance_fc_ids = None

# In fc - object id columns
point_fc_objectid = "OBJECTID"
distance_fc_objectid = "OBJECTID"


# out fc - path
out_fc = os.path.join(out_fc_gdb, out_fc_name)

# Out fc - column names for the ids from the input feature classes
out_fc_col_oid1 = 'OID1'  # Column name for the ids from the first fc
out_fc_col_oid2 = 'OID2'  # Column name for the ids from the second fc
out_fc_col_comb_id = 'OID_Comb'  # Column name for the combined first and second ids

# Out fc - column names for the index ranking of the shortest distance distance lines
out_fc_col_oid1_index = 'OID1_index'  # Index ranking for the shortest distance lines from the first fc
out_fc_col_oid2_index = 'OID2_index'  # Index ranking for the shortest distance lines from the second fc

# Out fc - column names for the coordinates
out_fc_col_oid1_x = 'OID1_x'
out_fc_col_oid1_y = 'OID1_y'
out_fc_col_oid2_x = 'OID2_x'
out_fc_col_oid2_y = 'OID2_y'


# arcpy - cursor
search_cursor = arcpy.da.SearchCursor
update_cursor = arcpy.da.UpdateCursor
# ---------------------------------------------------------------------------------------------------------------------


# PATHS ---------------------------------------------------------------------------------------------------------------
script_file_path = sys.argv[0]
# ---------------------------------------------------------------------------------------------------------------------


# ENVIRONMENTAL SETTINGS ----------------------------------------------------------------------------------------------
arcpy.env.overwriteOutput = True
# ---------------------------------------------------------------------------------------------------------------------


# MAIN PROGRAM --------------------------------------------------------------------------------------------------------
# Create distance lines
with Geometry(point_fc) as geom_fc:
    geom_fc.distance_lines(distance_fc, out_fc, overwrite_out_fc=overwrite)


# Add out_fc to the current active map
project = arcpy.mp.ArcGISProject("CURRENT")
active_map = project.activeMap


if active_map:
    # Determine definition query
    dq = ''

    if content_number_shortest_distance_from_point_fc:
        index_threshold = content_number_shortest_distance_from_point_fc - 1

        if point_fc != distance_fc:
            dq = '"{0}" <= {1}'.format(out_fc_col_oid1_index, index_threshold)
        else:
            dq = '"{0}" <= {2} OR "{1}" <= {2}'.format(out_fc_col_oid1_index, out_fc_col_oid2_index, index_threshold)

    if content_number_shortest_distance_from_distance_fc:
        index_threshold = content_number_shortest_distance_from_distance_fc - 1

        if dq:
            dq += " OR "

        if point_fc != distance_fc:
            dq += '"{0}" <= {1}'.format(out_fc_col_oid2_index, index_threshold)
        else:
            dq += '"{0}" <= {2} OR "{1}" <= {2}'.format(out_fc_col_oid1_index, out_fc_col_oid2_index, index_threshold)

    if content_number_longest_distance_from_point_fc:
        if dq:
            dq += " OR "

        if distance_fc_ids is None:
            distance_fc_ids = [row[0] for row in search_cursor(distance_fc, [distance_fc_objectid])]

        distance_fc_ids_number = len(distance_fc_ids)
        index_threshold = distance_fc_ids_number - content_number_longest_distance_from_point_fc

        if point_fc != distance_fc:
            dq += '"{0}" >= {1}'.format(out_fc_col_oid1_index, index_threshold)
        else:
            dq += '"{0}" >= {2} OR "{1}" >= {2}'.format(
                out_fc_col_oid1_index, out_fc_col_oid2_index, index_threshold - 1
            )

    if content_number_longest_distance_from_distance_fc:
        if dq:
            dq += " OR "

        if point_fc_ids is None:
            point_fc_ids = [row[0] for row in search_cursor(point_fc, [point_fc_objectid])]

        point_fc_ids_number = len(point_fc_ids)
        index_threshold = point_fc_ids_number - content_number_longest_distance_from_distance_fc

        if point_fc != distance_fc:
            dq += '"{0}" >= {1}'.format(out_fc_col_oid2_index, index_threshold)
        else:
            dq += '"{0}" >= {2} OR "{1}" >= {2}'.format(
                out_fc_col_oid1_index, out_fc_col_oid2_index, index_threshold - 1
            )

    # Check overwrite
    if overwrite is False:
        # - Get in_layer (= layer in content)
        layers = active_map.listLayers(content_lyr_display_name)
        layers_count = len(layers)

        if layers_count >= 1:
            # - Set definition query
            in_layer = layers[0]
            in_layer.definitionQuery = dq

            # - Set label
            if in_layer.supports("SHOWLABELS"):
                in_layer.showLabels = True

                for lblClass in in_layer.listLabelClasses():
                    if content_lyr_unit == "meters":
                        lblClass.expression = 'Round([Shape_Length], 2)&"m"'
                    elif content_lyr_unit == "kilometre":
                        lblClass.expression = 'Round([Shape_Length]/1000, 2)&"km"'
                    else:
                        pass

        else:
            error_message = "when using the option 'overwrite = False', u have to add the distance lines to the " \
                            "content. Please use the self defined display name to identify the content layer."
            arcpy.AddError(error_message)

    else:
        # - Get the *.lyrx-file
        rel_path = os.path.dirname(sys.path[0])
        lyr = os.path.join(rel_path, r"data\layer\distance_lines.lyrx")

        # - Add out_fc and *.lyrx-file to content
        in_layer_out_fc = active_map.addDataFromPath(out_fc)
        in_layer_lyr = active_map.addDataFromPath(lyr)

        # - Get & update connection properties
        in_layer_conn_prop = in_layer_out_fc.connectionProperties
        in_layer2_conn_prop = in_layer_lyr.connectionProperties
        in_layer_lyr.updateConnectionProperties(in_layer2_conn_prop, in_layer_conn_prop)

        # - Remove out_fc from the current active map
        active_map.removeLayer(in_layer_out_fc)

        # - Set name & definition query
        in_layer_lyr.name = content_lyr_display_name
        in_layer_lyr.definitionQuery = dq

        # - Set label
        if in_layer_lyr.supports("SHOWLABELS"):
            in_layer_lyr.showLabels = True

            for lblClass in in_layer_lyr.listLabelClasses():
                if content_lyr_unit == "meters":
                    lblClass.expression = 'Round([Shape_Length], 2)&"m"'
                elif content_lyr_unit == "kilometre":
                    lblClass.expression = 'Round([Shape_Length]/1000, 2)&"km"'
                else:
                    pass
# ---------------------------------------------------------------------------------------------------------------------
