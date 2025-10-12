import shutil
from sklearn.feature_selection import RFE
from sklearn.model_selection import cross_val_score
from sklearn.base import BaseEstimator, TransformerMixin
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
    

def get_artifacts(run_id:str, destination:str):
    run_id = "3f8f7a3df1084027bfbaf0d16a6b03fa"
    client = MlflowClient(tracking_uri="http://127.0.0.1:5000")

    run = client.get_run(run_id)
    path = run.info.artifact_uri.replace('file:///', '')

    shutil.copytree(path, destination)