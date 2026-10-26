"""圓角特寫預覽: 抽取口與頂部掀蓋缺口."""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from manifold3d import Manifold
import tissue_box as tb
from raster import render

plt.rcParams["font.sans-serif"] = ["WenQuanYi Zen Hei", "DejaVu Sans"]
C = np.array([0.33, 0.62, 0.86])
b = tb.body()
zc = tb.SLOT_Z if tb.SLOT_Z is not None else (tb.FLOOR + tb.H - tb.LID_T) / 2
slot_end = tb.to_trimesh(b ^ Manifold.cube([40, 25, 40]).translate([tb.W / 2 - 20, -5, zc + tb.SLOT_L / 2 - 25]))
top = tb.to_trimesh(b ^ Manifold.cube([50, 30, 30]).translate([tb.W / 2 - 25, -5, tb.H - 28]))
corner = tb.to_trimesh(b ^ Manifold.cube([30, 30, 30]).translate([-1, -1, -1]))
fig, axs = plt.subplots(1, 3, figsize=(18, 6.5))
for ax, (m, el, az, t) in zip(axs, [
    (slot_end, 20, -70, f"抽取口邊緣：內外兩側 R{tb.SLOT_EDGE_R}"),
    (top, 30, -65, f"掀蓋缺口：內外兩側 R{tb.SLOT_EDGE_R}"),
    (corner, 25, -55, f"盒身外角：R{tb.EDGE_R}"),
]):
    ax.imshow(render([(m, C, 1)], el, az, size=(700, 650))); ax.axis("off"); ax.set_title(t, fontsize=14)
fig.tight_layout(); fig.savefig(os.path.join(tb.OUT, "preview_rounded_edges.png"), dpi=110)
print("done")
