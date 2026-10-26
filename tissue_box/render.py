"""輸出預覽圖到 output/"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle, FancyArrowPatch
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import trimesh
import tissue_box as tb

plt.rcParams["font.sans-serif"] = ["Noto Sans CJK TC", "Noto Sans CJK JP", "WenQuanYi Zen Hei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False
LIGHT = np.array([0.4, -0.7, 0.6]); LIGHT /= np.linalg.norm(LIGHT)


def add_mesh(ax, mesh, color, alpha=1.0, offset=(0, 0, 0)):
    tris = mesh.vertices[mesh.faces] + np.array(offset)
    shade = 0.45 + 0.55 * np.clip(mesh.face_normals @ LIGHT, 0, 1)
    cols = np.clip(np.array(color)[None, :] * shade[:, None], 0, 1)
    cols = np.hstack([cols, np.full((len(cols), 1), alpha)])
    ax.add_collection3d(Poly3DCollection(tris, facecolors=cols, edgecolors="none"))


def box_mesh(x0, y0, z0, x1, y1, z1):
    m = trimesh.creation.box(extents=[x1 - x0, y1 - y0, z1 - z0])
    m.apply_translation([(x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2])
    return m


def setup(ax, lim, elev, azim, title):
    ax.set_xlim(lim[0]); ax.set_ylim(lim[1]); ax.set_zlim(lim[2])
    ax.set_box_aspect([l[1] - l[0] for l in lim])
    ax.view_init(elev=elev, azim=azim)
    ax.set_axis_off(); ax.set_title(title, fontsize=13)


body = tb.to_trimesh(tb.body())
lid = tb.to_trimesh(tb.lid())
lid_inst = lid.copy()
lid_inst.apply_transform(trimesh.transformations.rotation_matrix(np.pi, [1, 0, 0], [0, tb.D / 2, 0]))
lid_inst.apply_translation([0, 0, tb.H + tb.LID_T])  # 外表面朝上, 唇嵌入盒內
gap = tb.BOARD_T + tb.BOARD_CLR
g0 = (tb.D - gap) / 2 + tb.BOARD_CLR / 2
board = box_mesh(-40, g0, -120, tb.W + 40, g0 + tb.BOARD_T, tb.LEG_H)
BOX_C = np.array([0.33, 0.62, 0.86]); LID_C = np.array([0.95, 0.65, 0.25]); BOARD_C = np.array([0.6, 0.45, 0.3])
OUT = tb.OUT

# 1. 組合外觀 (從床的方向看) + 爆炸圖
from raster import render
lid_up = lid_inst.copy(); lid_up.apply_translation([0, 0, 60])
views = [
    ([(body, BOX_C, 1), (lid_inst, LID_C, 1), (board, BOARD_C, 1)], 20, -60, "組合外觀（從床／枕頭方向看，抽取口朝床）"),
    ([(body, BOX_C, 1), (lid_up, LID_C, 1), (board, BOARD_C, 1)], 28, -125, "爆炸圖（上蓋在頂部，整包從上方放入）"),
    ([(body, BOX_C, 1), (lid_inst, LID_C, 1), (board, BOARD_C, 1)], 5, 0, "側視（跨在床頭板上）"),
    ([(body, BOX_C, 1)], -25, -70, "底部（夾槽 21 mm + 45° 斜面）"),
]
fig, axs = plt.subplots(2, 2, figsize=(15, 13))
for ax, (items, el, az, t) in zip(axs.flat, views):
    ax.imshow(render(items, el, az, size=(900, 760))); ax.axis("off"); ax.set_title(t, fontsize=14)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "preview_3d.png"), dpi=110); plt.close(fig)

# 2. 側面剖面示意 (YZ)
fig, ax = plt.subplots(figsize=(9, 10))
s = tb.LEG_H; g1 = (tb.D + gap) / 2; gg0 = (tb.D - gap) / 2
prof = [(0, tb.LEG_H), (s, 0), (gg0, 0), (gg0, tb.LEG_H), (g1, tb.LEG_H), (g1, 0), (tb.D - s, 0), (tb.D, tb.LEG_H), (tb.D, tb.H), (0, tb.H)]
ax.add_patch(Polygon(prof, closed=True, fc=BOX_C, ec="k", alpha=0.35))
z0 = tb.LEG_H + tb.FLOOR
ax.add_patch(Rectangle((tb.WALL, z0), tb.D - 2 * tb.WALL, tb.H - z0, fc="white", ec="k"))
ax.add_patch(Rectangle((gg0 + tb.BOARD_CLR / 2, -110), tb.BOARD_T, 110 + tb.LEG_H, fc=BOARD_C, ec="k", alpha=0.8))
ax.text(tb.D / 2, -60, f"床頭板\n{tb.BOARD_T:.0f} mm", ha="center", va="center", color="white", fontsize=11, rotation=90)
pk = Rectangle((tb.WALL + 1, z0 + 5), 60, tb.H - z0 - 10, fc="#f4f1e8", ec="#999", hatch="||")
ax.add_patch(pk); ax.text(tb.WALL + 31, (z0 + tb.H) / 2, "衛生紙\n(直立)", ha="center", va="center", fontsize=11)
zc = (z0 + tb.H) / 2
ax.add_patch(Rectangle((-0.5, zc - tb.SLOT_W / 2), tb.WALL + 1, tb.SLOT_W, fc="red", ec="red"))
ax.add_patch(FancyArrowPatch((5, zc), (-70, zc), arrowstyle="-|>", mutation_scale=25, color="red", lw=2.5))
ax.text(-40, zc + 12, "抽取方向\n(朝床, 與床頭板垂直)", ha="center", color="red", fontsize=11)
ax.add_patch(Rectangle((0, tb.H), tb.D, tb.LID_T, fc=LID_C, ec="k"))
ax.add_patch(FancyArrowPatch((tb.D / 2, tb.H + 45), (tb.D / 2, tb.H + 8), arrowstyle="-|>", mutation_scale=20, color=LID_C, lw=2))
ax.text(tb.D / 2, tb.H + 50, "上蓋在頂部, 從上方放入整包", ha="center", fontsize=11)
ax.text(-75, -40, "← 床 / 枕頭側", fontsize=12); ax.text(tb.D + 5, -40, "牆側 →", fontsize=12)
for (a, b, z, t) in [(0, tb.D, -8 - 0, f"深 {tb.D:.0f}")]:
    pass
ax.annotate("", (tb.D + 12, 0), (tb.D + 12, tb.H), arrowprops=dict(arrowstyle="<->"))
ax.text(tb.D + 15, tb.H / 2, f"高 {tb.H:.0f} mm", rotation=90, va="center")
ax.annotate("", (0, tb.H + 20), (tb.D, tb.H + 20), arrowprops=dict(arrowstyle="<->"))
ax.text(tb.D / 2, tb.H + 23, f"深 {tb.D:.0f} mm", ha="center")
ax.annotate("", (gg0, tb.LEG_H + 6), (g1, tb.LEG_H + 6), arrowprops=dict(arrowstyle="<->"))
ax.text(tb.D / 2, tb.LEG_H + 9, f"夾槽 {gap:.0f}", ha="center", fontsize=9)
ax.set_xlim(-110, 150); ax.set_ylim(-115, 245); ax.set_aspect("equal"); ax.axis("off")
ax.set_title("側面剖面示意（寬 178 mm 沿床頭板方向）", fontsize=13)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "preview_section.png"), dpi=130); plt.close(fig)

# 3. 列印擺放 (A1 mini 180x180x180)
bed = box_mesh(0, 0, -2, 180, 180, 0)
b_p = body.copy(); b_p.apply_translation([1, (180 - tb.D) / 2, 0])
l_p = lid.copy(); l_p.apply_translation([1, (180 - tb.D) / 2, 0])
fig, axs = plt.subplots(1, 2, figsize=(15, 7.5))
for ax, (m, c, t) in zip(axs, [(b_p, BOX_C, "主體：開口朝上直立列印（45° 斜面免支撐）"), (l_p, LID_C, "上蓋：外表面貼床、內嵌唇朝上")]):
    ax.imshow(render([(m, c, 1), (bed, np.array([0.55, 0.55, 0.55]), 1)], 25, -55, size=(900, 800))); ax.axis("off"); ax.set_title(t, fontsize=14)
fig.suptitle("Bambu Lab A1 mini 列印平台 180 × 180 mm（灰色）／高度上限 180 mm", fontsize=15)
fig.tight_layout(rect=[0, 0, 1, 0.95]); fig.savefig(os.path.join(OUT, "preview_print_layout.png"), dpi=110); plt.close(fig)
print("done")
