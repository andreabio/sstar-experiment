#!/bin/bash
#SBATCH --job-name=sstar-qr-analysis
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --mem=16gb
#SBATCH --time=24:00:000
#SBATCH --no-requeue


snakemake -c 1 --profile config/slurm --rerun-incomplete --rerun-triggers mtime
