"""簡易 z-buffer 軟體算繪 (無外部依賴), 用來輸出乾淨的預覽圖."""
import numpy as np


def look(elev, azim):
    e, a = np.radians(elev), np.radians(azim)
    fwd = -np.array([np.cos(e) * np.cos(a), np.cos(e) * np.sin(a), np.sin(e)])  # 視線方向
    right = np.cross(fwd, [0, 0, 1]); right /= np.linalg.norm(right)
    up = np.cross(right, fwd)
    return right, up, fwd


def render(items, elev=20, azim=-60, size=(1000, 800), margin=40, bg=(1, 1, 1)):
    """items: list of (trimesh, rgb, alpha). 回傳 HxWx3 影像."""
    right, up, fwd = look(elev, azim)
    light = -fwd * 0.6 + up * 0.6 + right * 0.3; light /= np.linalg.norm(light)
    allv = np.vstack([m.vertices for m, _, _ in items])
    P = np.c_[allv @ right, allv @ up]
    lo, hi = P.min(0), P.max(0)
    Wd, Ht = size
    sc = min((Wd - 2 * margin) / (hi[0] - lo[0]), (Ht - 2 * margin) / (hi[1] - lo[1]))
    off = np.array([Wd, Ht]) / 2 - sc * (lo + hi) / 2
    img = np.ones((Ht, Wd, 3)) * np.array(bg)
    zbuf = np.full((Ht, Wd), np.inf)
    ebuf = np.zeros((Ht, Wd), dtype=np.int32)  # 物件 id, 用於輪廓
    nbuf = np.zeros((Ht, Wd, 3))
    layers = []
    for oid, (m, col, alpha) in enumerate(items, start=1):
        V = m.vertices
        S = np.c_[V @ right * sc + off[0], Ht - (V @ up * sc + off[1]), V @ fwd]
        N = m.face_normals
        shade = 0.35 + 0.65 * np.abs(N @ light)
        target = (img, zbuf, ebuf, nbuf) if alpha >= 1 else (np.zeros_like(img), np.full((Ht, Wd), np.inf), np.zeros_like(ebuf), np.zeros_like(nbuf))
        ti, tz, te, tn = target
        for f, (a, b, c) in enumerate(m.faces):
            pa, pb, pc = S[a], S[b], S[c]
            x0, x1 = int(max(0, np.floor(min(pa[0], pb[0], pc[0])))), int(min(Wd - 1, np.ceil(max(pa[0], pb[0], pc[0]))))
            y0, y1 = int(max(0, np.floor(min(pa[1], pb[1], pc[1])))), int(min(Ht - 1, np.ceil(max(pa[1], pb[1], pc[1]))))
            if x1 < x0 or y1 < y0:
                continue
            den = (pb[1] - pc[1]) * (pa[0] - pc[0]) + (pc[0] - pb[0]) * (pa[1] - pc[1])
            if abs(den) < 1e-9:
                continue
            xs, ys = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
            l1 = ((pb[1] - pc[1]) * (xs - pc[0]) + (pc[0] - pb[0]) * (ys - pc[1])) / den
            l2 = ((pc[1] - pa[1]) * (xs - pc[0]) + (pa[0] - pc[0]) * (ys - pc[1])) / den
            l3 = 1 - l1 - l2
            ins = (l1 >= -1e-6) & (l2 >= -1e-6) & (l3 >= -1e-6)
            z = l1 * pa[2] + l2 * pb[2] + l3 * pc[2]
            sub = tz[y0:y1 + 1, x0:x1 + 1]
            upd = ins & (z < sub)
            sub[upd] = z[upd]
            ti[y0:y1 + 1, x0:x1 + 1][upd] = np.array(col) * shade[f]
            te[y0:y1 + 1, x0:x1 + 1][upd] = oid
            tn[y0:y1 + 1, x0:x1 + 1][upd] = N[f]
        if alpha < 1:
            layers.append((ti, tz, alpha))
    # 輪廓線: 物件邊界、深度跳躍、法向折角
    edge = np.zeros((Ht, Wd), bool)
    for ax in (0, 1):
        de = np.diff(ebuf, axis=ax) != 0
        dz = np.abs(np.diff(np.where(np.isinf(zbuf), 1e6, zbuf), axis=ax)) > 3 / sc * 0 + 2.0
        dn = np.sum(np.diff(nbuf, axis=ax) ** 2, -1) > 0.3
        e = de | dz | dn
        if ax == 0:
            edge[1:] |= e
        else:
            edge[:, 1:] |= e
    img[edge] *= 0.25
    for ti, tz, alpha in layers:  # 半透明物件 (床頭板) 疊在後面不可見處
        m = np.isfinite(tz) & (tz < zbuf)
        img[m] = img[m] * (1 - alpha) + ti[m] * alpha
        behind = np.isfinite(tz) & ~m
        img[behind] = img[behind] * (1 - alpha * 0.25) + ti[behind] * alpha * 0.25
    return np.clip(img, 0, 1)
