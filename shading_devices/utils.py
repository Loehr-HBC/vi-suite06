### AUTOR: Felix Loehr                                                       ###
### EMAIL: felix_loehr@yahoo.de                                              ###
###                                                                          ###
### LICENCE: either GNU-LGPL version                                         ###
###          Or     CC-BY                                                    ###
###          (at your choice)                                                ###
###                                                                          ###
### ADDITIONAL: You are requested(!) to share a unmodified version           ###
###             of this script with your work, if you derive parts           ###
###             of your work from it.                                        ###
############################################################### 80 CHAR MARGIN #

# THIS WAS MEANT FOR VI-SUITE 0.4.6

from ..vi_func import newrow
CUSTOM_Mat_Props    = [ 'name', 0, 'thi', 'tc', 0, 'rho', 'shc',
                                0, 'tab', 'sab', 0, 'vab', 'rough']
CUSTOM_WinMat_Props = [0, 'thi', 'tc', 0, 'stn', 'fsn', 'bsn',
                       0, 'vtn', 'fvrn', 'bvrn', 0, 'itn', 'fie', 'bie']
import bpy

class DATABLOCK():
    def __init__(self):
        return

def DUMMY_readData():
    '''Fakes the readout of data for the Shade-Patch'''
    return DATABLOCK()

def box_props(layout, root, props=[], base=""):
    '''DOES:  Places props in pseudo-tabelaric fashion
       TAKES: layout
       root  - (origin of property),
       props - (list of property-names and 0s (for newline))
       base  - (basestring for long property-names;"")'''
    row = layout.row()
    for end in props:
        if end: row.prop(root, '{}{}'.format(base, end))
        else:   row = layout.row()

def MaterialLayout(layout, root, layer_idx=0, previous_material="", Mat_Props=None, WinMat_Props=None):
    '''    This funktion provides a layout-default.
    It exists for the mere purpose of enhancing readability,
    and customizability.
    Inputs:
      layout
      root (here cm)
      layer_idx=0 (index of layer. 0 is outside, ...)
      previous_material="" (Glass-Layer vs Gas-Layern oder Shade-Layer.)
      Mat_Props=['name', 0, 'thi', 'tc',  0, 'rho',
                 'shc',  0, 'tab', 'sab', 0, 'vab', 'rough']
          (Properties for CUSTOM materials, 0 for linebreak)
      WinMat_Props=[0, 'thi', 'tc', 0, 'stn', 'fsn', 'bsn',
                    0, 'vtn', 'fvrn', 'bvrn', 0, 'itn', 'fie', 'bie']
          (Properties for CUSTOM window materials, 0 for linebreak)
    Outputs:
      new_material ("Shade","Glass","Gas","GlassShaded" or "GasShaded")
                   (None for errors or if last layer done)'''

    ##### Vorbereitung #####
    ### Layer-Index - bezogene Kuerzel definieren
    if layer_idx>2: numtext = "{}th".format(          layer_idx + 1)
    else:           numtext = ["Outside","2nd","3rd"][layer_idx]
    if layer_idx==0:num     = "o"
    else:           num     = "{}".format(            layer_idx)
    ### Layer-Index - bezogene Werte abfragen
    layer_composition = getattr(root, "envi_layer{}".format( num), None)
    layer_MatClass    = getattr(root, "envi_type_l{}".format(num), None)
    if    Mat_Props==None:    Mat_Props = CUSTOM_Mat_Props
    if WinMat_Props==None: WinMat_Props = CUSTOM_WinMat_Props
    ### Layer-Indices ausschliessen, wenn zu hoch
    if layer_composition==None or layer_MatClass==None:
        return None

    ##### Anfang des eigentlichen Layouts
    row = layout.row()
    if layer_idx>=1:row.label("----------------")
    newrow(layout, "{} layer:".format(numtext), root,"envi_layer{}".format(num))
    ### Abfrage nach der Art des Aufbaus des Layers.
    if layer_composition == '1': ##### DATABASE
        if root.envi_con_type == "Window":
            if previous_material == "Glass": ### Gas
                row = layout.row()
                row.label("Gas Type:")
                row.prop(root, "envi_export_wgaslist_l{}".format(num))
                row.prop(root, "envi_export_l{}_thi".format(num))
                new_material = "Gas"
            else:### Glass
                newrow(layout, "Glass Type:", root, "envi_export_glasslist_l{}".format(num))
                new_material = "Glass"
            return new_material
        elif root.envi_con_type in ("Wall", "Roof", "Floor", "Door"):
            newrow(layout, "{} layer type:".format(numtext), root, "envi_type_l{}".format(num))
            newrow(layout, "{} layer material:".format(numtext), root, "envi_export_{}list_l{}".format(
                ("brick", "cladding", "concrete", "metal", "stone", "wood", "gas", "insulation")[int(layer_MatClass)], num)) #####}
            newrow(layout, "{} layer thickness:".format(numtext), root, "envi_export_l{}_thi".format(num))
            return "" ### Damit klar ist dass Wall-types funktionieren

    elif layer_composition == '2': ##### CUSTOM
        if root.envi_con_type != 'Window': ##### Standart-Materialien
            box_props(layout, root, Mat_Props, "envi_export_l{}_".format(num))
            if layer_MatClass == '8':
                newrow(layout, "TCTC:", root, "envi_tctc_l{}".format(num))
                newrow(layout, "Temps:Enthalpies:", root, "envi_tempsemps_l{}".format(num))
            return "" ### Damit klar ist dass Wall-types funktionieren

        else: ##### Fenster
            newrow(layout, "Name:", root, "envi_export_l{}_name".format(num))
            if previous_material=="Glass": ### Gas
                newrow(layout, "Gas Type:", root, "envi_export_wgaslist_l{}".format(num))
                newrow(layout, "{} layer thickness:".format(numtext), root, "envi_export_l{}_thi".format(num))
                new_material = "Gas"
            else:### Glass
                newrow(layout, "Optical data type:", root, "envi_export_l{}_odt".format(num))
                newrow(layout, "Construction Make-up:", root, "envi_export_l{}_sds".format(num))
                newrow(layout, "Translucent:", root, "envi_export_l{}_sdiff".format(num))
                box_props(layout, root, WinMat_Props, "envi_export_l{}_".format(num))
                new_material = "Glass"
            return new_material

def setUpSockets(node, values, as_input=True, force=False):
    '''setUpSockets(node, values, as_input=True, force=False)
    sets up a bunch of sockets with data given in the list 'values'.
    'as_input' decides wether it will be an input, or an output, while 'force'
    will add a socket, even if the default-handling for this type is unknown.
    Each entry in 'values' starts with type and name, and optional identifier.
    After these an optional default is declared. Depending on type,
    these options apply:
        int or float: default_value    (str/int/float           )
        string      : default_value    (str                     )
        color       : grayscale        (float                   )
                      grayscale+alpha  (float-iterable, length 2)
                      color_RGB        (float-iterable, length 3)
                      color_RGB+alpha  (float-iterable, length 4)
        vector      : each achsis      (      iterable, length 3)
        clamped     : default (int/float) - ! may enlage clamp-range !
            default,min,max                 (number-iterable, length 3)
            default,min,max,titled,valueOnly([number,number,number,bool,bool])
        enum        : default_value    (str)/
            default, allowed ([str, string-iterable(e.g. lists)])
            ! empty lists for allowed will allow every string !'''
    floats=["NodeSocketFloat",
            "NodeSocketFloatAngle",
            "NodeSocketFloatFactor",
            "NodeSocketFloatPercentage",
            "NodeSocketFloatTime",
            "NodeSocketFloatUnsigned"]
    ints = ["NodeSocketInt",          #Gut
            "NodeSocketIntFactor",    #Schlecht
            "NodeSocketIntPercentage",#Schlecht
            "NodeSocketIntUnsigned"]  #Gut
    strs = ["NodeSocketString"]#default_value=""
    vecs = ["NodeSocketVector",
            "NodeSocketVectorAcceleration",
            "NodeSocketVectorDirection",
            "NodeSocketVectorEuler",
            "NodeSocketVectorTranslation",
            "NodeSocketVectorVelocity",
            "NodeSocketVectorXYZ"]
    bools = ["NodeSocketBool"]
    colors= ["NodeSocketColor"]
    ### envi
    envis = ["So_En_Sched"]# schedule, had been EnViSchedSocket in v04
    ### eigene
    clamped = [ "ClampedFloatSocket",
                "ClampedIntSocket",]
    clv=    ["ClampedFloatVSocket"]
    enums = ["EnumSocket"]
    shade = ["EnViShadeSocket"]
    control=["EnViControlSocket"]

    act = [node.outputs, node.inputs][as_input].new
    for val in values:
        identifier = ""
        default    = None
        typ = val[0]
        name= val[1]
        if len(val)>2: identifier = val[2]
        if len(val)>3: default    = val[3]
        if typ in bools:
            skt = act(typ,name,identifier)
            if default!=None: skt.default_value=bool(default)
        elif typ in strs:
            act(typ,name,identifier)
            if default!=None: skt.default_value="{}".format(default)
        elif typ in colors:
            skt = act(typ,name,identifier)
            if        default == None: default=[0,0,0,1]
            elif type(default)==  int: default=[default]*3+[1]
            elif type(default)==float: default=[default]*3+[1]
            elif len( default)==    2: default=[default[0]]*3+[default[1]]
            elif len( default)==    3: default=list(default)+[1]
            skt.default_value=default
        elif typ in floats:
            skt = act(typ,name,identifier)
            skt.default_value=[default,0.0][default==None]
        elif typ in ints:
            skt = act(typ,name,identifier)
            skt.default_value=[default,0][default==None]
        elif typ in vecs:
            skt = act(typ,name,identifier)
            if  default!=None:
                skt.default_value=list(default)
        elif typ in clamped:
            skt = act(typ,name,identifier)
            number = type(skt.default_value)
            if        default==None: default=[]
            elif type(default)in(int,float):
                default= number(default)
                default=[default,min(default,0),max(default,1)]

            if len( default)>=3:
                skt.default_value= default[0]
                skt.min_value    = default[1]
                skt.max_value    = default[2]
            if len( default)==5:
                skt.titled       = bool(default[3])
                skt.valueOnly    = bool(default[4])
        elif typ in enums:
            skt = act(typ,name,identifier)
            if default==None: pass#default=("",[])
            elif type(default)()=="": skt.default_value=default
            elif type(default)==list:
                skt.default_value = default[0]
                skt.allowed = default[1]
        elif typ in shade or typ in control:
            skt = act(typ, name, identifier)
        elif typ in envis or typ in control:
            skt = act(typ, name, identifier)
        elif force==True:
            skt = act(typ, name, identifier)

def socketid(skt): ### wie nodeid, nur fuer sockets ## reihenfolge umdrehen?
    for ng in bpy.data.node_groups:
        if skt.node in ng.nodes[:]:
            if skt.is_output: IO = "OUTPUT"
            else: IO = "INPUT"
            return "{}@{}@{}@{}".format(skt.name,IO,skt.node.name,ng.name)

def nodeById(ID): ### bisher nirgends verwendet # Nimmt nodeid oder socketid
    if ID.count('@')==3: ID = ID.split('@',2)[2]
    return bpy.data.node_groups[ID.split('@')[1]].nodes[ID.split('@')[0]]

### CollectionProp: materials for the shaded-window-node
class EnVi_Multiple(bpy.types.PropertyGroup):
    '''This provides a StringProperty 'name' and a BoolProperty named use.
    Its used as selector for materials and checkboxes for the windows'''
    name  = bpy.props.StringProperty()
    use   = bpy.props.BoolProperty()

bpy.utils.register_class(EnVi_Multiple)

def update_shaded_materials(ng, context=""): # transplant into the nodetree?
    MATS = ng.envi_shaded_materials
    MATS.clear()
    for mat in bpy.data.materials:
        if mat.vi_params.envi_export and mat.vi_params.envi_nodes:# exported and nodes exist
            con = [n for n in mat.vi_params.envi_nodes.nodes # there's only one
                if n.bl_idname=="No_En_Mat_Con"][0] # construction per material
            if all((con.envi_con_type == "Window", # its a window
                    con.envi_con_con == "External",# and external ## mat.envi_boundary == False,
                   (con.envi_con_makeup!='1' # and either a preset or has layers > is probably valid
                 or con.inputs["Outer layer"].is_linked))): # mat.envi_layero
                MATS.add().name = mat.name # add material name to list of available windows
    ng.upd_mat_faces() # forces update of the EnViShadWinNodes material-pointers

### META: Clamped-Socket
class ClampedSocket_META():
    '''This socket meta provides utility for a clamped int/float-socket.
    The 'default_value' may be between 'max_value' and 'min_value'=0.
    Otherwise it will be corrected accordingly. Derived classes must have
    a int/float-vector (size=3) to the variable 'true_default_value' .
    'titled'=False and 'valueOnly'=True both referre to the layout.'''

    def upd(self, context=""): #TODO: Reihenfolge umkehren ermoeglichen
        if  self.max_value <= self.min_value:
            return ## safety against permanent recursion
        if  self.default_value<self.min_value:
            self.true_default_value[0]=self.min_value
        if  self.default_value>self.max_value:
            self.true_default_value[0]=self.max_value

    def upd_draw(self, context=""):#redraw erzwingen
        self.default_value=self.default_value

    @property
    def default_value(self):
        if self.valueOnly or self.is_output or not self.is_linked:
            return self.true_default_value[0]
        elif type(self.links[0].from_socket.default_value) in (int, float):
            return self.links[0].from_socket.default_value
        else: return self.links[0].from_socket.default_value[0]
    @property
    def min_value(self):
        if self.valueOnly or self.is_output or not self.is_linked:
            return self.true_default_value[1]
        elif type(self.links[0].from_socket.default_value) in (int, float):
            return getattr(self.links[0].from_socket, "min_value",
                           self.true_default_value[1])
        else: return self.links[0].from_socket.default_value[1]
    @property
    def max_value(self):
        if self.valueOnly or self.is_output or not self.is_linked:
            return self.true_default_value[2]
        elif type(self.links[0].from_socket.default_value) in (int, float):
            return getattr(self.links[0].from_socket, "max_value",
                           self.true_default_value[2])
        else: return self.links[0].from_socket.default_value[2]

    @default_value.setter
    def default_value(self,value):
        if type(value)()in [0,0.0,""]: ### floats, ints, strings
            self.true_default_value[0] = float(value)
        elif len(value)==1:            ### listen der laenge 1
            self.true_default_value[0] = float(value[0])
        elif len(value)==3:            ### vectoren, ...
            self.true_default_value[0] = float(value[0])
            self.true_default_value[1] = float(value[1])
            self.true_default_value[2] = float(value[2])
    @min_value.setter
    def min_value(self,value):
        self.true_default_value[1] = float(value)
    @max_value.setter
    def max_value(self,value):
        self.true_default_value[2] = float(value)

    titled    = bpy.props.BoolProperty(default=False,
                                       update=upd_draw)
    valueOnly = bpy.props.BoolProperty(default=True,
                                       update=upd_draw)

    def draw(self, context, layout, node, text):
        if self.is_output:
            if self.valueOnly: layout.label(text); return
            # if it is a output you'll only see it if you force it to
            # so why bother with only the value anyways?
        if self.valueOnly: box = layout
        else:              box = layout.box()
        if self.min_value >= self.max_value: box.alert = True
        if self.is_linked:
            row=box.row()
            row.alignment='CENTER'
            row.label(text)
        else:
            if self.titled:
                row=box.row()
                row.alignment='CENTER'
                row.label(text)
                text="Value"
            box.prop(self, "true_default_value",     text,index=0)
            if not self.valueOnly:
                row=box.row()
                row.prop(self, "true_default_value","Minimum",index=1)
                row.prop(self, "true_default_value","Maximum",index=2)
