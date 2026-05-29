# Mathematical Formalism – GNSSPos

Reference document for the algorithms implemented in GNSSPos (GPS_Sassuolo_Forlì campaign).
All conventions follow RTKLIB and standard geodetic practice unless noted.

---

## 1. Coordinate Systems

### 1.1 ECEF (Earth-Centred Earth-Fixed)
Cartesian frame fixed to the Earth.  
WGS84 ellipsoid parameters:

| Symbol | Value |
|--------|-------|
| $a$ | 6 378 137.0 m (semi-major axis) |
| $f$ | 1/298.257223563 (flattening) |
| $b = a(1-f)$ | 6 356 752.314 m (semi-minor axis) |
| $e^2 = 1 - (b/a)^2$ | first eccentricity squared |

### 1.2 Geodetic (WGS84)
Position expressed as $(\varphi, \lambda, h)$ — latitude, longitude, ellipsoidal height.

ECEF → Geodetic (iterative or closed-form Bowring):

$$X = (N + h)\cos\varphi\cos\lambda, \quad Y = (N + h)\cos\varphi\sin\lambda, \quad Z = \left(N\frac{b^2}{a^2} + h\right)\sin\varphi$$

where $N(\varphi) = a / \sqrt{1 - e^2\sin^2\varphi}$ is the radius of curvature in the prime vertical.

### 1.3 Local NEU (North–East–Up)
Local frame centred at a reference point $(\varphi_0, \lambda_0, h_0)$.  
Rotation from ECEF increments $\Delta\mathbf{X}$:

$$\begin{bmatrix} \Delta N \\ \Delta E \\ \Delta U \end{bmatrix} =
\begin{bmatrix}
-\sin\varphi_0\cos\lambda_0 & -\sin\varphi_0\sin\lambda_0 & \cos\varphi_0 \\
-\sin\lambda_0             &  \cos\lambda_0              & 0             \\
 \cos\varphi_0\cos\lambda_0 &  \cos\varphi_0\sin\lambda_0 & \sin\varphi_0
\end{bmatrix}
\Delta\mathbf{X}$$

Standard deviations in the RTKLIB `.pos` file are reported in this frame:
$\sigma_N$ (`sdn`), $\sigma_E$ (`sde`), $\sigma_U$ (`sdu`).

### 1.4 UTM Zone 32N (EPSG:32632)
Transverse Mercator projection, central meridian 9°E, scale factor 0.9996.  
Used for metric distance computations and plots. Conversion via pyproj:

```
(E, N) = Transformer("EPSG:4326", "EPSG:32632").transform(lon, lat)
```

### 1.5 Web Mercator (EPSG:3857)
Spherical Mercator; used for OpenStreetMap tile alignment in contextily plots.

---

## 2. GNSS Positioning Models

### 2.1 Single-Point Positioning (Standalone)
Pseudorange observation for satellite $s$ at receiver $r$:

$$P_r^s = \rho_r^s + c(\delta t_r - \delta t^s) + I_r^s + T_r^s + \varepsilon_P$$

where:
- $\rho_r^s$ — geometric range
- $c$ — speed of light
- $\delta t_r, \delta t^s$ — receiver and satellite clock errors
- $I_r^s$ — ionospheric delay (L1 pseudo-range, Klobuchar model in Experiment B)
- $T_r^s$ — tropospheric delay (Saastamoinen model)
- $\varepsilon_P$ — noise + multipath

With precise ephemeris (SP3 + CLK), $\delta t^s$ is replaced by the IGS final clock correction; $\rho_r^s$ is computed from SP3 satellite positions. Satellite ephemeris selection in `satpos()` (`ephemeris.c:656`): `EPHOPT_PREC` → `peph2pos()` reads `nav->peph[]`/`nav->pclk[]`; Klobuchar uses `nav->ion_gps[]` independently (`pntpos.c:133–136`), so NAV + SP3 + CLK coexist without conflict.

### 2.2 RTK Kinematic (Experiments C and D)
Double-difference carrier-phase observable between rover $r$, base $b$, satellites $s$, $k$:

$$\nabla\Delta\phi_{rb}^{sk} = \nabla\Delta\rho_{rb}^{sk} + \lambda\,\nabla\Delta N_{rb}^{sk} - \nabla\Delta I_{rb}^{sk} + \nabla\Delta T_{rb}^{sk} + \nabla\Delta\varepsilon_\phi$$

Double-differencing eliminates receiver clock errors ($\delta t_r, \delta t_b$) and satellite clock errors ($\delta t^s, \delta t^k$). For short-to-medium baselines ($\lesssim 20$ km) the differential ionosphere $\nabla\Delta I_{rb}^{sk}$ is small and can be modelled as zero (`pos1-ionoopt = off`) or with Klobuchar (`brdc`).

Ambiguity resolution: LAMBDA algorithm in continuous mode (`pos2-armode = continuous`). uBlox EVK-M8T is L1-only; float solutions (Q=2) are expected when integer fixing fails.

Configuration used (Experiment C): `ublox_kinematic.conf`.

---

## 3. IGS Precise Products

| Product | File pattern | Content | Source |
|---------|-------------|---------|--------|
| SP3 final | `IGS0OPSFIN_*_15M_ORB.SP3` | Satellite positions, 15 min | NASA CDDIS |
| CLK final | `IGS0OPSFIN_*_05M_CLK.CLK` | Satellite clocks, 5 min | NASA CDDIS |
| GIM (IONEX) | `IGS0OPSFIN_*_02H_GIM.INX` | Global ionosphere map, 2 h | NASA CDDIS |
| TRO | `*_MEDI00ITA_TRO.TRO` | Troposphere delay, MEDI station | NASA CDDIS |
| Broadcast NAV | `brdc*.23n` | Klobuchar coefficients, GLONASS channel numbers | IGS |

Priority rule (implemented, not enforced by RTKLIB):
1. SP3 + CLK (highest accuracy) — `pos1-sateph = precise`
2. Final NAV — `pos1-sateph = brdc`
3. Broadcast NAV — fallback

---

## 4. Inverse-Variance Weighted Combination (Experiment D)

### 4.1 Position

Let $N$ receivers produce position vectors at epoch $t$:

$$\underline{X}_i = \begin{bmatrix} n_i \\ e_i \\ u_i \end{bmatrix}$$

in the local NEU frame (northing $n$, easting $e$, up $u$, all in metres).

Per-component inverse-variance weights for receiver $i$, component $j \in \{n, e, u\}$:

$$w_{ij} = \frac{1/\sigma_{ji}^2}{\displaystyle\sum_{k=1}^{N} 1/\sigma_{jk}^2}$$

Diagonal weight matrix:

$$W_i = \begin{bmatrix} w_{in} & 0 & 0 \\ 0 & w_{ie} & 0 \\ 0 & 0 & w_{iu} \end{bmatrix}$$

Combined position estimate:

$$\hat{X} = \sum_{i=1}^{N} W_i\,\underline{X}_i$$

Note: $\sum_i w_{ij} = 1$ for each $j$, so $\hat{X}$ is a convex combination per component.

### 4.2 Covariance

Per-receiver NEU covariance matrix (from RTKLIB `.pos` fields):

$$C_i = \begin{bmatrix}
\sigma_{ni}^2  & \sigma_{ne,i} & \sigma_{un,i} \\
\sigma_{ne,i}  & \sigma_{ei}^2 & \sigma_{eu,i} \\
\sigma_{un,i}  & \sigma_{eu,i} & \sigma_{ui}^2
\end{bmatrix}$$

where the diagonal terms are squared values of `sdn`, `sde`, `sdu` and the off-diagonal terms are `sdne`, `sdeu`, `sdun` respectively.

Combined covariance:

$$\hat{C} = \sum_{i=1}^{N} W_i\,C_i\,W_i^T$$

Since $W_i$ is diagonal, element $(j,k)$ of $\hat{C}$ is:

$$\hat{C}_{jk} = \sum_{i=1}^{N} w_{ij}\,w_{ik}\,{C_i}_{jk}$$

### 4.3 Positive-Definiteness Regularisation

A necessary condition for a valid covariance matrix is $\det(\hat{C}) > 0$.  
If this fails (can occur when cross-correlation terms are large), iteratively scale all off-diagonal elements:

$$\hat{C}_{jk} \leftarrow 0.9 \cdot \hat{C}_{jk} \quad \forall\, j \neq k$$

until $\det(\hat{C}) > 0$.  Maximum iterations: 2000.

> **TODO (supervisors):** Alternative — project onto the nearest positive semi-definite matrix by eigenvalue clamping (Higham 1988):
> $$\hat{C} = V \max(\Lambda, 0) V^T, \quad \hat{C} = V\Lambda V^T \text{ (eigendecomposition)}$$

### 4.4 Output Standard Deviations

From the regularised $\hat{C}$:

$$\hat{\sigma}_n = \sqrt{\hat{C}_{00}}, \quad \hat{\sigma}_e = \sqrt{\hat{C}_{11}}, \quad \hat{\sigma}_u = \sqrt{\hat{C}_{22}}$$
$$\widehat{\sigma_{ne}} = \hat{C}_{01}, \quad \widehat{\sigma_{eu}} = \hat{C}_{12}, \quad \widehat{\sigma_{un}} = \hat{C}_{20}$$

Quality flag: $\hat{Q} = \min_i Q_i$, $\hat{n}_s = \min_i n_{s,i}$.

---

## 5. Time Alignment and Gap Filling

### 5.1 Common Time Window

Given $M$ series with index ranges $[t_{i,\min}, t_{i,\max}]$:

$$t_\text{start} = \max_i t_{i,\min}, \qquad t_\text{end} = \min_i t_{i,\max}$$

### 5.2 Linear Interpolation for Positions

For a missing epoch $t$ between bracketing epochs $t_1 < t < t_2$:

$$\alpha = \frac{t - t_1}{t_2 - t_1}, \qquad \hat{x}(t) = (1-\alpha)\,x(t_1) + \alpha\,x(t_2)$$

Applied to $(\varphi, \lambda, h)$.

### 5.3 Variance Propagation for Covariances

For the interpolated epoch, covariance elements follow:

$$\hat{\sigma}^2(t) = (1-\alpha)^2\,\sigma^2(t_1) + \alpha^2\,\sigma^2(t_2)$$

This is a conservative estimate (ignores temporal correlation between $t_1$ and $t_2$).

---

## 6. Accuracy Metrics

All metrics are computed in UTM32N metric space $(\hat{n}, \hat{e}, \hat{u})$, comparing experiment series $\mathbf{x}$ against reference series $\mathbf{r}$ (Experiment 0 baseline).

### 6.1 Root Mean Square Error (per axis)

$$\text{RMS}_j(T) = \sqrt{\frac{1}{T}\sum_{t=1}^{T} \left(x_j(t) - r_j(t)\right)^2}, \quad j \in \{n, e, u\}$$

Computed as a cumulative time series (running RMS up to epoch $T$).

### 6.2 Mean 3-D Distance

$$\mu_d = \frac{1}{T}\sum_{t=1}^{T} d(t), \qquad d(t) = \sqrt{(\Delta n)^2 + (\Delta e)^2 + (\Delta u)^2}$$

### 6.3 Standard Deviation of 3-D Distance

$$\sigma_d = \sqrt{\frac{1}{T}\sum_{t=1}^{T}\left(d(t) - \mu_d\right)^2}$$

---

## 7. Dataset – GPS Sassuolo / Forlì Campaign

| Item | Detail |
|------|--------|
| Date | 2023-06-27 (DOY 178, GPS week 2268) |
| Baseline | Leica 1200 at fixed base, Sassuolo area |
| Rovers (low-cost) | 3× uBlox EVK-M8T (COM23, COM24, COM25), L1-only |
| Rover (high-cost) | Leica 1200 rover (45601780), dual-frequency |
| Baseline NMEA | LocationAPI smartphone receiver (COM23 NMEA) |
| Flight session | Volo_1: 09:05 – 11:57 UTC |
| RTKLIB version | EX 2.5.0 (native Linux, compiled from rtklibexplorer/RTKLIB@b34) |

### Experiment Summary

| Exp | Mode | Receivers | Ephemeris | Result |
|-----|------|-----------|-----------|--------|
| 0 | NMEA GGA (baseline) | COM23 smartphone | — | $\sim$5 m 2-D accuracy |
| A | RTK kinematic | Leica 1200 rover + base | SP3+CLK | ~30 s valid data |
| B | Standalone | COM23/24/25 | SP3+CLK+NAV | Q=5 (single) |
| C | RTK kinematic | COM23/24/25 + Leica base | SP3+CLK+NAV | Q=2 (float) |
| D | Weighted fusion | COM23+24+25 (Exp C) | — | Q=2, $\sigma$ reduced ≈43% |

---

## 8. RTKLIB Source References

Key functions cited in code comments:

| Function | File | Role |
|----------|------|------|
| `satpos()` | `ephemeris.c:656` | Selects precise vs broadcast ephemeris |
| `peph2pos()` | `preceph.c:552` | Reads SP3 (`nav->peph`) and CLK (`nav->pclk`) |
| `ionocorr()` | `pntpos.c:235` | Applies ionosphere correction independently of sateph |
| `readpreceph()` | `postpos.c:456` | Loads SP3 + CLK into `nav_t` |
| `readobsnav()` | `postpos.c:537` | Loads broadcast NAV into `nav_t` |

`nav_t` stores SP3/CLK and broadcast data in **separate fields** — they do not conflict when both are passed to `rnx2rtkp`.
