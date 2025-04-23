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
def jacobi_kernel(u, u_new, indices, N, M):
    idx = cuda.grid(1)

    if idx < len(indices):
        i, j = indices[idx]

        # Only update interior points (no boundary points)
        if 0 < i < N-1 and 0 < j < M-1:
            # Debug: print the indices and current values
            if i == 10 and j == 10:  # Just as an example for debugging at a specific point
                print(f"Thread {idx} updating point ({i}, {j})")

            # Print old values before update (can cause performance drop)
            if i == 10 and j == 10:  # Debug specific point (optional)
                print(f"Before update u[{i},{j}]: {u[i,j]}, u_new[{i},{j}]: {u_new[i,j]}")
            
            # Jacobi update rule
            u_new[i, j] = 0.25 * (u[i-1, j] + u[i+1, j] + u[i, j-1] + u[i, j+1])
            
            # Debug: print the new value after the update
            if i == 10 and j == 10:  # Debug specific point (optional)
                print(f"After update u_new[{i},{j}]: {u_new[i,j]}")

# Main function for executing the Jacobi solver on the GPU
def jacobi_cuda(u, indices, max_iter):
    N, M = u.shape
    # Create device arrays for u and u_new
    u_device = cuda.to_device(u.astype(np.float32))
    u_new_device = cuda.device_array_like(u_device)

    # Transfer indices to device
    indices_device = cuda.to_device(indices)

    # Define grid and block size
    threads_per_block = 256
    blocks_per_grid = (len(indices) + threads_per_block - 1) // threads_per_block

    # Debug: Print initial u values (before the first iteration)
    print("Initial u values:")
    print(u[:5, :5])  # Print a small section to avoid overwhelming output

    # Perform the Jacobi iterations
    for iter_num in range(max_iter):
        # Debug: Print iteration number
        print(f"Iteration {iter_num+1}:")

        # Launch kernel for one Jacobi iteration
        jacobi_kernel[blocks_per_grid, threads_per_block](u_device, u_new_device, indices_device, N, M)

        # Swap u and u_new for the next iteration
        u_device, u_new_device = u_new_device, u_device

        # Debug: Print u after kernel execution
        if iter_num % 100 == 0:  # Print every 100th iteration to reduce output
            u_host = u_device.copy_to_host()
            print(f"u after iteration {iter_num+1} (first 5x5 block):")
            print(u_host[:5, :5])  # Print a small section to avoid overwhelming output

    # Return the result after all iterations
    return u_device.copy_to_host()


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
        # Generate indices for interior points
        indices = np.array(np.nonzero(all_interior_mask[i])).T  # (num_interior, 2)

        # Debug: Print out the first few indices
        print(f"Interior points for building {i+1}:")
        print(indices[:5])  # Print first 5 indices for debugging

        u_cuda = jacobi_cuda(all_u0[i], indices, MAX_ITER)
        all_u_cuda[i] = u_cuda
    print(f"CUDA Jacobi time: {time.time() - start:.4f} seconds")

    # Difference check
    diff = np.abs(all_u_numpy - all_u_cuda).max()
    print(f"Max difference between NumPy and CUDA: {diff:.6f}")