import pandas as pd
import numpy as np
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split


# Create classification model from feature data.

def createClassificationModel():
    try:
        trainingSet_df = pd.read_csv("./data/TrainingSet.csv")

        np_df = np.array(trainingSet_df)
        datax = np_df[:, 1:8]
        datay = np_df[:, 0]

        trnx, tstx, trny, tsty = train_test_split(datax, datay, test_size=0.3, random_state=100)

        trnx = pd.DataFrame(trnx)
        tstx = pd.DataFrame(tstx)

        # Neural network classification
        nn_model = MLPClassifier(activation='relu', solver='lbfgs', alpha=1e-5, hidden_layer_sizes=(5), random_state=1)
        nn_model.fit(X=trnx, y=trny)

        print(">> Success to create classification model")
        print('--------------------------------------------------------------\n')

        return nn_model, tstx, tsty

    except:
        print('>> [Error] File exceptions or nonexistent data')
