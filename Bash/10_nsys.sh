#!/bin/sh
#BSUB -q c02613
#BSUB -J gpujob
#BSUB -n 4
#BSUB -R "span[hosts=1]"
#BSUB -R "rusage[mem=1GB]"
#BSUB -gpu "num=1:mode=exclusive_process"
#BSUB -W 00:05
#BSUB -o 10_nsys_%J.out
#BSUB -e 10_nsys_%J.err
source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613

# Run the profiler
nsys profile -o 10_nsys python 02613-HPC/py_filer/9_cupy 10