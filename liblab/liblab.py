import pandas as pd

df = pd.read_excel("req2025.xlsx", header=[1])
print(df.columns.tolist())
