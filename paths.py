### NOTE This module provides utilities to handle paths in the vi-suite
#   TODO Add actual utilities. Currently we only have some paths
#   NOTE We no longer needed the inspect-module so I removed it and its calls...
#   TODO Check if there are any errors arising from a path (not) ending on "\"
#        vi_func exports to vi_progress. => path_Python MUST NOT end on "\"...
import os, sys

######## BEGIN: -DEFAULT PATHS- #############################################80#
### NOTE These are the shipped default paths. One might want to change them ...
#   start with the addon-path. It is our default __lib_path.
path_addon    = __lib_path = os.path.dirname(os.path.abspath(__file__))
#   NOTE with 1.65 GB the libraries we ship are quite heavy (the rest is 1.5 MB)
#        For ease of development we use thin copies by binding the libs relative
#        (we modified addon_utils to support extra addonpaths for rapid testing)
if os.path.basename(os.path.dirname(path_addon)).startswith("addons_test"):
    __lib_path = os.path.join(os.path.dirname(os.path.dirname(path_addon)),
                                            "addons_shared", "vi-suite06")
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

######## BEGIN: -CONVENIENCE VARIABLES- #####################################80#
addon_name = __name__.split(".")[0]# when imported __name__ is "addonname.paths"
######## END

######## BEGIN: -UTILITIES- #################################################80#
import bpy, addon_utils
# NOTE: while three times as long, this is much more powerfull than the original
def path_update():
    ### get the default paths (packed) NOTE: keys come from the prefs properties
    paths={"epbin"  : os.path.join(path_EPFiles,  sys.platform       ),
           "epweath": os.path.join(path_EPFiles,  'Weather',       ''), # currently not used ... at least not here
           "ofbin"  : os.path.join(path_OFFiles,  sys.platform, 'bin'), # NOTE: only occurrence
           "radlib" : os.path.join(path_RadFiles,               'lib'),
           "radbin" : os.path.join(path_RadFiles, sys.platform, 'bin'),
           "pybin"  : os.path.join(path_Python,   sys.platform, 'bin')}
    backup = dict(paths.items())
    ### update paths based on the addon-preferences (access to prefs is secured)
    vi_prefs = bpy.context.preferences.addons[addon_name].preferences # get pref
    # these are the paths we expect as base for relative paths in the preferences
    bases = [bpy.app.binary_path, *addon_utils.paths(),
        bpy.app.binary_path_python, *bpy.utils.script_paths()]
    bases_b = [ # these paths shouldn't be bases, but who knows ...
        bpy.utils.user_resource("CONFIG"), bpy.utils.user_resource("DATAFILES"),
        bpy.utils.user_resource("SCRIPTS"),bpy.utils.user_resource("AUTOSAVE"),
        bpy.utils.system_resource("DATAFILES"),
        bpy.utils.system_resource("SCRIPTS"),bpy.utils.system_resource("PYTHON")]
    ## make paths clean and absolute. Skips empty paths. Ignores matching files.
    for k in paths:
        pth = getattr(vi_prefs, k, "") # safely aquire paths from presets
        if not pth: continue# allows to do assignment in one place (end of loop)
        if os.path.isdir(bpy.path.abspath(pth)): # absolute & blendfile-relative
            apth = bpy.path.abspath(pth)
        elif pth.startswith("."): # path is relative, but not blendfile-relative
            for base in bases:  # check expected bases
                apth = os.path.realpath(os.path.join(base, pth))
                if os.path.isdir(apth): # only directories => don't use "exists"
                    break
            else:
                print("WARNING:",k,"-path:",pth)
                print("   Couldn't find path in standard directories:")
                print("   Searching in obscure directories ...")
                for base in bases_b:# check obscure bases
                    apth = os.path.realpath(os.path.join(base, pth))
                    if os.path.isdir(apth):
                        break
                else:
                    print("   ... Nope! Sorry. Was it a symlink? They're problematic.")
                    print("   ... Try prepending '../'s or parent-dirs to search above/below.")
                    print("   Skipping path (for now)")
                    continue # well, we tried. Go to the next path ...
        else:
            print("WARNING:",k,"-path:",pth)
            print("   Path didn't start with '.', nor was it found to be ...")
            print("   ... a directory absolute or relative to the blendfile!")
            continue
        # we got a matching path. let's set it ...
        paths[k] = apth
        print("Reading",k,"from",apth)
        if k=="radlib": # keep radiance default lib in case of missing items
            paths["radlib"] = os.pathsep.join((apth, backup["radlib"]))
    ### setup environment paths
    PATH = os.environ["PATH"]
    # Radiance needs special care ... so start with radiance; the rest is simple
    if paths["radlib"] not in os.environ.get('RAYPATH',""):                         # Radiance libraries
        os.environ["RAYPATH"] = paths["radlib"]
    if paths["radbin"] not in PATH:                                                 # Radiance binary
        if backup["radbin"]in PATH:# NOTE: why do we replace the path only here?
            PATH = PATH.replace(backup["radbin"], paths["radbin"]) # replace bin
        else: PATH = os.pathsep.join((PATH, paths["radbin"]))      # or just add
    if paths["epbin"]  not in PATH: PATH = os.pathsep.join((PATH, paths["epbin"]))  # EnergyPlus
    if paths["ofbin"]  not in PATH: PATH = os.pathsep.join((PATH, paths["ofbin"]))  # OpenFOAM
    if paths["ofbin"]  not in sys.path:           sys.path.append(paths["ofbin"])   # OpenFOAM
    if paths["pybin"]  not in PATH: PATH = os.pathsep.join((PATH, paths["pybin"]))  # Python
    if os.environ["PATH"]  != PATH: os.environ["PATH"] = PATH                       ## update path variable
######## END
