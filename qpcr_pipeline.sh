#!/bin/bash

# exit on error
set -e

# qPCR data processing pipeline
# this script processes BioRad qPCR data files based on the directory structure (qpcr_raw_data/<gene_folders>/<generated biorad files>)

# ----------------------
# 1. Directory Settings
# ----------------------

RAW_DATA_DIR=${1:-"qpcr_raw_data"} # either include folder path, or cd into folder with "qpcr_raw_data"
OUTPUT_DIR="qpcr_outputs"

# make output directory
mkdir -p "$OUTPUT_DIR"

echo "[STEP 1 COMPLETE] starting qPCR data processing pipeline..."

# ----------------------
# 2. qPCR Pipeline
# ----------------------

# process each gene folder (i.e. "nirS raw data", "nosZII raw data", etc.) ---------------------
for gene_dir in "$RAW_DATA_DIR"/*"raw data"; do
	
	# extract gene name from directory ---------------------
	gene=$(basename "$gene_dir" | sed 's/ raw data//g')
	echo "[STARTING PIPELINE] processing gene: $gene"

	# create output directory for gene ---------------------
	gene_output_dir="$OUTPUT_DIR/${gene}_processed_data"
	mkdir -p "$gene_output_dir"

	# process each run folder for gene ---------------------
	for run_dir in "$gene_dir"/Column_"${gene}"_run*; do
        if [ -d "$run_dir" ]; then
            dir_name=$(basename "$run_dir")
            
        	# extract run number and date ---------------------
		if [[ $dir_name =~ Column_${gene}_run([0-9]+)_([0-9]+[A-Za-z]+[0-9]+) ]]; then
                run_num="${BASH_REMATCH[1]}"
                run_date="${BASH_REMATCH[2]}"
                file_prefix="${gene}_run${run_num}"
		plate="$run_num"
                
                echo "[EXTRACTION SUCCESSFUL] processing $file_prefix (date: $run_date)"
		
		# find matching sample data file for run date ---------------------
		sample_file=$(find "$gene_dir" -name "${gene}_${run_date}_sample_df.csv")
		
		if [ -z "$sample_file" ]; then
                    echo "WARNING: No sample data file found for $run_date, skipping run"
                    continue
                fi

		# find qPCR Cq results file in run directory ---------------------
		qpcr_file=$(find "$run_dir" -name "*Quantification Cq Results_0.csv" | head -n 1)
                
                if [ -z "$qpcr_file" ]; then
                    echo "WARNING: No qPCR results file found in $run_dir, skipping run"
                    continue
                fi

		run_output_dir="$gene_output_dir/${file_prefix}_${run_date}"
                mkdir -p "$run_output_dir"

		# running python script ---------------------
		echo "[STARTING PY SCRIPT]"
		python process_qpcr_data.py "$qpcr_file" "$sample_file" "$plate" "$run_output_dir"

		if [ $? -eq 0 ]; then
                    echo "✓ Successfully processed $file_prefix"
                else
                    echo "✗ Error processing $file_prefix"
                fi
            else
                echo "Warning: Could not extract run information from: $dir_name"
            fi
        fi
    done
done

echo "[COMPLETE!!!] qPCR processing complete; results stored in $OUTPUT_DIR"





