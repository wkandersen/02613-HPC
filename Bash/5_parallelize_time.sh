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

export PYTHONPATH=$PYTHONPATH:$(pwd)/py_filer

source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613

python py_filer/5_calculations.py "5_parallelize_24764762.err"
# python py_filer/5_calculations.py "6_parallelize_24763394.err"