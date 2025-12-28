import numpy as np
import pandas as pd
from scipy.optimize import linprog
import matplotlib.pyplot as plt
import warnings

def solve_dual_measure_mixed(output_file='measure.txt'):
    print("--- SOLVING WITH CONTINUOUS + DIRAC MASSES (CORRECTED) ---")

    # 1. Setup Discretization
    epsilon = 1e-1 # Slightly relaxed epsilon
    a = 0.41

    # Continuous supports
    n_bins_1 = 300
    n_bins_2 = 300

    s1 = np.linspace(-1.808 + epsilon, 0.026 - epsilon, n_bins_1 + 1)
    s2 = np.linspace(a + epsilon, 1 - epsilon, n_bins_2 + 1)

    starts = np.concatenate([s1[:-1], s2[:-1]])
    ends   = np.concatenate([s1[1:],  s2[1:]])
    widths = ends - starts
    n_continuous = len(starts)

    # Dirac point locations
    # We include the user's points and ensuring points near edges are present for stability
    dirac_points = np.array([
        -1.5, -1.0, -0.5, 0.0, 0.5, 0.75, 0.9
    ])
    # Ensure they are sorted
    dirac_points.sort()
    n_dirac = len(dirac_points)

    n_vars_continuous = n_continuous
    n_vars_dirac = n_dirac
    n_vars_total = n_vars_continuous + n_vars_dirac + 1
    print(f"Continuous bins: {n_continuous}, Dirac points: {n_dirac}, Total vars: {n_vars_total}")

    # 2. Setup Evaluation Grid
    x_grid = np.linspace(-1.81, 1.01, 3000)
    x_critical = np.concatenate([starts, ends, dirac_points])
    x_eval = np.unique(np.concatenate([x_grid, x_critical]))
    x_eval.sort()

    valid_mask = (x_eval >= -1.0) & (x_eval <= 1.0)
    x_eval = x_eval[valid_mask]
    n_constraints = len(x_eval)
    print(f"Constraint points: {n_constraints}")

    # 3. Build Potential Matrix A
    def F_primitive(u):
        res = np.zeros_like(u)
        mask = np.abs(u) > 1e-12
        um = u[mask]
        res[mask] = um - um * np.log(np.abs(um))
        return res

    def LogKernel(dist):
        """ Correct kernel for Dirac masses: -log|r| """
        res = np.zeros_like(dist)
        dist_abs = np.abs(dist)
        # Avoid infinity for solver stability, clamp to small radius
        dist_abs[dist_abs < 1e-12] = 1e-12
        return -np.log(dist_abs)

    A = np.zeros((n_constraints, n_vars_continuous + n_vars_dirac))

    # Continuous parts (integral over intervals)
    for j in range(n_continuous):
        val_start = starts[j] - x_eval
        val_end   = ends[j]   - x_eval
        A[:, j] = F_primitive(val_end) - F_primitive(val_start)

    # Dirac parts (point evaluation) -- FIXED
    for j in range(n_dirac):
        point = dirac_points[j]
        A[:, n_continuous + j] = LogKernel(point - x_eval)

    # 4. Solve LP
    c = np.zeros(n_vars_total)
    c[-1] = -1.0  # maximize delta

    A_ub = np.hstack([-A, np.ones((n_constraints, 1))])
    b_ub = np.zeros(n_constraints)

    A_eq = np.zeros((1, n_vars_total))
    A_eq[0, :n_continuous] = widths
    A_eq[0, n_continuous:n_continuous + n_dirac] = 1.0
    b_eq = np.array([1.0])

    bounds = [(0, None)] * n_continuous + [(0, None)] * n_dirac + [(None, None)]

    print("Running Mixed Linear Program...")
    res = linprog(c, A_ub=A_ub, b_ub=b_ub,
                  A_eq=A_eq, b_eq=b_eq,
                  bounds=bounds, method='highs')
    print("LP success:", res.success)

    if not res.success:
        print("Optimization Failed:", res.message)
        return

    # Extract solution
    continuous_densities = res.x[:n_continuous]
    dirac_masses = res.x[n_continuous:n_continuous + n_dirac]
    delta_opt = res.x[-1]
    print(f"\n--- SUCCESS ---")
    print(f"Maximized Minimum Potential: {delta_opt:.6f}")

    # Build DataFrames
    continuous_df = pd.DataFrame({
        'start': starts,
        'end': ends,
        'width': widths,
        'density': continuous_densities,
        'mass': continuous_densities * widths
    })
    continuous_df = continuous_df[continuous_df['mass'] > 1e-9]

    dirac_df = pd.DataFrame({
        'point': dirac_points,
        'mass': dirac_masses
    })
    dirac_df = dirac_df[dirac_df['mass'] > 1e-9]

    # --- Taos-style OUTPUT ---
    discrete_parts = [(float(m), float(x)) for m, x in zip(dirac_df['mass'], dirac_df['point'])]

    continuous_parts = [
        (float(row['mass']), float(row['start']), float(row['end']))
        for _, row in continuous_df.iterrows()
    ]

    discrete_parts.sort(key=lambda t: t[0], reverse=True)

    with open(output_file, 'w') as f:
        f.write("[\n")
        f.write(" {\n")
        f.write("  \"best_measure\": {\n")
        f.write("   \"discrete_parts\": [\n")
        for i, (m, x) in enumerate(discrete_parts):
            comma = "," if i + 1 < len(discrete_parts) else ""
            f.write(f"    ({m:.12f}, {x:.12f}){comma}\n")
        f.write("   ],\n")
        f.write("   \"continuous_parts\": [\n")
        for i, (m, s, e) in enumerate(continuous_parts):
            comma = "," if i + 1 < len(continuous_parts) else ""
            f.write(f"    ({m:.12f}, {s:.12f}, {e:.12f}){comma}\n")
        f.write("   ]\n")
        f.write("  }\n")
        f.write(" }\n")
        f.write("]\n")

    print(f"Saved Taos-style measure to '{output_file}'")

    # --- PLOTTING (PRESERVING STYLE) ---
    print("Generating Mixed Plot...")

    x_plot = np.linspace(-2.0, 2.0, 4000)
    potential_plot = np.zeros_like(x_plot)

    # Use F_primitive (F_direct) for Continuous
    def F_direct(val):
        res = np.zeros_like(val)
        mask = np.abs(val) > 1e-12
        v = val[mask]
        res[mask] = v - v * np.log(np.abs(v))
        return res

    for _, row in continuous_df.iterrows():
        d = row['density']
        s = row['start']
        e = row['end']
        val_end = e - x_plot
        val_start = s - x_plot
        term = F_direct(val_end) - F_direct(val_start)
        potential_plot += d * term

    # Use LogKernel for Dirac -- FIXED
    for _, row in dirac_df.iterrows():
        d = row['mass']
        p = row['point']
        term = LogKernel(p - x_plot)
        potential_plot += d * term

    mask_search = (x_plot >= -1.0) & (x_plot <= 1.0)
    idx_min = np.argmin(potential_plot[mask_search])
    x_min = x_plot[mask_search][idx_min]

    # --- ORIGINAL PLOTTING CODE BLOCK ---
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 9), sharex=False)
    plt.subplots_adjust(hspace=0.35)

    # Top: Measure visualization, clamped to [0,1]
    ax1.cla()

    for _, row in continuous_df.iterrows():
        s = row['start']
        e = row['end']
        d = row['density']
        y = min(3.0 * d, 1.0)
        ax1.hlines(y, s, e, color='blue', linewidth=2.0, alpha=0.9)

    if len(continuous_df) > 0:
        ax1.plot([], [], color='blue', linewidth=2.0, label='Continuous')

    if len(dirac_df) > 0:
        dx = dirac_df['point'].values
        dm = dirac_df['mass'].values
        y_top = np.minimum(dm, 1.0)
        ax1.vlines(dx, 0, y_top, color='green', linewidth=2)
        ax1.plot(dx, y_top, '^', color='green', markersize=8, label='Dirac')

    # Use the actual epsilon variable to define the visual bounds
    # Support 1: Starts at -1.808 + eps, ends at 0.026
    ax1.axvspan(-1.808 + epsilon, 0.026, color='red', alpha=0.2, label='Support 1')
    
    # Support 2: Starts at a (or a+eps per your discrete setup), ends STRICTLY at 1 - eps
    # This will make the red bar stop at 0.9, leaving the "forbidden" tip white.
    ax1.axvspan(a, 1.0 - epsilon, color='red', alpha=0.2, label='Support 2')

    ax1.set_title("Measure $\\lambda$ (Blue=Continuous, Green=Dirac)")
    ax1.set_ylabel("Density / Mass")
    ax1.set_xlim(-2.0, 2.0)
    ax1.set_ylim(0.0, 1.2)
    ax1.grid(True, linestyle='--', alpha=0.5)
    ax1.legend(loc='upper right')

    # Bottom: Potential – show LP min and x*
    ax2.plot(x_plot, potential_plot, color='purple', linewidth=1.5, label=r"$U_\lambda(x)$")
    ax2.axhline(0, color='black', linestyle='--', linewidth=1, label='y=0')

    ax2.plot(x_min, delta_opt, 'ro', zorder=5,
             label=f"Min value = {delta_opt:.4f} at x ≈ {x_min:.4f}")

    ax2.set_title(f"Logarithmic Potential $U_\\lambda(x)$ on [-1, 1] (Score: {delta_opt:.4f})")
    ax2.set_ylabel(r"Potential $U_\lambda(x)$")
    ax2.set_xlabel("x")
    ax2.set_xlim(-1.0, 1.0)
    ax2.grid(True, linestyle='--', alpha=0.5)
    ax2.legend(loc='upper right')

    plt.savefig('plot.jpg', dpi=150)
    print("Saved 'plot.jpg'")

solve_dual_measure_mixed()