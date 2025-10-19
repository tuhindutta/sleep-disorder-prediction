import os
import yaml
import mlflow
from mlflow.models.signature import infer_signature
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import KFold
from sklearn.pipeline import Pipeline
import pickle
import argparse
from sleep_disorder.utilities import Selector, PipelineSelector, CrossVal, Scaler, read_list


def run_training(inp:str, cnf:str, artifacts_path:str, mlflow_uri:str):

    """
    Training function.

    This function takes the processed input csv path of data, training configuration path,
    MLFlow URI and integrates with mlflow for training and experimentation.

    Args:
        inp (str): Processed input csv path of data.
        cnf (str): Training configuration path.
            Configuration yaml example:
                num_features: 10
                kfold_split: 5
                model_params:
                    null
        mlflow_uri (str): MLFlow URI

    Returns:
        string:Success confirmation message.
    """

    with open(cnf, 'r') as file:
        config = yaml.safe_load(file)


    num_features = config['num_features']
    kfold_split = config['kfold_split']
    model_params = config['model_params']

    features2_exclude_from_scaling = read_list(os.path.join(artifacts_path, 'features2_exclude_from_scaling.txt'))


    df = pd.read_csv(inp)
    y = df.pop('sleep_disorder')
    X = df

    mlflow.set_tracking_uri(mlflow_uri)
    mlflow.set_experiment('sleep_disorder')

    with mlflow.start_run():

        log_reg_model = LogisticRegression(**model_params) if model_params is not None else LogisticRegression()
        scaler = Scaler(features2_exclude_from_scaling)
        selec = Selector(log_reg_model, num_features)
        rfe_data = selec.fit_transform(X, y)
        selected_columns = selec.selector.get_feature_names_out()
        X = pd.DataFrame(rfe_data, columns=selected_columns)

        model = Pipeline([
            ('pipeline_selector', PipelineSelector(selected_columns)),
            ('scaler', scaler),
            ('log_reg', log_reg_model)
        ])
        
        model.fit(X, y)
        kf = KFold(n_splits=kfold_split, shuffle=True, random_state=42)
        cv = CrossVal(model, kf)
        cv.fit(X, y)
        accuracy = cv.cv_score.get('accuracy')
        roc_auc_ovr = cv.cv_score.get('roc_auc_ovr')
        mlflow.log_param('columns_trained_in', selected_columns)
        mlflow.log_param('num_features', num_features)
        mlflow.log_param('kfold_split', kfold_split)
        mlflow.log_metric('accuracy', accuracy)
        mlflow.log_metric('roc_auc_ovr', roc_auc_ovr)
        sig = infer_signature(X, model.predict(X))
        mlflow.sklearn.log_model(
            sk_model=model,
            name="sleep-model",
            signature= sig,
            input_example=X.iloc[:5]
        )

    return "SUCCESS"

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