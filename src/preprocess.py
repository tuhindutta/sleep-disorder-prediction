import os
import pandas as pd
from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import MinMaxScaler
import pickle
import argparse


def run_preprocess(inp:str, otp:str, artifacts_path:str):
    df = pd.read_csv(inp).iloc[:, 1:]
    df.columns = ['_'.join(i.split(' ')).lower() for i in df.columns]
    # base = df.copy()

    features2_exclude_from_scaling = ['sleep_disorder']

    def drop_fields(df, *args):
        nonlocal features2_exclude_from_scaling
        features2_exclude_from_scaling += list(args)
        return df.drop(list(args), axis=1)

    df.bmi_category = df.bmi_category\
        .apply(lambda x: 'Normal' if x.strip().lower().startswith('normal') else x)

    fields2encode = ['gender', 'occupation', 'bmi_category']

    onehotencoder = OneHotEncoder(handle_unknown='ignore', sparse_output=False)
    encoded_df = onehotencoder.fit_transform(df.loc[:, fields2encode])

    features = []
    for feature in onehotencoder.get_feature_names_out():
        for encode_field in fields2encode:
            if feature.startswith(encode_field):
                renamed = feature.replace(encode_field, 'is').lower()
                features2_exclude_from_scaling.append(renamed)
                features.append(renamed)
                break

    encoded_df = drop_fields(pd.DataFrame(encoded_df, columns=features), 'is_female', 'is_normal')

    df = pd.concat([df.drop(fields2encode, axis=1), encoded_df], axis=1)

    df[['systolic_bp', 'diastolic_bp']] = df['blood_pressure'].str.split('/', expand=True)\
        .apply(lambda x: x.str.strip()).astype('int')
    df = drop_fields(df, 'blood_pressure')

    label_mapping = {"Normal": 0, "Sleep Apnea": 1, "Insomnia": 2}
    df.sleep_disorder = df.sleep_disorder.fillna('Normal').map(label_mapping)

    features2_exclude_from_scaling = list(set(features2_exclude_from_scaling).intersection(set(df.columns)))

    scaler = MinMaxScaler()
    scaled_df = df.drop(features2_exclude_from_scaling, axis=1)
    scaled_df = pd.DataFrame(scaler.fit_transform(scaled_df), columns=scaled_df.columns)
    df = pd.concat([scaled_df, df[features2_exclude_from_scaling]], axis=1)

    df.to_csv(otp, index=False)

    scaler_path = os.path.join(artifacts_path, 'scaler.pkl')
    with open(scaler_path, 'wb') as file:
        pickle.dump(scaler, file)


def main():
    parser = argparse.ArgumentParser(description='Training script')
    parser.add_argument('-i', '--input', help='Specify input data csv path.')
    parser.add_argument('-o', '--output', help='Specify output data csv parent path.')
    parser.add_argument('-a', '--artifacts', help='Specify artifacts save path.')
    args = parser.parse_args()

    inp = args.input + '.csv' if not args.input.endswith('.csv') else args.input
    otp = os.path.join(args.output, 'processed_data.csv')
    artifacts_path = args.artifacts

    run_preprocess(inp, otp, artifacts_path)


if __name__ == "__main__":
    main()