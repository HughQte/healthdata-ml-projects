import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# define path
# note: I would not provide data on Github
project_dir = Path.cwd().parent
data_path = project_dir / "data" / "raw" / "ucsf_fsx7.csv"

# Load the MRI data
mri = project_dir / "data" / "raw" / "ucsf_fsx7.csv"
mri_raw = pd.read_csv(mri)

# Overview of the dataset
# mri_raw.head()

# Display the original shape of the dataset
print("Original shape of the dataset:", mri_raw.shape)

# Inspect the dataset
# Number of unique subjects
print("\nUnique subjects:")
print(mri_raw["PTID"].nunique())

#Duplicated rows
print("\nDuplicated rows:")
print(mri_raw[["PTID", "IMAGEUID"]].duplicated().sum())

# QC summary from ALL original scan records
qc_cols = [c for c in mri_raw.columns if c.endswith("QC")]
for col in qc_cols:
    print(f"\n{col}")
    print(mri_raw[col].value_counts(dropna=False))

print("\nRecords belonging to repeated PTID–EXAMDATE groups:",
      mri_raw.duplicated(["PTID", "EXAMDATE"], keep=False).sum())

# Identify a failed QC at ANY visit and remove its entire participant history
failed_subjects = mri_raw.loc[
    mri_raw["OVERALLQC"].astype("string").str.strip().str.casefold().eq("fail").fillna(False),
    "PTID"
].dropna().unique()

mri_raw_qc = mri_raw.loc[~mri_raw["PTID"].isin(failed_subjects)].copy()

print("Subjects with at least one Overall QC Fail:", len(failed_subjects))
print("Subjects before QC exclusion:", mri_raw["PTID"].nunique())
print("Subjects after QC exclusion:", mri_raw_qc["PTID"].nunique())
print("Scan records removed:", len(mri_raw) - len(mri_raw_qc))
assert not mri_raw_qc["PTID"].isin(failed_subjects).any()

# Retain only 3T acquisitions from participants passing the exclusion rule
mri_3t = mri_raw_qc.loc[mri_raw_qc["FIELD_STRENGTH"] == "3T"].copy()
mri_3t["EXAMDATE"] = pd.to_datetime(mri_3t["EXAMDATE"], errors="coerce")
print("3T records before valid-date filter:", len(mri_3t))
print("Records missing EXAMDATE:", mri_3t["EXAMDATE"].isna().sum())
mri_3t = mri_3t.dropna(subset=["EXAMDATE"])

tie_cols = ["PTID", "EXAMDATE"]
if "IMAGEUID" in mri_3t.columns:
    tie_cols.append("IMAGEUID")

mri_baseline = (mri_3t.sort_values(tie_cols, kind="stable")
               .drop_duplicates("PTID", keep="first")
               .reset_index(drop=True))
print("Baseline records:", len(mri_baseline))
print("Unique baseline subjects:", mri_baseline["PTID"].nunique())
assert mri_baseline["PTID"].is_unique

# FreeSurfer measurement columns: ST<number><suffix>, including ST87sa
import re
mri_features = [c for c in mri_baseline.columns
                if re.fullmatch(r"ST\d+(CV|SA|TA|TS|SV)", c, flags=re.IGNORECASE)]

print("MRI feature count:", len(mri_features))

# Inspect differences from the expected Task 1 inventory
if len(mri_features) != 325:
    print("NOTE: Feature count differs from Task 1 (325). Check column names.")
