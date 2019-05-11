#
#    MakeHuman .mhx2 exporter
#    Copyright (C) Thomas Larsson 2014
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#


"""
Abstract
HM8 mesh info

"""
from collections import OrderedDict

VertexRanges = {
    "Body"      : (0, 13380),
    "Tongue"    : (13380, 13606),
    "Joints"    : (13606, 14598),
    "Eyes"      : (14598, 14742),
    "EyeLashes" : (14742, 14992),
    "LoTeeth"   : (14992, 15060),
    "UpTeeth"   : (15060, 15128),
    "Penis"     : (15128, 15328),
    "Tights"    : (15328, 18002),
    "Skirt"     : (18002, 18722),
    "Hair"      : (18722, 19150),
}

NBodyVerts = VertexRanges["Body"][1]
NTotalVerts = VertexRanges["Hair"][1] + 8

FirstJointVert = VertexRanges["Joints"][0]

JointNames = [
    "l-eye",
    "r-eye",
    "pelvis",
    "spine-4",
    "spine-3",
    "spine-2",
    "spine-1",
    "l-foot-2",
    "l-foot-1",
    "l-toe-5-3",
    "l-toe-5-4",
    "l-toe-4-3",
    "l-toe-4-4",
    "l-toe-3-3",
    "l-toe-3-4",
    "l-toe-2-4",
    "l-toe-2-3",
    "l-toe-2-2",
    "l-toe-3-2",
    "l-toe-4-2",
    "l-toe-5-2",
    "l-toe-5-1",
    "l-toe-4-1",
    "l-toe-3-1",
    "l-toe-2-1",
    "l-toe-1-3",
    "l-toe-1-2",
    "l-toe-1-1",
    "l-ankle",
    "l-knee",
    "l-upper-leg",
    "l-finger-2-4",
    "l-finger-3-4",
    "l-finger-4-4",
    "l-finger-5-4",
    "l-finger-5-3",
    "l-finger-4-3",
    "l-finger-3-3",
    "l-finger-2-3",
    "l-finger-2-2",
    "l-finger-3-2",
    "l-finger-4-2",
    "l-finger-5-2",
    "l-finger-5-1",
    "l-finger-4-1",
    "l-finger-3-1",
    "l-finger-2-1",
    "l-finger-1-4",
    "l-finger-1-3",
    "l-finger-1-2",
    "l-finger-1-1",
    "l-hand-3",
    "l-hand-2",
    "l-hand",
    "l-elbow",
    "l-shoulder",
    "l-clavicle",
    "l-scapula",
    "head",
    "l-lowerlid",
    "l-eye-target",
    "l-upperlid",
    "r-foot-2",
    "r-foot-1",
    "r-toe-5-3",
    "r-toe-5-4",
    "r-toe-4-3",
    "r-toe-4-4",
    "r-toe-3-3",
    "r-toe-3-4",
    "r-toe-2-4",
    "r-toe-2-3",
    "r-toe-2-2",
    "r-toe-3-2",
    "r-toe-4-2",
    "r-toe-5-2",
    "r-toe-5-1",
    "r-toe-4-1",
    "r-toe-3-1",
    "r-toe-2-1",
    "r-toe-1-3",
    "r-toe-1-2",
    "r-toe-1-1",
    "r-ankle",
    "r-knee",
    "r-upper-leg",
    "r-finger-2-4",
    "r-finger-3-4",
    "r-finger-4-4",
    "r-finger-5-4",
    "r-finger-5-3",
    "r-finger-4-3",
    "r-finger-3-3",
    "r-finger-2-3",
    "r-finger-2-2",
    "r-finger-3-2",
    "r-finger-4-2",
    "r-finger-5-2",
    "r-finger-5-1",
    "r-finger-4-1",
    "r-finger-3-1",
    "r-finger-2-1",
    "r-finger-1-4",
    "r-finger-1-3",
    "r-finger-1-2",
    "r-finger-1-1",
    "r-hand-3",
    "r-hand-2",
    "r-hand",
    "r-elbow",
    "r-shoulder",
    "r-clavicle",
    "r-scapula",
    "r-lowerlid",
    "r-eye-target",
    "r-upperlid",
    "neck",
    "jaw",
    "tongue-4",
    "tongue-3",
    "head-2",
    "tongue-2",
    "tongue-1",
    "mouth",
]


def getBaseMesh():
    struct = OrderedDict()
    struct["name"] = "hm8"
    struct["body_verts"] = VertexRanges["Body"][1]
    struct["total_verts"] = NTotalVerts
    helpers = struct["ranges"] = VertexRanges

    joints = struct["joints"] = OrderedDict()
    vn = VertexRanges["Joints"][0]
    for jname in JointNames:
        joints[jname] = (vn, vn+8)
        vn += 8
    joints["ground"] = (NTotalVerts-8, NTotalVerts)

    return struct