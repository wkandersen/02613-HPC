from os.path import join
import sys
import time
import numpy as np
from numba import cuda

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


@cuda.jit
def jacobi_kernel(u, u_new, interior_mask, N, M):
    i, j = cuda.grid(2)

    if 1 <= i < N-1 and 1 <= j < M-1:
        if interior_mask[i-1, j-1]:
            u_new[i, j] = 0.25 * (u[i, j-1] + u[i, j+1] + u[i-1, j] + u[i+1, j])
        else:
            u_new[i, j] = u[i, j]  # copy unchanged values

def jacobi_cuda(u, interior_mask, max_iter):
    N, M = u.shape
    interior_N, interior_M = N-2, M-2

    u_d = cuda.to_device(u)
    u_new_d = cuda.device_array_like(u_d)
    mask_d = cuda.to_device(interior_mask)

    threadsperblock = (16, 16)
    blockspergrid_x = (interior_N + threadsperblock[0] - 1) // threadsperblock[0]
    blockspergrid_y = (interior_M + threadsperblock[1] - 1) // threadsperblock[1]
    blockspergrid = (blockspergrid_x, blockspergrid_y)

    for _ in range(max_iter):
        jacobi_kernel[blockspergrid, threadsperblock](u_d, u_new_d, mask_d, interior_N, interior_M)
        u_d, u_new_d = u_new_d, u_d

    result = u_d.copy_to_host()
    return result

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
    LOAD_DIR = '/dtu/projects/02613_2025/data/modified_swiss_dwellings/'
    with open(join(LOAD_DIR, 'building_ids.txt'), 'r') as f:
        building_ids = f.read().splitlines()

    N = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    building_ids = building_ids[:N]

    all_u0 = np.empty((N, 514, 514))
    all_interior_mask = np.empty((N, 512, 512), dtype=bool)
    for i, bid in enumerate(building_ids):
        u0, mask = load_data(LOAD_DIR, bid)
        all_u0[i] = u0
        all_interior_mask[i] = mask

    MAX_ITER = 5000
    ABS_TOL = 1e-4

    # NumPy Jacobi timing
    start = time.time()
    all_u_numpy = np.empty_like(all_u0)
    for i in range(N):
        all_u_numpy[i] = jacobi(all_u0[i], all_interior_mask[i], MAX_ITER, ABS_TOL)
    print(f"NumPy Jacobi time: {time.time() - start:.4f} seconds")

    # CUDA Jacobi timing with debugging
    start = time.time()
    all_u_cuda = np.empty_like(all_u0)
    for i in range(N):
        u_cuda = jacobi_cuda(all_u0[i], all_interior_mask[i], MAX_ITER)
        all_u_cuda[i] = u_cuda
    print(f"CUDA Jacobi time: {time.time() - start:.4f} seconds")