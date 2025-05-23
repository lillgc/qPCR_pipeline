#!/usr/bin/env python
# coding: utf-8

# In[2]:


#!/usr/bin/env python3

import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error

def qpcr_measurements(cq_path, sample_path, plate):
    cq_data = pd.read_csv(cq_path)
    cq_data = cq_data.iloc[:, [1, 4] + list(range(7, 14))]
    sample_data = pd.read_csv(sample_path)
    sample_plate = sample_data[sample_data["Plate"] == plate]
    full_data = pd.merge(cq_data, sample_plate, on=["Well", "Content"], how="inner")
    full_data = full_data.dropna(subset=["Cq"])
    std_data = cq_data[cq_data.iloc[:, 1].astype(str).str.contains("Std", na=False)].dropna(subset=["Cq"])
    x = np.array(std_data[["Log Starting Quantity"]])
    y = np.array(std_data[["Cq"]])
    model = LinearRegression()
    model.fit(x, y)
    y_pred = model.predict(x)
    slope = model.coef_[0][0]
    intercept = model.intercept_[0]
    r2 = model.score(x, y)
    efficiency = ((10**(-1/slope))-1)*100
    mse = mean_squared_error(y, y_pred)
    rmse = np.sqrt(mse)
    return {
        "slope": slope,
        "intercept": intercept,
        "r2": r2,
        "efficiency": efficiency,
        "mse": mse,
        "rmse": rmse
    }

def save_qpcr_std_curve(cq_path, sample_path, plate, output_dir):
    cq_data = pd.read_csv(cq_path)
    cq_data = cq_data.iloc[:, [1, 4] + list(range(7, 14))]
    std_data = cq_data[cq_data.iloc[:, 1].astype(str).str.contains("Std", na=False)].dropna(subset=["Cq"])
    x = np.array(std_data[["Log Starting Quantity"]])
    y = np.array(std_data[["Cq"]])
    model = LinearRegression()
    model.fit(x, y)
    y_pred = model.predict(x)
    slope = model.coef_[0][0]
    intercept = model.intercept_[0]
    r2 = model.score(x, y)
    plt.figure(figsize=(8, 6))
    plt.scatter(x, y, color="blue")
    plt.plot(x, y_pred, color="blue", label=f'Fit: y = {slope:.3f}x + {intercept:.3f}, R² = {r2:.3f}')
    plt.xlabel("Concentration (Log Starting Quantity)")
    plt.ylabel("Cq Value")
    plt.title(f"Standard Curve for {plate}")
    plt.legend()
    output_path = os.path.join(output_dir, f"{plate}_std_curve.png")
    plt.savefig(output_path)
    plt.close()
    return output_path

def qpcr_calc_table(cq_path, sample_path, plate, output_dir):
    cq_data = pd.read_csv(cq_path)
    cq_data = cq_data.iloc[:, [1, 4] + list(range(7, 14))]
    sample_data = pd.read_csv(sample_path)
    sample_plate = sample_data[sample_data["Plate"].astype(str) == str(plate)]
    full_data = pd.merge(cq_data, sample_plate, on=["Well", "Content"], how="inner")
    full_data = full_data.dropna(subset=["Cq"])
    std_data = cq_data[cq_data.iloc[:, 1].astype(str).str.contains("Std", na=False)].dropna(subset=["Cq"])
    x = np.array(std_data[["Log Starting Quantity"]])
    y = np.array(std_data[["Cq"]])
    model = LinearRegression()
    model.fit(x, y)
    y_pred = model.predict(x)
    slope = model.coef_[0][0]
    intercept = model.intercept_[0]
    r2 = model.score(x, y)
    unkn_data = full_data[full_data.iloc[:, 1].astype(str).str.contains("Unkn", na=False)]
    unkn_data["calc_qty"] = 10**((unkn_data["Cq"] - intercept) / slope)
    unkn_data["per_ul_dna"] = (unkn_data["calc_qty"] / unkn_data["Dilution"]) / 2
    unkn_data["copies_in_dna"] = unkn_data["per_ul_dna"] * unkn_data["ul_dna_eluted"]
    unkn_data["copies_per_g_sample"] = unkn_data["copies_in_dna"] / unkn_data["mL_sample"]
    unkn_data["avg_copies_per_g_sample"] = unkn_data.groupby("Content")["copies_per_g_sample"].transform("mean")
    unkn_data["avg_std"] = unkn_data.groupby("Content")["copies_per_g_sample"].transform("std")
    output_path = os.path.join(output_dir, f"{plate}_calc_table.csv")
    unkn_data.to_csv(output_path, index=False)
    return output_path

def main():
    if len(sys.argv) != 5:
        print("Usage: process_qpcr_data.py <qpcr_file> <sample_data> <plate> <output_dir>")
        sys.exit(1)
    qpcr_file = sys.argv[1]
    sample_data = sys.argv[2]
    plate = sys.argv[3]
    output_dir = sys.argv[4]
    os.makedirs(output_dir, exist_ok=True)
    try:
        measurements = qpcr_measurements(qpcr_file, sample_data, plate)
        measurements_path = os.path.join(output_dir, f"{plate}_measurements.txt")
        with open(measurements_path, "w") as f:
            f.write(f"qPCR Measurements for {plate}\n")
            f.write(f"{'='*40}\n")
            f.write(f"Standard Curve Slope: {measurements['slope']:.4f}\n")
            f.write(f"Standard Curve Y-intercept: {measurements['intercept']:.4f}\n")
            f.write(f"R² value: {measurements['r2']:.4f}\n")
            f.write(f"Efficiency: {measurements['efficiency']:.2f}%\n")
            f.write(f"MSE: {measurements['mse']:.6f}\n")
            f.write(f"RMSE: {measurements['rmse']:.6f}\n")
        save_qpcr_std_curve(qpcr_file, sample_data, plate, output_dir)
        qpcr_calc_table(qpcr_file, sample_data, plate, output_dir)
        print(f"Successfully processed {plate}")
        print(f"Results saved to {output_dir}")
        return 0
    except Exception as e:
        print(f"Error processing {plate}: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())

