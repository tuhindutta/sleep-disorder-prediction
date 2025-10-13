# import os
import yaml
import mlflow
from mlflow.models.signature import infer_signature
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import KFold
# import pickle
import argparse
from utilities import Selector, CrossVal


def run_training(inp:str, cnf:str):
    with open(cnf, 'r') as file:
        config = yaml.safe_load(file)


    num_features = config['num_features']
    kfold_split = config['kfold_split']
    model_params = config['model_params']


    df = pd.read_csv(inp)
    y = df.pop('sleep_disorder')
    X = df

    mlflow.set_tracking_uri("http://127.0.0.1:5000")
    mlflow.set_experiment('sleep_disorder')

    with mlflow.start_run():

        model = LogisticRegression(**model_params) if model_params is not None else LogisticRegression()
        selec = Selector(model, num_features)
        data = pd.DataFrame(selec.fit_transform(X, y), columns=selec.selector.get_feature_names_out())
        model.fit(data, y)
        kf = KFold(n_splits=kfold_split, shuffle=True, random_state=42)
        cv = CrossVal(model, kf)
        cv.fit(data, y)
        cv_score = cv.cv_score
        accuracy = cv.cv_score.get('accuracy')
        roc_auc_ovr = cv.cv_score.get('roc_auc_ovr')
        mlflow.log_param('num_features', num_features)
        mlflow.log_param('kfold_split', kfold_split)
        mlflow.log_metric('accuracy', accuracy)
        mlflow.log_metric('roc_auc_ovr', roc_auc_ovr)
        sig = infer_signature(data, model.predict(data))
        model_info = mlflow.sklearn.log_model(
            sk_model=model,
            name="sleep-model",
            signature= sig,
            input_example=data.iloc[:5]
        )

    # selector_path = os.path.join(artifacts_path, 'feature_selector.pkl')
    # with open(selector_path, 'wb') as file:
    #     pickle.dump(selec, file)

    # model_path = os.path.join(artifacts_path, 'model.pkl')
    # with open(model_path, 'wb') as file:
    #     pickle.dump(model, file)


def main():
    parser = argparse.ArgumentParser(description='Training script')
    parser.add_argument('-i', '--input', help='Specify input data csv path.')
    parser.add_argument('-c', '--config', help='Specify train config.')
    # parser.add_argument('-a', '--artifacts', help='Specify artifacts save path.')
    args = parser.parse_args()

    inp = args.input + '.csv' if not args.input.endswith('.csv') else args.input
    cnf = args.config + '.yaml' if not args.config.endswith('.yaml') else args.config
    # artifacts_path = args.artifacts

    run_training(inp, cnf)


if __name__ == "__main__":
    main()