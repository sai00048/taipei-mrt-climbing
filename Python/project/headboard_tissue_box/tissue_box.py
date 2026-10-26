"""床頭板衛生紙抽取盒 v2 — 參數化模型 (Bambu Lab A1 mini, 180x180x180 mm)

座標: X = 沿床頭板寬度方向, Y = 深度 (Y=0 朝床/朝人, 往 +Y 是床頭板與牆), Z = 高度
盒子整個掛在床頭板朝床的那一面, 收納空間全部低於床頭板頂端;
只有頂部 TOP_T 厚的橫樑跨過床頭板頂端, 背面再用扣腳往下扣住床頭板.
衛生紙直立放置, 抽取口在朝床的垂直面上, 抽取方向與床頭板垂直; 上蓋在頂部且與頂面齊平.
"""
import os
import numpy as np
import trimesh
from manifold3d import Manifold, CrossSection, JoinType, OpType

# ---------- 參數 (mm) ----------
TISSUE_L = 140.0    # 衛生紙長 (與衛生紙開口同方向)
TISSUE_W = 100.0    # 衛生紙寬
TISSUE_H = 77.0     # 衛生紙厚 (朝床方向)
SLOT_VERTICAL = True  # True: 抽取開口與地面垂直 (長邊 140 站直); False: 開口水平 (長邊沿床頭板)
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
EDGE_R = 3.0        # 盒身外部所有邊角的圓角半徑
THIN_EDGE_R = 1.5   # 跨板橫樑與背面扣腳 (較薄) 的圓角半徑
SLOT_EDGE_R = 1.4   # 抽取口與手指缺口邊緣的圓角半徑 (前壁內外兩側)
LID_EDGE_R = 1.0    # 上蓋外緣圓角半徑

PACK_ALONG = TISSUE_W if SLOT_VERTICAL else TISSUE_L  # 衛生紙沿床頭板方向的尺寸
PACK_UP = TISSUE_L if SLOT_VERTICAL else TISSUE_W     # 衛生紙高度方向的尺寸
W = PACK_ALONG + TISSUE_CLR + 2 * WALL         # 外寬 (沿床頭板)
DB = TISSUE_H + TISSUE_CLR + 2 * WALL          # 盒子外深 (不含跨板部分)
H = FLOOR + PACK_UP + TISSUE_CLR + LID_T       # 外高
GAP = BOARD_T + BOARD_CLR
D_TOTAL = DB + GAP + BACK_T
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")


def yz_extrude_x(pts, length):
    """以 (y, z) 逆時針輪廓沿 X 擠出."""
    m = CrossSection([pts]).extrude(length)  # (u, v, w) = (y, z, x)
    return m.transform([[0, 0, 1, 0], [1, 0, 0, 0], [0, 1, 0, 0]])


def fillet_flare(r, n=16):
    """圓角輪廓: 回傳 (距表面深度 z, 擴孔量 e) 列表, z 由 0 到 r."""
    zs = np.linspace(0, r, n + 1)
    return [(z, r - np.sqrt(max(r * r - (r - z) ** 2, 0.0))) for z in zs]


def filleted_round_cut(radius, thick, r):
    """圓形開孔刀具 (旋轉體, 軸 = Z), 穿過 Z=0..thick 的壁, 兩側邊緣做半徑 r 的平滑圓角."""
    fl = fillet_flare(r)
    pts = [(0, -1), (radius + r, -1)]
    pts += [(radius + e, z) for z, e in fl]
    pts += [(radius + e, thick - z) for z, e in reversed(fl)]
    pts += [(radius + r, thick + 1), (0, thick + 1)]
    return Manifold.revolve(CrossSection([pts]), 96)


def filleted_slot_cut(length, width, thick, r):
    """圓角長孔刀具 (長邊沿 X, 中心在原點), 穿過 Z=0..thick 的壁, 兩側邊緣做半徑 r 的平滑圓角."""
    half = width / 2
    ends = [filleted_round_cut(half, thick, r).translate([sx * (length / 2 - half), 0, 0]) for sx in (-1, 1)]
    fl = fillet_flare(r)
    right = [(half + r, -1)] + [(half + e, z) for z, e in fl] + [(half + e, thick - z) for z, e in reversed(fl)] + [(half + r, thick + 1)]
    left = [(-y, z) for y, z in reversed(right)]
    mid = yz_extrude_x(right + left, length - width).translate([-(length - width) / 2, 0, 0])
    return Manifold.batch_boolean(ends + [mid], OpType.Add)


def rounded_box(p0, p1, r):
    """所有邊角半徑 r 的圓角方塊."""
    size = [b - a - 2 * r for a, b in zip(p0, p1)]
    core = Manifold.cube(size).translate([a + r for a in p0])
    return core.minkowski_sum(Manifold.sphere(r, 32))


def filleted_round_cut(radius, thick, r, n=16):
    """圓形開孔刀具 (旋轉體), 兩側表面邊緣做半徑 r 的平滑圓角."""
    zs = np.linspace(0, r, n + 1)
    flare = [radius + r - np.sqrt(max(r * r - (r - z) ** 2, 0.0)) for z in zs]
    pts = [(0, -1), (radius + r, -1)]
    pts += [(f, z) for f, z in zip(flare, zs)]
    pts += [(f, thick - z) for f, z in reversed(list(zip(flare, zs)))]
    pts += [(radius + r, thick + 1), (0, thick + 1)]
    return Manifold.revolve(CrossSection([pts]), 96)


def to_front_wall(cutter, x, z):
    """把在 XY 平面建立的刀具轉到前壁 (Y=0..WALL), 中心放在 (x, z)."""
    return cutter.rotate([-90, 0, 0]).translate([x, 0, z])  # (x,y,z)->(x,z,-y)


def body():
    y1 = DB + GAP            # 背面扣腳內側
    zt = H - TOP_T           # 床頭板頂端高度
    # 外形分三塊各自做圓角後聯集: 盒身 (EDGE_R), 跨板橫樑與背面扣腳 (較薄, 用 THIN_EDGE_R)
    box = rounded_box([0, 0, 0], [W, DB, H], EDGE_R)
    bridge = rounded_box([0, DB - 2 * EDGE_R, zt], [W, D_TOTAL, H], THIN_EDGE_R)
    leg = rounded_box([0, y1, H - BACK_LEG], [W, D_TOTAL, H], THIN_EDGE_R)
    outer = box + bridge + leg

    # 收納空間: 底板到上蓋下緣
    cavity = Manifold.cube([W - 2 * WALL, DB - 2 * WALL, H - LID_T - FLOOR + 0.01]).translate([WALL, WALL, FLOOR])
    # 上蓋凹槽: 比開口每邊多 LEDGE, 深 LID_T, 讓上蓋與頂面齊平
    recess = Manifold.cube([W - 2 * (WALL - LEDGE), DB - 2 * (WALL - LEDGE), LID_T + 1]).translate(
        [WALL - LEDGE, WALL - LEDGE, H - LID_T])

    # 抽取口: 朝床的垂直面 (Y=0)
    zc = SLOT_Z if SLOT_Z is not None else (FLOOR + H - LID_T) / 2
    slot = filleted_slot_cut(SLOT_L, SLOT_W, WALL, SLOT_EDGE_R)
    if SLOT_VERTICAL:
        slot = slot.rotate([0, 0, 90])  # 轉到前壁後即與地面垂直
    slot = to_front_wall(slot, W / 2, zc)

    # 前緣中央手指缺口, 方便掀開上蓋
    notch = to_front_wall(filleted_round_cut(NOTCH_R, WALL, SLOT_EDGE_R), W / 2, H)
    return outer - cavity - recess - slot - notch


def lid():
    pw = W - 2 * (WALL - LEDGE) - 2 * LID_CLR
    pd = DB - 2 * (WALL - LEDGE) - 2 * LID_CLR
    r = LID_EDGE_R
    plate = Manifold.cube([pw - 2 * r, pd - 2 * r, LID_T - 2 * r]).translate([r, r, r])
    plate = plate.minkowski_sum(Manifold.sphere(r, 24))
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
    faces = np.array(mesh.tri_verts)
    # 依 manifold 提供的合併表把重複頂點接回, 確保輸出的 STL 是封閉網格
    remap = np.arange(len(mesh.vert_properties))
    remap[np.array(mesh.merge_from_vert, dtype=int)] = np.array(mesh.merge_to_vert, dtype=int)
    return trimesh.Trimesh(vertices=np.array(mesh.vert_properties)[:, :3], faces=remap[faces])


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    b = to_trimesh(body())
    l = to_trimesh(lid())
    print("body bounds", b.bounds.tolist(), "watertight", b.is_watertight, "vol cm3", round(b.volume / 1000, 1))
    print("lid  bounds", l.bounds.tolist(), "watertight", l.is_watertight, "vol cm3", round(l.volume / 1000, 1))
    print("inner cavity", W - 2 * WALL, DB - 2 * WALL, H - LID_T - FLOOR)
    b.export(os.path.join(OUT, "tissue_box_body.stl"))
    l.export(os.path.join(OUT, "tissue_box_lid.stl"))
