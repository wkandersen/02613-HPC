#!/bin/sh
#BSUB -q c02613
#BSUB -J gpujob
#BSUB -n 4
#BSUB -R "span[hosts=1]"
#BSUB -R "rusage[mem=1GB]"
#BSUB -gpu "num=1:mode=exclusive_process"
#BSUB -W 00:30
#BSUB -o 10_cupy_fix_%J.out
#BSUB -e 10_cupy_fix_%J.err
source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613

time python py_filer/10_cupy_fix.py 10