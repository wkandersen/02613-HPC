#!/bin/bash

#BSUB -J sim_vis
#BSUB -q hpc
#BSUB -W 5
#BSUB -R "rusage[mem=2G]" 
#BSUB -R "select[model == XeonGold6126]"
#BSUB -R "span[hosts=1]"
#BSUB -n 1
#BSUB -o sim_vis_%J.out
#BSUB -e sim_vis_%J.err

source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613

python sim_vis.py 10