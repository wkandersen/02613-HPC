from os.path import join
import sys
import time

import numpy as np
import numba

def load_data(load_dir, bid):
    SIZE = 512
    u = np.zeros((SIZE + 2, SIZE + 2))
    u[1:-1, 1:-1] = np.load(join(load_dir, f"{bid}_domain.npy"))
    interior_mask = np.load(join(load_dir, f"{bid}_interior.npy"))
    return u, interior_mask


def jacobi(u, interior_mask, max_iter, atol=1e-6):
    u = np.copy(u)

    for _ in range(max_iter):
        u_new = 0.25 * (u[1:-1, :-2] + u[1:-1, 2:] + u[:-2, 1:-1] + u[2:, 1:-1])
        u_new_interior = u_new[interior_mask]
        delta = np.abs(u[1:-1, 1:-1][interior_mask] - u_new_interior).max()
        u[1:-1, 1:-1][interior_mask] = u_new_interior

        if delta < atol:
            break
    return u


@numba.njit
def jacobi_numba(u, interior_mask_indices, max_iter, atol=1e-6):
    u = u.copy()

    for _ in range(max_iter):
        u_new = 0.25 * (u[1:-1, :-2] + u[1:-1, 2:] + u[:-2, 1:-1] + u[2:, 1:-1])
        delta = 0.0

        for k in range(interior_mask_indices.shape[0]):
            i, j = interior_mask_indices[k, 0], interior_mask_indices[k, 1]
            diff = abs(u[1 + i, 1 + j] - u_new[i, j])
            if diff > delta:
                delta = diff
            u[1 + i, 1 + j] = u_new[i, j]

        if delta < atol:
            break

    return u


def summary_stats(u, interior_mask):
    u_interior = u[1:-1, 1:-1][interior_mask]
    mean_temp = u_interior.mean()
    std_temp = u_interior.std()
    pct_above_18 = np.sum(u_interior > 18) / u_interior.size * 100
    pct_below_15 = np.sum(u_interior < 15) / u_interior.size * 100
    return {
        'mean_temp': mean_temp,
        'std_temp': std_temp,
        'pct_above_18': pct_above_18,
        'pct_below_15': pct_below_15,
    }


if __name__ == '__main__':
    # Load data
    LOAD_DIR = '/dtu/projects/02613_2025/data/modified_swiss_dwellings/'
    with open(join(LOAD_DIR, 'building_ids.txt'), 'r') as f:
        building_ids = f.read().splitlines()

    if len(sys.argv) < 2:
        N = 1
    else:
        N = int(sys.argv[1])
    building_ids = building_ids[:N]

    # Load floor plans
    all_u0 = np.empty((N, 514, 514))
    all_interior_mask = np.empty((N, 512, 512), dtype='bool')
    for i, bid in enumerate(building_ids):
        u0, interior_mask = load_data(LOAD_DIR, bid)
        all_u0[i] = u0
        all_interior_mask[i] = interior_mask

    MAX_ITER = 5000
    ABS_TOL = 1e-4

    # Warm up Numba compile
    interior_mask_indices_example = np.array(np.nonzero(all_interior_mask[0])).T
    jacobi_numba(all_u0[0], interior_mask_indices_example, 1, ABS_TOL)

    # NumPy Jacobi
    start = time.time()
    all_u_numpy = np.empty_like(all_u0)
    for i, (u0, interior_mask) in enumerate(zip(all_u0, all_interior_mask)):
        u_numpy = jacobi(u0, interior_mask, MAX_ITER, ABS_TOL)
        all_u_numpy[i] = u_numpy
    print(f"NumPy Jacobi time: {time.time() - start:.4f} seconds")

    # Numba Jacobi
    start = time.time()
    all_u_numba = np.empty_like(all_u0)
    for i, (u0, interior_mask) in enumerate(zip(all_u0, all_interior_mask)):
        interior_mask_indices = np.array(np.nonzero(interior_mask)).T
        u_numba = jacobi_numba(u0, interior_mask_indices, MAX_ITER, ABS_TOL)
        all_u_numba[i] = u_numba
    print(f"Numba Jacobi time: {time.time() - start:.4f} seconds")

    # Max difference
    diff = np.abs(all_u_numpy - all_u_numba).max()
    print(f"Difference between implementations: {diff:.6f}")
