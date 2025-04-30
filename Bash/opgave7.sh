#!/bin/bash

#BSUB -J numba6
#BSUB -q hpc
#BSUB -W 45
#BSUB -R "rusage[mem=2G]" 
#BSUB -R "select[model == XeonGold6126]"
#BSUB -R "span[hosts=1]"
#BSUB -n 1
#BSUB -o Output/numba7_%J.out
#BSUB -e Output/numba7_%J.err


export PYTHONPATH=$PYTHONPATH:$(pwd)/py_filer

source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613

python py_filer/simulate_numba.py 10