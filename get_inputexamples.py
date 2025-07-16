import pandas as pd
import mysql.connector
import random
from datetime import datetime
from sentence_transformers import InputExample

# --------- CONFIGURE THESE VARIABLES ---------
MYSQL_HOST = 'localhost'
MYSQL_PORT = 3306
MYSQL_USER = 'root'
MYSQL_PASS = 'password'
MYSQL_DB = 'scheduler'
N_ROWS = 110  # updated as requested
NUM_NEGATIVES_PER_QUERY = 1  # optional negative pairs per row
# ---------------------------------------------

def format_timestamp(ts):
    if isinstance(ts, str):
        try:
            return datetime.strptime(ts, "%Y-%m-%d %H:%M:%S").strftime("%B %d, %Y at %I:%M %p")
        except Exception:
            return ts
    return str(ts)

def make_summary_text(row):
    parts = []
    if row.get("study_name"):
        parts.append(f"This appointment belongs to the study '{row['study_name']}'.")
    if row.get("patient_name"):
        parts.append(f"It was scheduled for patient '{row['patient_name']}'.")
    if row.get("visit_type"):
        parts.append(f"The visit type is '{row['visit_type']}'.")
    if row.get("visit_template"):
        parts.append(f"Visit template used was '{row['visit_template']}'.")
    if row.get("scheduled_start_time") and row.get("scheduled_end_time"):
        start = format_timestamp(row["scheduled_start_time"])
        end = format_timestamp(row["scheduled_end_time"])
        parts.append(f"Scheduled from {start} to {end}.")
    if row.get("appointment_status"):
        parts.append(f"Status: {row['appointment_status']}.")
    if row.get("appointment_status_reason"):
        parts.append(f"Reason: {row['appointment_status_reason']}.")
    comment = str(row.get("comment") or "").strip()
    if comment:
        parts.append(f"Comment: {comment}")
    return " ".join(parts)

def make_query_text(row):
    status = (row.get("appointment_status") or "").lower()
    reason = (row.get("appointment_status_reason") or "").lower()
    study = (row.get("study_name") or "").lower()

    if "no show" in reason:
        return f"appointments where the patient did not show up{f' in {study}' if study else ''}".strip()
    elif "completed" in reason:
        return f"appointments that were successfully completed{f' in {study}' if study else ''}".strip()
    elif "equip" in reason:
        return f"appointments cancelled due to equipment failure{f' in {study}' if study else ''}".strip()
    elif "checked-in" in status:
        return f"appointments where patient was checked in{f' in {study}' if study else ''}".strip()
    elif "checked-out" in status:
        return f"appointments where patient completed their visit{f' in {study}' if study else ''}".strip()
    elif "cancel" in status:
        return f"cancelled appointments{f' in {study}' if study else ''}".strip()
    elif "scheduled" in status:
        return f"appointments that are still scheduled{f' in {study}' if study else ''}".strip()
    else:
        return f"patient appointments{f' in {study}' if study else ''}".strip()

def generate_query_variants(base):
    return list(set([
        base,
        base.replace("appointments", "visits"),
        base.replace("appointments", "appointment records"),
        base.replace("cancelled", "canceled"),
        base.replace("that were", "").strip(),
        base.replace("patient", "subject"),
        base.capitalize()
    ]))

def generate_input_examples(df):
    examples = []

    for i, row in df.iterrows():
        summary = make_summary_text(row)
        if not summary:
            continue

        base_query = make_query_text(row)
        variants = generate_query_variants(base_query)

        for query_variant in variants:
            examples.append(InputExample(texts=[query_variant, summary], label=1.0))
    return examples

def generate_negative_examples(df, num_negatives_per=1):
    examples = []
    for i, row in df.iterrows():
        correct_query = make_query_text(row)
        wrong_indices = random.sample(range(len(df)), k=num_negatives_per)
        for idx in wrong_indices:
            if idx == i:
                continue
            wrong_summary = make_summary_text(df.iloc[idx])
            if wrong_summary:
                examples.append(InputExample(texts=[correct_query, wrong_summary], label=0.0))
    return examples

def main():
    # Connect to MySQL and pull data
    conn = mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASS,
        database=MYSQL_DB,
        port=MYSQL_PORT
    )

    sql = f"SELECT * FROM appointment_summary LIMIT {N_ROWS};"
    df = pd.read_sql(sql, conn)
    conn.close()

    print(f"\n Pulled {len(df)} records.")

    # Generate positive examples (with variants)
    pos_examples = generate_input_examples(df)
    print(f"Generated {len(pos_examples)} positive InputExamples.")

    # Generate optional hard negatives
    neg_examples = generate_negative_examples(df, num_negatives_per=NUM_NEGATIVES_PER_QUERY)
    print(f" Generated {len(neg_examples)} negative InputExamples.")

    all_examples = pos_examples + neg_examples

    # Save as pickle
    import pickle
    with open("input_examples.pkl", "wb") as fout:
        pickle.dump(all_examples, fout)

    # Show a sample
    sample = all_examples[0]
    print("\n Sample InputExample:")
    print("Query:  ", sample.texts[0])
    print("Summary:", sample.texts[1])
    print("Label:  ", sample.label)
    print(f"\n Total examples saved: {len(all_examples)}")

if __name__ == "__main__":
    main()
