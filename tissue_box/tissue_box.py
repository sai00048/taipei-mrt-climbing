"""床頭板衛生紙抽取盒 v1 — 參數化模型 (Bambu Lab A1 mini, 180x180x180 mm)

座標: X = 沿床頭板寬度方向, Y = 深度 (Y=0 朝床/朝人, Y=D 朝牆), Z = 高度
衛生紙直立放置, 抽取口在朝床的垂直面上, 抽取方向與床頭板垂直; 上蓋在頂部.
"""
import os
import numpy as np
import trimesh
from manifold3d import Manifold, CrossSection

# ---------- 參數 (mm) ----------
W = 178.0           # 外寬 (沿床頭板)
H = 178.0           # 外高 (含跨板腳)
D = 95.0            # 外深 (垂直床頭板)
WALL = 2.4          # 壁厚
FLOOR = 2.4         # 底厚
BOARD_T = 20.0      # 床頭板厚度 (之後可調)
BOARD_CLR = 1.0     # 床頭板夾槽餘隙
LEG_H = 30.0        # 跨板腳高度 (往下包住床頭板的深度)
SLOT_L = 120.0      # 抽取口長度
SLOT_W = 18.0       # 抽取口寬度
LID_T = 2.4         # 上蓋板厚
LIP_T = 1.6         # 上蓋內嵌唇厚
LIP_H = 8.0         # 上蓋內嵌唇深度
LID_CLR = 0.3       # 上蓋配合間隙
NOTCH_R = 9.0       # 側邊掀蓋手指缺口半徑

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "output")


def yz_extrude_x(pts, length):
    """以 (y, z) 輪廓沿 X 擠出."""
    m = CrossSection([pts]).extrude(length)  # (u, v, w) = (y, z, x)
    # 置換軸: x = w, y = u, z = v
    return m.transform([[0, 0, 1, 0], [1, 0, 0, 0], [0, 1, 0, 0]])


def stadium(length, width, depth, n=48):
    r = width / 2
    a = np.linspace(-np.pi / 2, np.pi / 2, n)
    right = [((length / 2 - r) + r * np.cos(t), r * np.sin(t)) for t in a]
    left = [(-(length / 2 - r) - r * np.cos(t), -r * np.sin(t)) for t in a]
    return CrossSection([right + left]).extrude(depth)  # 在 XY 平面, 沿 Z 擠出


def body():
    gap = BOARD_T + BOARD_CLR
    g0 = (D - gap) / 2
    g1 = g0 + gap
    s = LEG_H  # 45 度斜面, 免支撐
    prof = [
        (0, LEG_H), (s, 0), (g0, 0), (g0, LEG_H), (g1, LEG_H), (g1, 0),
        (D - s, 0), (D, LEG_H), (D, H), (0, H),
    ]
    outer = yz_extrude_x(prof, W)

    z0 = LEG_H + FLOOR
    cavity = Manifold.cube([W - 2 * WALL, D - 2 * WALL, H - z0 + 1]).translate([WALL, WALL, z0])

    # 抽取口: 朝床的垂直面 (Y=0), 置中於收納空間
    zc = (z0 + H) / 2
    slot = stadium(SLOT_L, SLOT_W, WALL + 2)  # XY 平面 -> 轉到 XZ 平面
    # 繞 X 轉 -90 度: (x, y, z) -> (x, z, -y), 擠出方向變成 +Y
    slot = slot.rotate([-90, 0, 0]).translate([W / 2, -1, zc])

    # 左右兩側頂端的手指缺口, 方便掀開上蓋
    notch = Manifold.cylinder(W + 2, NOTCH_R, NOTCH_R, 64).rotate([0, 90, 0])
    notch = notch.translate([-1, D / 2, H])
    return outer - cavity - slot - notch


def lid():
    plate = Manifold.cube([W, D, LID_T])
    iw = W - 2 * WALL - 2 * LID_CLR
    idp = D - 2 * WALL - 2 * LID_CLR
    lip_o = Manifold.cube([iw, idp, LIP_H])
    lip_i = Manifold.cube([iw - 2 * LIP_T, idp - 2 * LIP_T, LIP_H + 1]).translate([LIP_T, LIP_T, -0.5])
    lip = (lip_o - lip_i).translate([WALL + LID_CLR, WALL + LID_CLR, LID_T])
    # 列印方向: 外表面貼床, 內嵌唇朝上, 免支撐
    return plate + lip


def to_trimesh(m):
    mesh = m.to_mesh()
    return trimesh.Trimesh(vertices=np.array(mesh.vert_properties)[:, :3], faces=np.array(mesh.tri_verts))


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    b = to_trimesh(body())
    l = to_trimesh(lid())
    print("body bounds", b.bounds.tolist(), "watertight", b.is_watertight, "vol cm3", b.volume / 1000)
    print("lid  bounds", l.bounds.tolist(), "watertight", l.is_watertight, "vol cm3", l.volume / 1000)
    b.export(os.path.join(OUT, "tissue_box_body.stl"))
    l.export(os.path.join(OUT, "tissue_box_lid.stl"))
