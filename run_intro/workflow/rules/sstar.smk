# workflow/rules/sstar.smk

rule sstar_score:
    input:
        vcf=rules.run_msprime_simulation.output.vcf,
        ref_list=rules.run_msprime_simulation.output.ref_list,
        tgt_list=rules.run_msprime_simulation.output.tgt_list,
    output:
        score="results/sstar/rep_{rep}/sstar.phased.rep_{rep}.scores.tsv",
    params:
        win_len=50000,
        win_step=50000,
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
