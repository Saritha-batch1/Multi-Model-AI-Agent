import pandas as pd

def load_and_preview_dataset(csv_path):
    print("📌 Loading dataset from:", csv_path)
    df = pd.read_csv(csv_path)

    print("\n📌 Dataset Loaded Successfully!")
    print("\n🔹 Shape of Dataset:", df.shape)

    print("\n🔹 First 5 Rows:")
    print(df.head())

    print("\n🔹 Column Names:")
    print(list(df.columns))

    return df


def save_clean_copy(df, output_path):
    df.to_csv(output_path, index=False)
    print(f"\n✅ Cleaned dataset saved to: {output_path}")


if __name__ == "__main__":
    # File inside your folder
    input_file = "blood_count_dataset.csv"
    
    df = load_and_preview_dataset(input_file)

    # Optional: Save cleaned version
    save_clean_copy(df, "clean_blood_count_dataset.csv")
