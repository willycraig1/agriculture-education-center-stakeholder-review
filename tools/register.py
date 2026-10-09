"""Register the three Seibert CAD sheets to one coordinate frame and write tools/registration.json.

The sheets come from the same CAD model plotted at different scales and rotations:
  survey -> study plan : matched on surveyed tree symbols (RANSAC on tree centroids, then least squares)
  survey -> fencing    : seeded on the existing pond (survey EDGE OF WATER vs. the small pond in the
                         12.4 AC paddock), refined by ICP on the pond outline plus the campus turnout-yard
                         fence line, which appears on both the study plan and the fencing plan.
Transforms are similarities z' = m*z + t on complex page coordinates (PDF points, y down).

Run:  python tools/register.py   (needs pymupdf, numpy, scipy)
"""
import json, os, sys
import numpy as np
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cadpdf
from trees import tree_marks

SRC = os.path.join(HERE, "..", "source")
SURVEY = os.path.join(SRC, "Survey + Soils Map Info.pdf")
STUDY = os.path.join(SRC, "Clark Farm Study Plan-A0.1 (3)1.pdf")
FENCE = os.path.join(SRC, "Clark Farm Proposed Fencing Plan.pdf")


def sample(f, layers, step=1.0, box=None):
    pts = []
    for ds in cadpdf.export(f, layers).values():
        for d in ds:
            for it in d["items"]:
                if it[0] == "l":
                    a, b = it[1], it[2]
                    n = max(1, int(abs(b - a) / step))
                    pts += [(a.x + (b.x - a.x) * k / n, a.y + (b.y - a.y) * k / n) for k in range(n + 1)]
                elif it[0] == "c":
                    pts += [(q.x, q.y) for q in it[1:5]]
    P = np.array(pts)
    if box:
        x0, y0, x1, y1 = box
        P = P[(P[:, 0] >= x0) & (P[:, 0] <= x1) & (P[:, 1] >= y0) & (P[:, 1] <= y1)]
    return P


def lsq(a, b):
    am, bm = a.mean(), b.mean()
    m = (np.conj(a - am) @ (b - bm)) / (np.conj(a - am) @ (a - am))
    return m, bm - m * am


def icp(A, B, m, t, iters=80, trim=0.5):
    tree = cKDTree(B)
    a = A[:, 0] + 1j * A[:, 1]
    b = B[:, 0] + 1j * B[:, 1]
    for _ in range(iters):
        z = m * a + t
        d, i = tree.query(np.c_[z.real, z.imag])
        k = d <= np.quantile(d, trim)
        m, t = lsq(a[k], b[i[k]])
    z = m * a + t
    return m, t, float(np.median(tree.query(np.c_[z.real, z.imag])[0]))


def survey_to_study():
    A, _ = tree_marks(SURVEY)
    B, _ = tree_marks(STUDY)
    a = A[:, 0] + 1j * A[:, 1]
    b = B[:, 0] + 1j * B[:, 1]
    tb = cKDTree(np.c_[b.real, b.imag])
    rng = np.random.default_rng(1)
    best = (0, None)
    for _ in range(200000):
        i, j = rng.choice(len(a), 2, replace=False)
        k, l = rng.choice(len(b), 2, replace=False)
        m = (b[l] - b[k]) / (a[j] - a[i])
        if not 1.5 < abs(m) < 10:
            continue
        t = b[k] - m * a[i]
        z = m * a + t
        n = (tb.query(np.c_[z.real, z.imag])[0] < 1.5 * abs(m)).sum()
        if n > best[0]:
            best = (n, (m, t))
    m, t = best[1]
    for _ in range(10):
        z = m * a + t
        d, i = tb.query(np.c_[z.real, z.imag])
        k = d < abs(m)
        m, t = lsq(a[k], b[i[k]])
    z = m * a + t
    d = tb.query(np.c_[z.real, z.imag])[0]
    return m, t, int((d < abs(m)).sum()), float(np.median(d[d < abs(m)]))


def survey_to_fence(m_ss, t_ss):
    # seed: survey pond centre -> fencing-plan small pond centre, survey north -> sheet +x
    m0 = 1.17j
    t0 = complex(1746, 1387) - m0 * complex(1384.5, 690)
    pond_f = sample(FENCE, ["P-BELOW-LIGHT"], 1, (1700, 1350, 1800, 1420))
    yard_f = sample(FENCE, ["FENCE", "(none)"], 1, (1150, 1120, 1500, 1460))
    pond_s = sample(SURVEY, ["EDGE OF WATER"], 0.3)
    yard_st = sample(STUDY, ["FENCE"], 3)
    z = (yard_st[:, 0] + 1j * yard_st[:, 1] - t_ss) / m_ss   # study -> survey frame
    yard_s = np.c_[z.real, z.imag]
    return icp(np.r_[pond_s, yard_s], np.r_[pond_f, yard_f], m0, t0)


if __name__ == "__main__":
    m_ss, t_ss, n_in, res_ss = survey_to_study()
    m_sf, t_sf, res_sf = survey_to_fence(m_ss, t_ss)
    c = lambda z: [round(z.real, 6), round(z.imag, 6)]
    out = {
        "_about": __doc__.strip().splitlines()[0],
        "survey_to_study": {"m": c(m_ss), "t": c(t_ss), "scale": abs(m_ss),
                            "rotation_deg": float(np.degrees(np.angle(m_ss))),
                            "tree_inliers": n_in, "median_residual_pt": res_ss},
        "survey_to_fence": {"m": c(m_sf), "t": c(t_sf), "scale": abs(m_sf),
                            "rotation_deg": float(np.degrees(np.angle(m_sf))),
                            "median_residual_pt": res_sf},
        "fence_ft_per_pt": 2.59,
        "fence_ft_per_pt_note": "Calibrated from the 14.4 AC and 4.9 AC paddock labels (2.586 and 2.592 ft/pt); about 1 in = 186 ft on the 36x24 sheet.",
    }
    json.dump(out, open(os.path.join(HERE, "registration.json"), "w"), indent=2)
    print(json.dumps(out, indent=2))
