import numpy as np

class Camera:
    def __init__(self, pos, target, W, H, hfov_deg):
        self.pos = np.array(pos, float); self.W = W; self.H = H
        f = np.array(target, float) - self.pos; f /= np.linalg.norm(f)
        r = np.cross(f, [0, 0, 1.0]); r /= np.linalg.norm(r)
        u = np.cross(r, f)
        self.f, self.r, self.u = f, r, u
        self.F = (W / 2) / np.tan(np.radians(hfov_deg) / 2)

    def cam(self, p):
        d = np.atleast_2d(p) - self.pos
        return np.stack([d @ self.r, d @ self.u, d @ self.f], axis=1)

    def proj_c(self, c):
        return np.stack([self.W / 2 + self.F * c[:, 0] / c[:, 2], self.H / 2 - self.F * c[:, 1] / c[:, 2]], axis=1)

    def proj(self, p):
        return self.proj_c(self.cam(p))

    def clip_poly(self, p, near=2.0):
        """Clip a 3D polygon against camera near plane; return screen pts (or None) and cam coords."""
        c = self.cam(p)
        out = []
        n = len(c)
        for i in range(n):
            a, b = c[i], c[(i + 1) % n]
            ina, inb = a[2] >= near, b[2] >= near
            if ina: out.append(a)
            if ina != inb:
                t = (near - a[2]) / (b[2] - a[2]); out.append(a + (b - a) * t)
        if len(out) < 2: return None, None
        out = np.array(out)
        return self.proj_c(out), out

    def scale_at(self, p):
        """pixels per foot at world point p."""
        return self.F / self.cam(p)[0, 2]

    def horizon_y(self):
        # direction with zero elevation straight ahead
        d = np.array([self.f[0], self.f[1], 0.0]); d /= np.linalg.norm(d)
        c = np.array([d @ self.r, d @ self.u, d @ self.f])
        return self.H / 2 - self.F * c[1] / c[2]
