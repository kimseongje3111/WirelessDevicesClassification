import warnings
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn import metrics
from sklearn.preprocessing import *


# Evaluate performance of classification model from test dataset.

def evaluatePerformanceOfmodel(nn_model, tstx, tsty):
    warnings.filterwarnings(action='ignore')

    try:
        # Neural network classification
        nn_pred = nn_model.predict(X=tstx)

        # PCA
        rdf = tstx
        rdf[7] = nn_pred
        X = rdf[[0, 1, 2, 3, 4, 5, 6]]
        Y = rdf[[7]]

        x_std = StandardScaler().fit_transform(X)
        features = x_std.T
        covariance_matrix = np.cov(features)
        eig_vals, eig_vecs = np.linalg.eig(covariance_matrix)
        projected_X = x_std.dot(eig_vecs.T[0])

        result = pd.DataFrame(projected_X, columns=['(PC1)'])
        result['(Y-Axis)'] = LabelEncoder().fit_transform(Y)
        result['Source'] = Y

        print(">> Success to evaluation for classification model")
        print('>> Accuracy : ', metrics.accuracy_score(tsty, nn_pred))
        print('--------------------------------------------------------------\n')

        sns.set(color_codes=True)
        sns.lmplot('(PC1)', '(Y-Axis)', data=result, fit_reg=False, scatter_kws={"s": 20}, hue='Source')

        plt.title('PCA')
        plt.show()

    except:
        print('>> [Error] File exceptions or nonexistent data')
