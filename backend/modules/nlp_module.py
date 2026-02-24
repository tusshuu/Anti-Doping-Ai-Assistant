from rapidfuzz import process
import pandas as pd

df = pd.read_csv("database/wada_list.csv")
drug_list = df["substance"].str.lower().tolist()

def find_multiple_drugs(user_input, threshold=90):
    found_drugs = []

    # Split user input by comma
    user_drugs = [d.strip().lower() for d in user_input.split(",")]

    for user_drug in user_drugs:
        match = process.extractOne(user_drug, drug_list)

        if match and match[1] >= threshold:
            found_drugs.append(match[0])

    return list(set(found_drugs))
