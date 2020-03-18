"""
name: hurc_parser.py
class: 590PR Spring 2020
assignment: 3

This program is intended to satisfy the requirements of assignment 3.

It is dependent on these two data files as input
1. hurdat2-1851-2018-120319.txt
2. hurdat2-nepac-1949-2018-122019.txt

It outputs storm statistics to the console.

!!! ADD CONTRIBUTIONS BELOW !!!
Group Members: Full Name | NetID
1. David Mendoza | davidjm8
    - kilometer to nautical mile calculation
    - Initial attempt, find_hurricanes_hit_location()/hitter_or_not()
        * used Derek's current_coords() and modified form of Derek's Geodesic.WGS84 distance calculation
        * used modified form of Vel's radii calculation
    - Attempt, parse_user_input()
    - minor edits
2. Derek Otis | dhotis2
    - clean_coords()
    - calc_storm_stats()
        * date/delay calculation
        * distance calculation
    - hurdat2_data_to_dicts()
        * this is a revision of data_processing(), made by Vel Wu for assignment 2
    - merged David and Vel's solution for requirement 3, cleaned output.
3. Vel (Tien-Yun) Wu | tienyun2
    - calc_storm_stats()
        * Average Speed (average_speed) and Maximum Speed (maximum_speed) calculation for each storm
    - hitter_or_not()
        * Quadrant checks for storms hitting the user-input coordinates (collaboration with David)
    - hurdat2_data_to_dicts()
        * Prototyping the for-loops used to create list of storms (collaboration with Derek)
        * This method has since been much improved by Derek Otis for assignment 3
"""

from datetime import datetime
from geographiclib.geodesic import Geodesic


def parse_user_input():
    """
    prompts the user for coordinate input, and detects improper input hopefully
    latitude should be be between -90 and 90
    longitude should be between -180 and 180

    :return: tuple
    """
    while True:
        try:
            lat = round(float(input("Specify a latitude (e.g., 76.76). Southern latitudes are negative: ")), 2)
            long = round(float(input("Specify a longitude (e.g., 95.21). Western longitudes are negative: ")), 2)
        except ValueError:
            print("Latitude/longitude input must be a float value (60.6, -2.0, 100.55)\n")
            continue
        return lat, long


def storm_report(storm_dict):
    """prints total distance travelled + maximum and mean propagation speeds for each storm

    :param storm_dict: dictionary describing a storm, created by hurdat2_data_to_dicts()
    :type storm_dict: dictionary
    :return: None
    """
    system_id = storm_dict['storm_system_id']
    name = storm_dict['storm_name']
    max_speed = storm_dict['maximum_speed']
    avg_speed = storm_dict['average_speed']
    if storm_dict['distance']:
        distance = round(storm_dict['distance'] / 1.852, 2)
    else:
        distance = 'NO MOVEMENT LOGGED'

    print('\n++++++-NEW STORM-++++++')
    print(f'SYSTEM ID: {system_id}')
    print(f'NAME: {name}')
    print(f'DISTANCE TRACKED (nm): {distance}')
    print(f'MAX PROPAGATION SPEED (kt): {max_speed}')
    print(f'AVERAGE PROPAGATION SPEED (kt): {avg_speed}')


def clean_coords(latitude, longitude):
    """converts coordinates to a geographiclib-compatible form

    :param latitude: latitude in format 'XXX[N/S]'
    :type latitude: string
    :param longitude: latitude in format 'XXX[E/W]'
    :type longitude: string
    :return: a tuple containing cleaned lat and long"""
    # latitude cleaning
    if latitude[-2] == 'S':
        clean_lat = -(float(latitude[:-2]))
    else:
        clean_lat = float(latitude[:-2])

    # longitude cleaning
    if longitude[-2] == 'W':
        clean_long = -(float(longitude[:-2]))
    else:
        clean_long = float(longitude[:-2])

    return clean_lat, clean_long


def hitter_or_not(storm_dict, current_coords, lat, long, line_fields):
    """NOTE: MUTATES storm_dict (NATIVE TO SCOPE OF hurdat2_data_to_dicts(), PASSED VIA  calc_storm_stats()

    determines whether or not a storm affected the user's input coordinate.

    :param storm_dict: a dictionary describing a storm created by hurdat2_data_to_dicts()
    :type storm_dict: dictionary
    :param current_coords: current coordinates of the hurricane
    :type current_coords: tuple
    :param lat: user defined latitude parsed via parse_user_input()
    :type lat: float
    :param long: user defined longitude parsed via parse_user_input()
    :type long: float
    :param line_fields: a list of strings representing values on a data row in a hurdat2 data file
    :type line_fields: list containing strings
    :return: None"""
    distance_from_user = round((Geodesic.WGS84.Inverse(lat, long, current_coords[0], current_coords[1])['s12'] / 1000) / 1.852, 2)
    # maximum sustained wind and storm eye distance checks
    if int(line_fields[6][:-1]) >= 64:  # checks if maximum sustained wind >= 64kt (Cat. 1 hurricane)
        if distance_from_user <= 5.0:   # checks if w/ in 5.0 nautical miles of user-defined input coordinates
            storm_dict["is_hitter"] = True
        # Quadrant checks:  NE (1st Qdt), SE (4th Qdt), SW (3rd Qdt), NW (2nd Qdt)
        elif lat >= current_coords[0] and long >= current_coords[1] and float(line_fields[-4][:-1]) >= distance_from_user:
            storm_dict["is_hitter"] = True
        elif lat <= current_coords[0] and long >= current_coords[1] and float(line_fields[-3][:-1]) >= distance_from_user:
            storm_dict["is_hitter"] = True
        elif lat <= current_coords[0] and long <= current_coords[1] and float(line_fields[-2][:-1]) >= distance_from_user:
            storm_dict["is_hitter"] = True
        elif lat >= current_coords[0] and long <= current_coords[1] and float(line_fields[-1][:-1]) >= distance_from_user:
            storm_dict["is_hitter"] = True


def calc_storm_stats(line_fields, storm_dict, lat, long):
    """NOTE: MUTATES storm_dict (NATIVE TO SCOPE OF hurdat2_data_to_dicts())

    updates a dictionary describing a storm. Should be called iteratively on data rows as a hurdat2 data file
    is being read

    :param line_fields: a list of strings representing values on a data row in a hurdat2 data file
    :type line_fields: list containing strings
    :param storm_dict: a dictionary describing a storm created by hurdat2_data_to_dicts()
    :type storm_dict: dictionary
    :param lat: user defined latitude parsed via parse_user_input()
    :type lat: float
    :param long: user defined longitude parsed via parse_user_input()
    :type long: float
    :return: None"""
    # date/interval calculation
    date = line_fields[0][:-1]
    time = line_fields[1][:-1]
    current_datetime = datetime(int(date[:4]),
                                int(date[4:6]),
                                int(date[6:]),
                                int(time)//100)

    if storm_dict['util_last_date']:
        interval = (current_datetime - storm_dict['util_last_date']).seconds / 3600  # calculates interval in hours
        storm_dict['duration'] += interval
    else:
        interval = 0
    storm_dict['util_last_date'] = current_datetime

    # distance calculation
    latitude = line_fields[4]
    longitude = line_fields[5]
    current_coords = clean_coords(latitude, longitude)

    if storm_dict['util_last_coords']:
        distance = Geodesic.WGS84.Inverse(storm_dict['util_last_coords'][0],
                                          storm_dict['util_last_coords'][1],
                                          current_coords[0],
                                          current_coords[1])['s12'] / 1000  # calculates distance in kilometers
        storm_dict['distance'] += distance
    else:
        distance = 0
    storm_dict['util_last_coords'] = current_coords

    # speed calculation and checks
    # current speed
    if distance and interval:
        # check if this is maximum speed so far
        # If greater than the last recorded maximum speed, the current speed replaces it as the new maximum.
        # Nothing happens otherwise
        current_speed = round(distance / interval / 1.852, 2)
        if storm_dict["maximum_speed"] == "N/A" or storm_dict["maximum_speed"] < current_speed:
            storm_dict["maximum_speed"] = current_speed

    # Check whether the storm is hitting
    if not storm_dict["is_hitter"]:
        hitter_or_not(storm_dict, current_coords, lat, long, line_fields)


def hurdat2_data_to_dicts(filename, lat, long):
    """Iterates through each data file without holding the entire file in memory at once. Produces a list of
    dictionaries, with each dictionary describing one storm in the data file.

    :param filename: a filepath leading to a valid hurdat2 data file
    :type filename: string
    :param lat: user defined latitude parsed via parse_user_input()
    :type lat: float
    :param long: user defined longitude parsed via parse_user_input()
    :type long: float
    :return: a list of dictionaries describing storms
    """
    # initializes a container outside the for loop
    hurdat2_container = []

    # open file
    with open(filename, 'r') as infile:
        for line in infile:
            line_fields = line.split()

            # if the line starts with a letter, its a header and starts a new storm
            if line[0].isalpha():
                # if we have already processed at least one storm, clean and report on the last storm processed
                if len(hurdat2_container):
                    last_storm_dict = hurdat2_container[-1]
                    last_storm_dict['distance'] = round(last_storm_dict['distance'], 2)
                    if last_storm_dict['duration'] != 0:
                        avg_speed = round(last_storm_dict['distance'] / last_storm_dict['duration'] / 1.852, 2)
                        last_storm_dict['average_speed'] = avg_speed
                    storm_report(last_storm_dict)

                # initialize a new storm dictionary and append it to the container
                # Note: "maximum_speed" and "average_speed" will both be divided by 1.852 when they are assigned any value
                # This is because 1 knot = 1.852 km/hour, and km/hour is the unit used when speeds are first obtained
                # Source: https://en.wikipedia.org/wiki/Knot_(unit)
                new_storm_dict = {
                    "storm_system_id": line_fields[0][:-1],
                    "storm_name": line_fields[1][:-1],
                    "duration": 0,
                    "distance": 0,
                    "util_last_date": None,
                    "util_last_coords": None,
                    "maximum_speed" : "N/A",
                    "average_speed" : "N/A",
                    "is_hitter" : False
                }
                hurdat2_container.append(new_storm_dict)

            # if not, it is a data line and should be passed to the calc_storm_stats()
            else:
                storm_dict = hurdat2_container[-1]
                calc_storm_stats(line_fields, storm_dict, lat, long)
        # prints the last dictionary in the file
        # NOTE: PACIFIC DATASET HAS A REPEATED ENTRY AT THE END, STORM NAME "MADELINE"
        if len(hurdat2_container):
            last_storm_dict = hurdat2_container[-1]
            last_storm_dict['distance'] = round(last_storm_dict['distance'], 2)
            if last_storm_dict['duration'] != 0:
                avg_speed = round(last_storm_dict['distance'] / last_storm_dict['duration'] / 1.852, 2)
                last_storm_dict['average_speed'] = avg_speed
            storm_report(last_storm_dict)
        else:
            print('NO STORMS PROCESSED, PLEASE CHECK INPUT FILE')
        return hurdat2_container


def main():
    """main constitutes the main functionality of the file. Outputs propagation distance and speed statistics for
    hurricanes in the hurdat2 dataset. Also returns a list of hurricanes which affected a coordinate provided by the
    user.

    :return: None"""
    print('This program outputs propagation distance and speed statistics for all hurricanes in the HURDAT2 dataset.\n')
    print('Additionally, it will provide a list of hurricanes which affected a point specified by you.')
    print('NOTE: HURRICANES PRIOR TO 2003 MAY HAVE INSUFFICIENT DATA FOR DETERMINING WHETHER THEY HIT A GIVEN POINT.\n')

    lat, long = parse_user_input()
    list_all_dicts = []

    file1_dicts = hurdat2_data_to_dicts('hurdat2-1851-2018-120319.txt', lat, long)
    file2_dicts = hurdat2_data_to_dicts('hurdat2-nepac-1949-2018-122019.txt', lat, long)

    list_all_dicts.extend(file1_dicts)
    list_all_dicts.extend(file2_dicts)

    # prints list of hurricanes that have hit user-defined location
    hitters = [storm for storm in list_all_dicts if storm["is_hitter"]]
    if hitters:
        print('\nTHE FOLLOWING STORMS AFFECTED POINT ' + str(lat) + " " + str(long) + ':\n')
        for hitter in hitters:
            print(f'{hitter["storm_system_id"]}\t{hitter["storm_name"]}')
    else:
        print('\nNO STORMS AFFECTED POINT ' +  str(lat) + ' ' + str(long) + '.')


main()

