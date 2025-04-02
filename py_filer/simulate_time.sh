#!/bin/bash

#BSUB -J simulate_time
#BSUB -q hpc
#BSUB -W 5
#BSUB -R "rusage[mem=2G]" 
#BSUB -R "select[model == XeonGold6126]"
#BSUB -R "span[hosts=1]"
#BSUB -n 1
#BSUB -o simulate_time_%J.out
#BSUB -e simulate_time_%J.err

source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613

time python simulate.py 10