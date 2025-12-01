import pandas as pd

def preprocess(df):
    print("🔧 Starting preprocessing...\n")

    # 1. Clean column names
    df.columns = df.columns.str.lower().str.replace(" ", "_")

    # 2. Remove duplicates
    df = df.drop_duplicates()

    # 3. Convert numeric columns properly
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="ignore")

    # 4. Fill missing numeric values with mean
    df = df.fillna(df.mean(numeric_only=True))

    print("✅ Preprocessing Completed Successfully!")
    return df

if __name__ == "__main__":
    df = pd.read_csv("blood_count_dataset.csv")
    processed = preprocess(df)
    processed.to_csv("blood_count_dataset_cleaned.csv", index=False)

    print("\n📁 Saved cleaned dataset → blood_count_dataset_cleaned.csv")
