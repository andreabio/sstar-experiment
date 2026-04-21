#!/bin/bash
#SBATCH --job-name=sstar-experiment
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --mem=16G
#SBATCH --time=24:00:00
#SBATCH --no-requeue

snakemake -c 1 --profile config/slurm --rerun-incomplete --rerun-triggers mtime
