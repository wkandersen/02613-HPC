from os.path import join
import sys
import cupy as cp
import pandas as pd
import matplotlib.pyplot as plt

def load_data(load_dir, bid):
    SIZE = 512
    u = cp.zeros((SIZE + 2, SIZE + 2))
    u[1:-1, 1:-1] = cp.load(join(load_dir, f"{bid}_domain.npy"))
    interior_mask = cp.load(join(load_dir, f"{bid}_interior.npy"))
    return u, interior_mask

def jacobi(u, interior_mask, max_iter, atol=1e-6):
    u = cp.copy(u)
    for i in range(max_iter):
        u_new = 0.25 * (u[1:-1, :-2] + u[1:-1, 2:] + u[:-2, 1:-1] + u[2:, 1:-1])
        u_new_interior = u_new[interior_mask]
        delta = cp.abs(u[1:-1, 1:-1][interior_mask] - u_new_interior).max()
        u[1:-1, 1:-1][interior_mask] = u_new_interior
        if delta < atol:
            break
    return u

def summary_stats(u, interior_mask):
    u_interior = u[1:-1, 1:-1][interior_mask]
    mean_temp = float(u_interior.mean())
    std_temp = float(u_interior.std())
    pct_above_18 = float(cp.sum(u_interior > 18) / u_interior.size * 100)
    pct_below_15 = float(cp.sum(u_interior < 15) / u_interior.size * 100)
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

    # Load and simulate
    MAX_ITER = 20_000
    ABS_TOL = 1e-4
    results = []

    for bid in building_ids:
        u0, interior_mask = load_data(LOAD_DIR, bid)
        u = jacobi(u0, interior_mask, MAX_ITER, ABS_TOL)
        stats = summary_stats(u, interior_mask)
        stats['building_id'] = bid
        results.append(stats)

    # Convert to DataFrame
    df = pd.DataFrame(results)
    df = df[['building_id', 'mean_temp', 'std_temp', 'pct_above_18', 'pct_below_15']]

    avg_mean_temp = df['mean_temp'].mean()
    avg_std_temp = df['std_temp'].mean()
    count_above_18 = (df['pct_above_18'] >= 50).sum()
    count_below_15 = (df['pct_below_15'] >= 50).sum()

    # Histogram of mean temperatures
    plt.hist(df['mean_temp'], bins=20, edgecolor='black')
    plt.title('Distribution of Mean Temperatures')
    plt.xlabel('Mean Temperature (°C)')
    plt.ylabel('Number of Buildings')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('mean_temp_histogram.png')
    plt.close()


    # Save summary
    summary_df = pd.DataFrame([{
        'avg_mean_temp': avg_mean_temp,
        'avg_std_temp': avg_std_temp,
        'count_above_18': count_above_18,
        'count_below_15': count_below_15
    }])
    summary_df.to_csv('analysis_summary.csv', index=False)
