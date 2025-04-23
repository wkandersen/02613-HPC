#!/bin/bash

#BSUB -J simulate_time
#BSUB -q c02613
#BSUB -W 5
#BSUB -R "rusage[mem=2G]" 
#BSUB -R "select[model == XeonGold6126]"
#BSUB -R "span[hosts=1]"
#BSUB -n 1
#BSUB -o Output/kernprof_%J.out
#BSUB -e Output/Kernprof_%J.err


export PYTHONPATH=$PYTHONPATH:$(pwd)/py_filer

source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613

kernprof -l py_filer/simulate.py