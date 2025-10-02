# InDel Marker Design Using Transcriptome Data (Phalaenopsis-type *Dendrobium*)

A reproducible pipeline to design and validate PCR-based InDel markers from transcriptome-derived contigs (unigene set) in highly heterozygous *Dendrobium* (Phalaenopsis type). The workflow filters candidate InDels by allele types and size difference, extracts flanking sequences, designs multiple primer pairs per locus, and performs genome-wide specificity checks with BLAST before finalizing one primer pair per InDel.

> **Why this pipeline?** Phalaenopsis-type *Dendrobium* loci can present 1–4 alleles. For robust genotyping and clear gel separation, we (i) retained only 2 alternative allele types per locus and (ii) required a 15–28 bp indel size difference between REF and ALT, discarding all other sites.

---

## Repository Structure

```
.
├── scripts/
│   ├── step1.extract_indel.py
│   ├── step2.150bp.py
│   ├── step3.primerdesign.py
│   ├── step4.extract-primer.py
│   ├── step5.blast_compare.py
│   └── step6.final.py
├── data/                  # (optional) small test data or samples
├── results/               # outputs will be written here (see below)
├── README.md
├── requirements.txt
├── .gitignore
└── LICENSE
```

> If your lab policy disallows uploading large data (e.g., `unigene.fasta` or full BLAST DB), keep them locally and document paths in a config file. You can add sample/demo data under `data/` to show usage.

---

## Installation

### 1) Python environment
```bash
# (Option A) with venv
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2) BLAST+ (required for step 5)
Install NCBI BLAST+ binaries (e.g., `makeblastdb`, `blastn`) following the official docs. Ensure the executables are on your PATH:
```bash
makeblastdb -version
blastn -version
```

---

## Input Files

- `indelposition.txt`: tab/space-delimited. First column = unigene ID; second column = 0-based position of the InDel within the unigene sequence.
- `unigene.fasta`: FASTA of unigene/contig sequences.
- `unigene_query.txt`: BLAST tabular output (custom columns; see step 5).

> **Indel criteria used here**
> - Keep only loci with exactly 2 ALT allele types (down-selected from 1–4 observed).
> - Size difference REF vs ALT between **15–29 bp**.

---

## Workflow

### Step 1 — Extract unigene sequences for target InDel IDs
Reads IDs from `indelposition.txt` and pulls matching FASTA entries from `unigene.fasta`, writing `results/extracted_sequences.fasta`.  (Script: `scripts/step1.extract_indel.py`)

**Run**
```bash
python scripts/step1.extract_indel.py
```

**I/O**
- **In**: `indelposition.txt`, `unigene.fasta`
- **Out**: `results/extracted_sequences.fasta`

---

### Step 2 — Get 300 bp windows centered on InDel (±150 bp)
For each target, extracts the 300 bp window around the InDel site to avoid primers skipping the site. Writes `results/final_sequences_300bp.fasta`. (Script: `scripts/step2.150bp.py`)

**Run**
```bash
python scripts/step2.150bp.py
```

**I/O**
- **In**: `indelposition.txt`, `results/extracted_sequences.fasta`
- **Out**: `results/final_sequences_300bp.fasta`

---

### Step 3 — Primer design (Primer3)
Designs up to 5 primer pairs per target with: length 20–24 bp, Tm 56–60 °C, product size 260–280 bp. Exports a combined CSV. (Script: `scripts/step3.primerdesign.py`)

**Run**
```bash
python scripts/step3.primerdesign.py
```

**Key parameters**
- `PRIMER_NUM_RETURN = 5`
- `PRIMER_OPT_SIZE = 22` (min 20, max 24)
- `PRIMER_OPT_TM = 58` °C (min 56, max 60)
- `PRIMER_PRODUCT_SIZE_RANGE = 260–280 bp`

**I/O**
- **In**: `results/final_sequences_300bp.fasta`
- **Out**: `results/combined_primer_results_with_names.csv`

---

### Step 4 — Export primers to FASTA for BLAST
Converts the designed primer pairs to FASTA (`results/primers.fasta`) for downstream BLAST specificity checks. (Script: `scripts/step4.extract-primer.py`)

**Run**
```bash
python scripts/step4.extract-primer.py
```

**I/O**
- **In**: `results/combined_primer_results_with_names.csv`
- **Out**: `results/primers.fasta`

---

### Step 5 — Specificity filtering with BLAST
1) Prepare a local BLAST DB using draft genome (Sherpa *et al.*, 2022).  
2) `blastn` primers against the DB (recommend task `blastn-short` with stringent e-value).  
3) Parse results and enforce uniqueness rule: discard primers with non-unique significant hits; keep the first primer pair with unique forward+reverse hits per locus. (Script: `scripts/step5.blast_compare.py`)

**Example**
```bash
# make database (once)
makeblastdb -in Dendrobium_draft_genome.fa -dbtype nucl -out db/dendrobium

# run blast
blastn -task blastn-short -query results/primers.fasta -db db/dendrobium \
  -out results/unigene_query.txt -evalue 1e-2 -outfmt "6 qseqid sseqid pident length mismatch gapopen qstart qend sstart send evalue bitscore"

# filter/parse (keeps the first unique primer pair with forward+reverse)
python scripts/step5.blast_compare.py
```

**I/O**
- **In**: `results/unigene_query.txt`
- **Out**: `results/filtered_blast_results.txt`

---

### Step 6 — Finalize primer table
Merge the passing primer IDs back to the full design table and produce `results/filtered_combined_primer_results.csv` as the final deliverable. (Script: `scripts/step6.final.py`)

**Run**
```bash
python scripts/step6.final.py
```

**I/O**
- **In**: `results/filtered_blast_results.txt`, `results/combined_primer_results_with_names.csv`
- **Out**: `results/filtered_combined_primer_results.csv`

---

## Reproducible Run (all steps)

Assuming your inputs are in `./` and you want outputs under `results/`:
```bash
mkdir -p results db

python scripts/step1.extract_indel.py
python scripts/step2.150bp.py
python scripts/step3.primerdesign.py
python scripts/step4.extract-primer.py

# makeblastdb & blastn (see Step 5)
makeblastdb -in Dendrobium_draft_genome.fa -dbtype nucl -out db/dendrobium
blastn -task blastn-short -query results/primers.fasta -db db/dendrobium \
  -out results/unigene_query.txt -evalue 1e-2 -outfmt "6 qseqid sseqid pident length mismatch gapopen qstart qend sstart send evalue bitscore"

python scripts/step5.blast_compare.py
python scripts/step6.final.py
```

---

## Notes & Tips

- **Positions** in `indelposition.txt` should match the coordinate system of `unigene.fasta`. Step 2 uses ±150 bp; adjust if your amplicon needs change.
- **Primer3** parameters are encoded in the script; modify if your thermodynamics or product size constraints differ.
- **BLAST thresholds**: We used e-value < 0.01 as the uniqueness cut-off and required both forward and reverse to be uniquely matched for a given target before accepting a pair.
- **Heterozygosity**: Down-selection to 2 ALT allele types simplifies downstream scoring on standard agarose gels.

---

## Citation

If you use this pipeline, please cite:
## 
## This repository: **InDel-Marker-Design-Using-Transcriptome-Data** (GitHub).

---

## 中文说明（简要）

本流程面向高度杂合的蝴蝶兰型石斛：每个位点可能有 1–4 个等位。为便于分析，我们仅保留 **2 种 ALT 等位**，并要求 REF/ALT 片段长度差 **15–29 bp**。随后：
1) 从 `unigene.fasta` 提取对应序列；
2) 截取 InDel 位点上下游各 150 bp（总 300 bp）；
3) 用 Primer3 设计每个位点最多 5 对引物（长度 20–24 bp，Tm 56–60 °C，产物 260–280 bp）；
4) 导出引物 FASTA；
5) 在草图基因组上做 BLAST，按唯一性规则筛选；
6) 输出最终引物表。

详见上文步骤与运行示例。

---

## License

This project is licensed under the MIT License (see `LICENSE`).

