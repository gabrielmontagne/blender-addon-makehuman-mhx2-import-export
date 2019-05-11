# ##### BEGIN GPL LICENSE BLOCK #####
#
#  Authors:             Thomas Larsson
#  Script copyright (C) Thomas Larsson 2014
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
from bpy.props import *
from bpy_extras.io_utils import ImportHelper

from .utils import *
from .armature.rig_panel import BoneDrivers

# ---------------------------------------------------------------------
#   VisemeData class
# ---------------------------------------------------------------------

class VisemeData:
    def __init__(self):
        self._visemes = None
        self._moho = None
        self._layout = None
        self._mouthShapes = None

    def load(self):
        from .load_json import loadJsonRelative
        if self._moho is None:
            struct = loadJsonRelative("data/hm8/faceshapes/faceshapes.mxa")
            self._mouthShapes = [key for key in struct["targets"].keys() if key[0:4] in ["mout", "lips", "tong"]]
            struct = loadJsonRelative("data/hm8/faceshapes/visemes.mxa")
            self._layout = struct["layout"]
            self._visemes = struct["visemes"]
            self._moho = struct["moho"]


theVis = VisemeData()


def getMouthShapes():
    theVis.load()
    return theVis._mouthShapes

def getLayout():
    theVis.load()
    return theVis._layout

def getVisemes():
    theVis.load()
    return theVis._visemes

def getMoho():
    theVis.load()
    return theVis._moho


# ---------------------------------------------------------------------
#   Set viseme
# ---------------------------------------------------------------------

def getMeshes(rig):
    if rig.type == 'MESH':
        return [rig]
    elif rig.type == 'ARMATURE':
        meshes = []
        for ob in rig.children:
            if (ob.type == 'MESH' and
                ob.MhxHasFaceShapes):
                meshes.append(ob)
        return meshes
    else:
        return []


def setViseme(rig, vis, useKey=False, frame=1):
    if rig.MhxFaceShapeDrivers:
        for key in getMouthShapes():
            rig["Mhf"+key] = 0.0
        for key,value in getVisemes()[vis]:
            rig["Mhf"+key] = value
        if useKey:
            for key in getMouthShapes():
                rig.keyframe_insert('["Mhf%s"]' % key, frame=frame)
    elif rig.MhxFacePanel:
        for key in getMouthShapes():
            setPanelKey(rig, key, 0.0)
        for key,value in getVisemes()[vis]:
            setPanelKey(rig, key, value)
        if useKey:
            for key in getMouthShapes():
                pb,_fac,idx = getBoneFactor(rig, key)
                pb.keyframe_insert("location", index=idx, frame=frame)
    else:
        for ob in getMeshes(rig):
            if ob.data.shape_keys:
                for key in getMouthShapes():
                    if key in ob.data.shape_keys.key_blocks.keys():
                        skey = ob.data.shape_keys.key_blocks[key]
                        skey.value = 0.0
                for key,value in getVisemes()[vis]:
                    if key in ob.data.shape_keys.key_blocks.keys():
                        skey = ob.data.shape_keys.key_blocks[key]
                        skey.value = value
                if useKey:
                    for key in getMouthShapes():
                        if key in ob.data.shape_keys.key_blocks.keys():
                            skey = ob.data.shape_keys.key_blocks[key]
                            skey.keyframe_insert("value", frame=frame)


def getBoneFactor(rig, key):
    try:
        basis,suffix = key.rsplit("_",1)
    except IndexError:
        suffix = None
    if suffix not in ["left", "right"]:
        basis = key
    bname, channel, coord, _smin, _smax = BoneDrivers[basis]
    if suffix == "left":
        pb = rig.pose.bones[bname+".L"]
    elif suffix == "right":
        pb = rig.pose.bones[bname+".R"]
    else:
        pb = rig.pose.bones[bname]
    fac = coord[1]
    if channel == 'LOC_X':
        idx = 0
        if suffix == "right":
            fac = -fac
    elif channel == 'LOC_Z':
        idx = 2
    return pb, fac, idx


def setPanelKey(rig, key, value):
    pb,fac,idx = getBoneFactor(rig, key)
    offs = rig.MhxScale*value/fac
    pb.location[idx] = offs


class VIEW3D_OT_SetVisemeButton(bpy.types.Operator):
    bl_idname = "mhx2.set_viseme"
    bl_label = "X"
    bl_description = "Set viseme"
    bl_options = {'UNDO'}

    viseme = StringProperty()

    def execute(self, context):
        ob = context.object
        rig = getArmature(ob)
        if rig is None and ob.type == 'MESH':
            rig = ob
        scn = context.scene
        if rig:
            auto = scn.tool_settings.use_keyframe_insert_auto
            setViseme(rig, self.viseme, useKey=auto, frame=scn.frame_current)
            updateScene(context)
        return{'FINISHED'}

# ---------------------------------------------------------------------
#   Load Moho
# ---------------------------------------------------------------------

def loadMoho(rig, context, filepath, offs):
    context.scene.objects.active = rig
    moho = getMoho()
    bpy.ops.object.mode_set(mode='POSE')
    fp = open(filepath, "rU")
    for line in fp:
        words= line.split()
        if len(words) < 2:
            pass
        else:
            frame = int(words[0]) + offs
            vis = moho[words[1]]
            setViseme(rig, vis, True, frame)
    fp.close()
    #setInterpolation(rig)
    updateScene(context)
    print("Moho file %s loaded" % filepath)


class VIEW3D_OT_LoadMohoButton(bpy.types.Operator, ImportHelper):
    bl_idname = "mhx2.load_moho"
    bl_label = "Load Moho"
    bl_description = "Load Moho (.dat) file"
    bl_options = {'UNDO'}

    filename_ext = ".dat"
    filter_glob = StringProperty(default="*.dat", options={'HIDDEN'})
    filepath = StringProperty(subtype='FILE_PATH')

    def execute(self, context):
        rig = getArmature(context.object)
        if rig:
            loadMoho(rig, context, self.filepath, 1.0)
        return{'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

# ---------------------------------------------------------------------
#   Delete lipsync
# ---------------------------------------------------------------------

def deleteLipsync(rig):
    if (rig.MhxFaceShapeDrivers or
        rig.MhxFacePanel):
        deleteLipsyncRig(rig)
    else:
        for ob in getMeshes(rig):
            deleteLipsyncMesh(ob)


def deleteLipsyncMesh(ob):
    if (ob.data.shape_keys is None or
        ob.data.shape_keys.animation_data is None):
        return
    act = ob.data.shape_keys.animation_data.action
    if act is None:
        return
    n = len('key_blocks["')
    for fcu in act.fcurves:
        if fcu.data_path[n:n+4] in ["mout", "lips", "tong"]:
            act.fcurves.remove(fcu)
    for key in getMouthShapes():
        if key in ob.data.shape_keys.key_blocks.keys():
            skey = ob.data.shape_keys.key_blocks[key]
            skey.value = 0.0


def deleteLipsyncRig(rig):
    if rig.animation_data is None:
        return
    act = rig.animation_data.action
    if act is None:
        return
    if rig.MhxFaceShapeDrivers:
        for fcu in act.fcurves:
            if (fcu.data_path[0:5] == '["Mhf' and
                fcu.data_path[5:9] in ["mout", "lips", "tong"]):
                    act.fcurves.remove(fcu)
        for key in getMouthShapes():
            rig["Mhf"+key] = 0.0
    elif rig.MhxFacePanel:
        for key in getMouthShapes():
            pb,_fac,idx = getBoneFactor(rig, key)
            path = 'pose.bones["%s"].location' % pb.name
            for fcu in act.fcurves:
                if fcu.data_path == path:
                    act.fcurves.remove(fcu)
                    pb.location[idx] = 0.0


class VIEW3D_OT_DeleteLipsyncButton(bpy.types.Operator):
    bl_idname = "mhx2.delete_lipsync"
    bl_label = "Delete Lipsync"
    bl_description = "Delete F-curves associated with lipsync"
    bl_options = {'UNDO'}

    def execute(self, context):
        ob = context.object
        if ob.type == 'MESH':
            deleteLipsyncMesh(ob)
        else:
            rig = getArmature(ob)
            if rig:
                deleteLipsync(rig)
        updateScene(context)
        return{'FINISHED'}

# ---------------------------------------------------------------------
#   Bake face animation
# ---------------------------------------------------------------------

def bakeFaceAnim(rig):
    if not rig.MhxFaceShapeDrivers:
        print("")
        return
    if rig.animation_data is None:
        return
    act = rig.animation_data.action
    if act is None:
        return
    if rig.MhxFaceShapeDrivers:
        keypoints = {}
        for fcu in act.fcurves:
            if fcu.data_path[0:5] == '["Mhf':
                key = fcu.data_path.split('"')[1][3:]
                keypoints[key] = [tuple(kp.co) for kp in fcu.keyframe_points]
                act.fcurves.remove(fcu)
        for key in rig.keys():
            if key[0:3] == "Mhf":
                del rig[key]
        rig.MhxFaceShapeDrivers = False
        for ob in getMeshes(rig):
            if ob.data.shape_keys:
                for skey in ob.data.shape_keys.key_blocks:
                    skey.driver_remove("value")
                for key in keypoints.keys():
                    if key in ob.data.shape_keys.key_blocks.keys():
                        skey = ob.data.shape_keys.key_blocks[key]
                        for frame,value in keypoints[key]:
                            skey.value = value
                            skey.keyframe_insert("value", frame=frame)



class VIEW3D_OT_BakeFaceAnimButton(bpy.types.Operator):
    bl_idname = "mhx2.bake_face_anim"
    bl_label = "Bake Face Animation"
    bl_description = "Move facial F-curves from rig to mesh"
    bl_options = {'UNDO'}

    @classmethod
    def poll(self, context):
        rig = context.object
        return (rig and
                rig.type == 'ARMATURE' and
                rig.MhxFaceShapeDrivers)

    def execute(self, context):
        rig = getArmature(context.object)
        if rig:
            bakeFaceAnim(rig)
        updateScene(context)
        return{'FINISHED'}
