
key_cols = ['Hemoglobin_gdl','FastingGlucose_mgdl','TotalCholesterol_mgdl','LDL_mgdl','HDL_mgdl','Triglycerides_mgdl']
non_null_counts = df[key_cols].notnull().sum()
coverage = (non_null_counts / len(df) * 100).round(2)
print("Extraction coverage (% non-null):")
print(coverage)


status_cols = ['Hemoglobin_status','Glucose_status','TotalCholesterol_status','LDL_status','HDL_status','Triglycerides_status','Creatinine_status','Urea_status','TSH_status','VitaminD_status']
for col in status_cols:
    print("\n", col)
    print(df[col].value_counts(normalize=True).mul(100).round(1).astype(str) + '%')
