from rapidfuzz import process
import pandas as pd

df = pd.read_csv("database/wada_list.csv")

drug_list = df["substance"].tolist()

def find_multiple_drugs(user_input, threshold=80):
    found_drugs = []

    for drug in drug_list:
        match_score = process.extractOne(
            drug,
            [user_input],
        )

        if match_score and match_score[1] >= threshold:
            found_drugs.append(drug)

    return list(set(found_drugs))
