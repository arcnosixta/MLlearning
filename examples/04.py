import pandas as pd
df = pd.DataFrame({"area": [30, 50, 70, 90],
                   "rooms": [1, 2, 3, 3],
                   "price": [60, 105, 140, 175]})
print(df.head())
print(df.describe())
print("Missing:", df.isna().sum().to_dict())
print("Large homes:\n", df.loc[df["area"] > 50, ["area", "price"]])
