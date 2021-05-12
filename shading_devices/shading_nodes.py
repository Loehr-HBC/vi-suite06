# PATCH => shading-device (HBC)
import bpy
from ..vi_node import ( envinode_categories, EnViNodeCategory, EnViNodes,
    EnViNetwork as _EnViNetwork, No_En_Geo as ViGExEnNode)# Envi-Geometry Node (renamed since v04x)
from .utils import setUpSockets, ClampedSocket_META, socketid
from .utils import EnVi_Multiple, update_shaded_materials
from nodeitems_utils import NodeCategory, NodeItem, NodeItemCustom

# Standard NodeSockets
from bpy.types import NodeSocketInterfaceString, NodeSocketInterfaceFloat
#from bpy.types import NodeSocketInterfaceBool, NodeSocketInterfaceVector, NodeSocketInterfaceColor, NodeSocketInterfaceInt
# utility
# for the export
from collections import OrderedDict


# in-place-overwriting EnViNetwork # maybe later I could subclass from it?
# perhaps I could even just insert the update-function and the collection?
class EnViNetwork(bpy.types.NodeTree):
    '''A node tree for the creation of EnVi advanced ventilation networks.'''
    bl_idname = 'EnViN'
    bl_label = 'EnVi Network'
    bl_icon = 'FORCE_WIND'
    nodetypes = {}

    # for the shaded materials to choose in the ShadedWindow-node
    envi_shaded_materials : bpy.props.CollectionProperty(type=EnVi_Multiple)
    # update
    def upd_mat_faces(self, collection="", context=""):
        mats = [mat.name for mat in self.envi_shaded_materials]
        for node in self.nodes:
            if node.bl_idname=="EnViShadWinNode":
                if len(mats)==0: node.mat_def = ""
                elif node.mat_def not in mats:
                    node.mat_def = "" ## breaks changes (noisy default)
                    #node.mat_def = mats[0] ## hide changes (silent default)
                else: node.mat_def = node.mat_def

# in-place-expanding the postexport function to update the nodetrees materials
_postexport = ViGExEnNode.postexport
def postexport( node):
    _postexport(node)
    ### update-hook: materials in the ShadedWindow-node
    ngs = [ng for ng in bpy.data.node_groups if ng.bl_idname=="EnViN"]
    for ng in ngs: update_shaded_materials(ng)
ViGExEnNode.postexport = postexport

# skip this option entirely? otherwise it must be added AND drawn
# Adding is easy, drawing is not.
#    newrow(layout, "Shading device:", cm, 'envi_shadingdevice')

# EnVi shading material definitions # PATCH => shading-devices (HBC)
#    Material.envi_shadingdevice = bprop("", "Flag to siginify whether the material has a shading device.\nA shading device must be properly defined in the nodes of the EnVi-Network", True) ##### Shading device existent or not



############################################################### 80 CHAR MARGIN #
############### PATCH-Sockets => shading-device (HBC) ###############
# green and blue had been free
# Shade-Socket
class EnViShadeSocket(bpy.types.NodeSocket):
    """A socket for ShadingDevices"""
    bl_idname = 'EnViShadeSocket'
    bl_label = 'Shading device socket'
    bl_color = (0.0, 0.0, 0.5, 0.5)

    @property
    def SHADE_TYPE(self):
#        if self.is_output: return self.node.SHADE_TYPE
 #       elif self.is_linked:
  #          if self.links[0].is_valid:
   #             return self.links[0].from_node.SHADE_TYPE
        return self.SHADE.SHADE_TYPE # muesste reichen,
#        da dieser socket nur erzeugt wird, wenn eine verbindung zu
#        SHADE existiert
    @property
    def SHADE( self): # returns the node where the shade-material was defined
        if self.node.bl_idname=='EnViShadDevNode':  return self.node  # Shade
        elif self.is_output: return self.node.inputs[self.name].SHADE # forward
        elif len(  self.links)!=0:                                    # INPUT - forward
            return self.links[  0].from_socket.SHADE                  # forward
        else:                                                         # ERROR-Call
            raise KeyError("NODE: {} - NO SHADE PROVIDED".format(self.node.name))

    def draw(self, context, layout, node, text):
        if False:#self.is_linked and not self.is_output:
            if any(lk.is_valid for lk in self.links):
                text+="({})".format(self.SHADE_TYPE)
        layout.label(text=text)

    def draw_color(self, context, node):
        return (0.0, 0.0, 0.5, 1)
### Control-Socket
class EnViControlSocket(bpy.types.NodeSocket):
    """A socket for ShadingControls"""
    bl_idname = 'EnViControlSocket'
    bl_label = 'Shading control socket'
    bl_color = (0.0, 0.5, 0.0, 0.5)

    @property
    def CONTROL( self): # returns the node where the shade-material was defined
        if self.node.bl_idname=='EnViShadConNode': return self.node # Control
        elif self.is_output: return self.node.inputs[self.name].CONTROL # weiterleiten
        else:
            try:
                return self.links[0].from_socket.CONTROL          # weiterleiten
            except:
                raise KeyError("NODE: {}\n   NO CONTROL PROVIDED".format(self.name))

    def draw(self, context, layout, node, text):
        layout.label(text=text)

    def draw_color(self, context, node):
        return (0.0, 0.5, 0.0, 1)

### Clamped-Float-Socket
class ClampedFloatSocket(bpy.types.NodeSocket, ClampedSocket_META):
    """This socket provides a clamped float value.
    The 'default_value'=0 may only find its place between 'max_value'=1
    and 'min_value'=0. Otherwise it will be corrected accordingly.
    'titled'=False and 'valOnly'=True both referre to the layout."""
    bl_idname = 'ClampedFloatSocket'
    bl_label = 'Clamped float socket'
    bl_color = (0.6, 0.6, 0.6, 0.5)

    def upd(self, context=""):
        ClampedSocket_META.upd(self,context)
    ### This FloatVector actualy holds the data
    true_default_value : bpy.props.FloatVectorProperty(
            default = [0,0,1], update=upd)

    def draw_color(self, context="", node=""):
        return (0.6, 0.6, 0.6, [0.5,1][self.is_linked or self.is_output])

### Enum-Socket - WARNING! dependant on node-variable 'ENUM'!!!
class EnumSocket(bpy.types.NodeSocket):
    """ Socket for emulation of EnumProperty-sockets.
    This Socket has a StringProperty "default_value".
    Its owner-node must contain a dictionary "ENUM".
    If named there, it will draw the corresponding EnumProperty."""
    bl_idname = 'EnumSocket'
    bl_label = 'Enum socket'
    bl_color = (0.2, 0.2, 0.2, 0.5)

    def is_valid(self, value=None):
        if value == None: value=self.true_default_value
        if value in self.allowed_values: return True
        if self.allowed_values == []: return True
        return False

    @property
    def valid(self): self.is_valid(self.true_default_value)

    true_default_value : bpy.props.StringProperty()
    # If __allowed isnt empty, only values in __allowed can be valid.
    __allowed = []

    @property
    def default_value( self):
        nep = self.node.ENUM.get(self.name,"False")
        tdv = getattr(self.node,nep,self.true_default_value)

        if self.is_output==True: return tdv
        if self.is_linked==True:
            for l in self.links: # using links[0] would spam the console
                if l.is_valid:   # with utterly wrong/unneeded error-messages
                    skt = l.from_socket
                    sdv = skt.default_value
                    return [tdv,sdv][self.is_valid(sdv)]
#            if self.links[0].is_valid==True:
 #               skt = self.links[0].from_socket
  #              sdv = skt.default_value
#                print( [tdv,sdv][self.is_valid(sdv)])
   #             return [tdv,sdv][self.is_valid(sdv)]
        return tdv
    @property
    def allowed_values(self): return self.__allowed
    @default_value.setter
    def default_value( self, value):
        allowed = self.allowed_values
        if allowed==[]:
            self.true_default_value = "{}".format(value)
        elif "{}".format(value) in allowed:
            self.true_default_value = "{}".format(value)
    @allowed_values.setter
    def allowed_values(self, values):
        if values in [[],"",()]: self.__allowed = []
        else:
            allowed = ["{}".format(value) for value in values]
            if allowed!=[]: self.__allowed = allowed
        if self.__allowed!=[] and self.true_default_value not in self.__allowed:
            self.true_default_value=self.__allowed[0]

    def draw(self, context, layout, node, text):
        #self.advanced_draw(context, layout, node, text); return
        if self.is_linked: layout.label(text=text)
        else:
            propname = node.ENUM.get(self.name,"")
            if propname!="":
                layout.prop(node, propname)

    def advanced_draw(self, context, layout, node, text):
        enum = node.ENUM.get(self.name, "")
        if self.is_linked:
            val = getattr(self.links[0].from_socket, "default_value", None)
            if val==None:
                box = layout.box()
                box.label(text="INVALID INPUT TYPE")
                box.row().label(text="Input has no 'default_value'-String")
                return
            #if self.valid: layout.label(text=text)
            if self.is_valid(val): layout.label(text=text)
            else:
                box = layout.box()
                box.label(text="INVALID INPUT")
                box.box().label(text="{}".format(self.default_value))
                if enum != "":
                    box.label(text="This is used instead")
                    box.prop(node, enum)
        else:
            layout.alert=(self.__allowed!=[] and
                          self.true_default_value not in self.__allowed)
            layout.prop( node, enum)

    def draw_color(self, context, node):
        return (0.2, 0.2, 0.2, [0.5,1][self.is_linked])


############################################################### 80 CHAR MARGIN #
############### PATCH-Nodes => shading-device (HBC) ###############

# ShadingDevice
class EnViShadDevNode(bpy.types.Node, EnViNodes):
    """Node defining a shading device material"""
    bl_idname = 'EnViShadDevNode'
    bl_label  = 'Shading Device'
    bl_icon   = 'SOUND'

    ### update-functions. They MUST stay on top
    def update(self):
        if not self.initialised: return
        self.upd_shadeType()
        self.upd_layout()
    def upd_enumSocket(self, context):
        """This funktion may only be used in update-calls for EnumSocketProps.
        Any function that accepts self, and context and does NOT set/update
        the EnumSocketProp can be added to the hooks.
        (WARNING:no recursion-check)
        To do so create an optional dictionary 'node.ENUM_HOOKS' in this style:
        ENUM_HOOKS={socket.name:[function(node, context)]}"""
        skt = context.socket
        skt.default_value = getattr(self, self.ENUM[skt.name])
        enum_hooks = getattr(self, "ENUM_HOOKS",{})
        hooks = enum_hooks.get(skt.name, [])
        for hook in hooks: hook(self, context)

    def upd_layout(self, context=""):
        """Show/hide sockets depending on layout choice.
        Be aware that changes made remain and are applied if applicable."""

        ### hide all sockets: # the very basic ones will be unhid at the end
        for skt in self.inputs: skt.hide = True

        if self.SHADE_TYPE=="Blind":  self.upd_layout_B()
        if self.SHADE_TYPE=="Shade":  self.upd_layout_S()
        if self.SHADE_TYPE=="Screen": self.upd_layout_Sc()

        ### unhide the very basic sockets:
        for skt in self.inputs:
            if skt.name in [s[1] for s in self.skts__basic]:
                skt.hide = False
        ### unhide the outputs:
        # as there are no SHADE_TYPE-specific outputs, outputs wont be hidden.
        for skt in self.outputs: skt.hide = False

    def upd_layout_B( self):
        """Show/hide sockets depending on layout choice.
        Be aware that changes made remain and are applied if applicable."""

        ### rename-block { # rename to match definition-name
        if "Thickness (mm)" not in self.inputs:
            skt = [skt for skt in self.inputs
                   if skt.name.endswith("Thickness (mm)")][0]
            skt.name = "Thickness (mm)"
        if "Spacing (mm)" not in self.inputs:
            skt = [skt for skt in self.inputs
                   if skt.name.endswith("Spacing (mm)")][0]
            skt.name = "Spacing (mm)"
        ### }

        ## only sockets that concern me
        inputs  = [ skt for skt in self.skts_B_ALL
                    if skt[1] in self.inputs.keys() ]
        outputs = [ skt for skt in self.skts_B_ALL
                    if skt[1] in self.outputs.keys()]

        hideable = [skt for skt in inputs + outputs]

        # alle int<0 = verbergen ihre aktionsgruppe, die anderen zeigen nur sie
        hide = int(self.layout)<0

        actOn= [skt for skt in hideable
                if [skt in self.skts__SBSc,                # 0 # Shared
                    True,                                  # 1 # All
                    self.inputs[skt[1]].is_linked==True,   # 2 # Linked
                    "Diff"   in skt[1],                    # 3 # Diffuse
                    "Direct" in skt[1] or "Beam" in skt[1],# 4 # Direct/Beam
                    skt in self.skts__trans,               # 5 # Transmittance
                    skt in self.skts__refl,                # 6 # Reflectance
                    skt in self.skts__oMod                 # 7 # OpeningModifier
                    ][abs(int(self.layout))] ]

        for skt in hideable: self.inputs[skt[1]].hide = not hide
        for skt in    actOn: self.inputs[skt[1]].hide = hide

        ### rename-block { # rename to display precise name
        self.inputs["Thickness (mm)"].name = "Slat-Thickness (mm)"
        self.inputs[  "Spacing (mm)"].name = "Slat-Spacing (mm)"
        ### }
    def upd_layout_S( self):
        """Show/hide sockets depending on layout choice.
        Be aware that changes made remain and are applied if applicable."""

        ### rename-block { # rename to match definition-name
        if "Thickness (mm)" not in self.inputs:
            skt = [skt for skt in self.inputs
                   if skt.name.endswith("Thickness (mm)")][0]
            skt.name = "Thickness (mm)"
        ### }

        ## only sockets that concern me
        inputs  = [ skt for skt in self.skts_S_ALL
                    if skt[1] in self.inputs.keys() ]
        outputs = [ skt for skt in self.skts_S_ALL
                    if skt[1] in self.outputs.keys()]

        hideable = [skt for skt in inputs + outputs]

        # alle int<0 verbergen ihre aktionsgruppe, die anderen zeigen nur sie
        hide = int(self.layout)<0

        actOn= [skt for skt in hideable
                if [skt in self.skts__SBSc,                # 0 # Shared
                    True,                                  # 1 # All
                    self.inputs[skt[1]].is_linked==True,   # 2 # Linked
                    "Diff"   in skt[1],                    # 3 # Diffuse
                    "Direct" in skt[1] or "Beam" in skt[1],# 4 # Direct/Beam
                    skt in self.skts__trans,               # 5 # Transmittance
                    skt in self.skts__refl,                # 6 # Reflectance
                    skt in self.skts__oMod                 # 7 # OpeningModifier
                    ][abs(int(self.layout))] ]

        for skt in hideable: self.inputs[skt[1]].hide = not hide
        for skt in    actOn: self.inputs[skt[1]].hide = hide

        ### rename-block { # rename to display precise name
        self.inputs["Thickness (mm)"].name = "Shade-Thickness (mm)"
        ### }
    def upd_layout_Sc(self):
        """Show/hide sockets depending on layout choice.
        Be aware that changes made remain and are applied if applicable."""

        ### rename-block { # rename to match definition-name
        if "Thickness (mm)" not in self.inputs:
            skt = [skt for skt in self.inputs
                   if skt.name.endswith("Thickness (mm)")][0]
            skt.name = "Thickness (mm)"
        if "Spacing (mm)" not in self.inputs:
            skt = [skt for skt in self.inputs
                   if skt.name.endswith("Spacing (mm)")][0]
            skt.name = "Spacing (mm)"
        ### }

        ## only sockets that concern me
        inputs  = [ skt for skt in self.skts_Sc_ALL
                    if skt[1] in self.inputs.keys() ]
        outputs = [ skt for skt in self.skts_Sc_ALL
                    if skt[1] in self.outputs.keys()]

        hideable = [skt for skt in inputs + outputs]

        # alle str(int<0) verbergen ihre aktionsgruppe, die anderen zeigen nur sie
        hide = int(self.layout)<0

        actOn= [skt for skt in hideable
                if [skt in self.skts__SBSc,                # 0 # Shared
                    True,                                  # 1 # All
                    self.inputs[skt[1]].is_linked==True,   # 2 # Linked
                    "Diff"   in skt[1],                    # 3 # Diffuse
                    "Direct" in skt[1] or "Beam" in skt[1],# 4 # Direct/Beam
                    skt in self.skts__trans,               # 5 # Transmittance
                    skt in self.skts__refl,                # 6 # Reflectance
                    skt in self.skts__oMod                 # 7 # OpeningModifier
                    ][abs(int(self.layout))] ]

        for skt in hideable: self.inputs[skt[1]].hide = not hide
        for skt in    actOn: self.inputs[skt[1]].hide = hide

        ### rename-block { # rename to display precise name
        self.inputs["Thickness (mm)"].name = "Wire-Thickness (mm)"
        self.inputs[  "Spacing (mm)"].name = "Wire-Spacing (mm)"
        ### }

    def upd_shadeType(self, context=""): # general adjustments
        """Applies general adjustments, then calls individual adjustments."""
        SHADE_TYPE = self.SHADE_TYPE
        if SHADE_TYPE=="Blind":  self.upd_shadeType_Blinds()
        if SHADE_TYPE=="Shade":  self.upd_shadeType_Shades()
        if SHADE_TYPE=="Screen": self.upd_shadeType_Screens()
        # self.upd_name()
        return
    def upd_shadeType_Blinds( self, context=""): pass # adjustments for Blinds
    def upd_shadeType_Shades( self, context=""): pass # adjustments for Shades
    def upd_shadeType_Screens(self, context=""): pass # adjustments for Screens
    def upd_name(self, context=""):
        """Tries correcting the name."""
        st = ["Blind","Shade","Screen"]
        i  = st.index(self.SHADE_TYPE)
        self.name=self.name.replace(st[i-1],st[i]).replace(st[i-2],st[i])

    ### PROPS ### MUST stay below their update-functions.
    #             otherwise updates will raise errors.
    ## for the update-function 'update'
    @property
    def initialised(self): return len(self.skts__ALL)==len(self.inputs)
    ## better version of node.nodeid : now its a propfunktion
    @property # doesn't add much overhead, and is allways up to date.
    def nodeid(self): return nodeid(self)
    @property # to match with EnViShadConNode, allowing for the socket to check
    def SHADE_TYPE(self): return self.inputs["Shade Type"].default_value
    @property # returns the value of the active layout, matching the SHADE_TYPE
    def layout(  self):
        layouts=[self.layout_enum_B, self.layout_enum_S, self.layout_enum_Sc]
        return layouts[["Blind", "Shade", "Screen"].index(self.SHADE_TYPE)]
    @property # returns the name of the active layout, matching the SHADE_TYPE
    def layout_enum(self):
        idx = ["Blind", "Shade", "Screen"].index(self.SHADE_TYPE)
        return "layout_enum_{}".format(["B","S","Sc"][idx])
    @property # returns the name of this object, replacing unallowed chars by _
    def NAME(self):
        name = self.name
        for s in ",;!#": name = name.replace(s,"_")
        return name
    ## "Visible Sockets" - UI - Layout
    layout_items =[ # these items are shared along the "Layout"-Enums
        ("0",  "Shared",   "only show sockets that are shared along the types"),
        ("1",  "All",      "show all sockets"                                 ),
        ("-1", "None",     "hide all hideable sockets"                        ),
        ("2",  "Linked",   "only show sockets that are plugged in"            )]
    #    "Unlinked" would require to unlink liked ones in order to hide them
    layout_items_B = [ # these items are for the Blind-Layout-Enum
        ("3",  "Diffuse",        "only show sockets that define diffuse"      ),
        ("4",  "Direkt/Beam",    "only show sockets that define direct/beam"  ),
        ("5",  "Transmittance",  "only show sockets that define transmittance"),
        ("6",  "Reflectance",    "only show sockets that define reflectivity" ),
        ("7",  "Opening Multiplier",
         "only show sockets that define opening multipliers"                  ),

        ("-3","No Diffuse",      "only hide sockets that define diffuse"      ),
        ("-4","No Direkt/Beam",  "only hide sockets that define direct/beam"  ),
        ("-5","No Transmittance","only hide sockets that define transmittance"),
        ("-6","No Reflectance",  "only hide sockets that define reflectivity" ),
        ("-7","No Opening Multiplier",
         "only hide sockets that define opening multipliers"                  )]
    layout_items_S = [ # these items are for the Shade-Layout-Enum
        ("7",  "Opening Multiplier",
         "only show sockets that define opening multipliers"                  ),
        ("-7","No Opening Multiplier",
         "only hide sockets that define opening multipliers"                  )]
    layout_items_Sc= [ # these items are for the Screen-Layout-Enum
        ("7",  "Opening Multiplier",
         "only show sockets that define opening multipliers"                  ),
        ("-7","No Opening Multiplier",
         "only hide sockets that define opening multipliers"                  )]

    layout_enum_B : bpy.props.EnumProperty(name  = "Layout", default = "1",
                                           items = layout_items + layout_items_B,
                                           update= upd_layout)
    layout_enum_S : bpy.props.EnumProperty(name  = "Layout", default = "1",
                                           items = layout_items + layout_items_S,
                                           update= upd_layout)
    layout_enum_Sc : bpy.props.EnumProperty(name  = "Layout", default = "1",
                                           items = layout_items + layout_items_Sc,
                                           update= upd_layout)

    ### EnumSocketProps
    ## This dict contains the names of each EnumSocket
    ## and their corresponding EnumProperties in this node
    ENUM = {"Shade Type" :"shade_type",
            "Orientation":"slat_orientation",
            "Accounting Method":"AccMethod",
            "Angle of Resolution":"AngOfRes"}
    ## This optional dict contains the names of EnumSockets
    ## and their corresponding additional update-hooks.
    ## They will be called by upd_enumSocket.
    ## WARNING: no check against recursion!
    ENUM_HOOKS = {"Shade Type":[upd_layout,upd_shadeType]}

    # IMPORTANT: Do NOT implement "ComplexShade" into this Node.
    #            Complex Shades are ONLY for use with "ComplexFenestration"
    shade_type : bpy.props.EnumProperty(name = "Shade Type", default = "Blind",
        items =[("Blind",   "Blind",    "Venetian Blinds"),
                ("Shade",   "Shade",    "Shades of cloth"),
                ("Screen",  "Screen",   "Insect Screen"  )],
        update  =upd_enumSocket)

    AngOfRes : bpy.props.EnumProperty(name  = "Output Map", default = "0",
        items = [("0","No Map", "Do not create a map"),
                 ("1", "1 deg", "Use 1 degree as angular resolution"),
                 ("2", "2 deg", "Use 2 degree as angular resolution"),
                 ("3", "3 deg", "Use 3 degree as angular resolution"),
                 ("5", "5 deg", "Use 5 degree as angular resolution")],
        description="Angle of resolution for a 'Screen Transmittance Output Map'",
        update = upd_enumSocket)
    AccMethod : bpy.props.EnumProperty(name = "ReflectedLight",
        items = [("DoNotModel","Ignore Reflected Transmittance", ""),
                 ("ModelAsDirectBeam", "Model as direct beam",   ""),
                 ("ModelAsDiffuse",    "Model as diffuse",       "")],
        description="Method of accounting for light that is reflected trough the screen",
        default = "ModelAsDiffuse", update = upd_enumSocket)

    slat_orientation : bpy.props.EnumProperty( # slat orientation
        items =[("HORIZONTAL","HORIZONTAL","Slats run horizontal.(Standard)"),
                ("VERTICAL",  "VERTICAL",  "Slats run vertically."          )],
        name = "Orientation", default = "HORIZONTAL", update = upd_enumSocket)

    ### SOCKETS - declaration for use with the setUpSockets-utility
        # entries are of this format of format
        # [ type, name [, identifier [, default(-list)]] ]
    ## shared
    # sockets shared by ALL THREE shade-types
    skts__basic= [ ("EnumSocket", "Shade Type"),
        # thickness: Slat-, Shade-, Wire-,
        ("ClampedFloatSocket","Thickness (mm)",         "", [ 1,   0.1,  100]),# ]0, 100]
        ("ClampedFloatSocket","Conductivity (W/(m*K))", "", [44.9, 0.1,  401]),# ]0 inf[ #401 (W/mK)pure Copper.
        ("ClampedFloatSocket","Distance to glass (mm)", "", [50,    10, 1000]),# [10, 1000]
    ]
    skts__difRefl=[ # Reflectance
        ("ClampedFloatSocket","Diffuse Solar Reflectance",  "", 0.8),
        ("ClampedFloatSocket","Diffuse Visible Reflectance","", 0.7)]
    skts__oMod = [  # opening modifier
        ("ClampedFloatSocket","Opening Multiplier Top"           ),# [0, 1]
        ("ClampedFloatSocket","Opening Multiplier Bottom"        ),
        ("ClampedFloatSocket","Opening Multiplier Left",  "", 0.5),
        ("ClampedFloatSocket","Opening Multiplier Right", "", 0.5)]
    skts__SBSc = skts__basic + skts__difRefl + skts__oMod

    skts__SB  = [ # sockets shared by Shades and Blinds
        ("ClampedFloatSocket","Diffuse Solar Transmittance"    ),
        ("ClampedFloatSocket","Diffuse Visible Transmittance"  ),
        ("ClampedFloatSocket","Thermal Transmittance"          )]
    skts__SSc = [ # sockets shared by Shades and Screens
        ("ClampedFloatSocket","Thermal Emissivity","",[0.05,0.00001,0.99999])]
    # sockets shared by Blinds and Screens # spacing: Slat-, Wire-,
    skts__BSc = [("ClampedFloatSocket","Spacing (mm)","", [25, 0.1, 1000])]
    ## privat
    # sockets used only by Shades
    skts__S = [ ("ClampedFloatSocket", "AirFlow-Permeability", "", [0.1, 0, 1])]
    # sockets used only by Blinds
    skts__B = [ ("EnumSocket", "Orientation"),
    ("ClampedFloatSocket","Slat-Width (mm)", "", [  25, 0.1, 1000]),
    ("ClampedFloatSocket","Slat-Angle (deg)","", [45.0, 0.0,  180]),

    ("ClampedFloatSocket","Direct Solar Transmittance"        ),
    ("ClampedFloatSocket","Direct Visible Transmittance"      ),

    ("ClampedFloatSocket","Direct Solar Reflectance",  "", 0.8),
    ("ClampedFloatSocket","Direct Visible Reflectance","", 0.7),
    ("ClampedFloatSocket","Thermal Reflectance",       "", 0.9),

    ("ClampedFloatSocket","Direct Solar Reflectance(Backside)",   "", 0.8),
    ("ClampedFloatSocket","Direct Visible Reflectance(Backside)", "", 0.7),
    ("ClampedFloatSocket","Diffuse Solar Reflectance(Backside)",   "", 0.8),
    ("ClampedFloatSocket","Diffuse Visible Reflectance(Backside)", "", 0.7),
    ("ClampedFloatSocket","Thermal Reflectance(Backside)",      "", 0.9)]
    # sockets used only by Screens
    skts__Sc = [("EnumSocket","Accounting Method"),
                ("EnumSocket","Angle of Resolution")]
    skts_S_ALL  = skts__S  + skts__SSc + skts__SB  + skts__SBSc
    skts_B_ALL  = skts__B  + skts__BSc + skts__SB  + skts__SBSc
    skts_Sc_ALL = skts__Sc + skts__BSc + skts__SSc + skts__SBSc

    skts__def = skts__SBSc

    skts__ALL   = skts__basic[:2] + skts__BSc + skts__B[1:3] + skts__S
    skts__ALL  += skts__basic[2:] + [skts__B[0]] + skts__Sc  + skts__oMod
    skts__ALL  += skts__B[3:5]    + skts__SB     + skts__SSc + skts__B[5:7]
    skts__ALL  += skts__difRefl   + skts__B[7: ]

    skts__trans = [skt for skt in skts__ALL if "Transmittance" in skt[1]]
    skts__refl  = [skt for skt in skts__ALL if "Reflectance"   in skt[1]]


    ### INIT
    ### WICHTIG: init, nicht __init__. Sonst kein context
    def init(self, context):
        self.outputs.new("EnViShadeSocket", "Shade")
        setUpSockets(self, self.skts__ALL,  True)
        # request the drawing of and access to minimum and maximium value
        self.inputs["Slat-Angle (deg)"].valueOnly=False
        self.upd_layout() # force layout-update

    def export(self):
        SHADE_TYPE = self.SHADE_TYPE
        RET  = [ ("Type", SHADE_TYPE), ("Name", self.NAME)]

        if SHADE_TYPE not in ["Blind","Shade","Screen"]:
            raise ValueError("""ShadeType not in provided ShadeType-Values
            expected: {}
            got this: {}
            Please check the parameter 'Shade Type' in node@nodetree:
                {}""".format(['Blind', 'Shade', 'Screen'], Type, self.nodeid))
        if SHADE_TYPE == "Shade" : RET += self.export_S()
        if SHADE_TYPE == "Blind" : RET += self.export_B()
        if SHADE_TYPE == "Screen": RET += self.export_Sc()
        return OrderedDict( RET)
    def export_Sc(self):
        diameter= self.inputs["Wire-Thickness (mm)"].default_value
        spacing = self.inputs["Wire-Spacing (mm)"  ].default_value

        if spacing<=diameter: spacing = 1.5*diameter

        ALL = [
            ("Reflected Beam Transmittance Accounting Method",
                self.inputs["Accounting Method"].default_value),

            ("SolarDiff-Refl.F.", self.inputs[
                "Diffuse Solar Reflectance"].default_value),
            ("VisibDiff-Refl.F.", self.inputs[
                "Diffuse Visible Reflectance"].default_value),

            ("Thermal Emissivity", self.inputs["Thermal Emissivity"].default_value),

            ("Conductivity (W/(m*K))", self.inputs[
                "Conductivity (W/(m*K))"].default_value),

            ("Wire-Spacing (m)", spacing/1000),
            ("Wire-Thickness (m)", self.inputs[
                "Wire-Thickness (mm)"].default_value/1000),

            ("Screen2Glass-distance (m)", self.inputs[
                "Distance to glass (mm)"].default_value/1000),

            ("Opening Multiplier.T", self.inputs[
                "Opening Multiplier Top"   ].default_value),
            ("Opening Multiplier.B", self.inputs[
                "Opening Multiplier Bottom"].default_value),
            ("Opening Multiplier.L", self.inputs[
                "Opening Multiplier Left"  ].default_value),
            ("Opening Multiplier.R", self.inputs[
                "Opening Multiplier Right" ].default_value),

            ("Angle of Resolution for Output Map (deg)", self.inputs[
                "Angle of Resolution"].default_value),
            ]
        return ALL
    def export_B(self):
        ALL = [
            ("Orientation", self.inputs["Orientation"].default_value),

            ("Slat-Width", self.inputs["Slat-Width (mm)"].default_value/1000),
            ("Slat-Separation (m)", self.inputs[
                "Slat-Spacing (mm)"].default_value/1000),
            ("Slat-Thickness (m)", self.inputs[
                "Slat-Thickness (mm)"].default_value/1000),
            ("Slat-Angle (deg)", self.inputs[
                "Slat-Angle (deg)"].default_value),
            ("Slat-Conductivity (W/(m*K))", self.inputs[
                "Conductivity (W/(m*K))"].default_value),

            ("Direct Solar Transmittance", self.inputs[
                "Direct Solar Transmittance"].default_value),
            ("Direct Solar Reflectance(Frontside)", self.inputs[
                "Direct Solar Reflectance"].default_value),
            ("Direct Solar Reflectance(Backside)", self.inputs[
                "Direct Solar Reflectance(Backside)"].default_value),

            ("Diffuse Solar Transmittance", self.inputs[
                "Diffuse Solar Transmittance"].default_value),
            ("Diffuse Solar Reflectance(Frontside)", self.inputs[
                "Diffuse Solar Reflectance"].default_value),
            ("Diffuse Solar Reflectance(Backside)", self.inputs[
                "Diffuse Solar Reflectance(Backside)"].default_value),

            ("Direct Visible Transmittance", self.inputs[
                "Direct Visible Transmittance"].default_value),
            ("Direct Visible Reflectance(Frontside)", self.inputs[
                "Direct Visible Reflectance"].default_value),
            ("Direct Visible Reflectance(Backside)", self.inputs[
                "Direct Visible Reflectance(Backside)"].default_value),

            ("Diffuse Visible Transmittance", self.inputs[
                "Diffuse Visible Transmittance"].default_value),
            ("Diffuse Visible Reflectance(Frontside)", self.inputs[
                "Diffuse Visible Reflectance"].default_value),
            ("Diffuse Visible Reflectance(Backside)", self.inputs[
                "Diffuse Visible Reflectance(Backside)"].default_value),

            ("Thermal Transmittance",   self.inputs[
                "Thermal Transmittance"].default_value),
            ("Thermal Reflectance(Frontside)",   self.inputs[
                "Thermal Reflectance"].default_value),
            ("Thermal Reflectance(Backside)",   self.inputs[
                "Thermal Reflectance(Backside)"].default_value),

            ("Blind2Glass-distance (m)", self.inputs[
                "Distance to glass (mm)"].default_value/1000),
            ("Opening Multiplier.T", self.inputs[
                "Opening Multiplier Top"   ].default_value),
            ("Opening Multiplier.B", self.inputs[
                "Opening Multiplier Bottom"].default_value),
            ("Opening Multiplier.L", self.inputs[
                "Opening Multiplier Left"  ].default_value),
            ("Opening Multiplier.R", self.inputs[
                "Opening Multiplier Right" ].default_value),

            ("Slat-Angle-Minimium", self.inputs["Slat-Angle (deg)"].min_value),
            ("Slat-Angle-Maximum",  self.inputs["Slat-Angle (deg)"].max_value),
            ]
        return ALL
    def export_S(self):
        ALL = [
            ("SolarDiff-Transm.", self.inputs[
                "Diffuse Solar Transmittance"].default_value),
            ("SolarDiff-Refl.F.", self.inputs[
                "Diffuse Solar Reflectance"].default_value),

            ("VisibDiff-Transm.", self.inputs[
                "Diffuse Visible Transmittance"].default_value),
            ("VisibDiff-Refl.F.", self.inputs[
                "Diffuse Visible Reflectance"].default_value),
            ("Thermal Emissivity",self.inputs[
                "Thermal Emissivity"].default_value),
            ("Thermal-Transm.",   self.inputs[
                "Thermal Transmittance"].default_value),

            ("Thickness (m)", self.inputs[
                "Shade-Thickness (mm)"].default_value/1000),
            ("Conductivity (W/(m*K))", self.inputs[
                "Conductivity (W/(m*K))"].default_value),

            ("Shade2Glass-distance (m)", self.inputs[
                "Distance to glass (mm)"].default_value/1000),

            ("Opening Multiplier.T", self.inputs[
                "Opening Multiplier Top"   ].default_value),
            ("Opening Multiplier.B", self.inputs[
                "Opening Multiplier Bottom"].default_value),
            ("Opening Multiplier.L", self.inputs[
                "Opening Multiplier Left"  ].default_value),
            ("Opening Multiplier.R", self.inputs[
                "Opening Multiplier Right" ].default_value),

            ("AirFlow-Permeability", self.inputs[
                "AirFlow-Permeability"].default_value)
            ]
        return ALL

    def draw_buttons(self, context, layout):       # Darstellung
        ERRS = [] # errortracking for display on node.
        SHADE_TYPE = self.SHADE_TYPE

        invalid_chars = " ".join([s for s in ",;!#" if s in self.name])
        if invalid_chars:
            ERRS.append(["Prohibited chars found: {}".format(invalid_chars),
                         "Name must not contain any of these chars: . , ; ! #"])
        layout.row().prop(self, "name", text="Name")# reusing the unique node-name as shade material name
        layout.row().prop(self, self.layout_enum)

        slts = [skt for skt in self.inputs if skt.name.endswith("Thickness (mm)")  ]
        slss = [skt for skt in self.inputs if skt.name.endswith("Spacing (mm)")]
        if len(slss) + len(slts) < 2 or SHADE_TYPE=="Shade": pass
        elif   slss[0].default_value < slts[0].default_value:
            prep = ["Slat-","Wire-"][SHADE_TYPE == "Screen"]
            ERRS.append(["'{}-Spacing' must be equal to".format(prep),
                         "or bigger than '{}-Thickness'".format(prep)])

        if ERRS!=[]:
            lbox = layout.row().box()
            lbox.label(text="ERROR{}:".format(["","S"][len(ERRS)>1]))
#            self.use_custom_color, self.color = 1, (1, 0.2, 0.2, 0.2) # geht nur in update-funktionen
            for err in ERRS:
                if err != []:
                    box = lbox.box()
                    for e in err: box.row().label(text=e)
        return

### ShadingControls
class EnViShadConNode(bpy.types.Node, EnViNodes):
    """Node defining a shading device material"""
    bl_idname = 'EnViShadConNode'
    bl_label  = 'ShadingControl'
    bl_icon   = 'SOUND'

    ### update-functions. They MUST stay on top
    def update(self):
        if not self.initialised: return
        self.upd_placement()
        self.upd_layout()
#        self.outputs["Shade"].hide = not self.HAS_SHADE # shade wird aktuell zerstoert
    def upd_layout(self, context=""):
        ''
        ### Schedule
        if "Schedule" in self.inputs.keys():
            skt = self.inputs["Schedule"]
            skt.hide = self.CONTROL in [self.ctypes[i] for i in [0,1]]
            if self.CONTROL!="OnIfScheduleAllows":
                skt.name = "Schedule (optional)"
        elif "Schedule (optional)" in self.inputs.keys():
            skt = self.inputs["Schedule (optional)"]
            skt.hide = self.CONTROL in [self.ctypes[i] for i in [0,1]]
            if self.CONTROL=="OnIfScheduleAllows":
                skt.name = "Schedule"
        ### SetPoints
        # art von SetPoint1 definieren
        spt1=0
        if   self.CONTROL in [self.ctypes[i] for i in [0,1,2,]]: spt1 = 0 # NONE
        elif self.CONTROL in [self.ctypes[i] for i in [5,6,8,9,11,-4,-3,-2,-1]]: spt1 = 1 # degC
        elif self.CONTROL in [self.ctypes[i] for i in [7,10,12   ]]: spt1 = 2 # W
        elif self.CONTROL in [self.ctypes[i] for i in [3,4,13,14 ]]: spt1 = 3 # W/m2
        # benennung korrigieren
        sp_skts = [name for name in self.inputs.keys() if name.startswith("SetPoint1")]
        if sp_skts!=[]:
            # verzoegerung beim erzeugen beruecksichtigt
            skt = self.inputs[sp_skts[0]]
            if spt1==0:
                if skt.is_linked:
                    self.node_tree.links.remove(skt.links[0])
                skt.hide = True
            else:
                skt.hide = False
                skt.name = "SetPoint1{}".format([""," (degC)"," (W)"," (W/m2)"][spt1])

        if "SetPoint2 (W/m2)" in self.inputs.keys():
            # verzoegerung beim erzeugen beruecksichtigt
            skt = self.inputs["SetPoint2 (W/m2)"]
            if self.CONTROL in self.ctypes[-4:]:
                skt.hide = False
            else:
                if skt.is_linked:
                    self.node_tree.links.remove(skt.links[0])
                skt.hide = True
    def upd_enumSocket(self, context):
        """This funktion may only be used in update-calls for EnumSocketProps.
        Any function that accepts self, and context and does NOT set/update
        the EnumSocketProp can be added to the hooks.
        (WARNING:no recursion-check)
        To do so create an optional dictionary 'node.ENUM_HOOKS' in this style:
        ENUM_HOOKS={socket.name:[function(node, context)]}"""
        skt = context.socket
        var = self.ENUM.get(skt.name,None)
        if not var==None: skt.default_value = getattr(self, var,"")
        enum_hooks = getattr(self, "ENUM_HOOKS",{})
        hooks = enum_hooks.get(skt.name, [])
        for hook in hooks: hook(self, context)
    def upd_placement(self, context=""):
        """Swaps the EnumProperties to replace their appearent possibillities"""
        name = "Placement"
        if self.SHADE_TYPE=="Screen": self.ENUM[name]="placement_Sc"
        else: self.ENUM[name]="placement"
        return

    ### PROPS
    initialised : bpy.props.BoolProperty(default=False)# wurde das objekt fertig gestellt
    shade_type : bpy.props.EnumProperty( # art der Verschattung
        items =[("Blind",   "Blind",    "Venetian Blinds"),
                ("Shade",   "Shade",    "Shade"          ),
                ("Screen",  "Screen",   "Mosquito-Screen"),
               ],
        name    ="Shade Type",
        default ="Blind",
        update  =upd_placement)

    ### EnumSocketProps
    ENUM = {"Control Type":"control_type", "Placement":"placement",
            "Slat-Control":"slatAngleControl"}
    ENUM_HOOKS={"Slat-Control":[upd_layout],
            "Control Type":[upd_layout]}

    slat_items=[("FixedSlatAngle",       "FixedSlatAngle",
                "Slats wont be controlled"),
               ("ScheduledSlatAngle",   "ScheduledSlatAngle",
                "Slats follow an angle-schedule (deg)"),
               ("BlockBeamSolar",       "BlockBeamSolar",
                "Slats rotate to block direct beams of sunlight.")
              ]
    slatAngleControl : bpy.props.EnumProperty(
        items=slat_items[:],
        default="FixedSlatAngle",
        update =upd_enumSocket)
    placement_items =[("Interior", "internal",
                 "The shading device is placed on the inside of the window"),
                ("Exterior", "external",
                 "The shading device is placed on the outside of the window"),
                ("BetweenGlass" , "between" ,
                 "The shading device is placed between the inner two sheets of the window")]

    placement   : bpy.props.EnumProperty( # art der Verschattung
        items   = placement_items[:],
        name    ="Placement",
        default ="Exterior",
        update  =upd_enumSocket)
    placement_Sc : bpy.props.EnumProperty( # art der Verschattung
        items   = [placement_items[1]], # extern
        name    ="Placement",
        default ="Exterior",
        update  =upd_enumSocket)
    ctypes = ["AlwaysOn",
              "AlwaysOff",
        "OnIfScheduleAllows",                               #
        "OnIfHighSolarOnWindow",                            # Cool
        "OnIfHighHorizontalSolar",                          # Cool
        "OnIfHighOutdoorAirTemperature",                    # Cool
        "OnIfHighZoneAirTemperature",                       # Cool
        "OnIfZoneCooling",                                  # Cool
        "OnNightIfLowOutdoorTempAndOffDay",                 # heat
        "OnNightIfLowInsideTempAndOffDay",                  # heat
        "OnNightIfHeatingAndOffDay",                        # heat
        "OnNightIfLowOutdoorTempAndOnDayIfCooling",         # heat+cool
        "OnNightIfHeatingAndOnDayIfCooling",                # heat+cool
        "OffNightAndOnDayIfCoolingAndHighSolarOnWindow",    # cool
        "OnNightAndOnDayIfCoolingAndHighSolarOnWindow",     # cool
        "OffNightAndOnDayIfCoolingAndHighHorizontalSolar",  # -
        "OnNightAndOnDayIfCoolingAndHighHorizontalSolar",   # -

        "OnIfHighOutdoorAirTempAndHighSolarOnWindow",       # cool
        "OnIfHighOutdoorAirTempAndHighHorizontalSolar",     # cool
        "OnIfHighZoneAirTempAndHighSolarOnWindow",          # cool
        "OnIfHighZoneAirTempAndHighHorizontalSolar"]        # cool

    control_type : bpy.props.EnumProperty( # art der Verschattungs-steuerung
        items =[( "AlwaysOn",  "Always On" , ""),
                ("AlwaysOff",  "Always Off", ""),
                ("OnIfScheduleAllows", "Schedule",""),
            ]+[(s,s,"\n".join(["Read at https://energyplus.net/sites/all/",
                    "modules/custom/nrel_custom/pdfs/pdfs_v8.5.0/",
                    "InputOutputReference.pdf page 348"]))for s in ctypes[3:]],
        name    ="Control Types",
        default ="OnIfHighSolarOnWindow",
        update  =upd_enumSocket)

    ### Output-Declaration
    ## ShadeDevice musst have the identical(!) name for input and output
    #   or requesting the Shade will raise an error
    skts_out = [("EnViControlSocket", "Control"),
                ("EnViShadeSocket",   "Shade"  )]
    ### Input -Declaration
    skts_in  = [
        ("EnViShadeSocket", "Shade"),
        ("EnumSocket",      "Control Type"),
        ("EnumSocket",      "Placement"),
        ("So_En_Sched",     "Schedule"), # bl_idname changed since the v04x versions

        ("NodeSocketFloat", "SetPoint1 (degC)", "", 180),
        ("EnumSocket",      "Slat-Control"),
        ("So_En_Sched",     "Angle-Schedule"),
        ("NodeSocketFloat", "SetPoint2 (W/m2)")]

    ### utility
    def getSched(self, sched): # scheduleNode or None
        if sched in self.inputs.keys():
            skt = self.inputs[sched]
            if skt.is_linked: return skt.links[0].from_node
            return None
        return None

    ### GETTER&SETTER
    @property # matching with EnViShadDevNode
    def SHADE_TYPE(self): # allows the socket to check ### anpassen?
        Shade = self.inputs["Shade"]# allows to link multiple in row
        if self.HAS_SHADE: return Shade.links[0].from_socket.SHADE_TYPE
        return self.shade_type
    @property # PLACEMENT + SHADE_TYPE => field2
    def PLACEMENT(self):
        val = self.inputs["Placement"].default_value
        return val if val in [item[0] for item in self.placement_items] else "Exterior"
    @property # shading-controltype     => field4
    def CONTROL(self):
        val = self.inputs["Control Type"].default_value
        if val not in [base for base in self.ctypes]: val = self.ctypes[2]
        if self.SHADE_TYPE == "Screen" and val not in self.ctypes[:3]:
            if self.C_SCHEDULE: return self.ctypes[2]
            else:               return self.ctypes[0]
        return val
    @property # control-schedule        => field5
    def C_SCHEDULE(self): # schedule or None
        needed = self.getSched("Schedule")
        option = self.getSched("Schedule (optional)")
        return needed if needed!=None else option
    @property # angle-controltype       => field10
    def S_CONTROL(self):
        if "Slat-Control" in self.inputs.keys() and self.SHADE_TYPE=="Blind":
            skt = self.inputs["Slat-Control"]
            val = skt.default_value
            if skt.is_linked:
                return val if val in [item[0] for item in self.slat_items] else None
            return getattr(self, self.ENUM.get("Slat-Control","False"), None)
        return None
    @property # angle-schedule          => field11
    def A_SCHEDULE(self): # schedule or None
        return self.getSched("Angle-Schedule")
    @property
    def HAS_SHADE(self):
        Shade = self.inputs["Shade"]
        if Shade.is_linked:
            if Shade.links[0].is_valid: return True
        return False
    @property
    def node_tree(self): # gets its parent nodetree
        return [ng for ng in bpy.data.node_groups if self in ng.nodes[:]][0]

    def init(self, context):
        setUpSockets(self, self.skts_out, False, True)
        setUpSockets(self, self.skts_in,  True)
        self.initialised = True # das object wurde fertig gestellt
        self.upd_layout() # Layout-Update erzwingen

    def export(self):
        ALL = OrderedDict([
            ("Name",        self.name       ), # name                           =>field1
            ("ShadeType",   self.SHADE_TYPE ), # shade type
            ("Placement",   self.PLACEMENT  ), # placement                      =>field2
            ("Control",     self.CONTROL    ), # control                        =>field4
            ("Schedule",    self.C_SCHEDULE )])# scheduleNode oder none         =>field5

        # art von SetPoint1 definieren
        spt1=0
        if   self.CONTROL in [self.ctypes[i] for i in [0,1,2,]]: spt1 = 0 # NONE
        elif self.CONTROL in [self.ctypes[i] for i in [5,6,8,9,11,-4,-3,-2,-1]]: spt1 = 1 # degC
        elif self.CONTROL in [self.ctypes[i] for i in [7,10,12   ]]: spt1 = 2 # W
        elif self.CONTROL in [self.ctypes[i] for i in [3,4,13,14 ]]: spt1 = 3 # W/m2

        if spt1==0: #                                                           =>field6
            ALL.update({"SetPoint1" : None})
            ALL.update({"spt"       : ""  })
        else:
            sspt = [""," (degC)"," (W)"," (W/m2)"][spt1]
            ALL.update({"SetPoint1": [skt for skt in self.inputs if skt.name.startswith("SetPoint1")][0].default_value})
            ALL.update({"spt": sspt})
        ALL.update({"Is Control scheduled?":["YES","NO"][self.C_SCHEDULE==None]})#       =>field7
        ALL.update({"Is Glare-Control aktive?":    "NO"}                        )#       =>field8
        if self.HAS_SHADE:#                                                     =>field9
            ALL.update({"ShadingDeviceMaterial":self.inputs["Shade"].SHADE.name})
        else:
            ALL.update({"ShadingDeviceMaterial":None})
        ALL.update({"SlatAngleControl":    self.S_CONTROL })# inputs["Slat-Control"]),  =>field10
        ALL.update({"SlatAngleSchedule":   self.A_SCHEDULE})# scheduleNode oder None    =>field11
        if self.CONTROL in self.ctypes[-4:]:#                                           =>field12
            ALL.update({"SetPoint2 (W/m2)": self.inputs["SetPoint2 (W/m2)"].default_value})
        else:
            ALL.update({"SetPoint2 (W/m2)": None})
        return ALL

    def draw_buttons(self, context, layout):
        ERRS = []

        invalid_chars = " ".join([s for s in ",;!#" if s in self.name])
        if invalid_chars:
            ERRS.append(["Prohibited chars found: {}".format(invalid_chars),
                         "Name must not contain any of these chars: . , ; ! #"])

        layout.prop(self, "name", text="Name")
        if not self.HAS_SHADE:
            layout.prop(self, "shade_type")
            if "Shade" in self.outputs.keys():
                self.outputs.remove(self.outputs["Shade"])
        elif   "Shade" not in self.outputs.keys():
            self.outputs.new("EnViShadeSocket", "Shade")
        ## setpoints werden nur versteckt
        # SHADE_TYPE kann auch extern definiert werden.
        # hier kann leider nicht versteckt werden
        if self.SHADE_TYPE == "Blind":
            if "Slat-Control" not in self.inputs.keys():
                self.inputs.new( "EnumSocket", "Slat-Control")
            if "Slat-Control" in self.inputs.keys():
                if self.S_CONTROL=="ScheduledSlatAngle":
                    if "Angle-Schedule" not in self.inputs.keys():
                        self.inputs.new(*self.skts_in[-2])# add Angle-Schedule
                        # self.inputs.move(-1, -2)        # restore order
                else:
                    if "Angle-Schedule" in self.inputs.keys():
                        self.inputs.remove(self.inputs["Angle-Schedule"])
            else:
                if "Angle-Schedule" in self.inputs.keys():
                    self.inputs.remove(self.inputs["Angle-Schedule"])
        else:
            if "Slat-Control" in   self.inputs.keys():
                self.inputs.remove(self.inputs["Slat-Control"])
            if "Angle-Schedule" in self.inputs.keys():
                self.inputs.remove(self.inputs["Angle-Schedule"])

        if ERRS!=[]:
            lbox = layout.row().box()
            lbox.label(text="ERROR{}:".format(["","S"][len(ERRS)>1]))
            for err in ERRS:
                if err != []:
                    box = lbox.box()
                    for e in err: box.row().label(text=e)
        return

### ShadedWindows
class EnViShadWinNode(bpy.types.Node, EnViNodes):
    """Node defining a shading device material"""
    bl_idname = 'EnViShadWinNode'
    bl_label  = 'ShadedWindow'
    bl_icon   = 'SOUND'
    ### upd
    def upd_faces(self, context=""):
        self.faces.clear()
        self.zones.clear() # (EP-9-3-0)
        used = self.forbidden_faces
        # get objects, sorted by name
        #objs = sorted(bpy.context.visible_objects, key=lambda o:o.name)
        objs = sorted(bpy.data.collections["EnVi Geometry"].all_objects, key=lambda o:o.name)
        for obj in objs: ## all vi-zone - objekte
            if all((obj.type=='MESH',  # obj.layers[1], # this is handled by visibility
                   # obj.vi_params.vi_type=='1',     # it is an envi-surface
                   # obj.vi_params.envi_type=='0',   # it is a constructions
                    True)):
                # get polygons, sorted by index
                faces = sorted([face for face in obj.data.polygons],
                                key=lambda f:f.index)
                for face in faces:
                    mat = obj.data.materials[face.material_index]
                    if mat.name==self.mat_def: # store 'faceID'
                        #facename="{}@{}".format(face.index, obj.name)# vi-04
                        facename="{}_{}".format(obj.name, face.index)# vi-06
                        FACE = self.faces.add()
                        FACE.name = facename
                        FACE.use  = not facename in used
                self.zones.add().name = obj.name # attatch zone
    ### props
    zones   : bpy.props.CollectionProperty(type=EnVi_Multiple)
    faces   : bpy.props.CollectionProperty(type=EnVi_Multiple)
    mat_def : bpy.props.StringProperty(default="", update=upd_faces,
                description="Which material to use.")
    c_zone  : bpy.props.StringProperty(default="", name="zone",
                description="Which zone to use this shading system for.") # draw zone to use here...
    priority: bpy.props.IntProperty(min=1, max=99, default=1,
                description="Which shading system of a zone reacts first.\n"
                "Starting by #1 closing first.")
    ### GETTER&SETTER
    @property # all faces that are used by this node right now
    def used_faces(self): return [f.name for f in self.faces if f.use ==True]
    @property
    def node_tree(self): # gets its parent nodetree
        return [ng for ng in bpy.data.node_groups if self in ng.nodes[:]][0]
    @property
    def forbidden_faces(self):
        return [ fn for node in self.node_tree.nodes
                    if node.bl_idname==self.bl_idname
                    for fn in node.used_faces if node!=self]
    ### inputs
    skts_in  = [("EnViControlSocket", "Control"),
                ("EnViShadeSocket",   "Shade"  )]
    ### init
    def init(self, context):
        setUpSockets(self, self.skts_in,  True)
        update_shaded_materials(self.node_tree) # force material-update
    ### export
    def export(self):
        ALL = OrderedDict([
            ("Shade",   self.inputs[ "Shade" ].SHADE),
            ("Control", self.inputs["Control"].CONTROL),
            ("Material",self.mat_def),
            ("Zone",    self.c_zone),   # EP-9-3
            ("Priority",self.priority), # EP-9-3
            ("Faces",   self.used_faces)
        ])
        return ALL
    ### draw
    def draw_buttons(self, context, layout):
        layout.prop_search(self, 'mat_def',
                           self.node_tree, 'envi_shaded_materials',
                           icon='MATERIAL')
        layout.prop_search(self, 'c_zone',
                           self, 'zones',
                           icon='CUBE') # TODO: flop faces that are not in here...
        layout.prop(self, 'priority')
        for face in self.faces:
            use = face.use
            if face.name not in self.forbidden_faces:
                layout.row().prop(face, "use", text=face.name, toggle=1)

        ERRS = []
        invalid_chars = " ".join([s for s in ",;!#" if s in self.name])
        if invalid_chars:
            ERRS.append(["Prohibited chars found: {}".format(invalid_chars),
                         "Name must not contain any of these chars: . , ; ! #"])

        for skt in self.inputs:
            if not skt.is_linked: ERRS.append(["'{}' must be connected".format(skt.name)])
        if not self.c_zone: ERRS.append(["Zone not set.","Please set a zone."])
        if ERRS!=[]:
            lbox = layout.row().box()
            lbox.label(text="WARNING{}:".format(["","S"][len(ERRS)>1]))
#            self.use_custom_color, self.color = 1, (1, 0.2, 0.2, 0.2) # geht nur in update-funktionen
            for err in ERRS:
                if err != []:
                    box = lbox.box()
                    for e in err: box.row().label(text=e)
            lbox.row().label(text="These windows will be ignored")
        return
    def copy(self, oldnode):
        """applies changes to itself after being derived from oldnode"""
        self.mat_def = oldnode.mat_def # force faces-update
        return None


### Simple Value-Input-Node
class EnViFloatNode(bpy.types.Node, EnViNodes):
    """Reimplementation of the FloatValue-Node known from shaders"""
    bl_idname = 'EnViFloatNode'
    bl_label  = 'Value'
    bl_icon   = 'SOUND'

    def update(self):
        if "Value" in self.outputs:
            for l in self.outputs[0].links:
                getattr(l.to_node, "update", lambda x="":None)()
    def init(self, context):
        self.outputs.new('NodeSocketFloat',"Value")
    def draw_buttons(self, context, layout):
        layout.prop(self.outputs[0],"default_value",text="")
### Clamped-Float-Input-Node
class EnViCFloatNode(bpy.types.Node, EnViNodes):
    """Adds a Clamped-FloatValue-Node"""
    bl_idname = 'EnViCFloatNode'
    bl_label  = 'Clamped Value'
    bl_icon   = 'SOUND'

    def update(self):
        if "Value" in self.outputs:
            for l in self.outputs[0].links:
                getattr(l.to_node, "update", lambda x="":None)()
    def init(self, context):
        self.outputs.new('ClampedFloatSocket',"Value")
    def draw_buttons(self, context, layout):
        layout.prop(self.outputs[0],"true_default_value",text="Value",index=0)
        row = layout.row()
        row.prop(   self.outputs[0],"true_default_value",text="Min",  index=1)
        row.prop(   self.outputs[0],"true_default_value",text="Max",  index=2)
### String-Input-Node
class EnViStringNode(bpy.types.Node, EnViNodes):
    """Implementation of a StringValue-Node.
    Strings can be used to set/control enum-sockets"""
    bl_idname = 'EnViStringNode'
    bl_label  = 'String Value'
    bl_icon   = 'SOUND'

    def update(self):
        if "Value" in self.outputs:
            for l in self.outputs[0].links:
                getattr(l.to_node, "update", lambda x="":None)()
    def init(self, context):
        self.outputs.new('NodeSocketString',"Value")
    def draw_buttons(self, context, layout):
        layout.prop(self.outputs[0],"default_value", text="")
##### } Patch-Nodes

# END PATCH-Nodes => shading-device (HBC)
#'''

# this tuple is needed for registration purposes (done by vi-suite/__init__)
shading_device_classes = (# the nodetree is already listet by vi-suite/__init__
    EnViShadeSocket, EnViControlSocket, ClampedFloatSocket, EnumSocket,# sockets
    EnViShadDevNode, EnViShadConNode,   EnViShadWinNode,    # Shading Nodes
    EnViFloatNode,   EnViCFloatNode,    EnViStringNode  )   # Simple input nodes

### PATCH - Categories  => shading-device (HBC)
envinode_categories.extend([
    EnViNodeCategory("ShadNotes",   "Shade Nodes", items=[
        NodeItem("EnViShadDevNode", label="ShadingDevice"),
        NodeItem("EnViShadConNode", label="ShadingControl"),
        NodeItem("EnViShadWinNode", label="ShadedWindows")]),
    EnViNodeCategory("InputNodes",  "Basic Input Nodes", items=[
        NodeItem("EnViFloatNode",   label="Float Value"),
        NodeItem("EnViCFloatNode",  label="ClampedFloat Value"),
        NodeItem("EnViStringNode",  label="String(or Enum) Value")])
    ])
