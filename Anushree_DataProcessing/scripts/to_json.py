import pandas as pd

def convert_to_json(csv_path, json_path):
    df = pd.read_csv(csv_path)
    df.to_json(json_path, orient="records", indent=4)
    print("✅ JSON file created successfully!")

if __name__ == "__main__":
    convert_to_json("blood_count_dataset_cleaned.csv", "blood_count_dataset_cleaned.json")
