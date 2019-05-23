
from collections import defaultdict

import matplotlib.pyplot as plt
import numpy as np
import scipy
import scipy.spatial
import yafs.utils
import math
from matplotlib.collections import PatchCollection,PolyCollection
from yafs.utils import haversine_distance
from functools import partial
import pyproj
from shapely.ops import transform
from shapely.geometry import Point

from matplotlib.patches import Circle

class Coverage(object):
    def __init__(self):
        None

    def update_coverage_of_endpoints(self, **kwargs):
        return None

    def connection(self,point):
        return None

    @staticmethod
    def get_polygons_on_map():
        return None

    def connection_between_mobile_entities(self, fixed_endpoints, mobile_endpoints):
        # type: (dict, dict) -> dict
        """

        Args:
            fixed_endpoints: dict , {id_node: (lat,lng)}
            mobile_endpoints: dict, {code_mobile_entity: (lat,lng)}

        Returns:
            dict {code_mobility_entity : id_node}

        """
        return {}




class CircleCoverage(Coverage):
    def __init__(self, map, points,radius):
        self.points = points
        self.radius = radius #radius in km

        #Points on the map projection
        self.points_to_map  = [map.to_pixels(p[0], p[1]) for p in self.points]

        # Radius in the map projection
        b = self.__geodesic_point_buffer(points[0][0], points[0][1], self.radius)
        bonmap = map.to_pixels(b[0])
        ponmap = map.to_pixels(points[0][0],points[0][1])
        distance = math.sqrt(math.pow((bonmap[0]-ponmap[0]),2)+math.pow((bonmap[1]-ponmap[1]),2))
        self.radius_on_coordinates = distance

        # Region on the map projection
        self.regions_to_map = [Circle((region[0],region[1]),self.radius_on_coordinates) for region in self.points_to_map]

        # Color of the regions
        self.cmap = plt.cm.Accent
        self.colors_cells = self.cmap(np.linspace(0., 1., len(self.points)))[:, :3]



    def update_coverage_of_endpoints(self, map, points):
        """
        It updates the points, regions and colors in case of endpoints and mobile-endpoints changes
        Args:
            map:
            points:

        """
        self.points = points
        self.points_to_map = [map.to_pixels(p[0], p[1]) for p in self.points]

        self.regions_to_map = [Circle((region[0], region[1]), self.radius_on_coordinates) for region in self.points_to_map]

        self.colors_cells = self.cmap(np.linspace(0., 1., len(self.points)))[:, :3]


    def get_polygons_on_map(self):
        """
        This functions display network endpoint on the map representation
        Returns:
            a list of matplotlib Polygons
        """
        return PatchCollection(self.regions_to_map, facecolors=self.colors_cells, alpha=.25)


    def connection(self, point):
        """
        Compute the connection among a user and endpoints

        In this implementation the preference between several endpoints is given by the less distance
        Other policies can be implemented storing a historic of connections.

        Args:
            point: [lng,lat] a user position

        Returns:
            the index on self.points
        """

        most_close = [999999999] # the minimun value in all var. of array are infinity
        for idx,center in enumerate(self.points):
            dist = haversine_distance(point,center)
            if dist <= self.radius: #km to meters
                most_close.append(dist)
            else:
                most_close.append(float("inf"))

        min = np.argmin(most_close)
        if min == 0:
            return None
        return min-1



    def connection_between_mobile_entities(self, fixed_endpoints, mobile_endpoints,mobile_fog_entities):
        # type: (dict, dict) -> dict
        """

        Args:
            fixed_endpoints: dict , {id_node: (lat,lng)}
            mobile_endpoints: dict, {code_mobile_entity: (lat,lng)}

        Returns:
            dict {code_mobility_entity : id_node}

        """
        result = {}

        for code in mobile_fog_entities:
            # print mobile_fog_entities[code]
            if mobile_fog_entities[code]["connectionWith"] != None:
                result[code] = mobile_fog_entities[code]["connectionWith"]
            else:
                point = mobile_endpoints[code]
                idx = np.argmin(np.sum((np.array(fixed_endpoints.values()) - point) ** 2, axis=1))

                id_node = list(fixed_endpoints)[idx]
                pnode = fixed_endpoints[id_node]
                if self.__circle_intersection(point,pnode):
                    result[code] = [list(fixed_endpoints)[idx]]
        return result

    def __circle_intersection(self, center1, center2):
        """
        Based on: https://gist.github.com/xaedes/974535e71009fa8f090e

        Args:
            center1: coordinates of a circle
            center2: coordinates of a circle

        Returns: a boolean, in case of a circle is touching or included in the other circle

        """


        # return self.circle_intersection_sympy(circle1,circle2)
        x1, y1  = center1
        x2, y2  = center2
        r1 = self.radius
        # http://stackoverflow.com/a/3349134/798588
        dx, dy = x2 - x1, y2 - y1
        d = math.sqrt(dx * dx + dy * dy)
        if d > r1 + r1:
            return False ## no solutions, the circles are separate

        return True  # no solutions because one circle is contained within the other



    def __geodesic_point_buffer(self, lon, lat, km):
        """
        Based on: https://gis.stackexchange.com/questions/289044/creating-buffer-circle-x-kilometers-from-point-using-python

        Args:
            lon:
            lat:
            km:

        Returns:
            a list of coordinates with radius km and center (lat,long) in this projection
        """
        proj_wgs84 = pyproj.Proj(init='epsg:4326')
        # Azimuthal equidistant projection
        aeqd_proj = '+proj=aeqd +lat_0={lat} +lon_0={lon} +x_0=0 +y_0=0'
        project = partial(
            pyproj.transform,
            pyproj.Proj(aeqd_proj.format(lat=lat, lon=lon)),
            proj_wgs84)
        buf = Point(0, 0).buffer(km * 1000)  # distance in metres
        return transform(project, buf).exterior.coords[:]


class Voronoi(Coverage):
    def __init__(self, map, points):
        self.tree = None
        self.points = points
        self.__vor = scipy.spatial.Voronoi(self.points)
        self.regions, self.vertices = self.voronoi_finite_polygons_2d(self.__vor)

        self.cells = [map.to_pixels(self.vertices[region]) for region in self.regions]
        cmap = plt.cm.Set3
        self.colors_cells = cmap(np.linspace(0., 1., len(self.points)))[:, :3]

    def update_coverage_of_endpoints(self, map, points):
        self.points = points
        self.__vor = scipy.spatial.Voronoi(self.points)
        self.regions, self.vertices = self.voronoi_finite_polygons_2d(self.__vor)
        self.cells = [map.to_pixels(self.vertices[region]) for region in self.regions]
        cmap = plt.cm.Set3
        self.colors_cells = cmap(np.linspace(0., 1., len(self.points)))[:, :3]


    def get_polygons_on_map(self):
        return PolyCollection(self.cells, facecolors=self.colors_cells, alpha=.25,edgecolors="gray")


    def connection(self,point):
        """

        Args:
            point: [lng,lat]

        Returns:
            the index on self.points

        """
        return np.argmin(np.sum((self.points - point) ** 2, axis=1))




    def connection_between_mobile_entities(self,fixed_endpoints,mobile_endpoints):
        # type: (dict, dict) -> dict
        """

        Args:
            fixed_endpoints: dict , {id_node: (lat,lng)}
            mobile_endpoints: dict, {code_mobile_entity: (lat,lng)}

        Returns:
            dict {code_mobility_entity : id_node}

        """
        result = {}

        for k in mobile_endpoints:
            point = mobile_endpoints[k]
            idx = np.argmin(np.sum((np.array(fixed_endpoints.values()) - point) ** 2, axis=1))
            result[k] = list(fixed_endpoints)[idx]

        return result

    def voronoi_finite_polygons_2d(self, vor, radius=None):
        """Reconstruct infinite Voronoi regions in a
        2D diagram to finite regions.
        Source:
        [https://stackoverflow.com/a/20678647/1595060](https://stackoverflow.com/a/20678647/1595060)
        """
        if vor.points.shape[1] != 2:
            raise ValueError("Requires 2D input")
        new_regions = []
        new_vertices = vor.vertices.tolist()
        center = vor.points.mean(axis=0)
        if radius is None:
            radius = vor.points.ptp().max()
        # Construct a map containing all ridges for a
        # given point
        all_ridges = {}
        for (p1, p2), (v1, v2) in zip(vor.ridge_points,
                                      vor.ridge_vertices):
            all_ridges.setdefault(
                p1, []).append((p2, v1, v2))
            all_ridges.setdefault(
                p2, []).append((p1, v1, v2))
        # Reconstruct infinite regions
        for p1, region in enumerate(vor.point_region):
            vertices = vor.regions[region]
            if all(v >= 0 for v in vertices):
                # finite region
                new_regions.append(vertices)
                continue
            # reconstruct a non-finite region
            ridges = all_ridges[p1]
            new_region = [v for v in vertices if v >= 0]
            for p2, v1, v2 in ridges:
                if v2 < 0:
                    v1, v2 = v2, v1
                if v1 >= 0:
                    # finite ridge: already in the region
                    continue
                # Compute the missing endpoint of an
                # infinite ridge
                t = vor.points[p2] - \
                    vor.points[p1]  # tangent
                t /= np.linalg.norm(t)
                n = np.array([-t[1], t[0]])  # normal
                midpoint = vor.points[[p1, p2]]. \
                    mean(axis=0)
                direction = np.sign(
                    np.dot(midpoint - center, n)) * n
                far_point = vor.vertices[v2] + \
                            direction * radius
                new_region.append(len(new_vertices))
                new_vertices.append(far_point.tolist())
            # Sort region counterclockwise.
            vs = np.asarray([new_vertices[v]
                             for v in new_region])
            c = vs.mean(axis=0)
            angles = np.arctan2(
                vs[:, 1] - c[1], vs[:, 0] - c[0])
            new_region = np.array(new_region)[
                np.argsort(angles)]
            new_regions.append(new_region.tolist())
        return new_regions, np.asarray(new_vertices)

