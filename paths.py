### NOTE This module provides utilities to handle paths in the vi-suite
#   TODO Add actual utilities. Currently we only have some paths
#   NOTE We no longer needed the inspect-module so I removed it and its calls...
#   TODO Check if there are any errors arising from a path (not) ending on "\"
#        vi_func exports to vi_progress. => path_Python MUST NOT end on "\"...
import os

######## BEGIN: -DEFAULT PATHS- #############################################80#
### NOTE These are the shipped default paths. One might want to change them ...
#   start with the addon-path. It is our default __lib_path.
path_addon    = __lib_path = os.path.dirname(os.path.abspath(__file__))
#   paths to our external binaries / libraries. Ending them on a path-separator
#   allows to simply add filenames instead of os.path.join... which we still use ## explicit is better than implicit
path_EPFiles  = os.path.join(__lib_path,    "EPFiles",  "")
path_RadFiles = os.path.join(__lib_path,    "RadFiles", "")
path_OFFiles  = os.path.join(__lib_path,    "OFFiles",  "")
#   our replacement-python. Note that since we export this path added directly
#   into a string (for the vi-progress-bar) a trailing backslash would fail it.
path_Python   = os.path.join(__lib_path,    "Python"      )
# get fonts, images and models we want to use
path_Fonts    = os.path.join(__lib_path,    "Fonts",    "")
path_Images   = os.path.join(__lib_path,    "Images",   "")
######## END

######## BEGIN: -CONVENIENCE PATHS- #########################################80#
#   Currently, we only use NotoSans-Regular
path_Fonts_NotoSansRegular = os.path.join(path_Fonts, "NotoSans-Regular.ttf")
#   Databases for PV (default databases we ship)
path_EPFiles_PVdata       = os.path.join(path_EPFiles, 'PV_database.json')
path_EPFiles_PVdataSandia = os.path.join(path_EPFiles, 'SandiaPVdata.json')
######## END

