import numpy as np
import matplotlib.pyplot as plt
from os.path import join

# Modify this to your actual data directory
LOAD_DIR = '/dtu/projects/02613_2025/data/modified_swiss_dwellings/'

# Function to load data
def load_data(building_id):
    domain = np.load(join(LOAD_DIR, f"{building_id}_domain.npy"))
    interior = np.load(join(LOAD_DIR, f"{building_id}_interior.npy"))
    return domain, interior

# Function to visualize data
def visualize(building_id, name):
    domain, interior = load_data(building_id)
    
    fig, ax = plt.subplots(1, 2, figsize=(12, 6))
    
    ax[0].imshow(domain, cmap='coolwarm', origin='upper')
    ax[0].set_title(f'Initial Temperature Grid ({building_id})')
    
    ax[1].imshow(interior, cmap='gray', origin='upper')
    ax[1].set_title(f'Interior Mask ({building_id})')
    
    plt.show()
    plt.savefig(f'visualize{building_id}')

# Example usage
building_ids = ['1330', '1331', '1332']  
for bid in building_ids:
    visualize(bid, bid)