### NOTE This module provides utilities to handle paths in the vi-suite
#   TODO Add actual utilities. Currently we only have some paths
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

