import pandas as pd


def load_data(file_path):
    df = pd.read_csv(file_path)
    smell_columns = [col for col in df.columns if col not in ['Module', 'Provisioner', 'Category']]
    smell_columns = sorted(smell_columns)
    for col in smell_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        df[col] = (df[col] > 0).astype(int)
    return df, smell_columns


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

    for i, smell1 in enumerate(smell_columns):
        for j, smell2 in enumerate(smell_columns):
            if i == j:
                count = data[smell1].sum()
            else:
                count = (data[smell1] & data[smell2]).sum()
            percentage = (count / n_instances) * 100 if n_instances > 0 else 0
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



df, smell_columns = load_data("unverified-0107.csv")
labels = get_smell_labels()

provisioners = ['local-exec', 'remote-exec', 'data-external']

for provisioner in provisioners:
    prov_data = df[df['Provisioner'] == provisioner][smell_columns]
    if len(prov_data) > 0:
        cooccurrence = calculate_cooccurrence_percentage(prov_data, smell_columns)
        labeled_cooccurrence = rename_with_labels(cooccurrence, labels)
        print_table(labeled_cooccurrence, f"{provisioner}")
