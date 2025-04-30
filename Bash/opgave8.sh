#!/bin/bash

#BSUB -J numbacuda
#BSUB -q c02613
#BSUB -W 00:10
#BSUB -n 4
#BSUB -R "rusage[mem=1G]" 
#BSUB -R "span[hosts=1]"
#BSUB -gpu "num=1:mode=exclusive_process"
#BSUB -n 1
#BSUB -o Output/cuda7_%J.out
#BSUB -e Output/cuda7_%J.err


export PYTHONPATH=$PYTHONPATH:$(pwd)/py_filer

source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613

python py_filer/simulate_numba_cuda.py 10