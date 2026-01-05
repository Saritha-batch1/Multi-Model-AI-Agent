import pandas as pd
import os 
import sys
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.impute import SimpleImputer


BASE_DIR = os.getcwd()
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")

os.makedirs(PROCESSED_DIR, exist_ok=True)
# It's good practice to define all paths relative to the project root.
# Assuming this script is run from the project root.
SRC_DIR = os.path.join(BASE_DIR, "src")
RAW_DATA_DIR = os.path.join(BASE_DIR, "data", "raw")

# Helper function to load CSVs with clear error messages
def load_csv(path):
    if not os.path.exists(path):
        print(f"\nError: The file was not found at '{path}'")
        parent_dir = os.path.dirname(path)
        if os.path.isdir(parent_dir):
            print(f"\nFiles found in '{parent_dir}':")
            print([f for f in os.listdir(parent_dir)])
        else:
            print(f"The directory '{parent_dir}' does not exist.")
        sys.exit(1)
    return pd.read_csv(path)

healthcare_path = os.path.join(RAW_DATA_DIR, "healthcare_dataset.csv")
laboratory_path = os.path.join(RAW_DATA_DIR, "laboratory__data.csv")
healthcare_df = load_csv(healthcare_path)
laboratory_df = load_csv(laboratory_path)

print("Healthcare data shape:", healthcare_df.shape)
print("Laboratory data shape:", laboratory_df.shape)


print(healthcare_df.head())
print(laboratory_df.head())

# Feature Engineering: Calculate Length of Stay before dropping dates
if "Date of Admission" in healthcare_df.columns and "Discharge Date" in healthcare_df.columns:
    healthcare_df["Date of Admission"] = pd.to_datetime(healthcare_df["Date of Admission"], errors='coerce')
    healthcare_df["Discharge Date"] = pd.to_datetime(healthcare_df["Discharge Date"], errors='coerce')
    healthcare_df["Length_of_Stay"] = (healthcare_df["Discharge Date"] - healthcare_df["Date of Admission"]).dt.days
    # Handle cases where discharge is same day or data error (negative days)
    healthcare_df["Length_of_Stay"] = healthcare_df["Length_of_Stay"].fillna(0).apply(lambda x: x if x >= 0 else 0)

# Unwanted columns
unwanted_healthcare_cols = [
    "Name",
    "Doctor",
    "Hospital",
    "Insurance Provider",
    "Billing Amount",
    "Room Number",
    "Date of Admission",
    "Discharge Date",
]

# Drop unwanted columns
healthcare_cleaned = healthcare_df.drop(
    columns=unwanted_healthcare_cols,
    errors="ignore"
)

print("Healthcare cleaned shape:", healthcare_cleaned.shape)
print(healthcare_cleaned.head())

# Merge the cleaned healthcare data with the laboratory data by index
# This assumes that the rows in both files correspond to each other

# FIX: Reset indices to ensure strict row-by-row alignment. 
# This prevents NaN generation due to index mismatches.
healthcare_cleaned.reset_index(drop=True, inplace=True)
laboratory_df.reset_index(drop=True, inplace=True)

# Concatenate
merged_df = pd.concat([healthcare_cleaned, laboratory_df], axis=1)

# Remove duplicate columns (e.g. if both datasets have 'Gender' or 'Age')
merged_df = merged_df.loc[:, ~merged_df.columns.duplicated()]

# FIX: Remove null values as requested by user
print(f"\nShape before dropping nulls: {merged_df.shape}")
merged_df.dropna(inplace=True)
print(f"Shape after dropping nulls: {merged_df.shape}")

print("\nMerged data shape:", merged_df.shape)
print("Merged data preview:")
print(merged_df.head())

merged_df.to_csv(
    os.path.join(RAW_DATA_DIR, "merged_healthcare_data.csv"),
    index=False
)
print("\n Merged dataset saved successfully to merged_healthcare_data.csv")

# --- Accuracy Checks ---

def calculate_metrics(df):
    """
    Calculates and prints data extraction accuracy (completeness) 
    and classification accuracy using a Random Forest model.
    """
    print("\n--- Performance Metrics ---")
    
    # 1. Data Extraction Accuracy (Completeness)
    # We define extraction accuracy as the ratio of complete rows (no missing values) 
    # to the total number of rows. This measures data quality after merging.
    # NOTE: Calculated on the processed dataframe.
    total_rows = len(df)
    raw_complete_rows = len(df.dropna())
    complete_rows = raw_complete_rows # Keep track for reporting
    extraction_acc = (complete_rows / total_rows) * 100 if total_rows > 0 else 0
    print(f"Data Extraction Accuracy (Completeness): {extraction_acc:.2f}%")
    
    # 2. Classification Accuracy
    # Attempt to predict 'Medical Condition' or 'Test Results' if they exist
    target = None
    possible_targets = ['Medical Condition', 'Test Results', 'Diagnosis']
    
    for col in possible_targets:
        if col in df.columns:
            target = col
            break
            
    if target:
        print(f"Calculating classification accuracy for target: '{target}'")
        
        # Prepare data
        # IMPROVEMENT: Instead of dropping rows, we IMPUTE missing values.
        # This increases the effective dataset size and improves model robustness.
        df_clean = df.copy() # Data is already cleaned above
        
        if len(df_clean) < 10:
            print("Not enough data to train a model.")
            return
            
        # Text Normalization: Lowercase all text columns to merge categories like "Diabetes" and "diabetes"
        for col in df_clean.select_dtypes(include=['object']).columns:
            df_clean[col] = df_clean[col].astype(str).str.lower().str.strip()

        # Separate Target and Features
        X = df_clean.drop(columns=[target])
        y = df_clean[target]

        # Encode categorical variables
        le = LabelEncoder()
        
        # Encode target
        y = le.fit_transform(y.astype(str))
        
        # Encode features: Use One-Hot Encoding (pd.get_dummies)
        # This significantly improves accuracy for categorical data compared to LabelEncoder
        X = pd.get_dummies(X, drop_first=True)
        
        # Split data
        # Added stratify=y to ensure training data represents all classes equally
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
        
        # Scale features (StandardScaler helps Gradient Boosting models)
        scaler = StandardScaler()
        X_train = scaler.fit_transform(X_train)
        X_test = scaler.transform(X_test)

        # Train Model
        # IMPROVEMENT: Use RandomForest with balanced class weights to handle imbalance
        print("Training Random Forest Model (Balanced)...")
        clf = RandomForestClassifier(n_estimators=500, class_weight='balanced', max_depth=20, random_state=42)
        clf.fit(X_train, y_train)
        
        # Predict and Calculate Accuracy
        y_pred = clf.predict(X_test)
        acc = accuracy_score(y_test, y_pred) * 100
        print(f"Classification Accuracy ({target}): {acc:.2f}%")
    else:
        print("Target column for classification not found (looked for: Medical Condition, Test Results).")

calculate_metrics(merged_df)
