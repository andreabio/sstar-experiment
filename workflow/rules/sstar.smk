# workflow/rules/sstar.smk

import os
import numpy as np
import pandas as pd


rule sstar_score:
    input:
        # IMPORTANT: use RAW VCF from simulation (no biallelic filtering)
        vcf=rules.run_msprime_simulation.output.vcf,
        ref_list=rules.run_msprime_simulation.output.ref_list,
        tgt_list=rules.run_msprime_simulation.output.tgt_list,
    output:
        score="results/sstar/rep_{rep}/sstar.phased.rep_{rep}.scores.tsv",
    params:
        win_len=50000,
        win_step=10000,
    threads: 4
    resources:
        mem_gb=16,
    conda:
        "../envs/sstar.yaml",
    log:
        "logs/sstar/rep_{rep}/sstar_score.log",
    shell:
        r"""
        set -euo pipefail
        mkdir -p $(dirname {output.score}) $(dirname {log})

        sstar score \
          --vcf {input.vcf} \
          --ref {input.ref_list} \
          --tgt {input.tgt_list} \
          --output {output.score} \
          --thread {threads} \
          --win-len {params.win_len} \
          --win-step {params.win_step} \
          --phased \
          &> {log}
        """


rule sstar_quantile:
    input:
        score=rules.sstar_score.output.score,
    output:
        quantile="results/sstar/rep_{rep}/sstar.phased.rep_{rep}.quantile.tsv",
    params:
        quantiles=np.arange(0.5, 1, 0.005),
    threads: 1
    resources:
        mem_gb=4,
    run:
        df = pd.read_csv(input.score, sep="\t").dropna()
        mean_df = (
            df.groupby(["chrom", "start", "end"], as_index=False)["S*_score"]
              .mean()
              .dropna()
        )
        scores = np.quantile(mean_df["S*_score"].to_numpy(), params.quantiles)

        os.makedirs(os.path.dirname(output.quantile), exist_ok=True)
        with open(output.quantile, "w") as o:
            o.write("S*_score\tquantile\n")
            for val, q in zip(scores, params.quantiles):
                o.write(f"{val}\t{q}\n")
