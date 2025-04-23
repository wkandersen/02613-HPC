#!/bin/bash

#BSUB -J parallelize_time
#BSUB -q hpc
#BSUB -W 5
#BSUB -R "rusage[mem=2G]" 
#BSUB -R "select[model == XeonGold6126]"
#BSUB -R "span[hosts=1]"
#BSUB -n 1
#BSUB -o parallelize_time_%J.out
#BSUB -e parallelize_time_%J.err

source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613

python 02613-HPC/py_filer/5_parallelize