import pandas as pd
import shutil
from sklearn.feature_selection import RFE
from sklearn.model_selection import cross_val_score
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import MinMaxScaler
from mlflow.tracking import MlflowClient


class Selector(BaseEstimator, TransformerMixin):
    def __init__(self, model, no_of_features):
        self.model = model
        self.no_of_features = no_of_features
        self.selector = RFE(estimator=model, n_features_to_select=no_of_features)
    def fit(self, X, y=None):
        self.selector.fit(X, y)
        return self
    def transform(self, X):
        X_out = self.selector.transform(X)
        return X_out
    
class PipelineSelector(BaseEstimator, TransformerMixin):
    def __init__(self, columns:list):
        self.columns = columns
    def fit(self, X=None, y=None):
        return self
    def transform(self, X):
        X_out = X[self.columns]
        return X_out
    def fit_transform(self, X, y=None):
        X_out = self.transform(X)
        return X_out
    
class CrossVal(BaseEstimator, TransformerMixin):
    def __init__(self, model, cv):
        self.model = model
        self.cv = cv
    def fit(self, X, y):
        accuracy = float(cross_val_score(self.model, X, y, cv=self.cv, scoring='accuracy').mean())
        roc_auc_ovr = float(cross_val_score(self.model, X, y, cv=self.cv, scoring='roc_auc_ovr').mean())
        self.cv_score = {
            'accuracy': accuracy,
            'roc_auc_ovr': roc_auc_ovr
        }
        return self
    

class Artifacts:

    def __init__(self, mlflow_uri:str):
        self.client = MlflowClient(tracking_uri=mlflow_uri)

    def get_artifacts_path(self, model_name:str, model_version:int):
        model_version_obj = self.client.get_model_version(name=model_name, version=model_version)
        self.artifact_path_uri = model_version_obj.source

    def save(self, destination:str):
        shutil.copytree(self.artifact_path_uri, destination)
        return "Artifacts published."
    

class Scaler(BaseEstimator, TransformerMixin):
    def __init__(self, features2_exclude_from_scaling:list):
        self.features2_exclude_from_scaling = features2_exclude_from_scaling
        self.scaler = MinMaxScaler()

    def fit(self, data:pd.DataFrame, _):
        features2_exclude_from_scaling = set(self.features2_exclude_from_scaling).intersection(set(data.columns))
        subset_data = data.drop(features2_exclude_from_scaling, axis=1)
        self.subset_data_columns = subset_data.columns
        self.scaler.fit(subset_data)
        return self
    
    def transform(self, data:pd.DataFrame):
        scaled_df = pd.DataFrame(self.scaler.transform(data[list(self.subset_data_columns)]),
                                 columns=self.subset_data_columns,
                                 index=data.index)
        other_columns = [i for i in data.columns if i not in self.subset_data_columns]
        df = pd.concat([scaled_df, data[other_columns]], axis=1)
        return df
    

def write_list(lst:list, file_name:str):
    with open(file_name, 'w') as file:
        for item in lst:
            file.write(item + '\n')


def read_list(file_name:str):
    lst = []
    with open(file_name, 'r') as file:
        for line in file:
            lst.append(line.strip())
    return lst