"""床頭板衛生紙抽取盒 v2 — 參數化模型 (Bambu Lab A1 mini, 180x180x180 mm)

座標: X = 沿床頭板寬度方向, Y = 深度 (Y=0 朝床/朝人, 往 +Y 是床頭板與牆), Z = 高度
盒子整個掛在床頭板朝床的那一面, 收納空間全部低於床頭板頂端;
只有頂部 TOP_T 厚的橫樑跨過床頭板頂端, 背面再用扣腳往下扣住床頭板.
衛生紙直立放置, 抽取口在朝床的垂直面上, 抽取方向與床頭板垂直; 上蓋在頂部且與頂面齊平.
"""
import os
import numpy as np
import trimesh
from manifold3d import Manifold, CrossSection

# ---------- 參數 (mm) ----------
TISSUE_L = 140.0    # 衛生紙長 (沿床頭板, 與抽取口同方向)
TISSUE_W = 100.0    # 衛生紙寬 (直立後為高度)
TISSUE_H = 77.0     # 衛生紙厚 (直立後為深度, 朝床方向)
TISSUE_CLR = 4.0    # 衛生紙每個方向的總餘隙 (方便放入)
WALL = 3.0          # 壁厚
FLOOR = 2.4         # 底厚
BOARD_T = 27.4      # 床頭板厚度
BOARD_CLR = 1.0     # 床頭板夾槽餘隙
TOP_T = 5.0         # 跨在床頭板頂端的橫樑厚度 (= 高出床頭板的高度)
BACK_LEG = 40.0     # 背面扣腳往下的長度
BACK_T = 4.0        # 背面扣腳厚度
SLOT_L = 110.0      # 抽取口長度
SLOT_W = 18.0       # 抽取口寬度
SLOT_Z = None       # 抽取口中心高度 (None = 收納空間正中央)
LID_T = 2.4         # 上蓋厚 (與頂面齊平)
LEDGE = 1.5         # 上蓋承靠的內緣寬度
LIP_T = 1.6         # 上蓋內嵌唇厚
LIP_H = 6.0         # 上蓋內嵌唇深度
LID_CLR = 0.3       # 上蓋配合間隙
NOTCH_R = 9.0       # 前緣掀蓋手指缺口半徑

W = TISSUE_L + TISSUE_CLR + 2 * WALL           # 外寬 (沿床頭板)
DB = TISSUE_H + TISSUE_CLR + 2 * WALL          # 盒子外深 (不含跨板部分)
H = FLOOR + TISSUE_W + TISSUE_CLR + LID_T      # 外高
GAP = BOARD_T + BOARD_CLR
D_TOTAL = DB + GAP + BACK_T
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")


def yz_extrude_x(pts, length):
    """以 (y, z) 逆時針輪廓沿 X 擠出."""
    m = CrossSection([pts]).extrude(length)  # (u, v, w) = (y, z, x)
    return m.transform([[0, 0, 1, 0], [1, 0, 0, 0], [0, 1, 0, 0]])


def stadium(length, width, depth, n=48):
    r = width / 2
    a = np.linspace(-np.pi / 2, np.pi / 2, n)
    right = [((length / 2 - r) + r * np.cos(t), r * np.sin(t)) for t in a]
    left = [(-(length / 2 - r) - r * np.cos(t), -r * np.sin(t)) for t in a]
    return CrossSection([right + left]).extrude(depth)  # 在 XY 平面, 沿 Z 擠出


def body():
    y1 = DB + GAP            # 背面扣腳內側
    zt = H - TOP_T           # 床頭板頂端高度
    prof = [
        (0, 0), (DB, 0), (DB, zt), (y1, zt), (y1, H - BACK_LEG),
        (D_TOTAL, H - BACK_LEG), (D_TOTAL, H), (0, H),
    ]
    outer = yz_extrude_x(prof, W)

    # 收納空間: 底板到上蓋下緣
    cavity = Manifold.cube([W - 2 * WALL, DB - 2 * WALL, H - LID_T - FLOOR + 0.01]).translate([WALL, WALL, FLOOR])
    # 上蓋凹槽: 比開口每邊多 LEDGE, 深 LID_T, 讓上蓋與頂面齊平
    recess = Manifold.cube([W - 2 * (WALL - LEDGE), DB - 2 * (WALL - LEDGE), LID_T + 1]).translate(
        [WALL - LEDGE, WALL - LEDGE, H - LID_T])

    # 抽取口: 朝床的垂直面 (Y=0)
    zc = SLOT_Z if SLOT_Z is not None else (FLOOR + H - LID_T) / 2
    slot = stadium(SLOT_L, SLOT_W, WALL + 2)
    slot = slot.rotate([-90, 0, 0]).translate([W / 2, -1, zc])  # (x,y,z)->(x,z,-y), 沿 +Y 穿過前壁

    # 前緣中央手指缺口, 方便掀開上蓋
    notch = Manifold.cylinder(WALL + 2, NOTCH_R, NOTCH_R, 64).rotate([-90, 0, 0]).translate([W / 2, -1, H])
    return outer - cavity - recess - slot - notch


def lid():
    pw = W - 2 * (WALL - LEDGE) - 2 * LID_CLR
    pd = DB - 2 * (WALL - LEDGE) - 2 * LID_CLR
    plate = Manifold.cube([pw, pd, LID_T])
    iw = W - 2 * WALL - 2 * LID_CLR
    idp = DB - 2 * WALL - 2 * LID_CLR
    lip_o = Manifold.cube([iw, idp, LIP_H])
    lip_i = Manifold.cube([iw - 2 * LIP_T, idp - 2 * LIP_T, LIP_H + 1]).translate([LIP_T, LIP_T, -0.5])
    off = LEDGE
    lip = (lip_o - lip_i).translate([off, off, LID_T])
    # 列印方向: 外表面貼床, 內嵌唇朝上, 免支撐
    return plate + lip


def lid_installed():
    """回傳裝在盒子上的上蓋 (外表面朝上, 與頂面齊平)."""
    m = to_trimesh(lid())
    pd = DB - 2 * (WALL - LEDGE) - 2 * LID_CLR
    m.apply_transform(trimesh.transformations.rotation_matrix(np.pi, [1, 0, 0], [0, pd / 2, 0]))
    m.apply_translation([WALL - LEDGE + LID_CLR, WALL - LEDGE + LID_CLR, H])
    return m


def to_trimesh(m):
    mesh = m.to_mesh()
    return trimesh.Trimesh(vertices=np.array(mesh.vert_properties)[:, :3], faces=np.array(mesh.tri_verts))


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    b = to_trimesh(body())
    l = to_trimesh(lid())
    print("body bounds", b.bounds.tolist(), "watertight", b.is_watertight, "vol cm3", round(b.volume / 1000, 1))
    print("lid  bounds", l.bounds.tolist(), "watertight", l.is_watertight, "vol cm3", round(l.volume / 1000, 1))
    print("inner cavity", W - 2 * WALL, DB - 2 * WALL, H - LID_T - FLOOR)
    b.export(os.path.join(OUT, "tissue_box_body.stl"))
    l.export(os.path.join(OUT, "tissue_box_lid.stl"))
