import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import make_pipeline
train = pd.DataFrame({"area": [30., np.nan, 80.], "district": ["A", "B", "A"]})
test = pd.DataFrame({"area": [np.nan], "district": ["C"]})
prep = ColumnTransformer([
    ("number", SimpleImputer(strategy="median"), ["area"]),
    ("category", make_pipeline(SimpleImputer(strategy="most_frequent"),
         OneHotEncoder(handle_unknown="ignore", sparse_output=False)), ["district"])])
print(prep.fit_transform(train))
print("New district:", prep.transform(test))
