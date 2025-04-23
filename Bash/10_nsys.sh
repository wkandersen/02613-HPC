#!/bin/sh
#BSUB -q gpua10 
#BSUB -J gpujob
#BSUB -n 4
#BSUB -R "span[hosts=1]"
#BSUB -R "rusage[mem=1GB]"
#BSUB -gpu "num=1:mode=exclusive_process"
#BSUB -W 00:30
#BSUB -o 10_nsys_%J.out
#BSUB -e 10_nsys_%J.err
source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613

nsys profile -o 10_nsys python py_filer/9_cupy.py 10
nsys stats 10_nsys.nsys-rep