import re
import matplotlib.pyplot as plt
import sys

file_path = sys.argv[1]

# Read and extract real times
with open(file_path, 'r') as f:
    content = f.read()

real_times = re.findall(r'real\s+(\d+)m([\d.]+)s', content)
real_seconds = [int(m) * 60 + float(s) for m, s in real_times]

# Calculate speed-ups as a dictionary
speed_up = {i+1: real_seconds[0] / real_seconds[i] for i in range(1, len(real_seconds))}

# Plot
plt.figure(figsize=(8, 5))
plt.plot(list(speed_up.keys()), list(speed_up.values()), marker='o', linestyle='-')
plt.title('Speed-up Relative to First Run')
plt.xlabel('Run Index')
plt.ylabel('Number of Processes')
plt.grid(True)
plt.tight_layout()
plt.savefig(f'Speed-ups{sys.argv[1]}.png')

# real_seconds[0] is the baseline sequential time
baseline = real_seconds[0]

parallel_fractions = {}

with open(f'calc_{sys.argv[1]}.txt', 'w') as t:
    for i, current_time in enumerate(real_seconds):
        p = i + 1
        s = baseline / current_time if i != 0 else 1

        if p == 1:
            f = 0.0
        else:
            f = (p * (s - 1)) / (s * (p - 1)) # using amd
            f = round(f, 1)

        parallel_fractions[p] = f
        
    
        t.write(f'p = {p}\n')
        t.write(f'Parallel fraction: {f:.1f}\n')
        t.write(f'Theoretical maximum speed up: {1/(1-f)}\n')
        t.write(f'Calculated speed up: {s:.1f}\n')