---
editor_options: 
  markdown: 
    wrap: 72
---

# qPCR_pipeline

This github repo contains the following:

1.  complete python function & pipeline

2.  raw data files in correct directory structure (currently contains all data for 8 & 16 HRT samples [genes: nirS, nirK, nosZI, nosZII, 16S])

3.  intermediate output files (if enough storage)

4.  final cleaned qpcr data files (ready for visualization in other software)

------------------------------------------------------------------------

## python & shell script descriptions

1.  `qpcr_pipeline` = shell script that converts raw BioRad Cq files (w/
    separate sample_df files) to various qpcr measurements

-   output: standard curve for each plate, linear regression stats for
    each plate, table with qpcr measurements for each plate

-   output format: created stacked directories ("qpcr_outputs" -\>
    "{gene}\_processed_data" -\> "{gene}\_{run}\_{date}" -\> "3 output
    files")

2.  `process_qpcr_data.py` = python script embedded in `qpcr_pipeline`
    that contains functions to complete tasks

3.  `condense_qpcr_output.sh` = shell script that condenses calculation
    tables for each plate into one csv file and extracts sample
    information to new columns

-   output: condensed csv file containing all calculations for each gene
    for each date

-   output format: created directory ("cleaned_qpcr_output"" -\>
    "{gene}\_{date}.csv")

4.  `clean_qpcr_output.py` = python script embedded in
    `condense_qpcr_output.sh` that merges individual calculation tables,
    extracts sample information from sample ID, and selects for
    important columns

------------------------------------------------------------------------
