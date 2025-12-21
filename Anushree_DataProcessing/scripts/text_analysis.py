import pandas as pd

def analyze_data(df):
    print("\n=== 🔍 DATA ANALYSIS REPORT ===\n")

    print("📌 Shape of Dataset:")
    print(df.shape)

    print("\n📌 Column Names:")
    print(df.columns.tolist())

    print("\n📌 Data Types:")
    print(df.dtypes)

    print("\n📌 Missing Values:")
    print(df.isnull().sum())

    print("\n📌 Basic Statistics:")
    print(df.describe())

    print("\n📌 Sample Records:")
    print(df.head())

if __name__ == "__main__":
    df = pd.read_csv("blood_count_dataset.csv")
    analyze_data(df)
