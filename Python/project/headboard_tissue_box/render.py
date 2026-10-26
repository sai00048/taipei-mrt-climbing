"""輸出預覽圖到 output/"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle, FancyArrowPatch
import trimesh
import tissue_box as tb
from raster import render

plt.rcParams["font.sans-serif"] = ["WenQuanYi Zen Hei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


def box_mesh(x0, y0, z0, x1, y1, z1):
    m = trimesh.creation.box(extents=[x1 - x0, y1 - y0, z1 - z0])
    m.apply_translation([(x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2])
    return m


body = tb.to_trimesh(tb.body())
lid = tb.to_trimesh(tb.lid())
lid_inst = tb.lid_installed()
zt = tb.H - tb.TOP_T                       # 床頭板頂端
by0 = tb.DB + tb.BOARD_CLR / 2             # 床頭板朝床面
board = box_mesh(-50, by0, -60, tb.W + 50, by0 + tb.BOARD_T, zt)
BOX_C = np.array([0.33, 0.62, 0.86]); LID_C = np.array([0.95, 0.65, 0.25]); BOARD_C = np.array([0.6, 0.45, 0.3])
OUT = tb.OUT

# 1. 3D 預覽
lid_up = lid_inst.copy(); lid_up.apply_translation([0, 0, 60])
views = [
    ([(body, BOX_C, 1), (lid_inst, LID_C, 1), (board, BOARD_C, 1)], 20, -60, "組合外觀（從床／枕頭方向看，抽取口朝床）"),
    ([(body, BOX_C, 1), (lid_up, LID_C, 1), (board, BOARD_C, 1)], 30, -120, "爆炸圖（上蓋在頂部，整包從上方放入）"),
    ([(body, BOX_C, 1), (lid_inst, LID_C, 1), (board, BOARD_C, 1)], 3, 0, "側視（盒子整個掛在床頭板朝床那面）"),
    ([(body, BOX_C, 1), (lid_inst, LID_C, 1), (board, BOARD_C, 1)], 25, 125, "背面（橫樑跨過床頭板 + 背面扣腳）"),
]
fig, axs = plt.subplots(2, 2, figsize=(15, 13))
for ax, (items, el, az, t) in zip(axs.flat, views):
    ax.imshow(render(items, el, az, size=(900, 760))); ax.axis("off"); ax.set_title(t, fontsize=14)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "preview_3d.png"), dpi=110); plt.close(fig)

# 2. 側面剖面示意 (YZ)
fig, ax = plt.subplots(figsize=(10, 10))
y1 = tb.DB + tb.GAP
prof = [(0, 0), (tb.DB, 0), (tb.DB, zt), (y1, zt), (y1, tb.H - tb.BACK_LEG),
        (tb.D_TOTAL, tb.H - tb.BACK_LEG), (tb.D_TOTAL, tb.H), (0, tb.H)]
ax.add_patch(Polygon(prof, closed=True, fc=BOX_C, ec="k", alpha=0.45))
z_top_cav = tb.H - tb.LID_T
ax.add_patch(Rectangle((tb.WALL, tb.FLOOR), tb.DB - 2 * tb.WALL, z_top_cav - tb.FLOOR, fc="white", ec="k"))
ax.add_patch(Rectangle((tb.WALL - tb.LEDGE, z_top_cav), tb.DB - 2 * (tb.WALL - tb.LEDGE), tb.LID_T, fc=LID_C, ec="k"))
ax.add_patch(Rectangle((by0, -70), tb.BOARD_T, zt + 70, fc=BOARD_C, ec="k", alpha=0.85))
ax.text(by0 + tb.BOARD_T / 2, -20, f"床頭板 {tb.BOARD_T:.1f} mm", ha="center", va="center", color="white", fontsize=11, rotation=90)
ax.add_patch(Rectangle((tb.WALL + tb.TISSUE_CLR / 2, tb.FLOOR), tb.TISSUE_H, tb.TISSUE_W, fc="#f4f1e8", ec="#999", hatch="||"))
ax.text(tb.WALL + tb.TISSUE_CLR / 2 + tb.TISSUE_H / 2, tb.FLOOR + tb.TISSUE_W * 0.75, f"衛生紙(直立)\n{tb.TISSUE_L:.0f}×{tb.TISSUE_W:.0f}×{tb.TISSUE_H:.0f}", ha="center", va="center", fontsize=10, bbox=dict(fc="white", ec="none", alpha=0.8))
zc = tb.SLOT_Z if tb.SLOT_Z is not None else (tb.FLOOR + z_top_cav) / 2
ax.add_patch(Rectangle((-0.5, zc - tb.SLOT_W / 2), tb.WALL + 1, tb.SLOT_W, fc="red", ec="red"))
ax.add_patch(FancyArrowPatch((5, zc), (-70, zc), arrowstyle="-|>", mutation_scale=25, color="red", lw=2.5))
ax.text(-38, zc + 8, "抽取方向\n(朝床, 與床頭板垂直)", ha="center", color="red", fontsize=11)
ax.axhline(zt, color="gray", ls=":", lw=1)
ax.text(tb.D_TOTAL + 8, zt - 3, "床頭板頂端", va="top", fontsize=10, color="gray")
ax.annotate("", (tb.D_TOTAL + 5, zt), (tb.D_TOTAL + 5, tb.H), arrowprops=dict(arrowstyle="<->", color="purple"))
ax.text(tb.D_TOTAL + 8, tb.H + 2, f"只高出 {tb.TOP_T:.0f} mm", color="purple", fontsize=11)
ax.annotate("", (-85, 0), (-85, zt), arrowprops=dict(arrowstyle="<->"))
ax.text(-88, zt / 2, f"盒高 {tb.H:.1f}\n（頂端以下 {zt:.1f}）", rotation=90, va="center", ha="right", fontsize=10)
ax.annotate("", (0, tb.H + 25), (tb.D_TOTAL, tb.H + 25), arrowprops=dict(arrowstyle="<->"))
ax.text(tb.D_TOTAL / 2, tb.H + 28, f"總深 {tb.D_TOTAL:.1f}（盒 {tb.DB:.0f} + 夾槽 {tb.GAP:.1f} + 扣腳 {tb.BACK_T:.0f}）", ha="center")
ax.add_patch(FancyArrowPatch((tb.DB / 2, tb.H + 60), (tb.DB / 2, tb.H + 6), arrowstyle="-|>", mutation_scale=20, color=LID_C, lw=2))
ax.text(tb.DB / 2, tb.H + 63, "上蓋在頂部（與頂面齊平）", ha="center", fontsize=11)
ax.text(-105, -65, "← 床 / 枕頭側", fontsize=12); ax.text(tb.D_TOTAL + 5, -65, "牆側 →", fontsize=12)
ax.set_xlim(-125, 200); ax.set_ylim(-75, tb.H + 85); ax.set_aspect("equal"); ax.axis("off")
ax.set_title(f"側面剖面示意（寬 {tb.W:.0f} mm 沿床頭板方向）", fontsize=13)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "preview_section.png"), dpi=130); plt.close(fig)

# 3. 列印擺放 (A1 mini 180x180x180)
bed = box_mesh(0, 0, -2, 180, 180, 0)
b_p = body.copy(); b_p.apply_translation([(180 - tb.W) / 2, (180 - tb.D_TOTAL) / 2, 0])
l_p = lid.copy(); l_p.apply_translation([(180 - l_p.extents[0]) / 2, (180 - l_p.extents[1]) / 2, 0])
fig, axs = plt.subplots(1, 2, figsize=(15, 7.5))
for ax, (m, c, t) in zip(axs, [(b_p, BOX_C, "主體：開口朝上直立列印（背面扣腳下方需支撐）"), (l_p, LID_C, "上蓋：外表面貼床、內嵌唇朝上")]):
    ax.imshow(render([(m, c, 1), (bed, np.array([0.55, 0.55, 0.55]), 1)], 25, -55, size=(900, 800))); ax.axis("off"); ax.set_title(t, fontsize=14)
fig.suptitle("Bambu Lab A1 mini 列印平台 180 × 180 mm（灰色）／高度上限 180 mm", fontsize=15)
fig.tight_layout(rect=[0, 0, 1, 0.95]); fig.savefig(os.path.join(OUT, "preview_print_layout.png"), dpi=110); plt.close(fig)
print("done")
