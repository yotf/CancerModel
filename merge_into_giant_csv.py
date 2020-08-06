import os
import pandas as pd
mean_folder = "./Mean_CSVs/"
fnames = os.listdir(mean_folder)
giant_df = pd.DataFrame()
for f in fnames:
    df = pd.read_csv(os.path.join(mean_folder,f))
    for c in df.columns:
        if "Unnamed: 0" in c:
            continue
        new_column_name = c + "---" + "_".join(f.split(".")[0].split("_")[1:])
        
        print (new_column_name)
        giant_df[new_column_name]=df[c]

print (giant_df)
giant_df.to_csv("Giant_CSV_of_merged_Mean_CSVs.csv")
