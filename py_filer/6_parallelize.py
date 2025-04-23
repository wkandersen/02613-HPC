from os.path import join
import sys
import numpy as np
from multiprocessing import Pool, cpu_count

def load_data(load_dir, bid):
    SIZE = 512
    u = np.zeros((SIZE + 2, SIZE + 2))
    u[1:-1, 1:-1] = np.load(join(load_dir, f"{bid}_domain.npy"))
    interior_mask = np.load(join(load_dir, f"{bid}_interior.npy"))
    return u, interior_mask

def jacobi(u, interior_mask, max_iter, atol=1e-6):
    u = np.copy(u)
    for i in range(max_iter):
        u_new = 0.25 * (u[1:-1, :-2] + u[1:-1, 2:] + u[:-2, 1:-1] + u[2:, 1:-1])
        u_new_interior = u_new[interior_mask]
        delta = np.abs(u[1:-1, 1:-1][interior_mask] - u_new_interior).max()
        u[1:-1, 1:-1][interior_mask] = u_new_interior
        if delta < atol:
            break
    return u

def summary_stats(u, interior_mask):
    u_interior = u[1:-1, 1:-1][interior_mask]
    return {
        'mean_temp': u_interior.mean(),
        'std_temp': u_interior.std(),
        'pct_above_18': np.sum(u_interior > 18) / u_interior.size * 100,
        'pct_below_15': np.sum(u_interior < 15) / u_interior.size * 100
    }

def process_one_floorplan(args):
    u0, interior_mask, bid = args
    u = jacobi(u0, interior_mask, MAX_ITER, ABS_TOL)
    stats = summary_stats(u, interior_mask)
    return bid, stats


if __name__ == '__main__':
    LOAD_DIR = '/dtu/projects/02613_2025/data/modified_swiss_dwellings/'

    # Read building IDs
    with open(join(LOAD_DIR, 'building_ids.txt'), 'r') as f:
        building_ids = f.read().splitlines()

    # Limit number of buildings (e.g., for assignment)
    if len(sys.argv) >= 2:
        N = int(sys.argv[1])
    else:
        N = 10  # default fallback

    building_ids = building_ids[:N]

    # Load data for all floorplans
    all_u0 = []
    all_interior_mask = []
    for bid in building_ids:
        u0, mask = load_data(LOAD_DIR, bid)
        all_u0.append(u0)
        all_interior_mask.append(mask)

    # Set solver parameters
    MAX_ITER = 20000
    ABS_TOL = 1e-4

    # Prepare input tuples for multiprocessing
    input_data = [(u0, mask, bid) for u0, mask, bid in zip(all_u0, all_interior_mask, building_ids)]

    # Run dynamic parallel processing
    with Pool(processes=cpu_count()) as pool:
        results = pool.imap_unordered(process_one_floorplan, input_data)

        # Output CSV results
        print("building_id, mean_temp, std_temp, pct_above_18, pct_below_15")
        for bid, stats in results:
            print(f"{bid}, {stats['mean_temp']}, {stats['std_temp']}, "
                  f"{stats['pct_above_18']}, {stats['pct_below_15']}")
