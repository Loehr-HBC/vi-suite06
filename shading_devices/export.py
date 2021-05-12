# Leider MUESSEN wir in mehrfach in envi_export eingreifen.
# eine vereinfachte Fassung ist wohl nicht umsetzbar.

# folgende Eingriffe nötig:
#1 from .shading_devices.export import setup_Shades
#(opt) in Zeile 43 nach 'Southall\n' das einfügen:
#   !- Adaptions: Felix Loehr - University of Applied Science Biberach\n
#2 vor Zeile 62 die folgende Zeile einfügen:
#        shaded_mats = {} # PATCH => shaded materials(HBC)
#3 nach Zeile 105 diese Zeilen einfügen:
#                    if curlaynames and mat.envi_con_type=="Window":
 #                       if not mat.envi_boundary:
  #                          shaded_mats.update({mat.name:curlaynames})
#4 vor Zeile 165 diese Zeilen einfügen:
#                    if conlist and mat.envi_con_type=="Window":
 #                       if not mat.envi_boundary:
  #                          shaded_mats.update({mat.name:conlist})
#5 vor Zeile 175 diese Zeile einfügen:
#        ShadedWindows = setup_Shades(en_idf, enng, shaded_mats)
#6 in Zeile 228 das hier:
#   'autocalculate', '', '',
# damit ersetzen:
#   'autocalculate', ShadedWindows.get("{}@{}".format(face.index, obj.name),""), '',

# TODO: eine automatische setup-utility schreiben die das patchen uebernimmt?

from ..envi_func import epentry, epschedwrite
from collections import OrderedDict

# We reduce the invasiveness by wrapping it into a function
def setup_Shades(en_idf, enng, shaded_mats, verbose=True):
    # defining Shades
    if verbose: print("PATCH: preparing ... 'Shading Devices'")
    en_idf.write("!-   ===========  ALL OBJECTS IN CLASS: SHADING DEVICE & CONTROL ===========\n\n")
    # gathering Nodes: EnViShadWinNode
    ShadWinNodes   = [n for n in enng.nodes
        if hasattr(n, 'mat_def') and n.mat_def in shaded_mats.keys()]
    if verbose:
        print("PATCH: %i ShadedWindows-Nodes given"%len(ShadWinNodes))
        print("PATCH: %i Shaded Materials given"%len(shaded_mats))
    SchedNames    = {}
    AngSchedNames = {}
    ShadConstrs   = []
    ShadeWritten  = []
    ContrWritten  = {}
    SchedWritten  = []
    ShadedWindows = {}
    for ShadWinNode in ShadWinNodes: # we go through each of them
        DATA = ShadWinNode.export()
        Shade, Control = [DATA["Shade"], DATA["Control"]]
        if verbose:
            print("PATCH: processing ShadedWindows-Node '%s'"%ShadWinNode.name)
        if None in [Shade, Control]: continue # silently drop unconnected windows
        if len(DATA["Faces"])==0:    continue # silently drop unwanted shades #
        # NOTE: be aware that unexistent materials,
        #       after a reexport can cause the same behaviour !
        SHADE   = Shade.export()
        CONTROL = Control.export()

        ### preparing shade
        if verbose: print("PATCH: ... preparing Shade")
        stype = SHADE["Type"]
        del SHADE["Type"]
        ShadeName = SHADE["Name"].replace(",","_").replace(";","_")
        #ShadeName = ShadeName.replace(" ","_").replace("__","_")## in nodes anzupassen## hilfsfunktion?
        if ShadeName not in ShadeWritten:
            shade_text = epentry("WindowMaterial:{}".format(stype),
                                [k for k in SHADE.keys()],
                                [v for v in SHADE.values()] )
            ShadeWritten.append(ShadeName)
        else: shade_text=""

        ### preparing / writing construction
        # eine version pro shade-material / material - kombi anlegen
        if verbose: print("PATCH: ... writing Construction")
        ##### ANPASSEN: wenn zwei(oder mehr) verschiedene Materialien auf das
        #   selbe Shading-Controll zugreifen, muss jedes davon dafuer neu erzeugt
        #   werden. => auch CONTROL anpassen
        ##### WORKAROUND BISHER: Die entsprechenden Shading-Control-Nodes ein mal
        #   pro ShadedWindows-Node-Material kopieren.
        ConstName = "{}__{}__{}".format(DATA["Material"], ShadeName, CONTROL["Placement"])
        if ConstName not in ShadConstrs:
            conNode = shaded_mats[DATA["Material"]]# fetch the construction-node
            conFull = conNode.ep_write(DATA["Material"], return_construction=True)[1]
            constr = conFull[1][1:] # [params, paramsvs] (+[params, paramsvs] verschattet) # pop off the name
            # NOTE: This is why we need the constructions from 'shaded_mats'.
            #       They help define the construction for shaded windows.
            if CONTROL["Placement"]=="BetweenGlass":
                constr[-2] = ShadeName
            elif CONTROL["Placement"]=="Interior":
                constr = constr + [ShadeName]
            else: constr = [ShadeName] + constr

            params   = ["Name","Outside layer"]+["Layer {}".format(i + 1)
                                                 for i in range(len(constr)-1)]
            paramsvs = [ConstName]+constr
            constr_text = epentry("Construction", params, paramsvs)
            ShadConstrs.append(ConstName)
        else: constr_text = ""

        ### preparing Control
        if verbose: print("PATCH: ... preparing Control")
        ContrName = CONTROL["Name"].replace(",","_").replace(";","_")
        if ContrName not in ContrWritten:
            ctype   = CONTROL["Control"]
            del CONTROL["Control"]
            spt  = CONTROL["spt"] # SetPointType = string
            cschd= CONTROL["Schedule"]
            #print(cschd)
            if cschd==None:
                ShadConSched=""
            else:
                if cschd.name in SchedNames: ShadConSched=SchedNames[cschd.name]
                else:
                    if len(cschd.outputs[0].links)==1: # nur ein Abnehmer
                        ShadConSched = "ShadConSched__{}__{}".format(
                                    ContrName, cschd.name)
                    else:
                        ShadConSched = "ShadConSched__{}".format(cschd.name)
                    SchedNames[cschd.name] = ShadConSched
            scheduled=["YES","NO"][cschd==None]
            aschd = CONTROL["SlatAngleSchedule"]
            if aschd==None: AngConSched=""
            else:
                if aschd.name in SchedNames: AngConSched=AngSchedNames[aschd.name]
                else:
                    if len(aschd.outputs[0].links)==1: # nur ein Abnehmer
                        AngConSched = "AngConSched__{}__{}".format(
                                    ContrName, aschd.name)
                    else:
                        AngConSched = "AngConSched__{}".format(aschd.name)
                    AngSchedNames[aschd.name] = AngConSched
            slAngCon =CONTROL["SlatAngleControl"]
            if  slAngCon==None or stype!='Blind': slAngCon = ""
            if  slAngCon==""  and stype=='Blind': slAngCon = "FixedSlatAngle"
            if  slAngCon=="ScheduledSlatAngle"  and AngConSched=="":
                slAngCon = "FixedSlatAngle"
            params   =[
                "Name",
                "Zone Name", # Zone Name => EnergyPlus-9-3-0
                "Shading Priority (starts with 1)", # EP-9-3
                "Shading Type",
                "Shaded Construction",
                "Control Type",
                "Control-Schedule Name",
                "SetPoint1{}".format(spt),
                "Is Control scheduled?",
                "Is Glare-Control aktive?",
                "Shading Material",
                "Slat-Angle-Control (Blinds Only)",
                "Slat-Angle-Schedule",
                "SetPoint2 (W/m2)",
                "Daylighting Controls Object Name",
                "Multiple Surface Control Type (Group/Sequential)"]
            paramsvs = [
                ContrName,
                None,   # EP-9-3
                None,   # EP-9-3
                CONTROL["Placement"]+stype,
                ConstName,
                ctype,
                ShadConSched,
                [CONTROL["SetPoint1"],""][CONTROL["SetPoint1"]==None],
                scheduled,
                CONTROL["Is Glare-Control aktive?"],
                "",
                slAngCon,
                AngConSched,
                [CONTROL["SetPoint2 (W/m2)"],""][CONTROL["SetPoint2 (W/m2)"]==None],
                "",
                "Group"]
#           contr_list = ["WindowProperty:ShadingControl", params, paramsvs]
            contr_zip = zip(params, paramsvs)
            ContrWritten.update({ContrName: contr_zip})
        else: contr_zip = ContrWritten[ContrName]

        # make a local copy of the OrderedDict
        contr_od = OrderedDict(contr_zip)
        contr_od["Name"] = "{}__{}".format(ContrName, DATA["Zone"])
        contr_od["Zone Name"] = DATA["Zone"]
        contr_od["Shading Priority (starts with 1)"] = DATA["Priority"]

        ### preparing / adding Faces
        if verbose: print("PATCH: ... preparing faces")
        for idx, faceID in enumerate(DATA["Faces"]):
            ShadedWindows[faceID] = ContrName
            contr_od.update({"Fenestration-#{}".format(idx): "win-"+faceID})

        ### preparing / writing schedules
        if ShadConSched and not ShadConSched in SchedWritten:
            cschd_text = cschd.epwrite(ShadConSched, 'Any Number') # bool( !=0)
            SchedWritten.append(ShadConSched)
            en_idf.write(cschd_text)
        if AngConSched  and not AngConSched in SchedWritten:
            aschd_text = cschd.epwrite(AngConSched,  'Any Number') # angle -180, 180
            SchedWritten.append(AngConSched)
            en_idf.write(aschd_text)

        ### Controller einpflegen.
        contr_text = epentry("WindowShadingControl",
                             list(contr_od.keys()), list(contr_od.values()))

        if constr_text:en_idf.write(constr_text)
        if contr_text: en_idf.write(contr_text)
        if shade_text: en_idf.write(shade_text)

    return ShadedWindows
