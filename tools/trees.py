"""Turn a CAD tree-symbol layer (many small strokes per symbol) into one point per tree."""
import numpy as np
from scipy.cluster.vq import kmeans2
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from scipy.spatial import cKDTree

import cadpdf


def tree_marks(f, layer="TreesMARK", split_parts=None):
    """Return (array of [x, y, symbol_size, n_strokes], median stroke size).

    Strokes closer than about one stroke size are joined into a symbol. If split_parts is given,
    groups with many more strokes than one symbol (touching symbols) are split with k-means.
    """
    ds = cadpdf.export(f, [layer]).get(layer, [])
    R = np.array([[d["rect"].x0, d["rect"].y0, d["rect"].x1, d["rect"].y1] for d in ds])
    C = np.c_[(R[:, 0] + R[:, 2]) / 2, (R[:, 1] + R[:, 3]) / 2]
    size = np.median(np.maximum(R[:, 2] - R[:, 0], R[:, 3] - R[:, 1]))
    pairs = cKDTree(C).query_pairs(size * 0.9, output_type="ndarray")
    n = len(C)
    M = coo_matrix((np.ones(len(pairs)), (pairs[:, 0], pairs[:, 1])), shape=(n, n))
    k, lab = connected_components(M, directed=False)
    out = []
    for i in range(k):
        idx = lab == i
        groups = [(R[idx], C[idx])]
        if split_parts and idx.sum() > 1.5 * split_parts:
            kk = int(round(idx.sum() / split_parts))
            _, sub = kmeans2(C[idx], kk, seed=1, minit="++")
            groups = [(R[idx][sub == j], C[idx][sub == j]) for j in range(kk) if (sub == j).any()]
        for r, _c in groups:
            out.append(((r[:, 0].min() + r[:, 2].max()) / 2, (r[:, 1].min() + r[:, 3].max()) / 2,
                        max(r[:, 2].max() - r[:, 0].min(), r[:, 3].max() - r[:, 1].min()), len(r)))
    return np.array(out), size
