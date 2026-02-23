
import pandas as pd

df = pd.read_csv("database/wada_list.csv")

def check_drugs(drug_names):
    results = []

    for drug in drug_names:
        row = df[df["substance"].str.lower() == drug.lower()]

        if not row.empty:
            status = row.iloc[0]["banned_status"]
            category = row.iloc[0]["category"]

            results.append({
                "substance": drug,
                "category": category,
                "status": status
            })

    return results
