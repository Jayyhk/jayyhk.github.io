import matplotlib.pyplot as plt


def compute_full_count_probability(p):
    P = [[0 for _ in range(4)] for _ in range(5)]
    for b in range(4, -1, -1):
        for s in range(3, -1, -1):
            if b == 4:
                P[b][s] = 1
            elif s == 3:
                P[b][s] = 0
            else:
                P[b][s] = (
                    P[b + 1][s] * (4 * p + (1 - p) * P[b][s + 1]) - (P[b][s + 1]) ** 2
                ) / (P[b + 1][s] - 2 * P[b][s + 1] + 4 * p + (1 - p) * P[b][s + 1])

    A = [[0 for _ in range(4)] for _ in range(5)]
    for b in range(4, -1, -1):
        for s in range(3, -1, -1):
            if b == 4 or s == 3:
                A[b][s] = 0
            else:
                A[b][s] = (p * (4 - P[b][s + 1])) / (
                    P[b + 1][s] - P[b][s + 1] + p * (4 - P[b][s + 1])
                )

    F = [[0 for _ in range(4)] for _ in range(5)]
    for b in range(4, -1, -1):
        for s in range(3, -1, -1):
            if b == 4 or s == 3:
                F[b][s] = 0
            elif b == 3 and s == 2:
                F[b][s] = 1
            else:
                F[b][s] = (
                    (A[b][s]) ** 2 * F[b + 1][s]
                    + 2 * A[b][s] * (1 - A[b][s]) * F[b][s + 1]
                    + (1 - A[b][s]) ** 2 * (1 - p) * F[b][s + 1]
                )

    return F[0][0]


def golden_section_max(f, a=0.0, b=1.0, tol=1e-12, max_iter=10000):
    phi = (1 + 5**0.5) / 2
    invphi = 1 / phi
    c = b - invphi * (b - a)
    d = a + invphi * (b - a)
    fc = f(c)
    fd = f(d)
    it = 0
    while (b - a) > tol and it < max_iter:
        if fc < fd:
            a, c, fc = c, d, fd
            d = a + invphi * (b - a)
            fd = f(d)
        else:
            b, d, fd = d, c, fc
            c = b - invphi * (b - a)
            fc = f(c)
        it += 1
    p_star = 0.5 * (a + b)
    return p_star, f(p_star)


# Compute optimal p and q
p_star, q = golden_section_max(compute_full_count_probability, 0.0, 1.0)
print(f"Optimal p: {round(float(p_star), 10)}")
print(f"Optimal q: {round(float(q), 10)}")

# Plot p vs q
p_values = []
f_values = []
for i in range(100001):
    p = i / 100000.0
    try:
        f = compute_full_count_probability(p)
        p_values.append(p)
        f_values.append(f)
    except ZeroDivisionError:
        pass  # Skip p values that cause division by zero
plt.figure(figsize=(10, 6))
plt.plot(p_values, f_values, label="q(p) = F[0][0]")
plt.axvline(
    x=p_star,
    color="r",
    linestyle="--",
    label=f"Maximum q ≈ {q:.10f} at p ≈ {p_star:.10f}",
)
plt.xlabel("p (Probability of Home Run)")
plt.ylabel("q (Probability of Reaching a Full Count)")
plt.title("Relationship between p and q in Robot Baseball")
plt.legend()
plt.grid(True)
plt.show()
