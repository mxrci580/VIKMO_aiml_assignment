import pandas as pd

def load_catalogue(path):
    return pd.read_csv(path)

if __name__ == "__main__":
    df = load_catalogue("data/catalogue.csv")

    print(df.head())
    print(f"\nRows: {len(df)}")