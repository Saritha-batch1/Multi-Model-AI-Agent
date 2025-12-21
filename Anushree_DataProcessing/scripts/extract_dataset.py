import pandas as pd

def load_blood_dataset(path):
    print("📌 Loading dataset...")
    df = pd.read_csv(path)
    print("✅ Dataset Loaded Successfully!\n")
    print(df.head())   # show first 5 rows
    return df

if __name__ == "__main__":
    load_blood_dataset("blood_count_dataset.csv")
