#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import sys
import pandas as pd
import numpy as np
import re
from pathlib import Path

def extract_fields(sample_id):
    # handle missing or non-string sample IDs
    if pd.isna(sample_id):
        return "", "media", np.nan, ""
    sample_id = str(sample_id)
    
    # C_material
    if sample_id.startswith("WC"):
        c_material = "woodchip"
    elif sample_id.startswith("CC"):
        c_material = "corncob"
    elif sample_id.startswith("INF"):
        c_material = "influent"
    else:
        c_material = ""
        
    # Sample_source
    if sample_id.startswith("INF"):
        sample_source = "water"
    elif sample_id.endswith("W"):
        sample_source = "water"
    else:
        sample_source = "media"
        
    # Week
    # extract last number group before optional 'W'
    m = re.search(r'(\d+)(W)?$', sample_id)
    week = int(m.group(1)) if m else np.nan
    
    # HRT
    if not pd.isna(week):
        hrt = 8 if week <= 20 else 16
    else:
        hrt = ""

    
    return c_material, sample_source, week, hrt

def main():
    gene = sys.argv[1]
    date = sys.argv[2]
    out_csv = sys.argv[3]
    calc_tables = sys.argv[4:]

    dfs = []
    for f in calc_tables:
        df = pd.read_csv(f)
        # Select only desired columns
        sel = df[["SampleID", "Plate", "Date", "avg_copies_per_g_sample", "avg_std"]].copy()
        # Derive new columns
        sel[["C_material", "Sample_source", "Week", "HRT"]] = sel["SampleID"].apply(
            lambda x: pd.Series(extract_fields(str(x)))
        )
        sel["Gene"] = gene
        dfs.append(sel)

    if dfs:
        result = pd.concat(dfs, ignore_index=True)
        result.to_csv(out_csv, index=False)
    else:
        print("No data found.")

if __name__ == "__main__":
    main()

