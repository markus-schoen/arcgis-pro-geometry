# SCRIPT --------------------------------------------------------------------------------------------------------------
# Geometry class, mainly based on ESRIs arcpy.Geometry():
# - https://pro.arcgis.com/en/pro-app/latest/arcpy/classes/geometry.htm
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
# Thanks to FelixIP and BERA from gis.stackexchange.com for the inspiration:
# - https://gis.stackexchange.com/questions/286439/need-tool-for-arcmap-to-draw-circle-touching-three-points
# Thanks to Curtis Price for the rotation inspiration:
# - https://github.com/usgs/arcgis-sample/blob/master/scripts/RotateFeatureClass.py
# ---------------------------------------------------------------------------------------------------------------------


# ---------------------------------------------------------------------------------------------------------------------
# TODO /
# ---------------------------------------------------------------------------------------------------------------------


# MODULES -------------------------------------------------------------------------------------------------------------
import arcpy
from copy import deepcopy
import json
import math
import numpy as np
# ---------------------------------------------------------------------------------------------------------------------


# GENERAL INFORMATION -------------------------------------------------------------------------------------------------
__author__ = 'Markus Schön'
__copyright__ = 'Copyright 2021 by Markus Schön'
__license__ = 'Apache License, Version 2.0'
# ---------------------------------------------------------------------------------------------------------------------


# VARIABLES -----------------------------------------------------------------------------------------------------------
search_cursor = arcpy.da.SearchCursor
update_cursor = arcpy.da.UpdateCursor
# ---------------------------------------------------------------------------------------------------------------------


# CLASSES -------------------------------------------------------------------------------------------------------------
class Geometry:
    def __init__(self, feature):
        """
        This is a collection of geometry functions for ArcGIS Pro.

        Notes:
        - This class is mainly based on ESRIs arcpy.Geometry() class:
          https://pro.arcgis.com/en/pro-app/latest/arcpy/classes/geometry.htm
        - You can use the with-statement.
        - You can use selected features.

        :param str feature: Feature layer or class.
        :rtype: object
        :return: Geometry object
        """

        self.feature = feature
        self.__shape = None
        self.__desc = arcpy.Describe(self.feature)
        self.__feature_number = None

    def __enter__(self):
        """
        Enable with-statement.
        :rtype: object
        :return: Geometry instance.
        """

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Delete the geometry instance.
        """

        del self

    # Properties
    @property
    def feature_number(self):
        """
        Get number of features (Read Only).
        :rtype: int
        :return: Number of features.
        """

        if self.__feature_number is None:
            self.__feature_number = int(arcpy.GetCount_management(self.feature).getOutput(0))
        return self.__feature_number

    @property
    def shape(self):
        """
        Create a list of geometry objects (Read Only).
        :rtype: list
        :return: List of geometry objects.
        """

        if self.__shape is None:
            self.__shape = arcpy.CopyFeatures_management(self.feature, arcpy.Geometry())
        return self.__shape

    @property
    def shape_type(self):
        """
        The geometry type: polygon, polyline, point, multipoint, multipatch, dimension, or annotation (Read Only).
        https://pro.arcgis.com/en/pro-app/latest/arcpy/classes/geometry.htm --> Properties --> type

        :rtype: str
        :return: geometry type.
        """
        
        return self.shape[0].type

    @property
    def spatial_reference(self):
        """
        The geometry spatial reference (Read Only).
        :rtype: str
        :return: Geometry spatial reference.
        """
        
        return self.shape[0].spatialReference

    @staticmethod
    def __copy_missing_fields(in_feature, out_feature):
        """
        Copy all missing fields from an input feature to another feature class.

        Hint: This is useful when copying geometry to a feature class. In this case we are missing all fields and
        attributes.

        :param str in_feature: Input feature layer/class. The fields will be copied from this feature layer/class
        :param str out_feature: Output feature layer/class. The fields will be added to this feature class.
        """

        # Get fields (from the input feature)
        ignore_type = ['Geometry', 'GlobalID', 'OID']
        ignore_field = ['OBJECTID', 'Shape', 'Shape_Length', 'Shape_Area']

        fields = [x for x in arcpy.ListFields(in_feature) if x.type not in ignore_type and x.name not in ignore_field]
        fields_accepted = [x.name for x in fields]

        if fields:
            # Add fields to the output feature
            for x in fields:
                arcpy.AddField_management(
                    out_feature, x.name, x.type, x.precision, x.scale, x.length, x.aliasName, x.isNullable, x.required,
                    x.domain
                )

            # Collect attributes and polygons
            content = list(search_cursor(in_feature, fields_accepted))

            # Add attributes to fields
            with update_cursor(out_feature, fields_accepted) as cur:
                row_counter = 0
                for row in cur:
                    row[:] = content[row_counter]
                    cur.updateRow(row)
                    row_counter += 1

            del content

    def boundary(self, out_fc):
        """
        Create a boundary feature class.
        :param str out_fc: Path for the boundary feature class.
        :rtype: str
        :return: Boundary feature class path
        """

        # Create boundary feature class
        boundaries = [x.boundary() for x in self.shape]
        arcpy.CopyFeatures_management(boundaries, out_fc)

        # Copy missing fields and attributes
        self.__copy_missing_fields(self.feature, out_fc)

        return out_fc

    def extent(self, out_fc):
        """
        Create an extent feature class.
        :param str out_fc: Path for the extent feature class.
        :rtype: str
        :return: Extent feature class path
        """

        # Create boundary feature class
        extents = [x.extent.polygon for x in self.shape]
        arcpy.CopyFeatures_management(extents, out_fc)

        # Copy missing fields and attributes
        self.__copy_missing_fields(self.feature, out_fc)

        return out_fc

    def circle_from_three_points(self, out_circle_feature_class, out_circle_centroid_feature_class=None):
        """
        For a given point feature layer, every three point features will be taken to create a circle:
        - https://gis.stackexchange.com/questions/286439/need-tool-for-arcmap-to-draw-circle-touching-three-points
          (--> Thanks to FelixIP and BERA from gis.stackexchange.com for the inspiration).

        Conditions
        - The Geometry class needs to be initialized with a point feature layer/class.
        - The number of the features needs to be a multiple of three --> Every three features will be taken to create a
          circle.

        :param str out_circle_feature_class: Output feature class path for the created circles.
        :param str out_circle_centroid_feature_class: Output feature class path for the created circle centroids.
        """

        if self.shape_type != "point":
            arcpy.AddError("The method only works for point feature classes!")
            message = "The feature '{0}' has shape type {1}!\n".format(self.feature, self.shape_type)
            arcpy.AddError(message)
            exit()

        elif any([x.isMultipart for x in self.shape]):
            arcpy.AddError("The method only works for single part feature classes!")
            message = "The feature '{0}' has multipart features\n!".format(self.feature)
            arcpy.AddError(message)
            exit()

        elif len(self.shape) % 3 != 0:
            arcpy.AddError("The method only works for groups of three points!")
            message = "The feature '{0}' has {1} points!\n".format(self.feature, len(self.shape))
            arcpy.AddError(message)
            exit()

        circle_points = []
        circle_radius = []

        # Group points
        first_points = [p.firstPoint for p in self.shape]
        points_zip = zip(first_points[0::3], first_points[1::3], first_points[2::3])

        points_counter = 0
        for points in points_zip:
            # Calculate centroid coordinates
            matrix = [[p.X, p.Y, 1] for p in points]
            det_a = np.linalg.det(matrix)

            if det_a != 0:
                # An unique solution exists
                matrix = [[(p.X ** 2 + p.Y ** 2) / 2, p.Y, 1] for p in points]
                x = np.linalg.det(matrix) / det_a

                matrix = [[p.X, (p.X ** 2 + p.Y ** 2) / 2, 1] for p in points]
                y = np.linalg.det(matrix) / det_a
                del matrix

                # Create point geometry
                p = arcpy.PointGeometry(arcpy.Point(x, y), self.spatial_reference)
                circle_points.append(p)

                # Calculate radius
                r = self.shape[points_counter * 3].distanceTo(p)
                circle_radius.append(r)

                # raise points_counter
                points_counter += 1

            else:
                # There is no solution for the LGS. It does not exist a point with the same distance to all three points
                arcpy.AddError("There is no solution for the method 'circle_from_three_points'!")
                arcpy.AddError("It does not exist a point with the same distance to all three points!")

        # Create feature classes
        if circle_points:
            if out_circle_centroid_feature_class is None:
                out_circle_centroid_feature_class = 'memory/circle_centroid_fc'

            # Create circle centroids fc
            arcpy.CopyFeatures_management(circle_points, out_circle_centroid_feature_class)

            # - Add radius to the circle centroids fc
            arcpy.AddField_management(out_circle_centroid_feature_class, 'distance', 'Double')
            with update_cursor(out_circle_centroid_feature_class, ['distance']) as cursor:
                index_counter = 0
                for row in cursor:
                    row[0] = circle_radius[index_counter]
                    cursor.updateRow(row)
                    index_counter += 1

            # Create circle fc
            arcpy.Buffer_analysis(out_circle_centroid_feature_class, out_circle_feature_class, 'distance')

        else:
            pass

    def convex_hull(self, out_fc):
        """
        Create a convex hull feature class.
        :param str out_fc: Path for the convex hull feature class.
        :rtype: str
        :return: Convex hull feature class path
        """

        # Create convex hull feature class
        convex_hulls = [x.convexHull() for x in self.shape]
        arcpy.CopyFeatures_management(convex_hulls, out_fc)

        # Copy missing fields and attributes
        self.__copy_missing_fields(self.feature, out_fc)

        return out_fc

    def hull_rectangle(self, out_fc):
        """
        Create a hull rectangle feature class.
        :param str out_fc: Path for the hull rectangle feature class.
        :rtype: str
        :return: Hull rectangle feature class path
        """

        # Create convex hull feature class
        polygons = []

        for coordinate_list in [list(map(float, x.hullRectangle.replace(',', '.').split())) for x in self.shape]:
            array = arcpy.Array()

            for i in range(4):  # Every rectangle has four coordinate pairs
                x = coordinate_list[i * 2]
                y = coordinate_list[i * 2 + 1]
                array.add(arcpy.Point(x, y))

            polygons.append(arcpy.Polygon(array, self.spatial_reference))

        arcpy.CopyFeatures_management(polygons, out_fc)

        # Copy missing fields and attributes
        self.__copy_missing_fields(self.feature, out_fc)

        return out_fc

    def cut(self, cut_polyline, out_fc):
        """
        Cut a polyline/polygon by a polyline.
        :param str cut_polyline: The initialized polyline/polygon will be cut by the cut_polyline.
        :param str out_fc: Path for the cut feature class.
        :rtype: str
        :return: Cut feature class path.
        """

        cut_polyline_geom = Geometry(cut_polyline)

        if cut_polyline_geom.shape_type != 'polyline':
            arcpy.AddError('The cutting polyline has shape type {0}!'.format(cut_polyline_geom.shape_type))

        if self.shape_type == 'point':
            arcpy.AddError('The main feature has shape type "point" and cannot be cut!')
        else:
            cut = [x for x in self.shape]
            for cut_pol in cut_polyline_geom.shape:
                cut_add = []  # collect all cut features
                cut_rem = []  # collect all features that will be replaced by cut features

                for x in cut:
                    try:
                        cut_pieces = x.cut(cut_pol)
                        for cut_piece in cut_pieces:
                            cut_add.append(cut_piece)
                        cut_rem.append(x)
                    except Exception as e:
                        print(e)

                cut = [x for x in cut + cut_add if x not in cut_rem]  # Cut features are replaced by cut for next round

            arcpy.CopyFeatures_management(cut, 'memory/out_fc')
            arcpy.MultipartToSinglepart_management('memory/out_fc', out_fc)

            del cut_polyline_geom
            arcpy.Delete_management('memory/out_fc')

            return out_fc
    
    def distance_lines(self, other_fc, out_fc, overwrite_out_fc=True):
        """
        Create distance lines between the initialized feature layer and the other feature layer 'other_fc'.
        :param other_fc: 2nd feature class to calculate the distance lines.
        :param out_fc: Calculated distance lines.
        :param overwrite_out_fc: Overwrite the output feature class in case of True. By setting this value to False,
        it is possible to run the script again without creating new distance lines. This could be helpful in case of
        setting new definition queries with the toolbox tool because the script runs faster.
        :return: Distance line feature class between all features of the geometry feature class and the other feature
        class.
        :rtype: None
        """

        # Preparation
        # - In fc - object id columns
        first_fc_id = "OBJECTID"
        second_fc_id = "OBJECTID"

        # - Out fc - column names for the ids from the input feature classes
        out_fc_col_oid1 = 'OID1'            # Column name for the ids from the first fc
        out_fc_col_oid2 = 'OID2'            # Column name for the ids from the second fc
        out_fc_col_comb_id = 'OID_Comb'     # Column name for the combined first and second ids

        # - Out fc - column names for the index ranking of the shortest distance distance lines
        out_fc_col_oid1_index = 'OID1_index'  # Index ranking for the shortest distance lines from the first fc
        out_fc_col_oid2_index = 'OID2_index'  # Index ranking for the shortest distance lines from the second fc

        # - Out fc - column names for the coordinates
        out_fc_col_oid1_x = 'OID1_x'
        out_fc_col_oid1_y = 'OID1_y'
        out_fc_col_oid2_x = 'OID2_x'
        out_fc_col_oid2_y = 'OID2_y'

        # Main part
        if not arcpy.Exists(out_fc) or overwrite_out_fc is True:
            geom_other = Geometry(other_fc)

            if self.shape_type != "point":
                arcpy.AddError("Only point features are accepted, not '{0}'".format(self.shape_type))
                exit()

            elif geom_other.shape_type in ['multipoint', 'multipatch', 'dimension', 'annotation']:
                message_gt = "The first feature class has geometry type '{0}'." \
                             "Please only use 'polygon', 'polyline' oder 'point'!".format(self.shape_type)
                arcpy.AddError(message_gt)
                exit()

            if any([x.isMultipart for x in self.shape]):
                message_1st_fc_mp = "The first feature class is not allowed to have multipart's!"
                arcpy.AddError(message_1st_fc_mp)
                exit()

            elif any([x.isMultipart for x in geom_other.shape]):
                message_2nd_fc_mp = "The seconds feature class is not allowed to have multipart's!"
                arcpy.AddError(message_2nd_fc_mp)
                exit()

            elif not self.spatial_reference:
                message_1st_fc_sr = "The first feature class needs to have defined a coordinate system!"
                arcpy.AddError(message_1st_fc_sr)
                exit()

            elif not geom_other.spatial_reference:
                message_2nd_fc_sr = "The second feature class needs to have defined a coordinate system!"
                arcpy.AddError(message_2nd_fc_sr)
                exit()

            elif self.spatial_reference != geom_other.spatial_reference:
                message_sr_match = "Both feature classes needs to have defined the same coordinate systems!"
                arcpy.AddError(message_sr_match)
                exit()

            else:
                lines = []  # Collect all smallest distance lines between the feature layer and the other feature layer
                xy_list = []  # Collect the distance line start and end points.

                # Case: self.shape_type == 'point'
                # --> Collect the distance lines + their start and endpoints
                for geom_fc_part in self.shape:
                    for geom_other_part in geom_other.shape:
                        if geom_other.shape_type == "point":
                            pass

                        elif geom_other.shape_type == "polyline":
                            geom_other_part = geom_other_part.snapToLine(geom_fc_part)

                        elif geom_other.shape_type == "polygon":
                            geom_other_part = geom_other_part.boundary()
                            geom_other_part = geom_other_part.snapToLine(geom_fc_part)

                        geom_centroids = [geom_fc_part.centroid, geom_other_part.centroid]

                        array = arcpy.Array(geom_centroids)
                        polyline = arcpy.Polyline(array)
                        lines.append(polyline)

                        xy_list.append(geom_centroids)

                # Create distance line feature class
                arcpy.CopyFeatures_management(lines, out_fc)
                arcpy.DefineProjection_management(out_fc, self.spatial_reference)

                # Add attributes
                # - Calculate attributes
                fc_ids = [row[0] for row in search_cursor(self.feature, [first_fc_id])]
                other_fc_ids = [row[0] for row in search_cursor(other_fc, [second_fc_id])]

                check_dict = {}  # Temporarily collect (oid1, oid2) combinations. Main goal is to fill the delete_dict.
                delete_dict = {}  # Collect all (oid1, oid2) combinations that occur several times. If self.feature
                # and other_fc match, the associated polylines will be deleted.

                counter = 0
                combinations = {}
                for fc_id in fc_ids:
                    for other_fc_id in other_fc_ids:
                        geom_centroids = xy_list[counter]

                        comb = "(" + str(fc_id) + ", " + str(other_fc_id) + ")"
                        comb_inv = "(" + str(other_fc_id) + ", " + str(fc_id) + ")"

                        combinations[counter] = {
                            'oid1': fc_id,
                            'oid2': other_fc_id,
                            'comb': comb,
                            'comb_inv': comb_inv,
                            'oid1_x': geom_centroids[0].X,
                            'oid1_y': geom_centroids[0].Y,
                            'oid2_x': geom_centroids[1].X,
                            'oid2_y': geom_centroids[1].Y
                        }

                        if check_dict.get(comb) is None and comb != comb_inv:
                            check_dict[comb] = True
                            check_dict[comb_inv] = True
                        else:
                            delete_dict[comb] = True

                        counter += 1

                del check_dict

                # - Add fields
                arcpy.AddField_management(out_fc, out_fc_col_oid1, 'TEXT')
                arcpy.AddField_management(out_fc, out_fc_col_oid2, 'TEXT')
                arcpy.AddField_management(out_fc, out_fc_col_comb_id, 'TEXT')

                arcpy.AddField_management(out_fc, out_fc_col_oid1_x, 'DOUBLE')
                arcpy.AddField_management(out_fc, out_fc_col_oid1_y, 'DOUBLE')
                arcpy.AddField_management(out_fc, out_fc_col_oid2_x, 'DOUBLE')
                arcpy.AddField_management(out_fc, out_fc_col_oid2_y, 'DOUBLE')

                # - Write field attributes
                counter = 0
                id_comb2length_dict = {}
                fields = [
                    out_fc_col_oid1, out_fc_col_oid2, out_fc_col_comb_id, 'Shape_Length',
                    out_fc_col_oid1_x, out_fc_col_oid1_y, out_fc_col_oid2_x, out_fc_col_oid2_y
                ]
                with update_cursor(out_fc, fields) as cursor:
                    for row in cursor:
                        row[0] = combinations[counter]['oid1']
                        row[1] = combinations[counter]['oid2']
                        comb = combinations[counter]['comb']
                        row[2] = comb

                        row[4] = combinations[counter]['oid1_x']
                        row[5] = combinations[counter]['oid1_y']
                        row[6] = combinations[counter]['oid2_x']
                        row[7] = combinations[counter]['oid2_y']

                        cursor.updateRow(row)

                        id_comb2length_dict[comb] = row[3]
                        counter += 1

                # Create length based rankings
                # - Create a dictionary 'fc_out_dict', mapping oid1 to a list of length sorted (oid1, oid2) combinations
                fc_out_dict = {}
                fc_id_2_length_2_id_comb_list_dict = {}
                for oid1 in fc_ids:
                    oid1_str = str(oid1)
                    fc_id_2_length_2_id_comb_list_dict[oid1] = {}

                    for oid_tuple in id_comb2length_dict:
                        oid_tuple_list = oid_tuple.strip('()').replace(', ', ',').replace("u'", "").replace("'", "")
                        oid_tuple_list_first_value = oid_tuple_list.split(',')[0]

                        if oid1_str == oid_tuple_list_first_value:
                            shape_length = id_comb2length_dict[oid_tuple]

                            if shape_length not in fc_id_2_length_2_id_comb_list_dict[oid1]:
                                fc_id_2_length_2_id_comb_list_dict[oid1][shape_length] = []

                            fc_id_2_length_2_id_comb_list_dict[oid1][shape_length].append(oid_tuple)

                    fc_out_dict[oid1_str] = []
                    for length in sorted(fc_id_2_length_2_id_comb_list_dict[oid1]):
                        fc_out_dict[oid1_str] += fc_id_2_length_2_id_comb_list_dict[oid1][length]

                # - Create a dictionary 'other_fc_out_dict', mapping oid2 to a list of length sorted (oid1, oid2)
                #   combinations
                other_fc_out_dict = {}
                other_fc_id_2_length_2_id_comb_list_dict = {}
                for oid2 in other_fc_ids:
                    oid2_str = str(oid2)
                    other_fc_id_2_length_2_id_comb_list_dict[oid2] = {}

                    for oid_tuple in id_comb2length_dict:
                        oid_tuple_list = oid_tuple.strip('()').replace(', ', ',').replace("u'", "").replace("'", "")
                        oid_tuple_list_first_value = oid_tuple_list.split(',')[1]

                        if oid2_str == oid_tuple_list_first_value:
                            shape_length = id_comb2length_dict[oid_tuple]

                            if shape_length not in other_fc_id_2_length_2_id_comb_list_dict[oid2]:
                                other_fc_id_2_length_2_id_comb_list_dict[oid2][shape_length] = []

                            other_fc_id_2_length_2_id_comb_list_dict[oid2][shape_length].append(oid_tuple)

                    other_fc_out_dict[oid2_str] = []
                    for length in sorted(other_fc_id_2_length_2_id_comb_list_dict[oid2]):
                        other_fc_out_dict[oid2_str] += other_fc_id_2_length_2_id_comb_list_dict[oid2][length]

                # - Add fields
                arcpy.AddField_management(out_fc, out_fc_col_oid1_index, 'SHORT')
                arcpy.AddField_management(out_fc, out_fc_col_oid2_index, 'SHORT')

                # - Write rankings
                counter = 0
                fields = [
                    out_fc_col_comb_id,
                    out_fc_col_oid1,
                    out_fc_col_oid2,
                    out_fc_col_oid1_index,
                    out_fc_col_oid2_index
                ]

                with update_cursor(out_fc, fields) as cursor:
                    for row in cursor:
                        if self.feature == other_fc:
                            comb = combinations[counter]['comb']
                            counter += 1
                            if delete_dict.get(comb) is True:
                                cursor.deleteRow()
                                continue
                            else:
                                comb, oid1, oid2 = row[0: 3]
                                row[3] = fc_out_dict[oid1].index(comb) - 1
                                row[4] = other_fc_out_dict[oid2].index(comb) - 1
                                cursor.updateRow(row)
                        else:
                            comb, oid1, oid2 = row[0: 3]
                            row[3] = fc_out_dict[oid1].index(comb)
                            row[4] = other_fc_out_dict[oid2].index(comb)
                            cursor.updateRow(row)

    def inner_circle(self, out_circle, out_point=None, accuracy=0.01):
        """
        Create maximum inner circles and centroids for the initialized polygon feature layer.
        :param str out_circle: Feature class containing the inner circles.
        :param str out_point: Feature class containing the inner circle centroids.
        :param float accuracy: The calculation accuracy. This is needed to stop the approximation in some cases.
        """

        def converge_to_the_center(polygon, centroids_list, distances_list):
            """
            Calculate the the maximum inner circle centroids by convergence.

            :param shape polygon: Polygon shape object.
            :param list centroids_list: List of inner circle centroid point geometries.
            :param list distances_list: List of inner circle radius for every inner circle centroid.
            """

            dist = 0

            while True:
                try:
                    feature_boundary = polygon.boundary()
                    feature_centroid = polygon.centroid

                    point_geom = arcpy.PointGeometry(feature_centroid, self.spatial_reference)
                    min_dist = feature_boundary.distanceTo(point_geom)

                    dist += min_dist

                    if min_dist <= accuracy or shape.pointCount is 2:
                        centroids_list.append(point_geom)
                        distances_list.append(dist)
                        break

                    polygon = polygon.buffer(float("-{0}".format(min_dist)))

                except Exception as e:
                    arcpy.AddMessage(e)
                    break

        delete_list = []

        # Calculate inner circle centroids and radius
        shapes = arcpy.MultipartToSinglepart_management(self.feature, arcpy.Geometry())

        centroid_list = []
        distance_list = []

        for shape in shapes:
            converge_to_the_center(shape, centroid_list, distance_list)

        # Create inner circle centroid feature class
        if out_point is None:
            out_point = 'memory/out_point'
            delete_list.append(out_point)

        arcpy.CopyFeatures_management(centroid_list, out_point)

        # - Add Fields with distance information to inner circle centroid feature class
        arcpy.AddField_management(out_point, 'radius', 'Double')
        with update_cursor(out_point, 'radius') as cursor:
            counter = 0
            for row in cursor:
                row[0] = distance_list[counter]
                cursor.updateRow(row)
                counter += 1

        # Create inner circle feature class:
        arcpy.Buffer_analysis(out_point, out_circle, 'radius')

        # Clear memory
        for element in delete_list:
            arcpy.DeleteField_management(element)

    def numerate(self, sort_by='top_left', field_name='id'):
        """
        Numerate all features by it's coordinates.
        To store the results, this method creates a short integer field. The lowest value is 1.

        :param str sort_by: Feature sort options:
        - top_left:     Sort from top to bottom. Elements with same y are sorted from left to right.
        - top_right:    Sort from top to bottom. Elements with same y are sorted from right to left.
        - bottom_left:  Sort from bottom to top. Elements with same y are sorted from left to right.
        - bottom_right: Sort from bottom to top. Elements with same y are sorted from right to left.
        - right_top:    Sort from right to left. Elements with same x are sorted from top to bottom.
        - right_bottom: Sort from right to left. Elements with same x are sorted from bottom to top.
        - left_top:     Sort from left to right. Elements with same x are sorted from top to bottom.
        - left_bottom:  Sort from left to right. Elements with same x are sorted from bottom to top.
        :param str field_name: Name of the added short integer field.
        """

        dictionary = {
            'top_left': [1, True, False],       # [y -> index 1, top 2 bottom -> reverse, left 2 right -> no reverse]
            'top_right': [1, True,  True],      # [y -> index 1, top 2 bottom -> reverse, right 2 left -> reverse]
            'bottom_left': [1, False, False],   # [y -> index 1, bottom 2 top -> no reverse, left 2 right -> no reverse]
            'bottom_right': [1, False, True],   # [y -> index 1, bottom 2 top -> no reverse, right 2 left -> reverse]
            'right_top': [0, True, True],       # [x -> index 0, right 2 left -> reverse, top 2 bottom -> reverse]
            'right_bottom': [0, True, False],   # [x -> index 0, right 2 left -> reverse, bottom 2 top -> no reverse]
            'left_top': [0, False, True],       # [x -> index 0, left 2 right -> no reverse, top 2 bottom -> reverse]
            'left_bottom': [0, False, False],   # [x -> index 0, left 2 right -> no reverse, bottom 2 top -> no reverse]
        }

        xy_index, reverse_1, reverse_2 = dictionary[sort_by]

        if self.shape_type == 'point':
            # Add numeration field
            if field_name not in arcpy.ListFields(self.feature):
                arcpy.AddField_management(self.feature, field_name, 'Short')

            # Get oid to id (=numeration) dictionary
            oid_x_y_list = [row for row in search_cursor(self.feature, ['SHAPE@X', 'SHAPE@Y', 'OID@'])]
            oid_x_y_list_sorted = sorted(oid_x_y_list, key=lambda row: row[xy_index + 1 % 2], reverse=reverse_2)
            oid_x_y_list_sorted = sorted(oid_x_y_list_sorted, key=lambda row: row[xy_index], reverse=reverse_1)
            oid_2_id_dict = {x[1][2]: x[0] + 1 for x in enumerate(oid_x_y_list_sorted)}

            # Update feature class numeration field
            with update_cursor(self.feature, ['OID@', field_name]) as cur:
                for row in cur:
                    oid = row[0]
                    row[1] = oid_2_id_dict[oid]
                    cur.updateRow(row)

        else:
            arcpy.AddError("This method only works for point feature classes!")

    def polyline_to_polygon(self, out_polygon):
        """
        Create a polygon feature class from a polyline feature (layer/class).
        We keep the original spatial reference.

        :param str out_polygon: Output polygon feature class path.

        :rtype: str
        :return: Output polygon feature class path.
        """

        # Get feature set dictionary
        # https://developers.arcgis.com/documentation/common-data-types/featureset-object.htm
        feature_set = arcpy.FeatureSet()
        feature_set.load(self.feature)
        dictionary = json.loads(feature_set.JSON)

        # Edit feature set dictionary
        # - Set geometry type
        dictionary['geometryType'] = 'esriGeometryPolygon'

        # - Set array types
        json_dump = json.dumps(dictionary)  # Create string from dictionary

        array_types = {'curvePaths': 'curveRings', 'paths': 'rings'}
        for array_type in array_types:
            json_dump = json_dump.replace(array_type, array_types[array_type])

        # Save edited feature set dictionary to a polygon feature class
        try:
            fs = arcpy.FeatureSet()
            fs.load(json_dump)
            arcpy.CopyFeatures_management(fs, out_polygon)
        except AttributeError as e:
            arcpy.AddWarning(f'Spatial reference: {dictionary["spatialReference"]}')
            arcpy.AddWarning(f"Attribute Error:\nThe coordinates doesn't match the coordinate system\n\nOriginal:\n{e}")
            out_polygon = ''
        except Exception as e:
            arcpy.AddWarning(e)
            out_polygon = ''

        return out_polygon

    def points_along_feature(self, out_fc, distance=0.5):
        """
        Creates points along a polyline or polygon feature (layer/class) for a selected distance.
        One multipoint is created for each feature.

        :param str out_fc: Output feature class path for the created multipoints.
        :param float distance: Distance between each following point.
        """

        # Get lines
        if self.shape_type == 'polygon':
            shapes = [x.boundary() for x in self.shape]
        elif self.shape_type == 'polyline':
            shapes = self.shape
        else:
            shapes = None

        # Create out_fc
        if shapes:
            point_list = []

            # Create multipoints (for every shape)
            for shape in shapes:
                array = arcpy.Array()

                length = 0
                number_of_points = int(shape.length / distance)

                for i in range(number_of_points + 1):
                    length += distance
                    point_geometry = shape.positionAlongLine(length)
                    centroid = point_geometry.centroid
                    array.add(centroid)

                if array:
                    point_list.append(arcpy.Multipoint(array, self.spatial_reference))

            # Create out_fc (from collected multipoints)
            if point_list:
                arcpy.CopyFeatures_management(point_list, out_fc)

    @staticmethod
    def rotate_xy(x, y, rotation_angle=0, x_cnt=0, y_cnt=0):
        """
        Rotate x, y values bye center point coordinates x_cnt, y_cnt and a rotation angle.

        # Thanks to Curtis Price for the rotation inspiration:
        # - https://github.com/usgs/arcgis-sample/blob/master/scripts/RotateFeatureClass.py

        :param float x: X value to be rotated.
        :param float y: Y value to be rotated.
        :param float rotation_angle: Number of degrees with which to rotate.
        :param float x_cnt: X value around which to rotate. (x_cnt = abbreviation for 'x center').
        :param float y_cnt: Y value around which to rotate. (y_cnt = abbreviation for 'y center').

        :rtype: list
        :return: List [x, y] with rotated xy values.
        """

        # Move x, y to the origin (First we wan't to rotate through the coordinate origin and then we move back)
        x -= x_cnt
        y -= y_cnt

        # Get angle radian (clockwise rotation)
        rotation_angle = -1 * rotation_angle  # Factor -1 means clockwise rotation
        rotation_angle = math.radians(rotation_angle)

        # Rotate x, y through the coordinate origin (and then move back)
        x_rot = (x * math.cos(rotation_angle)) - (y * math.sin(rotation_angle)) + x_cnt
        y_rot = (x * math.sin(rotation_angle)) + (y * math.cos(rotation_angle)) + y_cnt

        return x_rot, y_rot

    def rotate_fc(self, out_feature, rotation_value='xy', rotation_angle=0, rotation_x=None, rotation_y=None):
        """
        Rotate an input feature class. Curves will be respected.

        :param str out_feature: Output feature class path.
        :param str rotation_value:
            - 'xy':
               Use the values 'rotation_x' and 'rotation_y' for rotation.
            - 'in_feature_centroid':
               For every feature, the features centroid will be used for rotation. The tool acts like handling single
               part features.
            - 'in_feature_true_centroid':
               For every feature, the features true centroid will be used for rotation. The tool acts like handling
               single part features.
        :param float rotation_angle: Input rotation value.
        :param float rotation_x: (Optional) X value around which to rotate. This value will only be used in case of 
        rotation_value = 'xy'.
        :param float rotation_y: (Optional) Y value around which to rotate. This value will only be used in case of 
        rotation_value = 'xy'.
        
        :rtype: str
        :return: Output feature class path.
        """

        # Preparation
        # - Output feature
        if out_feature != self.__desc.catalogPath:
            arcpy.CopyFeatures_management(self.feature, out_feature)

        # - Check shape_type
        if self.shape_type in ['point', 'multipoint']:
            if rotation_value in ['in_feature_centroid', 'in_feature_true_centroid']:
                # Centroid rotation - Points do not have to be rotated around themselves.
                return out_feature

        # - Ensure, rotation angle < 360°
        rotation_angle = int(rotation_angle) % 360 + (rotation_angle - int(rotation_angle))

        # - Check rotation value
        #   Collect rotation centroids in case rotation_value != 'xy'
        in_feature_centroid_list = []  # Feature rotation centroids

        if rotation_value != 'xy':
            feature_mem = 'memory/feature_single_parts'
            arcpy.MultipartToSinglepart_management(out_feature, feature_mem)

            with search_cursor(feature_mem, 'SHAPE@') as cur:
                for row in cur:
                    if rotation_value == 'in_feature_centroid':
                        in_feature_centroid_list.append(row[0].centroid)
                    elif rotation_value == 'in_feature_true_centroid':
                        in_feature_centroid_list.append(row[0].trueCentroid)
                    else:
                        arcpy.AddError('Missing rotation type!')

            arcpy.Delete_management(feature_mem)

        # Rotation
        with update_cursor(out_feature, 'SHAPE@JSON') as cur:
            cnt_in_feature_centroid = 0

            for row in cur:
                if row[0] is None:
                    # - Can't rotate NoneType values
                    continue

                row_dict = json.loads(row[0])

                # - Points
                if row_dict.get('x'):
                    # - - Hint: type(row_dict['x']) == float
                    # - - Get x, y values
                    x = row_dict['x']
                    y = row_dict['y']

                    # - - Rotate x, y values
                    x_rot, y_rot = self.rotate_xy(x, y, rotation_angle, rotation_x, rotation_y)

                    # - - Update x, y values
                    row_dict['x'] = x_rot
                    row_dict['y'] = y_rot

                # - MultiPoints
                for key in ['points']:
                    if row_dict.get(key):
                        # - - Hint: type(row_dict[key]) == list

                        cnt_1 = 0  # Save value_list index position within the list 'row_dict[key]'.
                        for value_list in row_dict[key]:
                            # - - Hint: type(value_list) == list
                            # - Get x, y values
                            x = value_list[0]
                            y = value_list[1]

                            # - Rotate x, y values
                            x_rot, y_rot = self.rotate_xy(x, y, rotation_angle, rotation_x, rotation_y)

                            # - Update x, y values
                            value_list[0] = x_rot
                            value_list[1] = y_rot

                            # - - Update row_dict dictionary
                            row_dict[key][cnt_1] = value_list
                            cnt_1 += 1

                # - Polylines & Polygons
                for key in ['paths', 'rings', 'curveRings', 'curvePaths']:
                    if row_dict.get(key):
                        # - - Hint: type(row_dict[key]) == list

                        cnt_1 = 0  # Save value_list index position within the list 'row_dict[key]'.
                        for value_list in row_dict[key]:
                            # - - Hint: type(value_list) == list
                            # - - Check rotation_value - edit rotation_x/y in case of a centroid rotation
                            if rotation_value != 'xy':
                                rotation_x = in_feature_centroid_list[cnt_in_feature_centroid].X
                                rotation_y = in_feature_centroid_list[cnt_in_feature_centroid].Y
                                cnt_in_feature_centroid += 1

                            cnt_2 = 0  # Save iterable index position within the list 'value_list'.
                            for iterable in value_list:
                                # - - Hint: type(iterable) in [list, dict]

                                if type(iterable) is list:
                                    # - - key in ['paths', 'rings']
                                    # - Get x, y values
                                    x = iterable[0]
                                    y = iterable[1]

                                    # - Rotate x, y values
                                    x_rot, y_rot = self.rotate_xy(x, y, rotation_angle, rotation_x, rotation_y)

                                    # - Update x, y values
                                    iterable[0] = x_rot
                                    iterable[1] = y_rot

                                    # - - Update row_dict dictionary
                                    row_dict[key][cnt_1][cnt_2] = iterable

                                elif type(iterable) is dict:
                                    # - - key in ['curveRings', 'curvePaths']

                                    for sub_key in iterable:
                                        cnt_3 = 0  # - - Save sub_value index position within the list iterable[sub_key]
                                        for sub_value in iterable[sub_key]:
                                            # - - Hint: type(sub_value) in [list, int, float]

                                            if type(sub_value) == list:
                                                # - Get x, y values
                                                x = sub_value[0]
                                                y = sub_value[1]

                                                # - Rotate x, y values
                                                x_rot, y_rot = self.rotate_xy(
                                                    x, y, rotation_angle, rotation_x, rotation_y
                                                )

                                                # - Update x, y values
                                                sub_value[0] = x_rot
                                                sub_value[1] = y_rot

                                                # - - Update row_dict dictionary
                                                row_dict[key][cnt_1][cnt_2][sub_key][cnt_3] = sub_value

                                            elif type(sub_value) in (int, float):
                                                pass

                                            else:
                                                arcpy.AddWarning(sub_value)
                                            cnt_3 += 1
                                cnt_2 += 1
                            cnt_1 += 1

                # - Save edits
                row[0] = json.dumps(row_dict)
                cur.updateRow(row)

        return out_feature
# ---------------------------------------------------------------------------------------------------------------------


# FUNCTIONS -----------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------


# PREPARATION ---------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------


# ENVIRONMENTAL SETTINGS ----------------------------------------------------------------------------------------------
arcpy.env.overwriteOutput = True
# ---------------------------------------------------------------------------------------------------------------------


# MAIN PROGRAM --------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    pass
# ---------------------------------------------------------------------------------------------------------------------
