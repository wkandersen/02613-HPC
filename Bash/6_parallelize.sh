#!/bin/bash

#BSUB -J 6_parallelize
#BSUB -q hpc
#BSUB -W 60
#BSUB -R "rusage[mem=5G]" 
#BSUB -R "select[model == XeonGold6126]"
#BSUB -R "span[hosts=1]"
#BSUB -n 16
#BSUB -o 6_parallelize_%J.out
#BSUB -e 6_parallelize_%J.err

source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613

time python py_filer/6_parallelize.py 25 1
time python py_filer/6_parallelize.py 25 2
time python py_filer/6_parallelize.py 25 3
time python py_filer/6_parallelize.py 25 4
time python py_filer/6_parallelize.py 25 5
time python py_filer/6_parallelize.py 25 6
time python py_filer/6_parallelize.py 25 7
time python py_filer/6_parallelize.py 25 8
time python py_filer/6_parallelize.py 25 9
time python py_filer/6_parallelize.py 25 10
time python py_filer/6_parallelize.py 25 11
time python py_filer/6_parallelize.py 25 12
time python py_filer/6_parallelize.py 25 13
time python py_filer/6_parallelize.py 25 14
time python py_filer/6_parallelize.py 25 15
time python py_filer/6_parallelize.py 25 16