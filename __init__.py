# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name": "VI-Suite",
    "author": "Ryan Southall",
    "version": (0, 6, 0),
    "blender": (2, 83),
    "api":"",
    "location": "Node Editor & 3D View > Properties Panel",
    "description": "Radiance/EnergyPlus exporter and results visualiser",
    "warning": "This is a beta script. Some functionality is buggy",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Import-Export"}

if "bpy" in locals():
    import imp
    imp.reload(vi_operators)
    imp.reload(vi_ui)
    imp.reload(vi_func)
    imp.reload(vi_node)
    imp.reload(envi_mat)
else:
    import sys, os, inspect
    evsep = {'linux': ':', 'darwin': ':', 'win32': ';'}
    addonpath = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

    if sys.platform in ('darwin', 'linux', 'win32'):      
        if os.environ.get('PYTHONPATH'):
            if os.path.join(addonpath, 'Python', sys.platform) not in os.environ['PYTHONPATH']:
                os.environ['PYTHONPATH'] += os.path.join(addonpath, 'Python', sys.platform)
        else:
            os.environ['PYTHONPATH'] = os.path.join(addonpath, 'Python', sys.platform)
               
        sys.path.append(os.path.join(addonpath, 'Python', sys.platform))   
         
    from .vi_node import vinode_categories, envinode_categories, envimatnode_categories, ViNetwork, No_Loc, So_Vi_Loc, ViSPNode, ViWRNode, ViSVFNode, So_Vi_Res, ViSSNode
    from .vi_node import No_Li_Geo, No_Li_Con, No_Li_Sen, So_Li_Geo, So_Li_Con, No_Text, So_Text, No_CSV
    from .vi_node import No_Li_Im, So_Li_Im, No_Li_Gl, No_Li_Fc 
    from .vi_node import No_Li_Sim, No_ASC_Import
    from .vi_node import No_En_Net_Zone, No_En_Net_Occ, So_En_Net_Eq, So_En_Net_Inf, So_En_Net_Hvac, No_En_Net_Hvac
    from .vi_node import No_En_Geo, So_En_Geo, EnViNetwork, EnViMatNetwork, No_En_Con, So_En_Con
    from .vi_node import No_En_Mat_Con, No_En_Mat_Sc, No_En_Mat_Sh, No_En_Mat_ShC, No_En_Mat_Bl, No_En_Mat_Op, No_En_Mat_Tr, No_En_Mat_Gas, So_En_Mat_Ou, So_En_Mat_Op, No_En_Mat_Sched
    from .vi_node import So_En_Net_Occ, So_En_Sched, No_En_Net_Sched, No_En_Sim, No_Vi_Chart, So_En_Res, So_En_ResU, So_En_Net_TSched, No_En_Net_Eq, No_En_Net_Inf
    from .vi_node import No_En_Net_TC, No_En_Net_SFlow, No_En_Net_SSFlow, So_En_Net_SFlow, So_En_Net_SSFlow, So_En_Mat_PV, No_En_Mat_PV
    from .vi_node import So_En_Mat_PVG, No_En_Mat_PVG, No_Vi_Metrics, So_En_Mat_Tr, So_En_Mat_Gas, So_En_Net_Bound, No_En_Net_ACon, No_En_Net_Ext
    from .vi_node import No_En_Net_EMSZone, No_En_Net_Prog, So_En_Net_Act, So_En_Net_Sense
    from .vi_func import iprop, bprop, eprop, fprop, sprop, fvprop, sunpath1
    from .vi_func import lividisplay
    from .livi_func import rtpoints, lhcalcapply, udidacalcapply, compcalcapply, basiccalcapply, radmat, radbsdf, retsv
    from .envi_func import enunits, enpunits, enparametric, resnameunits, aresnameunits
    #    from .flovi_func import fvmat, ret_fvbp_menu, ret_fvbu_menu, ret_fvbnut_menu, ret_fvbnutilda_menu, ret_fvbk_menu, ret_fvbepsilon_menu, ret_fvbomega_menu, ret_fvbt_menu, ret_fvba_menu, ret_fvbprgh_menu
    #    from .vi_display import setcols

    from .vi_operators import NODE_OT_WindRose, NODE_OT_SVF, NODE_OT_En_Con, NODE_OT_En_Sim, NODE_OT_TextUpdate
    from .vi_operators import MAT_EnVi_Node, NODE_OT_Shadow, NODE_OT_CSV, NODE_OT_ASCImport, NODE_OT_FileSelect, NODE_OT_HdrSelect
    from .vi_operators import NODE_OT_Li_Geo, NODE_OT_Li_Con, NODE_OT_Li_Pre, NODE_OT_Li_Sim
    from .vi_operators import NODE_OT_Li_Im, NODE_OT_Li_Gl, NODE_OT_Li_Fc, NODE_OT_En_Geo, OBJECT_OT_VIGridify2, NODE_OT_En_UV
    from .vi_operators import NODE_OT_Chart, NODE_OT_En_PVA, NODE_OT_En_PVS, NODE_OT_En_LayS, NODE_OT_En_ConS, TREE_OT_goto_mat, TREE_OT_goto_group
    from .vi_operators import OBJECT_OT_Li_GBSDF, OBJECT_OT_GOct, MATERIAL_OT_Li_LBSDF, MATERIAL_OT_Li_SBSDF, MATERIAL_OT_Li_DBSDF
    from .vi_display import VIEW3D_OT_WRDisplay, VIEW3D_OT_SVFDisplay, VIEW3D_OT_Li_BD, VIEW3D_OT_Li_DBSDF, VIEW3D_OT_SSDisplay, NODE_OT_SunPath
    from .vi_display import script_update, col_update, leg_update, w_update, t_update, livires_update, e_update
    from .vi_ui import VI_PT_3D, VI_PT_Mat, VI_PT_Ob, VI_PT_Gridify, TREE_PT_envim, TREE_PT_envin, TREE_PT_vi
    from .vi_dicts import colours

import bpy, nodeitems_utils
from bpy.app.handlers import persistent
from bpy.props import StringProperty, EnumProperty, IntProperty, FloatProperty
from bpy.types import AddonPreferences

def return_preferences():
    return bpy.context.preferences.addons[__name__].preferences
    
def abspath(self, context):
    if self.radbin != bpy.path.abspath(self.radbin):
        self.radbin = bpy.path.abspath(self.radbin)
    if self.radlib != bpy.path.abspath(self.radlib):
        self.radlib = bpy.path.abspath(self.radlib)
    if self.epbin != bpy.path.abspath(self.epbin):
        self.epbin = bpy.path.abspath(self.epbin)
    if self.epweath != bpy.path.abspath(self.epweath):
        self.epweath = bpy.path.abspath(self.epweath)
    if self.ofbin != bpy.path.abspath(self.ofbin):
        self.ofbin = bpy.path.abspath(self.ofbin)
    if self.oflib != bpy.path.abspath(self.oflib):
        self.oflib = bpy.path.abspath(self.oflib)  
    if self.ofetc != bpy.path.abspath(self.ofetc):
        self.ofetc = bpy.path.abspath(self.ofetc)

def flovi_levels(self, context):
    if self.flovi_slmin > self.flovi_slmax:
       self.flovi_slmin -= 1 
       
def unititems(self, context):  
    try:
        scene = context.scene
        svp = scene.vi_params
        
        if svp['liparams']['unit'] == 'W/m2 (f)':
            return [('firradm2', 'W/m2', 'Full spectrum irradiance per metre square'),
                    ('firrad', 'W', 'Full spectrum irradiance')]
        elif svp['liparams']['unit'] == 'Lux':
            return [('illu', 'Lux', 'Illuminance'), 
                    ('virradm2', 'Watts/m2', 'Visible spectrum illuminance'),
                    ('virrad', 'Watts', 'Visible spectrum illuminance')]
        elif svp['liparams']['unit'] == 'lxh':
            return [('illuh', 'Lux-hours', 'Lux-hours'), ('virradh', 'kWh (v)', 'kilo-Watt hours (visible)'), ('virradhm2', 'kWh/m2 (v)', 'kilo-Watt hours per square metre (visible)')]
        elif svp['liparams']['unit'] == 'kWh (f)':
            return [('firradh', 'kWh (f)', 'kilo-Watt hours (solar spectrum)'), 
                    ('firradhm2', 'kWh/m2 (f)', 'kilo-Watt hours per square metre (solar spectrum)')]
        elif svp['liparams']['unit'] == 'DA (%)':
            return[("da", "DA", "Daylight Autonomy"), 
                   ("sda", "sDA", "Spatial Daylight Autonomy"), 
                   ("udilow", "UDI (low)", "Useful daylight illuminance (low)"), 
                   ("udisup", "UDI (supp)", "Useful daylight illuminance (supplemented)"), 
                   ("udiauto", "UDI (auto)", "Useful daylight illuminance (autonomous)"), 
                   ("udihi", "UDI (high)", "Useful daylight illuminance (high)"), 
                   ("ase", "ASE", "Annual Sunlight Exposure"), 
                   ("maxlux", "Lux level (max)", "Maximum lux level"), 
                   ("avelux", "Lux level (ave)", "Average lux level"), 
                   ("minlux", "Lux level (min)", "Minimum lux level")]
        elif svp['liparams']['unit'] == '% Sunlit':
            return [('sm', '% Sunlit', '% of time sunlit')]
        elif svp['liparams']['unit'] == 'SVF (%)':
            return [('svf', 'SVF (%)', '% of sky visible')]
        else:
            return [('None', 'None','None' )]
    except:
        return [('None', 'None','None' )]   
    
def bsdf_direcs(self, context):
    try:
        return [tuple(i) for i in context.scene.vi_params['liparams']['bsdf_direcs']]
    except:
        return [('None', 'None', 'None')]
    
class VIPreferences(AddonPreferences):
    bl_idname = __name__    
    radbin: StringProperty(name = '', description = 'Radiance binary directory location', default = '', subtype='DIR_PATH', update=abspath)
    radlib: StringProperty(name = '', description = 'Radiance library directory location', default = '', subtype='DIR_PATH', update=abspath)
    epbin: StringProperty(name = '', description = 'EnergyPlus binary directory location', default = '', subtype='DIR_PATH', update=abspath)
    epweath: StringProperty(name = '', description = 'EnergyPlus weather directory location', default = '', subtype='DIR_PATH', update=abspath)
    ofbin: StringProperty(name = '', description = 'OpenFOAM binary directory location', default = '', subtype='DIR_PATH', update=abspath)
    oflib: StringProperty(name = '', description = 'OpenFOAM library directory location', default = '', subtype='DIR_PATH', update=abspath)
    ofetc: StringProperty(name = '', description = 'OpenFOAM letc directory location', default = '', subtype='DIR_PATH', update=abspath)
    ui_dict = {"Radiance bin directory:": 'radbin', "Radiance lib directory:": 'radlib', "EnergyPlus bin directory:": 'epbin',
               "EnergyPlus weather directory:": 'epweath', 'OpenFOAM bin directory': 'ofbin', 'OpenFOAM lib directory': 'oflib', 'OpenFOAM etc directory': 'ofetc'}

    def draw(self, context):
        layout = self.layout 
        
        for entry in self.ui_dict:
            row = layout.row()
            row.label(text=entry)   
            row.prop(self, self.ui_dict[entry])

class VI_Params_Scene(bpy.types.PropertyGroup): 
    vipath: sprop("VI Path", "Path to files included with the VI-Suite ", 1024, addonpath) 
    solday: IntProperty(name = "", description = "Day of year", min = 1, max = 365, default = 1, update=sunpath1)
    solhour: bpy.props.FloatProperty(name = "", description = "Time of day", subtype='TIME', unit='TIME', min = 0, max = 24, default = 12, update=sunpath1)
    sp_hour_dash: fvprop(4, "",'Main colour of the hour lines', [1.0, 0.0, 0.0, 0.0], 'COLOR', 0, 1) 
    sp_hour_main: fvprop(4, "",'Dash colour of the hour lines', [1.0, 1.0, 0.0, 1.0], 'COLOR', 0, 1)
    sp_season_main: fvprop(4, "",'Main colour of the season lines', [1.0, 0.0, 0.0, 1.0], 'COLOR', 0, 1)
    sp_season_dash: fvprop(4, "",'Dash colour of the season lines', [1.0, 1.0, 1.0, 0.0], 'COLOR', 0, 1)
    sp_sun_colour: fvprop(4, "",'Sun colour', [1.0, 1.0, 0.0, 1.0], 'COLOR', 0, 1)
    sp_globe_colour: fvprop(4, "",'Sun colour', [0.0, 0.0, 1.0, 0.1], 'COLOR', 0, 1)
    sp_sun_angle: FloatProperty(name = "", description = "Sun size", min = 0, max = 1, default = 0.01, update=sunpath1)
    sp_sun_size: iprop("",'Sun size', 1, 50, 10)
    sp_sun_strength: FloatProperty(name = "", description = "Sun strength", min = 0, max = 100, default = 0.1, update=sunpath1)
    sp_season_dash_ratio: fprop("", "Ratio of line to dash of season lines", 0, 5, 0)
    sp_hour_dash_ratio: fprop("", "Ratio of line to dash of hour lines", -1, 1, 0.5)
    sp_hour_dash_density: fprop("", "Ratio of line to dash of hour lines", 0, 5, 1)
    sp_line_width: iprop("", "Sun path line width", 0, 50, 2)
    latitude: FloatProperty(name = "", description = "Site decimal latitude (N is positive)", 
                            min = -89.99, max = 89.99, default = 52.0, update = sunpath1)
    longitude: FloatProperty(name = "", description = "Site decimal longitude (E is positive)", 
                             min = -180, max = 180, default = 0.0, update = sunpath1)
    sp_suns: EnumProperty(items = [('0', 'Single', 'Single sun'), 
                                   ('1', 'Monthly', 'Monthly sun for chosen time'), 
                                   ('2', 'Hourly', 'Hourly sun for chosen date')], 
                                    name = '', description = 'Sunpath sun type', default = '0', update=sunpath1)
    sp_sst: FloatProperty(name = "", description = "Sun strength", min = 0, max = 100, default = 0.1, update=sunpath1)
    sp_ssi: FloatProperty(name = "", description = "Sun size", min = 0, max = 1, default = 0.01, update=sunpath1)
    sp_sd: IntProperty(name = "", description = "Day of year", min = 1, max = 365, default = 1, options={'ANIMATABLE'}, update=sunpath1)
    sp_sh: FloatProperty(name = "", description = "Time of day", subtype='TIME', unit='TIME', 
                         min = 0, max = 24, default = 12, options={'ANIMATABLE'}, update=sunpath1)
    sp_hd: bprop("", "",0)
    sp_up: bprop("", "",0)
    sp_td: bprop("", "",0)
    li_disp_panel: iprop("Display Panel", "Shows the Display Panel", -1, 2, 0)
    li_disp_menu: EnumProperty(items = unititems, name = "", description = "BLiVi metric selection", update = livires_update)  
    vi_display_rp_fsh: fvprop(4, "", "Font shadow", [0.0, 0.0, 0.0, 1.0], 'COLOR', 0, 1)
    vi_display_rp_fs: iprop("", "Point result font size", 4, 24, 24)
    vi_display_rp_fc: fvprop(4, "", "Font colour", [0.0, 0.0, 0.0, 1.0], 'COLOR', 0, 1)
    vi_display_rp_sh: bprop("", "Toggle for font shadow display",  False)
    vi_display: bprop("", "Toggle result display",  False)
    vi_disp_3d: bprop("VI 3D display", "Boolean for 3D results display",  False)
    vi_leg_unit: sprop("", "Legend unit", 1024, "")
    vi_leg_max: bpy.props.FloatProperty(name = "", description = "Legend maximum", min = 0, max = 1000000, default = 1000, update=leg_update)
    vi_leg_min: bpy.props.FloatProperty(name = "", description = "Legend minimum", min = 0, max = 1000000, default = 0, update=leg_update)
    vi_leg_col: EnumProperty(items = colours, name = "", description = "Legend scale", default = 'rainbow', update=col_update)
    vi_leg_levels: IntProperty(name = "", description = "Day of year", min = 2, max = 100, default = 20, update=leg_update)
    vi_leg_scale: EnumProperty(items = [('0', 'Linear', 'Linear scale'), ('1', 'Log', 'Logarithmic scale')], name = "", description = "Legend scale", default = '0', update=leg_update)    
    wind_type: eprop([("0", "Speed", "Wind Speed (m/s)"), ("1", "Direction", "Wind Direction (deg. from North)")], "", "Wind metric", "0")
    vi_disp_trans: bpy.props.FloatProperty(name = "", description = "Sensing material transparency", min = 0, max = 1, default = 1, update = t_update)
    vi_disp_wire: bpy.props.BoolProperty(name = "", description = "Draw wire frame", default = 0, update=w_update)
    vi_disp_mat: bpy.props.BoolProperty(name = "", description = "Turn on/off result material emission", default = 0, update=col_update)
    vi_disp_ems: bpy.props.FloatProperty(name = "", description = "Emissive strength", default = 1, min = 0, update=col_update)
    vi_scatt_max: EnumProperty(items = [('0', 'Data', 'Get maximum from data'), ('1', 'Value', 'Specify maximum value')], 
                                            name = "", description = "Set maximum value", default = '0')
    vi_scatt_min: EnumProperty(items = [('0', 'Data', 'Get minimum from data'), ('1', 'Value', 'Specify minimum value')], 
                                            name = "", description = "Set minimum value", default = '0')
    vi_scatt_max_val: fprop("",'Maximum value', 1, 30, 20)
    vi_scatt_min_val: fprop("",'Minimum value', 0, 10, 0)
    vi_scatt_col: EnumProperty(items = colours, name = "", description = "Scatter colour", default = 'rainbow')
    vi_disp_refresh: bprop("", "Refresh display",  False)
    vi_res_mod: sprop("", "Result modifier", 1024, "")
    vi_res_process: EnumProperty(items = [("0", "None", ""), ("1", "Modifier", ""), ("2", "Script", "")], name = "", description = "Specify the type of data processing", default = "0", update = script_update)
    script_file: StringProperty(description="Text file to show", update = script_update)
    ss_disp_panel: iprop("Display Panel", "Shows the Display Panel", -1, 2, 0)
    vi_display_rp: bprop("", "", False)
    vi_display_rp_off: fprop("", "Surface offset for number display", 0, 5, 0.001)
    vi_display_sel_only: bprop("", "", False)
    vi_display_vis_only: bprop("", "", False)
    vi_disp_3dlevel: FloatProperty(name = "", description = "Level of 3D result plane extrusion", min = 0, max = 500, default = 0, update = e_update)
    vi_bsdf_direc: EnumProperty(items = bsdf_direcs, name = "", description = "BSDf display direction") 
    vi_bsdfleg_max: bpy.props.FloatProperty(name = "", description = "Legend maximum", min = 0, max = 1000000, default = 100)
    vi_bsdfleg_min: bpy.props.FloatProperty(name = "", description = "Legend minimum", min = 0, max = 1000000, default = 0)
    vi_bsdfleg_scale: EnumProperty(items = [('0', 'Linear', 'Linear scale'), ('1', 'Log', 'Logarithmic scale')], name = "", description = "Legend scale", default = '0')    
    en_disp_type: EnumProperty(items = enparametric, name = "", description = "Type of EnVi display") 
    resas_disp: bprop("", "", False) 
    reszt_disp: bprop("", "", False) 
    reszh_disp: bprop("", "", False) 
    resaa_disp: bprop("", "", False) 
    
    (resaa_disp, resaws_disp, resawd_disp, resah_disp, resas_disp, reszt_disp, reszh_disp, reszhw_disp, reszcw_disp, reszsg_disp, reszppd_disp, 
     reszpmv_disp, resvls_disp, resvmh_disp, resim_disp, resiach_disp, reszco_disp, resihl_disp, reszlf_disp, reszof_disp, resmrt_disp,
     resocc_disp, resh_disp, resfhb_disp, reszahw_disp, reszacw_disp, reshrhw_disp, restcvf_disp, restcmf_disp, restcot_disp, restchl_disp, 
     restchg_disp, restcv_disp, restcm_disp, resldp_disp, resoeg_disp, respve_disp, respvw_disp, respveff_disp, respvt_disp) = resnameunits() 
     
    (resazmaxt_disp, resazmint_disp, resazavet_disp, 
     resazmaxhw_disp, resazminhw_disp, resazavehw_disp, 
     resazth_disp, resazthm_disp, 
     resazmaxcw_disp, resazmincw_disp, resazavecw_disp, 
     resaztc_disp, resaztcm_disp, 
     resazmaxco_disp, resazaveco_disp, resazminco_disp, 
     resazlmaxf_disp, resazlminf_disp, resazlavef_disp,
     resazmaxshg_disp, resazminshg_disp, resazaveshg_disp,
     resaztshg_disp, resaztshgm_disp)  = aresnameunits() 
#    envi_flink: bprop("", "Associate flow results with the nearest object", False)
    
class VI_Params_Object(bpy.types.PropertyGroup): 
    # VI-Suite object definitions
    vi_type: eprop([("0", "None", "Not a VI-Suite specific object"), 
                    ("1", "EnVi Surface", "Designates an EnVi surface"), 
                    ("2", "CFD Domain", "Specifies an OpenFoam BlockMesh"), 
                    ("3", "CFD Geometry", "Specifies an OpenFoam geometry"),
                    ("4", "Light Array", "Specifies a LiVi lighting array"), 
                    ("5", "Complex Fenestration", "Specifies complex fenestration for BSDF generation")], 
                    "", "Specify the type of VI-Suite zone", "0")

    # LiVi object properties
    livi_merr: bprop("LiVi simple mesh export", "Boolean for simple mesh export", False)
    ies_name: bpy.props.StringProperty(name="", description="Name of the IES file", default="", subtype="FILE_PATH")
    ies_strength: fprop("", "Strength of IES lamp", 0, 1, 1)
    ies_unit: eprop([("m", "Meters", ""), ("c", "Centimeters", ""), ("f", "Feet", ""), ("i", "Inches", "")], "", "Specify the IES file measurement unit", "m")
    ies_colmenu: eprop([("0", "RGB", ""), ("1", "Temperature", "")], "", "Specify the IES colour type", "0")
    ies_rgb: fvprop(3, "",'IES Colour', [1.0, 1.0, 1.0], 'COLOR', 0, 1)
    ies_ct: iprop("", "Colour temperature in Kelven", 0, 12000, 4700)
    licalc: bprop("", "", False)
    limerr: bprop("", "", False)
    manip: bprop("", "", False) 
    bsdf_proxy: bprop("", "", False)
    compcalcapply = compcalcapply    
    basiccalcapply = basiccalcapply 
    rtpoints = rtpoints
    udidacalcapply = udidacalcapply
    lividisplay = lividisplay
    lhcalcapply = lhcalcapply
    li_bsdf_direc: EnumProperty(items = [('+b -f', 'Backwards', 'Backwards BSDF'), 
                                         ('+f -b', 'Forwards', 'Forwards BSDF'), 
                                         ('+b +f', 'Bi-directional', 'Bi-directional BSDF')], name = '', description = 'BSDF direction', default = '+b -f')
    li_bsdf_proxy: bprop("", "Include proxy geometry in the BSDF", False)
    li_bsdf_tensor: EnumProperty(items = [(' ', 'Klems', 'Uniform Klems sample'), 
                                          ('-t3', 'Symmentric', 'Symmetric Tensor BSDF'), 
                                          ('-t4', 'Assymmetric', 'Asymmetric Tensor BSDF')], name = '', description = 'BSDF tensor', default = ' ')
    li_bsdf_res: EnumProperty(items = [('1', '2x2', '2x2 sampling resolution'), 
                                       ('2', '4x4', '4x4 sampling resolution'), 
                                       ('3', '8x8', '8x8 sampling resolution'), 
                                       ('4', '16x16', '16x16 sampling resolution'), 
                                       ('5', '32x32', '32x32 sampling resolution'), 
                                       ('6', '64x64', '64x64 sampling resolution'), 
                                       ('7', '128x128', '128x128 sampling resolution')], name = '', description = 'BSDF resolution', default = '4')
    li_bsdf_tsamp: IntProperty(name = '', description = 'Tensor samples per region', min = 1, max = 10000, default = 4)
    li_bsdf_ksamp: IntProperty(name = '', description = 'Klem samples', min = 1, default = 2000)
    li_bsdf_rcparam: sprop("", "rcontrib parameters", 1024, "")
    bsdf_running: bprop("", "Running BSDF calculation", False)
    radbsdf = radbsdf
    retsv = retsv
    envi_type: eprop([("0", "Construction", "Thermal Construction"), ("1", "Shading", "Shading Object"), ("2", "Chimney", "Thermal Chimney")], "EnVi surface type", "Specify the EnVi surface type", "0")
    envi_hab: bprop("", "Flag to tell EnVi this is a habitable zone", False)
    flovi_fl: IntProperty(name = '', description = 'SnappyHexMesh object features levels', min = 1, max = 20, default = 4) 
    flovi_slmax: IntProperty(name = '', description = 'SnappyHexMesh surface maximum levels', min = 1, max = 20, default = 4, update=flovi_levels)   
    flovi_slmin: IntProperty(name = '', description = 'SnappyHexMesh surface minimum levels', min = 1, max = 20, default = 3, update=flovi_levels)     
    flovi_sl: IntProperty(name = '', description = 'SnappyHexMesh surface minimum levels', min = 0, max = 20, default = 3)

class VI_Params_Material(bpy.types.PropertyGroup):
    radtex: bprop("", "Flag to signify whether the material has a texture associated with it", False)
    radnorm: bprop("", "Flag to signify whether the material has a normal map associated with it", False)
    ns: fprop("", "Strength of normal effect", 0, 5, 1)
    nu: fvprop(3, '', 'Image up vector', [0, 0, 1], 'VELOCITY', -1, 1)
    nside: fvprop(3, '', 'Image side vector', [-1, 0, 0], 'VELOCITY', -1, 1)
    radcolour: fvprop(3, "Material Colour",'Material Colour', [0.8, 0.8, 0.8], 'COLOR', 0, 1)
    radcolmenu: eprop([("0", "RGB", "Specify colour temperature"), ("1", "Temperature", "Specify colour temperature")], "Colour type:", "Specify the colour input", "0")
    radrough: fprop("Roughness", "Material roughness", 0, 1, 0.1)
    radspec: fprop("Specularity", "Material specular reflection", 0, 1, 0.0)
    radtrans: fprop("Transmission", "Material diffuse transmission", 0, 1, 0.1)
    radtranspec: fprop("Trans spec", "Material specular transmission", 0, 1, 0.1)
    radior: fprop("IOR", "Material index of refractionn", 0, 5, 1.5)
    radct: iprop("Temperature (K)", "Colour temperature in Kelven", 0, 12000, 4700)
    radintensity: fprop("Intensity", u"Material radiance (W/sr/m\u00b2)", 0, 100, 1)   
    radfile: sprop("", "Radiance file material description", 1024, "")
    vi_shadow: bprop("VI Shadow", "Flag to signify whether the material represents a VI Shadow sensing surface", False)
    livi_sense: bprop("LiVi Sensor", "Flag to signify whether the material represents a LiVi sensing surface", False)
    livi_compliance: bprop("LiVi Compliance Surface", "Flag to signify whether the material represents a LiVi compliance surface", False)
    gl_roof: bprop("Glazed Roof", "Flag to signify whether the communal area has a glazed roof", False)
    hspacetype = [('0', 'Public/Staff', 'Public/Staff area'), ('1', 'Patient', 'Patient area')]
    rspacetype = [('0', "Kitchen", "Kitchen space"), ('1', "Living/Dining/Study", "Living/Dining/Study area"), ('2', "Communal", "Non-residential or communal area")]
    respacetype = [('0', "Sales", "Sales space"), ('1', "Occupied", "Occupied space")]
    lespacetype = [('0', "Healthcare", "Healthcare space"), ('1', "Other", "Other space")]
    
    hspacemenu: eprop(hspacetype, "", "Type of healthcare space", '0')
    brspacemenu: eprop(rspacetype, "", "Type of residential space", '0')
    crspacemenu: eprop(rspacetype[:2], "", "Type of residential space", '0')
    respacemenu: eprop(respacetype, "", "Type of retail space", '0')
    lespacemenu: eprop(lespacetype, "", "Type of space", '0')
    BSDF: bprop("", "Flag to signify a BSDF material", False)
    mattype: eprop([("0", "Geometry", "Geometry"), ("1", 'Light sensor', "LiVi sensing material".format(u'\u00b3')), ("2", "FloVi boundary", 'FloVi blockmesh boundary')], "", "VI-Suite material type", "0")
    envi_nodes: bpy.props.PointerProperty(type = bpy.types.NodeTree)
    envi_type: sprop("", "EnVi Material type", 64, "None")
    envi_shading: bprop("", "Flag to signify whether the material contains shading elements", False)
    envi_boundary: bprop("", "Flag to signify whether the material represents a zone boundary", False)
    envi_export: bprop("Material Export", "Flag to tell EnVi to export this material", False) 
    pport: bprop("", "Flag to signify whether the material represents a Photon Port", False)
    radtypes = [('0', 'Plastic', 'Plastic Radiance material'), ('1', 'Glass', 'Glass Radiance material'), ('2', 'Dielectric', 'Dialectric Radiance material'),
                ('3', 'Translucent', 'Translucent Radiance material'), ('4', 'Mirror', 'Mirror Radiance material'), ('5', 'Light', 'Emission Radiance material'),
                ('6', 'Metal', 'Metal Radiance material'), ('7', 'Anti-matter', 'Antimatter Radiance material'), ('8', 'BSDF', 'BSDF Radiance material'), ('9', 'Custom', 'Custom Radiance material')]
    radmatmenu: eprop(radtypes, "", "Type of Radiance material", '0')
    radmatdict = {'0': ['radcolour', 0, 'radrough', 'radspec'], '1': ['radcolour'], '2': ['radcolour', 0, 'radior'], '3': ['radcolour', 0, 'radspec', 'radrough', 0, 'radtrans',  'radtranspec'], '4': ['radcolour'], 
    '5': ['radcolmenu', 0, 'radcolour', 0, 'radct',  0, 'radintensity'], '6': ['radcolour', 0, 'radrough', 'radspec'], '7': [], '8': [], '9': []}
    radmat = radmat
    li_bsdf_proxy_depth: fprop("", "Depth of proxy geometry", -10, 10, 0)
    
class VI_Params_Collection(bpy.types.PropertyGroup):
    envi_zone: bprop("EnVi Zone", "Flag to tell EnVi to export this collection", False) 
    envi_geo: bprop("EnVi Zone", "Flag to tell EnVi this is a geometry collection", False)
    envi_hab: bprop("", "Flag to tell EnVi this is a habitable zone", False)
    
@persistent
def update_chart_node(dummy):
    try:
        for ng in [ng for ng in bpy.data.node_groups if ng.bl_idname == 'ViN']:
            [node.update() for node in ng.nodes if node.bl_label == 'VI Chart']
    except Exception as e:
        print('Chart node update failure:', e)

@persistent        
def update_dir(dummy):
    if bpy.context.scene.vi_params.get('viparams'):
        fp = bpy.data.filepath
        bpy.context.scene.vi_params['viparams']['newdir'] = os.path.join(os.path.dirname(fp), os.path.splitext(os.path.basename(fp))[0])
               
@persistent
def display_off(dummy):
    if bpy.context.scene.vi_params.get('viparams') and bpy.context.scene.vi_params['viparams'].get('vidisp'):
        
        ifdict = {'sspanel': 'ss', 'lipanel': 'li', 'enpanel': 'en', 'bsdf_panel': 'bsdf'}
        if bpy.context.scene.vi_params['viparams']['vidisp'] in ifdict:
            bpy.context.scene.vi_params['viparams']['vidisp'] = ifdict[bpy.context.scene.vi_params['viparams']['vidisp']]
        bpy.context.scene.vi_params.vi_display = 0
                    
@persistent
def select_nodetree(dummy): 
    for space in getViEditorSpaces():
        vings = [ng for ng in bpy.data.node_groups if ng.bl_idname == 'ViN']
        if vings:
            space.node_tree = vings[0]
            space.node_tree.use_fake_user = 1

    for space in getEnViEditorSpaces():
        envings = [ng for ng in bpy.data.node_groups if ng.bl_idname == 'EnViN']
        if envings:
            space.node_tree = envings[0]
            
    for space in getEnViMaterialSpaces():
        try:
            if space.node_tree != bpy.context.active_object.active_material.vi_params.envi_nodes:
                envings = [ng for ng in bpy.data.node_groups if ng.bl_idname == 'EnViMatN' and ng == bpy.context.active_object.active_material.vi_params.envi_nodes]
                if envings:
                    space.node_tree = envings[0]
        except Exception as e:
            print(e)
        
bpy.app.handlers.depsgraph_update_post.append(select_nodetree)
        
def getViEditorSpaces():
    if bpy.context.screen:
        return [area.spaces.active for area in bpy.context.screen.areas if area and area.type == "NODE_EDITOR" and area.spaces.active.tree_type == "ViN" and not area.spaces.active.edit_tree]
    else:
        return []
        
def getEnViEditorSpaces():
    if bpy.context.screen:
        return [area.spaces.active for area in bpy.context.screen.areas if area and area.type == "NODE_EDITOR" and area.spaces.active.tree_type == "EnViN" and not area.spaces.active.edit_tree]
    else:
        return []

def getEnViMaterialSpaces():
    if bpy.context.screen:        
        return [area.spaces.active for area in bpy.context.screen.areas if area and area.type == "NODE_EDITOR" and area.spaces.active.tree_type == "EnViMatN"]
    else:
        return []
        

def path_update():
    vi_prefs = bpy.context.preferences.addons[__name__].preferences
    epdir = vi_prefs.epbin if vi_prefs and vi_prefs.epbin and os.path.isdir(vi_prefs.epbin) else os.path.join('{}'.format(addonpath), 'EPFiles', str(sys.platform))
    radldir = vi_prefs.radlib if vi_prefs and os.path.isdir(vi_prefs.radlib) else os.path.join('{}'.format(addonpath), 'RadFiles', 'lib')
    radbdir = vi_prefs.radbin if vi_prefs and os.path.isdir(vi_prefs.radbin) else os.path.join('{}'.format(addonpath), 'RadFiles', str(sys.platform), 'bin') 
    ofbdir = vi_prefs.ofbin if vi_prefs and os.path.isdir(vi_prefs.ofbin) else os.path.join('{}'.format(addonpath), 'OFFiles', 'bin') 
    ofldir = vi_prefs.oflib if vi_prefs and os.path.isdir(vi_prefs.oflib) else os.path.join('{}'.format(addonpath), 'OFFiles', 'lib')
    ofedir = vi_prefs.ofetc if vi_prefs and os.path.isdir(vi_prefs.ofetc) else os.path.join('{}'.format(addonpath), 'OFFiles')
    os.environ["PATH"] += "{0}{1}".format(evsep[str(sys.platform)], os.path.dirname(bpy.app.binary_path))

    if not os.environ.get('RAYPATH') or radldir not in os.environ['RAYPATH'] or radbdir not in os.environ['PATH']  or epdir not in os.environ['PATH']:
        if vi_prefs and os.path.isdir(vi_prefs.radlib):
            os.environ["RAYPATH"] = '{0}{1}{2}'.format(radldir, evsep[str(sys.platform)], os.path.join(addonpath, 'RadFiles', 'lib'))
        else:
            os.environ["RAYPATH"] = radldir
           
        os.environ["PATH"] += "{0}{1}{0}{2}{0}{3}".format(evsep[str(sys.platform)], radbdir, epdir, ofbdir) 
        if not os.environ.get("LD_LIBRARY_PATH"):
            os.environ["LD_LIBRARY_PATH"] = "{0}{1}".format(evsep[str(sys.platform)], ofldir) if os.environ.get("LD_LIBRARY_PATH") else "{0}{1}".format(evsep[str(sys.platform)], ofldir)
        else:
            os.environ["LD_LIBRARY_PATH"] += "{0}{1}".format(evsep[str(sys.platform)], ofldir) if os.environ.get("LD_LIBRARY_PATH") else "{0}{1}".format(evsep[str(sys.platform)], ofldir)
        os.environ["WM_PROJECT_DIR"] = ofedir
        

#def tupdate(self, context):
#    for o in [o for o in context.scene.objects if o.type == 'MESH'  and 'lightarray' not in o.name and o.hide == False and o.layers[context.scene.active_layer] == True and o.get('lires')]:
#        o.show_transparent = 1
#    for mat in [bpy.data.materials['{}#{}'.format('vi-suite', index)] for index in range(1, context.scene.vi_leg_levels + 1)]:
#        mat.use_transparency, mat.transparency_method, mat.alpha = 1, 'MASK', context.scene.vi_disp_trans
#    cmap(self)
#        
#def wupdate(self, context):
#    o = context.active_object
#    if o and o.type == 'MESH':
#        (o.show_wire, o.show_all_edges) = (1, 1) if context.scene.vi_disp_wire else (0, 0)
#
#    
#def liviresupdate(self, context):
#    setscenelivivals(context.scene)
#    for o in [o for o in bpy.data.objects if o.lires]:
#        o.lividisplay(context.scene)  
#    e_update(self, context)
#
#def script_update(self, context):
#    if context.scene.vi_params.vi_res_process == '2':
#        script = bpy.data.texts[context.scene.script_file]
#        exec(script.as_string())
        
def flovi_levels(self, context):
    if self.flovi_slmin > self.flovi_slmax:
       self.flovi_slmin -= 1 

classes = (VIPreferences, ViNetwork, No_Loc, So_Vi_Loc, ViSPNode, NODE_OT_SunPath, NODE_OT_TextUpdate, NODE_OT_FileSelect, NODE_OT_HdrSelect,
           VI_PT_3D, VI_Params_Scene, VI_Params_Object, VI_Params_Material, VI_Params_Collection, ViWRNode, ViSVFNode, NODE_OT_WindRose, VIEW3D_OT_WRDisplay, 
           NODE_OT_SVF, So_Vi_Res, VI_PT_Mat, VIEW3D_OT_SVFDisplay, MAT_EnVi_Node, ViSSNode, NODE_OT_Shadow, VIEW3D_OT_SSDisplay,
           No_Li_Geo, No_Li_Con, No_Li_Sen, So_Li_Geo, NODE_OT_Li_Geo, So_Li_Con, NODE_OT_Li_Con, No_Text, So_Text,
           No_Li_Im, So_Li_Im, NODE_OT_Li_Im, NODE_OT_Li_Pre, No_Li_Sim, NODE_OT_Li_Sim, VIEW3D_OT_Li_BD,
           No_Li_Gl, No_Li_Fc, NODE_OT_Li_Gl, NODE_OT_Li_Fc, No_En_Geo, VI_PT_Ob, NODE_OT_En_Geo, EnViNetwork, No_En_Net_Zone,
           EnViMatNetwork, No_En_Mat_Con, VI_PT_Gridify, OBJECT_OT_VIGridify2, No_En_Mat_Sc, No_En_Mat_Sh, No_En_Mat_ShC, No_En_Mat_Bl,
           NODE_OT_En_UV, No_En_Net_Occ, So_En_Net_Occ, So_En_Sched, So_En_Net_Inf, So_En_Net_Hvac, So_En_Net_Eq,
           No_En_Mat_Op, No_En_Mat_Tr, So_En_Mat_Ou, So_En_Mat_Op, So_En_Mat_Tr, So_En_Mat_Gas, No_En_Con, 
           So_En_Con, So_En_Geo, NODE_OT_En_Con, No_En_Sim, NODE_OT_En_Sim, No_En_Mat_Gas,
           No_Vi_Chart, So_En_Res, So_En_ResU, NODE_OT_Chart, No_En_Net_Hvac, So_En_Net_TSched, No_En_Net_Eq, No_En_Net_Sched, No_En_Net_Inf,
           No_En_Net_TC, No_En_Net_SFlow, No_En_Net_SSFlow, So_En_Net_SFlow, So_En_Net_SSFlow, So_En_Mat_PV, No_En_Mat_PV, No_En_Mat_Sched,
           So_En_Mat_PVG, No_En_Mat_PVG, NODE_OT_En_PVA, No_Vi_Metrics, NODE_OT_En_PVS, NODE_OT_En_LayS, NODE_OT_En_ConS, So_En_Net_Bound,
           No_En_Net_ACon, No_En_Net_Ext, No_En_Net_EMSZone, No_En_Net_Prog, So_En_Net_Act, So_En_Net_Sense, 
           TREE_PT_vi, TREE_PT_envin, TREE_PT_envim,  TREE_OT_goto_mat, TREE_OT_goto_group, 
           OBJECT_OT_Li_GBSDF, MATERIAL_OT_Li_LBSDF, MATERIAL_OT_Li_SBSDF, OBJECT_OT_GOct, MATERIAL_OT_Li_DBSDF, VIEW3D_OT_Li_DBSDF, NODE_OT_CSV, No_CSV,
           NODE_OT_ASCImport, No_ASC_Import)
                     
def register():
    for cl in classes:
        bpy.utils.register_class(cl)
  
    Object, Scene, Material, Collection = bpy.types.Object, bpy.types.Scene, bpy.types.Material, bpy.types.Collection
    Scene.vi_params = bpy.props.PointerProperty(type = VI_Params_Scene)
    Object.vi_params = bpy.props.PointerProperty(type = VI_Params_Object)
    Material.vi_params = bpy.props.PointerProperty(type = VI_Params_Material)
    Collection.vi_params = bpy.props.PointerProperty(type = VI_Params_Collection)
    
    nodeitems_utils.register_node_categories("Vi Nodes", vinode_categories)
    nodeitems_utils.register_node_categories("EnVi Nodes", envinode_categories)
    nodeitems_utils.register_node_categories("EnVi Material Nodes", envimatnode_categories)
    
    if update_chart_node not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(update_chart_node)
        
    if display_off not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(display_off)
        
    if update_dir not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(update_dir)
        
    path_update()

def unregister():
    nodeitems_utils.unregister_node_categories("EnVi Material Nodes")
    nodeitems_utils.unregister_node_categories("EnVi Nodes")
    nodeitems_utils.unregister_node_categories("Vi Nodes")
    
    
    for cl in reversed(classes):
        bpy.utils.unregister_class(cl)

    if update_chart_node in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(update_chart_node)

    if display_off in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(display_off)
        
    if update_dir in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(update_dir)
        
