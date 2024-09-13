# apply softmax to all entries in the FREQUENCY column

import pandas as pd

# get the FREQUENCY column
df = pd.read_csv("words.csv")
freqs = df["FREQUENCY"].tolist()

for i, freq in enumerate(freqs):
    freqs[i] = float(freq) / 200000

df["FREQUENCY"] = freqs
df.to_csv("words2.csv", index=False)

