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

import bpy
from .vi_func import newrow, retdates, logentry, get_materials

try:
    import matplotlib
    matplotlib.use('qt5agg', force = True)
    import matplotlib.pyplot as plt
    import matplotlib.cm as mcm
    import matplotlib.colors as mcolors
    from matplotlib.patches import Rectangle
    from matplotlib.collections import PatchCollection
    mp = 1
except:
    mp = 0

class VI_PT_3D(bpy.types.Panel):
    '''VI-Suite 3D view panel'''
    bl_label = "VI Display"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "VI-Suite"

    def draw(self, context):
        scene = context.scene
        svp = scene.vi_params
        cao = context.active_object
        layout = self.layout

        if not mp:
            row = layout.row()
            row.label(text = "No matplotlib install")
            return

        if cao:
            covp = cao.vi_params

#        try:
#        print(cao.active_material.vi_params.get('bsdf'), cao.active_material.vi_params['bsdf']['type'], covp.vi_type)
        if cao and cao.active_material and cao.active_material.vi_params.get('bsdf'):
            if cao.active_material.vi_params['bsdf'].get('type') and cao.active_material.vi_params['bsdf']['type'] == 'LBNL/Klems Full' and covp.vi_type == '5':
                row = layout.row()
                row.operator("view3d.bsdf_display", text="BSDF Display")

                if svp['viparams']['vidisp'] == 'bsdf_panel':
                    newrow(layout, 'Direction:', svp, "vi_bsdf_direc")
                    newrow(layout, 'BSDF max:', svp, "vi_bsdfleg_max")
                    newrow(layout, 'BSDF min:', svp, "vi_bsdfleg_min")
                    newrow(layout, 'BSDF scale:', svp, "vi_bsdfleg_scale")
                    newrow(layout, 'BSDF colour:', svp, "vi_leg_col")

#        except Exception as e:
#            logentry("Problem with BSDF panel display: {}".format(e))

        if svp.get('viparams') and svp['viparams'].get('vidisp'):
            if not svp.vi_display and svp['viparams']['vidisp'] == 'wr' and 'Wind_Plane' in [o.vi_params['VIType'] for o in bpy.data.objects if o.vi_params.get('VIType')]:
                row = layout.row()
                row.operator('view3d.wrdisplay', text = 'Wind Metrics')

            elif svp['viparams']['vidisp'] == 'wr' and svp.vi_display:
                row = layout.row()
                row.label(text = 'Scatter properties:')
                newrow(layout, 'Wind metric:', svp, 'wind_type')
                newrow(layout, 'Scatter colour:', svp, 'vi_scatt_col')
                newrow(layout, 'Max:', svp, 'vi_scatt_max')

                if svp.vi_scatt_max == '1':
                    newrow(layout, 'Max value:', svp, 'vi_scatt_max_val')

                newrow(layout, 'Min:', svp, 'vi_scatt_min')

                if svp.vi_scatt_min == '1':
                    newrow(layout, 'Min value:', svp, 'vi_scatt_min_val')

                newrow(layout, 'Refresh:', svp, 'vi_disp_refresh')

            elif svp['viparams']['vidisp'] == 'sp' and svp.vi_display:
                row = layout.row()
                row.prop(context.space_data.shading, "light")
                newrow(layout, "Latitude:", svp, 'latitude')
                newrow(layout, "Longitude:", svp, 'longitude')
                (sdate, edate) = retdates(svp.sp_sd, 365, 2015)
                time_disps = ((("Day of year: {}/{}".format(sdate.day, sdate.month), "sp_sd"),
                ("Time of day: {}:{}".format(int(svp.sp_sh), int((svp.sp_sh*60) % 60)), "sp_sh")),
                [("Time of day: {}:{}".format(int(svp.sp_sh), int((svp.sp_sh*60)) % 60), "sp_sh")],
                [("Day of year: {}/{}".format(sdate.day, sdate.month), "sp_sd")])

                for i in time_disps[int(svp['spparams']['suns'])]:
                    newrow(layout, i[0], svp, i[1])

                for i in (("Sun strength:", "sp_sun_strength"), ("Sun angle:", "sp_sun_angle")):
                    newrow(layout, i[0], svp, i[1])

                newrow(layout, "Line width:", svp, 'sp_line_width')
                newrow(layout, "Solstice colour:", svp, 'sp_season_main')
                newrow(layout, "Hour main colour:", svp, 'sp_hour_main')
                newrow(layout, "Hour dash colour:", svp, 'sp_hour_dash')
                newrow(layout, "Hour dash ratio:", svp, 'sp_hour_dash_ratio')
                newrow(layout, "Hour dash density:", svp, 'sp_hour_dash_density')
                newrow(layout, "Sun size:", svp, 'sp_sun_size')
                newrow(layout, "Sun colour:", svp, 'sp_sun_colour')
                newrow(layout, "Globe colour:", svp, 'sp_globe_colour')

                time_disps = ((("Display time:", "sp_td"), ("Display hours:", "sp_hd")),
                           [("Display hours:", "sp_hd")], [("Display hours:", "sp_hd")])

                for i in time_disps[int(svp['spparams']['suns'])]:
                    newrow(layout, i[0], svp, i[1])

                if (svp['spparams']['suns'] == '0' and (svp.sp_td or svp.sp_hd)) or svp.sp_hd:
                    for i in (("Font size:", "vi_display_rp_fs"),
                            ("Font colour:", "vi_display_rp_fc"),
                            ("Font shadow:", "vi_display_rp_sh")):
                        newrow(layout, i[0], svp, i[1])
                    if svp.vi_display_rp_sh:
                        newrow(layout, "Shadow colour:", svp, "vi_display_rp_fsh")

            elif svp['viparams']['vidisp'] in ('svf', 'ss', 'li', 'lc'):
                if not svp.vi_display:
                    row = layout.row()
                    row.prop(svp, "vi_disp_3d")
                    row = layout.row()

                    if svp['viparams']['vidisp'] == 'svf':
                        row.operator("view3d.svfdisplay", text="Sky View Display")
                    elif svp['viparams']['vidisp'] == 'ss':
                        row.operator("view3d.ssdisplay", text="Shadow Display")
                    elif svp['viparams']['vidisp'] == 'li':
                        row.operator("view3d.libd", text="Radiance Display")

                elif [o for o in bpy.data.objects if o.name in svp['liparams']['livir']]:
                    if not svp.ss_disp_panel:
                        newrow(layout, 'Result type:', svp, "li_disp_menu")
                        newrow(layout, 'Legend unit:', svp, "vi_leg_unit")
                        newrow(layout, 'Processing:', svp, "vi_res_process")

                    if svp.vi_res_process == '1':
                        newrow(layout, 'Modifier:', svp, "vi_res_mod")
                    elif svp.vi_res_process == '2':
                        layout.prop_search(svp, 'script_file', bpy.data, 'texts', text='File', icon='TEXT')

                    newrow(layout, 'Frame:', svp, "vi_frames")
                    newrow(layout, 'Legend max:', svp, "vi_leg_max")
                    newrow(layout, 'Legend min:', svp, "vi_leg_min")
                    newrow(layout, 'Legend scale:', svp, "vi_leg_scale")
                    newrow(layout, 'Legend colour:', svp, "vi_leg_col")
                    newrow(layout, 'Legend levels:', svp, "vi_leg_levels")
                    newrow(layout, 'Emitter materials:', svp, "vi_disp_mat")

                    if svp.vi_disp_mat:
                        newrow(layout, 'Emitter strength:', svp, "vi_disp_ems")

                    if svp['liparams']['unit'] in ('DA (%)', 'sDA (%)', 'UDI-f (%)',
                            'UDI-s (%)', 'UDI-a (%)', 'UDI-e (%)', 'ASE (hrs)',
                            'Max lux', 'Avg lux', 'Min lux', 'kWh', 'kWh/m2'):
                        newrow(layout, 'Scatter max:', svp, "vi_scatt_max_val")
                        newrow(layout, 'Scatter min:', svp, "vi_scatt_min_val")

                    if cao and cao.type == 'MESH':
                        newrow(layout, 'Draw wire:', svp, 'vi_disp_wire')

                    if int(svp.vi_disp_3d) == 1:
                        newrow(layout, "3D Level", svp, "vi_disp_3dlevel")

                    newrow(layout, "Transparency", svp, "vi_disp_trans")

                    if context.mode != "EDIT":
                        row = layout.row()
                        row.label(text="{:-<48}".format("Point visualisation "))
                        newrow(layout, 'Enable:', svp, 'vi_display_rp')

                        if svp.vi_display_rp:
                            for title, prop in [
                                ("Selected only:",  "vi_display_sel_only"),
                                ("Visible only:",   "vi_display_vis_only"),
                                ("Font size:",      "vi_display_rp_fs"),
                                ("Font colour:",    "vi_display_rp_fc"),
                                ("Font shadow:",    "vi_display_rp_sh"),
                                ("Shadow colour:",  "vi_display_rp_fsh"),
                                ("Position offset:","vi_display_rp_off")]:
                                newrow(layout, title, svp, prop)

                        row = layout.row()
                        row.label(text="{:-<60}".format(""))
                newrow(layout, 'Refresh:', svp, 'vi_disp_refresh')

            if svp.vi_display:
                newrow(layout, 'Display active', svp, 'vi_display')

class VI_PT_Mat(bpy.types.Panel):
    bl_label = "VI-Suite Material"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "material"

    def draw(self, context):
        cm, scene = context.material, context.scene

        if cm:
            svp = scene.vi_params
            mvp = cm.vi_params
            layout = self.layout
            newrow(layout, 'Material type', mvp, "mattype")

            if mvp.mattype in ('0', '1'):
                rmmenu(layout, cm)
                if not mvp.envi_nodes or (mvp.envi_nodes.name != cm.name and mvp.envi_nodes.name in [m.name for m in bpy.data.materials]):# in bpy.data.node_groups:
                    row = layout.row()
                    row.operator("material.envi_node", text = "Create EnVi Nodes")

            elif mvp.mattype == '2':
                newrow(layout, "Netgen max cell size:", mvp, "flovi_ng_max")
                newrow(layout, "Type:", mvp, "flovi_bmb_type")

                if mvp.flovi_bmb_type in ('0', '1') and svp.get('flparams') and svp['flparams'].get('solver_type'):
                    newrow(layout, "p type:", mvp, "flovi_bmbp_subtype")

                    if mvp.flovi_bmbp_subtype in ('fixedValue', 'totalPressure'):
                        if mvp.flovi_bmbp_subtype == 'totalPressure':
                            newrow(layout, "p0 value:", mvp, "flovi_bmbp_p0val")
                            newrow(layout, "Gamma value:", mvp, "flovi_bmbp_gamma")
                        newrow(layout, "Field value:", mvp, "flovi_p_field")

                        if not mvp.flovi_p_field:
                            newrow(layout, "Pressure value:", mvp, "flovi_bmbp_val")

                    newrow(layout, "U type:", mvp, "flovi_bmbu_subtype")

                    if mvp.flovi_bmbu_subtype in ('fixedValue', 'pressureInletOutletVelocity', 'inletOutlet'):
                        newrow(layout, "Field value:", mvp, "flovi_u_field")
                        if not mvp.flovi_u_field:
                            newrow(layout, "Velocity value:", mvp, "flovi_u_type")
                            if mvp.flovi_u_type == '0':
                                newrow(layout, "Velocity value:", mvp, "flovi_bmbu_val")
                            else:
                                newrow(layout, "Azimuth:", mvp, "flovi_u_azi")
                                newrow(layout, "Speed:", mvp, "flovi_u_speed")
                    if svp.get('flparams') and svp['flparams'].get('params'):
                        if 'l' not in svp['flparams']['params']:
                            newrow(layout, "Nut type:", mvp, "flovi_bmbnut_subtype")
                            if mvp.flovi_bmbnut_subtype == 'fixedValue':
                                newrow(layout, "Nut field:", mvp, "flovi_nut_field")
                                if not mvp.flovi_u_field:
                                    newrow(layout, "Nut value:", mvp, "flovi_bmbnut_val")
                            if 'k' in svp['flparams']['params']:
                                newrow(layout, "k type:", mvp, "flovi_k_subtype")
                                if mvp.flovi_k_subtype == 'fixedValue':
                                    newrow(layout, "K field:", mvp, "flovi_k_field")
                                    if not mvp.flovi_k_field:
                                        newrow(layout, "K value:", mvp, "flovi_k_val")
                                elif mvp.flovi_k_subtype == 'turbulentIntensityKineticEnergyInlet':
                                    newrow(layout, "K intensity:", mvp, "flovi_k_intensity")
                                    newrow(layout, "K field:", mvp, "flovi_k_field")
                                    if not mvp.flovi_k_field:
                                        newrow(layout, "K value:", mvp, "flovi_k_val")
                                newrow(layout, "Epsilon type:", mvp, "flovi_bmbe_subtype")
                                if mvp.flovi_bmbe_subtype == 'fixedValue':
                                    newrow(layout, "Epsilon field:", mvp, "flovi_e_field")
                                    if not mvp.flovi_e_field:
                                        newrow(layout, "Epsilon value:", mvp, "flovi_bmbe_val")
                            elif 'o' in svp['flparams']['params']:
                                newrow(layout, "k type:", mvp, "flovi_k_subtype")
                                if mvp.flovi_k_subtype == 'fixedValue':
                                    newrow(layout, "k field:", mvp, "flovi_k_field")
                                    if not mvp.flovi_k_field:
                                        newrow(layout, "k value:", mvp, "flovi_k_val")
                                newrow(layout, "Omega type:", mvp, "flovi_bmbo_subtype")
                                if mvp.flovi_bmbo_subtype == 'fixedValue':
                                    newrow(layout, "Omega field:", mvp, "flovi_o_field")
                                    if not mvp.flovi_o_field:
                                        newrow(layout, "Omega value:", mvp, "flovi_bmbo_val")

                            elif 's' in svp['flparams']['params']:
                                newrow(layout, "Nutilda type:", mvp, "flovi_bmbnutilda_subtype")
                                if mvp.flovi_bmbnutilda_subtype == 'fixedValue':
                                    newrow(layout, "Nutilda field:", mvp, "flovi_nutilda_field")
                                    if not mvp.flovi_nutilda_field:
                                        newrow(layout, "Nutilda value:", mvp, "flovi_bmbnutilda_val")

                            if 't' in svp['flparams']['params']:
                                newrow(layout, "T type:", mvp, "flovi_bmbt_subtype")
                                if mvp.flovi_bmbt_subtype == 'fixedValue':
                                    newrow(layout, "T field:", mvp, "flovi_t_field")
                                    if not mvp.flovi_t_field:
                                        newrow(layout, "T value:", mvp, "flovi_bmbt_val")
                                elif mvp.flovi_bmbt_subtype == 'inletOutlet':
                                    newrow(layout, "T field:", mvp, "flovi_t_field")
                                    if not mvp.flovi_t_field:
                                        newrow(layout, "T inlet value:", mvp, "flovi_bmbti_val")
                                        newrow(layout, "T value:", mvp, "flovi_bmbt_val")
                                newrow(layout, "p_rgh type:", mvp, "flovi_prgh_subtype")
                                newrow(layout, "p_rgh field:", mvp, "flovi_prgh_field")
                                if not mvp.flovi_prgh_field:
                                    newrow(layout, "p_rgh p:", mvp, "flovi_prgh_p")
                                    newrow(layout, "p_rgh value:", mvp, "flovi_prgh_val")
                                if 'b' in svp['flparams']['params']:
                                    newrow(layout, "alphat type:", mvp, "flovi_a_subtype")
                                if 'p' in svp['flparams']['params']:
                                    newrow(layout, "Rad type:", mvp, "flovi_rad_subtype")
                                    newrow(layout, "Emissivity mode:", mvp, "flovi_rad_em")
                                    newrow(layout, "Emissivity value:", mvp, "flovi_rad_e")
                                    newrow(layout, "radiation value:", mvp, "flovi_rad_val")
                newrow(layout, "Probe:", mvp, "flovi_probe")

class VI_PT_Ob(bpy.types.Panel):
    bl_label = "VI-Suite Object Definition"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        if context.object and context.object.type in ('LIGHT', 'MESH', 'EMPTY'):
            return True

    def draw(self, context):
        obj = context.object
        ovp = obj.vi_params
        layout = self.layout

        if obj.type == 'MESH':
            row = layout.row()
            row.prop(ovp, 'vi_type')

            if ovp.vi_type == '0':
                row = layout.row()
                row.label(text = '-- Octree generation --')
                newrow(layout, 'Triangulate:', ovp, 'triangulate')
                newrow(layout, 'Fallback:', ovp, 'fallback')
                row = layout.row()
                row.operator('object.vi_genoct', text = "Generate Octree")

            elif ovp.vi_type == '1':
                newrow(layout, "Type:", ovp, 'envi_type')

#                if ovp.envi_type == '0':
#                    newrow(layout, "Habitable:", ovp, 'envi_hab')

            elif ovp.vi_type == '2':
                pass

        if (obj.type == 'LIGHT' and obj.data.type != 'SUN') or ovp.vi_type == '4':
            newrow(layout, 'IES file:', ovp, "ies_name")
            newrow(layout, 'IES Dimension:', ovp, "ies_unit")
            newrow(layout, 'IES Strength:', ovp, "ies_strength")
            newrow(layout, 'IES Colour:', ovp, "ies_colmenu")

            if ovp.ies_colmenu == '0':
                newrow(layout, 'IES RGB:', ovp, "ies_rgb")
            else:
                newrow(layout, 'IES Temperature:', ovp, "ies_ct")

        elif ovp.vi_type == '5':
            if any([obj.material_slots[i].material.vi_params.radmatmenu == '8'
                    for i in [f.material_index for f in obj.data.polygons]]):
                newrow(layout, 'Direction:', ovp, 'li_bsdf_direc')
#                newrow(layout, 'Proxy:', ovp, 'li_bsdf_proxy')

#                if ovp.li_bsdf_proxy:
#                    newrow(layout, 'Length unit:', ovp, 'li_bsdf_dimen')

                newrow(layout, 'Klems/Tensor:', ovp, 'li_bsdf_tensor')

                if ovp.li_bsdf_tensor != ' ':
                    newrow(layout, 'resolution:', ovp, 'li_bsdf_res')
                    newrow(layout, 'Samples:', ovp, 'li_bsdf_tsamp')
                else:
                    newrow(layout, 'Samples:', ovp, 'li_bsdf_ksamp')
                newrow(layout, 'RC params:', ovp, 'li_bsdf_rcparam')

                if not ovp.bsdf_running:
                    row = layout.row()
                    row.operator("object.gen_bsdf", text="Generate BSDF")
            else:
                row = layout.row()
                row.label(text = 'No BSDF material applied')

        if obj.type == 'EMPTY' or (ovp.vi_type == '3' and obj.type == 'MESH' and len(obj.data.polygons) == 1):
            newrow(layout, 'CFD probe:', ovp, 'flovi_probe')

def rmmenu(layout, cm):
    mvp = cm.vi_params
    row = layout.row()
    row.label(text = 'LiVi Radiance type:')
    row.prop(mvp, 'radmatmenu')
    row = layout.row()

    for prop in mvp.radmatdict[mvp.radmatmenu]:
        if prop:
             row.prop(mvp, prop)
        else:
            row = layout.row()

    if mvp.radmatmenu == '8':
        newrow(layout, 'Proxy depth:', mvp, 'li_bsdf_proxy_depth')
        newrow(layout, 'Up vector:', mvp, 'li_bsdf_up')
        row = layout.row()
        row.operator("material.load_bsdf", text="Load BSDF")
    elif mvp.radmatmenu == '9':
        layout.prop_search(mvp, 'radfile', bpy.data, 'texts', text='File', icon='TEXT')
    if mvp.get('bsdf'):
        row.operator("material.del_bsdf", text="Delete BSDF")
        row = layout.row()
        row.operator("material.save_bsdf", text="Save BSDF")
    if mvp.radmatmenu in ('1', '2', '3', '7'):
        newrow(layout, 'Photon port:', mvp, 'pport')
    if mvp.radmatmenu in ('0', '1', '2', '3', '6'):
        newrow(layout, 'Textured:', mvp, 'radtex')
        if mvp.radtex:
            newrow(layout, 'Normal map:', mvp, 'radnorm')
            if mvp.radnorm:
                # newrow(layout, 'Strength:', mvp, 'ns')
                newrow(layout, 'Image green vector:', mvp, 'nu')
                newrow(layout, 'Image red vector:', mvp, 'nside')

    row = layout.row()
    row.label(text = "-----------------------------------------")

class VI_PT_Gridify(bpy.types.Panel):
    bl_label = "VI Gridify"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "mesh_edit"
    bl_category = "VI-Suite"

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator("object.vi_gridify2", text="Grid the object")

class TREE_PT_vi(bpy.types.Panel):
    bl_label = "VI-Suite"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "VI-Suite"

    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type in ('ViN', 'EnViN', 'EnViMatN')

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        visuite_groups = [g for g in bpy.data.node_groups if g.bl_idname == 'ViN']

        for g in visuite_groups:
            emboss = False
            if len(context.space_data.path) > 0:
                emboss = context.space_data.path[-1].node_tree.name == g.name
            op = col.operator('tree.goto_group', text=g.name, emboss=emboss, icon='NODETREE')
            op.tree_type = "ViN"
            op.tree = g.name

        col.separator()
        col.separator()
        col.separator()

class TREE_PT_envim(bpy.types.Panel):
    bl_label = "EnVi Materials"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "VI-Suite"

    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type in ('ViN', 'EnViN', 'EnViMatN')

    def draw(self, context):
        layout = self.layout
        materials = get_materials()
        col = layout.column(align=True)

        for mat in materials:
            name = mat.name

            try:
                icon_val = layout.icon(mat)
            except:
                icon_val = 1
                print("WARNING [Mat Panel]: Could not get icon value for %s" % name)
            if mat.users:
                op = col.operator('tree.goto_mat',
                                  text=name,
                                  emboss=(mat == context.space_data.id),
                                  icon_value=icon_val)
                op.mat = name
            else:
                row = col.row(align=True)
                op = row.operator('tree.goto_mat',
                                  text=name,
                                  emboss=(mat == context.space_data.id),
                                  icon_value=icon_val)
                op.mat = name
                op = row.operator('tree.goto_mat',
                                  text="",
                                  emboss=(mat == context.space_data.id),
                                  icon='ORPHAN_DATA')
                op.mat = name

        if not materials:
            col.label(text="No EnVi Materials")

class TREE_PT_envin(bpy.types.Panel):
    bl_label = "EnVi Networks"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "VI-Suite"

    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type in ('ViN', 'EnViN', 'EnViMatN')

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        envin_groups = [g for g in bpy.data.node_groups if g.bl_idname == 'EnViN']

        for g in envin_groups:
            emboss = False

            if len(context.space_data.path) > 0:
                emboss = context.space_data.path[-1].node_tree.name == g.name

            op = col.operator('tree.goto_group', text=g.name, emboss=emboss, icon='NODETREE')
            op.tree_type = "EnViN"
            op.tree = g.name

        if not envin_groups:
            col.label(text="No EnVi Network")

        col.separator()
