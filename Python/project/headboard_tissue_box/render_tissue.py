"""示意圖: 衛生紙在盒內的擺放方向 (開口面 140x100 朝床)."""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import trimesh
from manifold3d import Manifold
import tissue_box as tb
from raster import render

plt.rcParams["font.sans-serif"] = ["WenQuanYi Zen Hei", "DejaVu Sans"]


def box_mesh(x0, y0, z0, x1, y1, z1):
    m = trimesh.creation.box(extents=[x1 - x0, y1 - y0, z1 - z0])
    m.apply_translation([(x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2])
    return m


c = tb.TISSUE_CLR / 2
x0, y0, z0 = tb.WALL + c, tb.WALL + c, tb.FLOOR
pack = box_mesh(x0, y0, z0, x0 + tb.TISSUE_L, y0 + tb.TISSUE_H, z0 + tb.TISSUE_W)
# 衛生紙本身的抽取開口 (在 140x100 那一面, 朝床)
zc = z0 + tb.TISSUE_W / 2
opening = box_mesh(x0 + 25, y0 - 0.6, zc - 4, x0 + tb.TISSUE_L - 25, y0 + 0.5, zc + 4)
zt = tb.H - tb.TOP_T
by0 = tb.DB + tb.BOARD_CLR / 2
board = box_mesh(-30, by0, -40, tb.W + 30, by0 + tb.BOARD_T, zt)
half = tb.to_trimesh(tb.body() - Manifold.cube([tb.W / 2 + 1, 300, 300]).translate([-1, -50, -50]))

BOX_C = np.array([0.33, 0.62, 0.86]); BOARD_C = np.array([0.6, 0.45, 0.3])
PACK_C = np.array([0.97, 0.95, 0.9]); RED = np.array([0.9, 0.15, 0.15])
fig, axs = plt.subplots(1, 2, figsize=(16, 8))
axs[0].imshow(render([(pack, PACK_C, 1), (opening, RED, 1), (board, BOARD_C, 1)], 18, -60, size=(900, 800)))
axs[0].set_title("衛生紙擺放方向：開口在 140×100 那一面，朝床（紅色 = 開口）\n140 沿床頭板橫向、100 為高度、77 厚度朝床", fontsize=13)
axs[1].imshow(render([(half, BOX_C, 1), (pack, PACK_C, 1), (opening, RED, 1), (board, BOARD_C, 1)], 18, -60, size=(900, 800)))
axs[1].set_title("剖半的盒子：衛生紙開口正對盒子前面的抽取口", fontsize=13)
for a in axs:
    a.axis("off")
fig.tight_layout(); fig.savefig(os.path.join(tb.OUT, "preview_tissue_orientation.png"), dpi=110)
print("done")
