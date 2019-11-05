'''
Author: Ting Ting Huang
Date Created: 1/24/19
Purpose: This script is used to convert JSON formats of
the following direction data:
    1. Directions: Primary to Primary
    2. Directions: Primary to Secondary
    3. Directions: Zone to Primary
    Original Format:[{k:v}]
into CSV files. This is used to reorganize the current
data of WayFinder App.
'''
import json
import csv
import argparse
import sys
from pathlib import Path

def create_arg_parser():
    '''Parses the arguments and returns an ArgumenentParse object [input, additional, output, format key]'''
    parser = argparse.ArgumentParser(description='Processes json files into csv')
    parser.add_argument("inputPath", help="The json file you wish to convert in csv.")
    parser.add_argument("additionalPath", nargs='?', default=None, help="An additional json file you'd like to use for specification purposes. Ex. Zone file for primary formatting.")
    parser.add_argument("outputPath", help="The location you'd live the csv file to export")

    #Flags to see which format to use
    #Either choose the primary to primary/secondary format or zone to primary format
    parser.add_argument("--format", choices=['p', 'z2p', 'z2s'], help="Enter p for primary to primary/secondary. Enter z for zone to primary.")

    return parser

#PrimaryStart_End Function
def pstart_end(basis):
    '''Builds a single row with extending directions and respective image URL
    given that there are more than one row with the same Primary Start & End
    pairing.'''
    main_dict = dict()
    destination = None

    for key in basis:

        if 'destination_P_name' in key: #Primary to Primary
            destination = key['destination_P_name']
        else:                           #Primary to Secondary
            destination = key['s_name']

        if (key['p_name'], destination) not in main_dict:
            main_dict[(key['p_name'], destination)] = {'Directions': [], 'Image URL': []}
        main_dict[(key['p_name'], destination)]['Directions'].append(key['text'])
        main_dict[(key['p_name'], destination)]['Image URL'].append(key['image_url'])

        #Check if there is a discrepancy between Directions and Image URLs (Assuming they are constant pairs)
        if len(main_dict[(key['p_name'], destination)]['Directions']) != len(main_dict[(key['p_name'], destination)]['Image URL']):
            print("ERROR: Discrepancy in length of Directions and Image URLs found in following: ")
            print(main_dict[(key['p_name'], destination)])

    return main_dict

def zstart_end(basis):
    '''Build a single row with extending directions and respective image URL
    given that there are more than one row with the same Zone Start &
    Primary/Secondary End pairing. Ignore anything that is not Primary or
    Secondary.'''

    p_dict = dict()
    s_dict = dict()

    for key in basis:
        if key['p_name'][0] == 'S':
            if (key['z_name'], key['p_name']) not in s_dict:
                s_dict[(key['z_name'], key['p_name'])] = {'Directions': [], 'Image URL': []}
            s_dict[(key['z_name'], key['p_name'])]['Directions'].append(key['text'])
            s_dict[(key['z_name'], key['p_name'])]['Image URL'].append(key['image_url'])

            #Check if there is a discrepancy between Directions and Image URLs (Assuming they are constant pairs)
            if len(s_dict[(key['z_name'], key['p_name'])]['Directions']) != len(s_dict[(key['z_name'], key['p_name'])]['Image URL']):
                print("ERROR: Discrepancy in length of Directions and Image URLs found in following: ")
                print(s_dict[(key['z_name'], key['p_name'])])
        else:
            if (key['z_name'], key['p_name']) not in p_dict:
                p_dict[(key['z_name'], key['p_name'])] = {'Directions': [], 'Image URL': []}
            p_dict[(key['z_name'], key['p_name'])]['Directions'].append(key['text'])
            p_dict[(key['z_name'], key['p_name'])]['Image URL'].append(key['image_url'])

            #Check if there is a discrepancy between Directions and Image URLs (Assuming they are constant pairs)
            if len(p_dict[(key['z_name'], key['p_name'])]['Directions']) != len(p_dict[(key['z_name'], key['p_name'])]['Image URL']):
                print("ERROR: Discrepancy in length of Directions and Image URLs found in following: ")
                print(p_dict[(key['z_name'], key['p_name'])])

    return (p_dict, s_dict)

rh_list = ['Zone', 'Start', 'End']
zrh_list = ['Zone', 'Primary']
def row_headers(l, d):
    '''Builds a list of row headers from an already initalized list;
    Encompass the max amount of Directions and Image URLS'''
    max_len = 0
    count = 1

    for key in d:
        max_len = max(len(d[key]['Directions']), max_len)

    while count <= max_len:
        dir_count = 'DIRECTIONS ' + str(count)
        url_count = 'IMAGE URL ' + str(count)
        l.append(dir_count)
        l.append(url_count)
        count += 1

    return l

def primary_zone_pair(pzd):
    '''Takes in the primary zone data and builds a dictionary with the primaries
    as keys and the zone it is in as values.'''
    main_dict = dict()

    for each in pzd:
        if each['p_name'] not in main_dict:
            main_dict[each['p_name']] = each['z_name']

    return main_dict

def match_check(sorted_pdata, zp_pairing):
    '''Checks if the primaries in sorted_pdata exists in zp_pairing, if it does
    not exist - print out the non-existent key and returns a list of tuples
    without those keys.'''
    checked = []

    for p in sorted_pdata:
        if p[0] not in zp_pairing:
            print(p)
            sorted_pdata.remove(p)
        else:
            checked.append(p)

    return checked

#FORMATTING FUNCTION CALLS: P --> Primary to Primary & Primary to Secondary, Z --> Zone to Primary
def p(pdata, data, zdata):
    '''Takes in the primary start and end information data, headers for the csv,
    and the raw direction data to create a new csv file in Primary to Primary or Primary
    to Secondary format.'''
    count = 0
    zp_pairing = primary_zone_pair(zdata) #{'Primary': 'Zone'}

    #Sorted by Alphanumerical Order
    sorted_pdata = sorted(sorted(pdata, key=lambda x: (x[1][0], int(x[1][1:]))), key=lambda x: (x[0][0], int(x[0][1:])))
    #Sorted by Zones
    final_sort = sorted(sorted(match_check(sorted_pdata, zp_pairing), key=lambda x: int(zp_pairing[x[0]].split()[1])), key=lambda x: zp_pairing[x[0]].split()[0][0], reverse=True)

    #Track Zones
    current_zone = list(zp_pairing.values())[0]

    #test print print("testing: ", final_sort[0][1][0])

    for direction in final_sort:
        if count == 0:
            #Write Headers Accordingly
            #Primary to Primary Headers
            if final_sort[0][1][0] != 'S':
                csv_writer.writerow(row_headers(['ZONE', 'PRIMARY START', 'PRIMARY END'], pstart_end(data)))
            #Primary to Secondary Headers
            else:
                csv_writer.writerow(row_headers(['ZONE', 'PRIMARY', 'SECONDARY'], pstart_end(data)))
            #csv_writer.writerow(headers) #Call row_headers function here, first check the first "end" starts with s, if so then this, else then that
            count += 1

        #Problem with Zone Here
        row_info = ['', direction[0], direction[1]]
        if zdata != None:
            for k,v in zp_pairing.items():
                if k == direction[0]:
                    row_info = [v, direction[0], direction[1]]
            add_on = [item for tuple in zip(pdata[direction]['Directions'], pdata[direction]['Image URL']) for item in tuple]
            row_info.extend(add_on)

            #Check to group by zone
            if row_info[0] != current_zone:
                csv_writer.writerow([])
                current_zone = row_info[0]

            csv_writer.writerow(row_info)

def z(zdata, data): #headers,
    '''Takes in the headers for the csv and the raw direction data to create a new csv
    file in Zone to Primary format.'''
    count = 0

    #Sorted by Alphanumerical Order
    sorted_zdata = sorted(sorted(zdata, key=lambda x: (x[1][0], int(x[1][1:]))), key=lambda x: (x[0].split()[0][0], int(x[0].split()[1])))
    #Sorted by Zones
    final_sort = sorted(sorted(sorted_zdata, key=lambda x: int(x[0].split()[1])), key=lambda x: x[0].split()[0], reverse=True)

    #Initialized Dictionary
    start_groups = dict()

    for direction in final_sort:
        if count == 0:
            #Write Headers Accordingly
            #Zone to Primary Headers
            if final_sort[0][1][0] != 'S':
                csv_writer.writerow(row_headers(['START ZONE', 'PRIMARY'], zstart_end(data)[0]))
            #Zone to Secondary headers
            else:
                csv_writer.writerow(row_headers(['START ZONE', 'SECONDARY'], zstart_end(data)[1]))
            count += 1

        #Check to group by Primary Start
        if direction[0] not in start_groups:
            if bool(start_groups) == False:
                start_groups = {direction[0]: 1}
            else:
                start_groups[direction[0]] = 1
                #Writes a blank row to separate groups/Replaces the black line in the spreadsheet
                csv_writer.writerow([])

        row_info = [direction[0], direction[1]]
        add_on = [item for tuple in zip(zdata[direction]['Directions'], zdata[direction]['Image URL']) for item in tuple]
        row_info.extend(add_on)
        csv_writer.writerow(row_info)


if __name__ == '__main__':
    arg_parser = create_arg_parser()
    parsed_args = arg_parser.parse_args(sys.argv[1:])

    #FILEPATH VERIFICATION: Input, Additional, and Output
    #Verify Input Filepath
    if Path(parsed_args.inputPath).exists():
        #Parse the original json
        with open(parsed_args.inputPath) as direction_data:
            data = json.load(direction_data)
    else:
        print("ERROR: Input directory does not exist.")
    #Verify Additional Filepath
    if parsed_args.additionalPath != None:
        if Path(parsed_args.additionalPath).exists():
            #Parse the original json
            with open(parsed_args.additionalPath) as zone_data:
                data2 = json.load(zone_data)
    else:
        data2 = None

    #Verify Output Filepath
    #Verifies the parent directory
    dir_check = "/".join(str(parsed_args.outputPath).split("/")[:-1])
    if Path(dir_check).is_dir():
        #Open a CSV file to write into & create the CSV writer object
        csv_file = open(parsed_args.outputPath,'w+') #w+ opens the file for writing & reading from it
        csv_writer = csv.writer(csv_file)

        #Check for format type
        if parsed_args.format == 'p': #Convert json files to primary to primary or primary to secondary format
            p(pstart_end(data), data, data2) #should be primary specific Function    , row_headers(rh_list, pstart_end(data))
            zone_data.close()

        elif parsed_args.format == 'z2p':
            z(zstart_end(data)[0], data) #--> 0 is primary dictionary

        else: #parsed_args.format == 'z2s':
            z(zstart_end(data)[1], data) #--> 1 is secondary dictionary
            #z(zstart_end(data), row_headers(zrh_list, zstart_end(data)), data)

        #Close the files that were opened
        direction_data.close()
        csv_file.close()

    else:
        print("ERROR: Output directory does not exist.")
