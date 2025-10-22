import pandas as pd


def load_data(file_path):
    df = pd.read_csv(file_path)
    smell_columns = [col for col in df.columns if col not in ['Module', 'Provisioner', 'Category']]
    smell_columns = sorted(smell_columns)
    for col in smell_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    module_smells = df.groupby('Module')[smell_columns].max()
    return (module_smells > 0).astype(int)


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



def calculate_cooccurrence_percentage(data):
    smell_columns = sorted(data.columns.tolist())
    n_modules = len(data)
    cooccurrence = pd.DataFrame(0.0, index=smell_columns, columns=smell_columns)

    for i, smell1 in enumerate(smell_columns):
        for j, smell2 in enumerate(smell_columns):
            if i == j:
                count = data[smell1].sum()
            else:
                count = ((data[smell1] == 1) & (data[smell2] == 1)).sum()
            percentage = (count / n_modules) * 100 if n_modules > 0 else 0
            cooccurrence.loc[smell1, smell2] = round(percentage, 2)

    return cooccurrence


def rename_with_labels(df, labels):
    df_renamed = df.copy()
    df_renamed.index = [labels.get(idx, idx) for idx in df_renamed.index]
    df_renamed.columns = [labels.get(col, col) for col in df_renamed.columns]
    return df_renamed


def print_table(df, title):
    print(f"{title}")

    header = "| Smell | " + " | ".join(df.columns) + " |"
    separator = "|" + "|".join([" --- "] * (len(df.columns) + 1)) + "|"

    print(header)
    print(separator)

    for index, row in df.iterrows():
        values = " | ".join([f"{val}" for val in row])
        print(f"| {index} | {values} |")


verified_data = load_data("verified-0107.csv")
unverified_data = load_data("unverified-0107.csv")

verified_cooccurrence = calculate_cooccurrence_percentage(verified_data)
unverified_cooccurrence = calculate_cooccurrence_percentage(unverified_data)

labels = get_smell_labels()
verified_labeled = rename_with_labels(verified_cooccurrence, labels)
unverified_labeled = rename_with_labels(unverified_cooccurrence, labels)

print_table(verified_labeled, "Verified")
print_table(unverified_labeled, "Unverifed")
