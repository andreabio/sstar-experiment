#!/bin/bash
#SBATCH --job-name=sstar-experiment
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --mem=16G
#SBATCH --time=24:00:00
#SBATCH --no-requeue

source ~/.bashrc
conda activate sstar-experiment

snakemake -s workflow/Snakefile \
  --cores 8 \
  --use-conda \
  --rerun-incomplete \
  --rerun-triggers mtime
