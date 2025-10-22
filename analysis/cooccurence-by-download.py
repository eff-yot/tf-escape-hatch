import pandas as pd
from itertools import combinations


def load_data(file_path):
    df = pd.read_csv(file_path)
    smell_columns = sorted([col for col in df.columns if col not in ['Module', 'Provisioner', 'Category']])

    if 'Category' in df.columns:
        df['Category'] = df['Category'].astype(str).str.split('_').str[0]

    for col in smell_columns:
        df[col] = df[col].replace('', 0).fillna(0)
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        df[col] = (df[col] > 0).astype(int)

    aggregated = df.groupby(['Module', 'Category'])[smell_columns].max().reset_index()
    return aggregated, smell_columns


def get_smell_labels():
    return {
        'Arbitrary Resource Interaction': 'ARI',
        'Command Injection via Unsanitized Input': 'CI',
        'Excessive Permissions': 'EP',
        'Execution of Unverified Programs': 'EIVP',
        'File Content Injection': 'FCI',
        'Inconsistent Configuration': 'ICFG',
        'Insecure Communication': 'IC',
        'Insecure Handling of Secrets': 'IHTS',
        'Non-Idempotent Execution': 'NE',
        'Unsanitized Path Traversal': 'UPT'
    }


def calculate_cooccurrence_percentage(data, smell_columns):
    smell_columns = sorted(smell_columns)
    n_instances = len(data)
    cooccurrence = pd.DataFrame(0.0, index=smell_columns, columns=smell_columns)

    for _, row in data.iterrows():
        present_smells = [i for i, smell in enumerate(smell_columns) if row[smell] == 1]

        for i, j in combinations(present_smells, 2):
            smell1, smell2 = smell_columns[i], smell_columns[j]
            cooccurrence.loc[smell1, smell2] += 1
            cooccurrence.loc[smell2, smell1] += 1

        for i in present_smells:
            smell = smell_columns[i]
            cooccurrence.loc[smell, smell] += 1

    cooccurrence = (cooccurrence / n_instances * 100).round(2)
    return cooccurrence


def rename_with_labels(df, labels):
    df_renamed = df.copy()
    df_renamed.index = [labels.get(idx, idx) for idx in df_renamed.index]
    df_renamed.columns = [labels.get(col, col) for col in df_renamed.columns]
    return df_renamed


def print_markdown_table(df, title):
    print(f"{title}")

    header = "| Smell | " + " | ".join(df.columns) + " |"
    separator = "|" + "|".join([" --- "] * (len(df.columns) + 1)) + "|"

    print(header)
    print(separator)

    for index, row in df.iterrows():
        values = " | ".join([f"{val}" for val in row])
        print(f"| {index} | {values} |")


df, smell_columns = load_data("unverified-0107.csv")
labels = get_smell_labels()

categories = sorted(df['Category'].unique())

for category in categories:
    category_data = df[df['Category'] == category][smell_columns]
    if len(category_data) > 0:
        cooccurrence = calculate_cooccurrence_percentage(category_data, smell_columns)
        labeled_cooccurrence = rename_with_labels(cooccurrence, labels)
        print_markdown_table(labeled_cooccurrence, f"{category}")
