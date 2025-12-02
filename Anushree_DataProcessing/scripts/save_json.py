import pandas as pd

def save_as_json(csv_path, json_path):
    df = pd.read_csv(csv_path)
    df.to_json(json_path, orient="records", indent=4)
    print("Saved extracted parameters to:", json_path)

if __name__ == "__main__":
    save_as_json("extracted_parameters.csv", "extracted_parameters.json")
