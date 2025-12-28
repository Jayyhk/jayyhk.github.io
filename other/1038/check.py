import ast
import numpy as np
import matplotlib.pyplot as plt

# ==========================================
# 1. PARAMETERS & CONSTRAINTS
# ==========================================
FILENAME = "measure.txt"
EPSILON = 0.1
A_VAL = 0.41

# "Problem 4.1" Safe Zones
# Left: [-1.808 + eps, 0.026]
# Right: [a, 1 - eps]
LEFT_ZONE = (-1.808 + EPSILON, 0.026)
RIGHT_ZONE = (A_VAL, 1.0 - EPSILON)

# ==========================================
# 2. HELPER FUNCTIONS
# ==========================================
def in_safe_zone(x, tolerance=1e-7):
    """Checks if x is within the Left or Right safe zone."""
    in_left = (x >= LEFT_ZONE[0] - tolerance) and (x <= LEFT_ZONE[1] + tolerance)
    in_right = (x >= RIGHT_ZONE[0] - tolerance) and (x <= RIGHT_ZONE[1] + tolerance)
    return in_left or in_right

def log_potential_point(x, weight, pos):
    """Potential from a point mass: w * log(1/|x-t|)"""
    if abs(x - pos) < 1e-12:
        return np.inf  # Singularity
    return weight * np.log(1.0 / abs(x - pos))

def log_potential_segment(x, weight, a, b):
    """Potential from a uniform mass distributed on [a, b]."""
    if abs(b - a) < 1e-12: 
        return log_potential_point(x, weight, a)
    
    rho = weight / (b - a)
    
    def F(u):
        if abs(u) < 1e-12: return 0.0
        return u - u * np.log(abs(u))

    # Integral of log(1/|x-t|) on [a,b] is F(x-a) - F(x-b)
    val = F(x - a) - F(x - b)
    return rho * val

# ==========================================
# 3. VERIFICATION LOGIC
# ==========================================
def verify():
    print(f"--- Loading {FILENAME} ---")
    try:
        with open(FILENAME, 'r') as f:
            content = f.read()
            # FIX: Use ast.literal_eval instead of json.load
            # This handles Python tuple syntax (...) correctly
            data = ast.literal_eval(content)
            
            measure = data[0]['best_measure']
            discrete = measure.get('discrete_parts', [])
            continuous = measure.get('continuous_parts', [])
            
    except Exception as e:
        print(f"ERROR: Could not parse file. {e}")
        return

    print(f"Parameters: epsilon={EPSILON}, a={A_VAL}")
    print(f"Allowed Support: {LEFT_ZONE} U {RIGHT_ZONE}")
    
    all_passed = True
    
    # --- CHECK 1: SUPPORT ---
    print("\n[CHECK 1] Verifying Support...")
    support_fail = False
    
    # Check discrete masses
    for w, pos in discrete:
        if not in_safe_zone(pos):
            print(f"  FAIL: Point mass at {pos:.6f} is OUTSIDE allowed zones.")
            support_fail = True
            
    # Check continuous segments
    for w, start, end in continuous:
        # Check both endpoints
        if not (in_safe_zone(start) and in_safe_zone(end)):
            # Also ensure it doesn't span across the forbidden gap
            # (i.e. start in Left, end in Right)
            if (start < LEFT_ZONE[1] and end > RIGHT_ZONE[0]):
                print(f"  FAIL: Segment [{start:.4f}, {end:.4f}] crosses forbidden gap.")
                support_fail = True
            elif not in_safe_zone(start):
                print(f"  FAIL: Segment start {start:.6f} is OUTSIDE.")
                support_fail = True
            elif not in_safe_zone(end):
                print(f"  FAIL: Segment end {end:.6f} is OUTSIDE.")
                support_fail = True

    if not support_fail:
        print("  PASS: All support is within safe zones.")
    else:
        all_passed = False

    # --- CHECK 2: POSITIVITY ON [-1, 1] ---
    print("\n[CHECK 2] Verifying Positivity on [-1, 1]...")
    x_vals = np.linspace(-1.0, 1.0, 5000)
    potentials = np.zeros_like(x_vals)

    for i, x in enumerate(x_vals):
        p = 0.0
        for w, pos in discrete:
            p += log_potential_point(x, w, pos)
        for w, start, end in continuous:
            p += log_potential_segment(x, w, start, end)
        potentials[i] = p

    min_pot = np.min(potentials)
    print(f"  Minimum Potential: {min_pot:.6f}")

    if min_pot >= -1e-6: # Allow tiny numerical error
        print("  PASS: Potential is non-negative on [-1, 1].")
    else:
        print("  FAIL: Potential dips below zero.")
        all_passed = False

    # --- PLOT ---
    plt.figure(figsize=(10, 5))
    plt.plot(x_vals, potentials, label=r"$U_\lambda(x)$", color='blue')
    plt.axhline(0, color='red', linestyle='--', linewidth=1)
    
    # Shade allowed zones
    plt.axvspan(LEFT_ZONE[0], LEFT_ZONE[1], color='green', alpha=0.1, label='Allowed (Left)')
    plt.axvspan(RIGHT_ZONE[0], RIGHT_ZONE[1], color='orange', alpha=0.1, label='Allowed (Right)')
    
    plt.title(f"Verification Plot (Min: {min_pot:.4f})")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig("verification_plot.png")
    print("\nSaved plot to verification_plot.png")

    # --- FINAL VERDICT ---
    print("\n" + "="*30)
    if all_passed:
        print("VERDICT: SUCCESS - Fits all constraints.")
    else:
        print("VERDICT: FAILURE - Constraints violated.")
    print("="*30)

if __name__ == "__main__":
    verify()