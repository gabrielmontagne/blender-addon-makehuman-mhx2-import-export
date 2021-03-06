# ##### BEGIN GPL LICENSE BLOCK #####
#
#  Authors:             Thomas Larsson
#  Script copyright (C) Thomas Larsson 2014-2018
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


import os
import math
import bpy
from mathutils import Euler
from .error import *
if bpy.app.version < (2,80,0):
    from .buttons27 import BvhImport, UseHeadBool
else:
    from .buttons28 import BvhImport, UseHeadBool

#------------------------------------------------------------------------
#    Quick and dirty BVH load.
#------------------------------------------------------------------------

def faceshiftBvhLoad(filepath, useHead, context):
    rig = context.object
    readingBlendShapes = False
    readingMotion = False
    isFaceshift13 = False
    firstUnknown = ""

    props = {}
    bones = {}
    pmotion = {}
    bmotion = {}
    idx = 0
    R = math.pi/180
    with open(filepath) as fp:
        for line in fp:
            words = line.split()
            if len(words) == 0:
                continue
            elif readingMotion:
                for idx,bone in bones.items():
                    angles = [float(words[idx+n])*R for n in range(3,6)]
                    euler = Euler(angles, 'ZXY')
                    bmotion[bone].append(euler)
                for idx,prop in props.items():
                    strength = float(words[idx+5])/90.0
                    pmotion[prop].append(strength)
            else:
                key = words[0]
                if key == "JOINT":
                    joint = words[1]
                    idx += 6
                    if readingBlendShapes:
                        try:
                            prop = "Mfa%s" % FaceShiftShapes[joint]
                        except KeyError:
                            if firstUnknown == "":
                                firstUnknown = joint
                            if joint == "LipsTogether":
                                isFaceshift13 = True
                        props[idx] = prop
                        pmotion[prop] = []
                    elif joint == "Blendshapes":
                        readingBlendShapes = True
                    elif useHead:
                        try:
                            bnames = FaceShiftBones[joint]
                        except KeyError:
                            bnames = []
                        for bname in bnames:
                            try:
                                bone = rig.data.bones[bname]
                            except:
                                bone = None
                            if bone:
                                bones[idx] = bname
                                bmotion[bname] = []
                elif key == "MOTION":
                    if not readingBlendShapes:
                        raise MhxError("This is not a FaceShift BVH file")
                    readingBlendShapes = False
                elif key == "Frame":
                    readingMotion = True

    if isFaceshift13:
        warning = (
            "Warning: This seems to be a Faceshift 1.3 file.\n" +
            "MHX2 only supports Faceshift 1.2 and lower.")
    elif firstUnknown:
        warning = (
            "Warning: This does not seem to be a Faceshift BVH file.\n" +
            "First unknown shape: %s" % firstUnknown)
    else:
        warning = ""

    return bmotion,pmotion,warning

#------------------------------------------------------------------------
#    Faceshift translation table
#------------------------------------------------------------------------

FaceShiftBones = {
    "Neck" : ["neck", "neck02"],
    "eye_left" : ["eye.L"],
    "eye_right" : ["eye.R"],
}

FaceShiftShapes = {
 "neutral" :        "Rest",
 "BrowsD_L" :       "LeftBrowDown",
 "BrowsD_R" :       "RightBrowDown",
 "BrowsU_C" :       "BrowsUp",
 "BrowsU_L" :       "LeftInnerBrowUp",
 "BrowsU_R" :       "RightInnerBrowUp",
 "CheekSquint_L" :  "LeftCheekUp",
 "CheekSquint_R" :  "RightCheekUp",
 "ChinLowerRaise" : "ChinUp",
 "ChinUpperRaise" : "UpperLipUp3",
 "EyeBlink_L" :     "LeftUpperLidClosed",
 "EyeBlink_R" :     "RightUpperLidClosed",
 "EyeDown_L" :      "LeftEyeDown",
 "EyeDown_R" :      "RightEyeDown",
 "EyeIn_L" :        "LeftEyeturnRight",
 "EyeIn_R" :        "RightEyeturnLeft",
 "EyeOpen_L" :      "LeftUpperLidOpen",
 "EyeOpen_R" :      "RightUpperLidOpen",
 "EyeOut_L" :       "LeftEyeturnLeft",
 "EyeOut_R" :       "RightEyeturnRight",
 "EyeSquint_L" :    "LeftLowerLidUp",
 "EyeSquint_R" :    "RightLowerLidUp",
 "EyeUp_L" :        "LeftEyeUp",
 "EyeUp_R" :        "RightEyeUp",
 "JawChew" :        "JawClosedOffset",
 "JawFwd" :         "ChinForward",
 "JawLeft" :        "ChinLeft",
 "JawRight" :       "ChinRight",
 "JawOpen" :        "JawDrop",
 "LipsFunnel" :     "LipsOpenKiss",
 "LipsLowerClose" : "lowerLipUp",
 "LipsLowerDown" :  "lowerLipDown",
 "LipsLowerOpen" :  "LowerLipsDown2",
 "LipsPucker" :     "LipsKiss",
 "LipsStretch_L" :  "MouthLeftSmile",
 "LipsStretch_R" :  "MouthRightSmile",
 "LipsUpperClose" : "UpperLipDown",
 "LipsUpperOpen" :  "UpperLipUp",
 "LipsUpperUp" :    "UpperLipUp2",
 "MouthDimple_L" :  "MouthLeftPullSide",
 "MouthDimple_R" :  "MouthRightPullSide",
 "MouthFrown_L" :   "MouthLeftPullDown",
 "MouthFrown_R" :   "MouthRightPullDown",
 "MouthLeft" :      "MouthMoveLeft",
 "MouthRight" :     "MouthMoveRight",
 "MouthSmile_L" :   "MouthLeftPlatysma",
 "MouthSmile_R" :   "MouthRightPlatysma",
 "Puff" :           "CheeksPump",
 "Sneer" :          "FaceTension",
}

#------------------------------------------------------------------------
#    Assign motion to rig properties and bones
#------------------------------------------------------------------------

def assignMotion(context, bmotion, pmotion):
    rig = context.object
    if (rig.animation_data and rig.animation_data.action):
        rig.animation_data.action = None

    for bname in bmotion.keys():
        pb = rig.pose.bones[bname]
        pb.keyframe_insert(data_path="rotation_quaternion", frame=1)

    for prop in pmotion.keys():
        path = '["%s"]' % prop
        try:
            rig.keyframe_insert(data_path=path, frame=1)
        except TypeError:
            print("Missing pose:", prop)

    bcurves = {}
    for fcu in rig.animation_data.action.fcurves:
        words = fcu.data_path.split('"')
        if words[0] == "pose.bones[":
            bone = words[1]
            try:
                fcus = bcurves[bone]
            except KeyError:
                fcus = bcurves[bone] = {}
            fcus[fcu.array_index] = fcu
        else:
            addKeyPoints(fcu, pmotion[words[1]])

    for bname,fcus in bcurves.items():
        quats = [euler.to_quaternion() for euler in bmotion[bname]]
        for n in range(4):
            points = [quat[n] for quat in quats]
            addKeyPoints(fcus[n], points)


def addKeyPoints(fcu, points):
    points = list(points)
    nFrames = len(points)
    fcu.keyframe_points.add(nFrames-1)
    for n,val in enumerate(points):
        kp = fcu.keyframe_points[n]
        kp.co = (n+1, val)

#------------------------------------------------------------------------
#    Button
#------------------------------------------------------------------------

class MHX_OT_LoadFaceshiftBvh(bpy.types.Operator, BvhImport, UseHeadBool):
    bl_idname = "mhx2.load_faceshift_bvh"
    bl_label = "Load FaceShift BVH File (.bvh)"
    bl_description = "Load facesthift from a bvh file"
    bl_options = {'UNDO'}

    @classmethod
    def poll(self, context):
        rig = context.object
        return (rig and rig.MhxFaceRigDrivers)

    def draw(self, context):
        self.layout.prop(self, "useHead")

    def execute(self, context):
        try:
            bmotion,pmotion,warning = faceshiftBvhLoad(self.properties.filepath, self.useHead, context)
            assignMotion(context, bmotion, pmotion)
            print("Faceshift file %s loaded." % self.properties.filepath)
            if warning:
                raise MhxError(warning)
        except MhxError:
            handleMhxError(context)
        return{'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

#----------------------------------------------------------
#   Initialize
#----------------------------------------------------------

classes = [
    MHX_OT_LoadFaceshiftBvh,
]

def initialize():
    for cls in classes:
        bpy.utils.register_class(cls)


def uninitialize():
    for cls in classes:
        bpy.utils.unregister_class(cls)