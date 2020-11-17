#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# summary TODO

import os, sys, datetime
import argparse
import shutil
import json
from dateutil.tz import tzlocal
from lib.exif_read import ExifRead as EXIF

# from lib.exif_write import ExifEdit
from shapely.geometry import Point, GeometryCollection, shape


def list_images(directory):
    """
    Create a list of image tuples sorted by capture timestamp.
    @param directory: directory with JPEG files
    @return: a list of image tuples with time, directory, lat,long...
    """
    file_list = []
    for root, sub_folders, files in os.walk(directory):
        file_list += [
            os.path.join(root, filename)
            for filename in files
            if filename.lower().endswith(".jpg")
        ]

    files = []
    # get DateTimeOriginal data from the images and sort the list by timestamp
    for filepath in file_list:
        metadata = EXIF(filepath)
        # metadata.read()
        try:
            t = metadata.extract_capture_time()
            geo = metadata.extract_geo()
            files.append((filepath, t, Point(geo["longitude"], geo["latitude"])))

        except KeyError as e:
            # if any of the required tags are not set the image is not added to the list
            print("Skipping {0}: {1}".format(filename, e))

    files.sort(key=lambda timestamp: timestamp[1])
    # print_list(files)
    return files


def import_geojson(geojson_file):
    """
    import the geojson file and create a dict with the commune's name as the key
    and a shape object as the value
    """
    with open(geojson_file) as f:
        features = json.load(f)["features"]
    GeometryCollection([shape(feature["geometry"]).buffer(0) for feature in features])
    cities = {}
    for feature in features:
        city_name = feature["properties"]["NOM_COM"]
        city_shape = shape(feature["geometry"])
        cities[city_name] = city_shape

    return cities


def check_point_in_city(point, city_shape):

    return city_shape.contains(point)


def find_point_city(point, cities_shapes, first_check=None):
    """
    find outer polygon for each image (store the previous correct polygon to speed up calculation
     time as the next image will probably be in the same one)
    """
    if first_check is not None:
        if check_point_in_city(point, cities_shapes[first_check]):
            return first_check

    for city in cities_shapes:
        if check_point_in_city(point, cities_shapes[city]):
            return city


def copy_to_destination(image_path, source_directory, destination_directory):
    """
    Copy image to the destination directory, keeping the subfolder path
    """
    relative_path = os.path.relpath(image_path, source_directory)
    full_destination_path = os.path.join(destination_directory, relative_path)
    os.makedirs(
        os.path.join(destination_directory, os.path.dirname(relative_path)),
        exist_ok=True,
    )
    shutil.copy2(image_path, full_destination_path)


def arg_parse():
    """Parse the command line
    options  :
    json_file, source, destination
    """
    parser = argparse.ArgumentParser(
        description="Script to find in which polygon a geolocalized image belongs to"
    )
    parser.add_argument("-v", "--version", action="version", version="release 1.0")
    parser.add_argument(
        "-j", "--json_file", help="Path to the geojson file", required=True
    )
    parser.add_argument(
        "-s",
        "--source",
        help="Path to the images folder. Sub folder are scanned too",
        required=True,
    )
    parser.add_argument(
        "-d",
        "--destination",
        help="Path to the destination folder in which the images will be copied",
    )
    args = parser.parse_args()
    print(args)
    return args


def main():
    print("image source path is:", args.source)
    print("importing geojson: ", args.json_file)
    cities_dict = import_geojson(args.json_file)
    # create image list with point position for shapely
    print("creating image list...")
    images_list = list_images(args.source)
    # find outer polygon for each image
    print("searching for city...")
    previous_city = None
    for image in images_list:
        city = find_point_city(image[2], cities_dict)
        print("{} -> {}".format(image[0], city))
        if city is not None:
            previous_city = city
        if city is not None and args.destination:
            # copy images to a new directory named with the city name
            copy_to_destination(
                image[0], args.source, os.path.join(args.destination, city)
            )

    print("End of Script")


if __name__ == "__main__":
    # Parsing the command line arguments
    args = arg_parse()
    # print(args.json_file)
    main()