import pandas as pd

def extract_key_parameters(path):
    df = pd.read_csv(path)

    print("\n📌 Identified Key Parameters:")
    for col in df.columns:
        print("-", col)

    return df.columns.tolist()

if __name__ == "__main__":
    extract_key_parameters("blood_count_dataset.csv")
