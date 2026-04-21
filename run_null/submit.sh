#!/bin/bash
#SBATCH --job-name=sstar-null
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=64G
#SBATCH --time=48:00:00
#SBATCH --no-requeue

source ~/.bashrc
conda activate sstar-experiment

cd /lisc/data/scratch/anthropology/SocialGenomics/CaptureBait/sstar-experiment/run_null

snakemake -s workflow/Snakefile \
  --cores 16 \
  --use-conda \
  --rerun-incomplete \
  --rerun-triggers mtime
