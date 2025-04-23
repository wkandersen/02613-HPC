#!/bin/sh
#BSUB -q gpua10
#BSUB -J gpujob
#BSUB -n 4
#BSUB -R "span[hosts=1]"
#BSUB -R "rusage[mem=4GB]"
#BSUB -gpu "num=1:mode=exclusive_process"
#BSUB -W 6:00
#BSUB -o 12_cupy_%J.out
#BSUB -e 12_cupy_%J.err
source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613

python py_filer/12_all.py 4571