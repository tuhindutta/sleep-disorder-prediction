python .\src\preprocess.py -i "C:\Users\Tuhin Kumar Dutta\.cache\kagglehub\datasets\varishabatool\disorder\versions\1\Sleep_health_and_lifestyle_dataset.csv" -o .\data\processed\ -a .\models\

python .\src\train.py -i .\data\processed\processed_data.csv -a .\models\


mlflow server `
>>   --backend-store-uri sqlite:///D:/MyFiles/Projects/Python/mlflow/mlflow.db `
>>   --default-artifact-root file:///D:/MyFiles/Projects/Python/mlflow/artifacts `
>>   --host 0.0.0.0 --port 5000