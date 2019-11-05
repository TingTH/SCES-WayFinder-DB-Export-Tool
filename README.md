# wayfinder-db-export-tool

WAYFINDER DATABASE EXPORT TOOL: DOCUMENTATION & INSTRUCTION MANUAL

DATE: Wednesday, March 13, 2019.

--------------------
GUIDE ON HOW TO USE
--------------------
Command Line & Arguments:
Takes in the arguments "python3 json_to_csv.py input_file additional_file output_file --format type" and outputs a csv file.

      python3               --> Python version.

      json_to_csv.py        --> Name of the script.

      input_file            --> Any JSON file you're primarily using.
                                (Ex. primaryToprimary.json)

      additional_file       --> Any additional JSON file you need.
                                (Ex. A zone file called primaryTozone.json if you selected primary format)
                                NOTE: This can be left blank if you selected zone format.

      output_file           --> The directory file path + name you'd like your csv to be.
                                (Ex. /Users/username/Desktop/wayfinder-db-export-tool/Directions_ZoneToPrimary.csv)

      --format              --> Flag to indicate the next argument is the formatting type.

      type                  --> p for PrimaryToPrimary or PrimaryToSecondary or z for ZoneToPrimary

Example Command Line Runs
-------------------------
[Primary to Primary Format]

      python3 json_to_csv.py p2p.json p2z.json /Users/username/Desktop/folder/Directions_PrimaryToPrimary.csv --format p

[Primary to Secondary Format]

      python3 json_to_csv.py p2s.json p2z.json /Users/username/Desktop/folder/Directions_PrimaryToSecondary.csv --format p

[Zone to Primary Format]

      python3 json_to_csv.py z2ps.json /Users/username/Desktop/folder/Directions_ZoneToPrimary.csv --format z2p

[Zone to Secondary Format]

      python3 json_to_csv.py z2ps.json /Users/username/Desktop/folder/Directions_ZoneToSecondary.csv --format z2s
