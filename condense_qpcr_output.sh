#!/bin/bash

# exit on error
set -e

# qPCR output data processing pipeline
# this script condenses & cleans tables generated in the "qpcr_pipeline.sh" script

# ----------------------
# 1. Directory Settings (line 10)
# ----------------------

CONDENSED_DIR="cleaned_qpcr_output"
mkdir -p "$CONDENSED_DIR"

# ------------------------
# 1. Loop & .py Functions
# ------------------------

# loop through each gene folder in qpcr_outputs (line 20)
for gene_folder in qpcr_outputs/*_processed_data; do
    gene=$(basename "$gene_folder" | sed 's/_processed_data//')
    echo "Processing gene: $gene"

    # find all unique dates from folder names (e.g., nosZI_run4_18Feb25)
    dates=$(find "$gene_folder" -type d -name "${gene}_run*" | sed -E "s/.*_([0-9]{1,2}[A-Za-z]+[0-9]{2})$/\1/" | sort | uniq) 
    echo "found date for: $gene"

    for date in $dates; do
        calc_tables=()
        while IFS= read -r file; do
            calc_tables+=("$file")
        done < <(find "$gene_folder" -type d -name "*_${date}" -exec find {} -type f -name "*_calc_table.csv" \; | sort)

        echo "===== Files found for $gene on $date ==============================================="
        if [ ${#calc_tables[@]} -eq 0 ]; then
            echo "No files found"
            continue
        else
            for f in "${calc_tables[@]}"; do
                echo "  $f"
            done
        fi
        echo "====="

        # output file name
        out_csv="${CONDENSED_DIR}/${gene}_${date}.csv"
        echo "output_csvs successfully made"

        # call Python script
        python clean_qpcr_output.py "$gene" "$date" "$out_csv" "${calc_tables[@]}"
        echo "Condensed file for $gene $date: $out_csv"
	echo "===================================================================================="
    done
done
