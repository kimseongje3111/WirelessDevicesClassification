import pandas as pd
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt
from sklearn.preprocessing import *
from sklearn.cluster import *

# Calculate inter-burst-latency value by source.
# Create feature if number is more than certain number.
# Feature ---> Y : source / X : points of clustering centers and mean
# Add feature data.

ONE_SECONDS = 1000
TWO_MENETES = 2 * 60 * 1000

sources = {}
interBurstLatency = {}

feature_df = pd.DataFrame(columns=('source', 'x1', 'y1', 'x2', 'y2', 'x3', 'y3', 'mean'))
data_count = 0


def scaler(name, data):
    scaler = StandardScaler()
    robust_scaler = RobustScaler()
    minmax_scaler = MinMaxScaler(feature_range=(0, 1))

    if name == 'standard':
        return scaler.fit_transform(data)

    elif name == 'robust':
        return robust_scaler.fit_transform(data)

    elif name == 'minmax':
        return minmax_scaler.fit_transform(data)


def std_based_outlier(df):
    return df[~(np.abs(df.iloc[:, 1] - df.iloc[:, 1].mean()) > (1.5 * df.iloc[:, 1].std()))].fillna(0)


def calculateInterBurstLatencyBySource(srcList, probeRequests):
    global sources
    global interBurstLatency

    for item in range(0, len(srcList)):
        src = srcList[item]

        for captureData in probeRequests[item]:
            time = captureData.sniff_time

            if src not in sources:
                sources[src] = [time]
            else:
                sources[src].append(time)

    # inter-burst-latency value by source.
    for src, time in sources.items():
        interBurst = []
        preArrivalTime = time[0]

        for nowArrivalTime in time[1:-1]:
            deltaTime = nowArrivalTime - preArrivalTime
            temp = str(deltaTime).split(':')

            if 'day' not in temp[0]:

                hour = int(temp[0]) * 60 * 60 * ONE_SECONDS
                minute = int(temp[1]) * 60 * ONE_SECONDS
                second = float(temp[2]) * ONE_SECONDS
                total = hour + minute + second

                if total >= ONE_SECONDS and total <= TWO_MENETES:
                    interBurst.append(int(total))

                preArrivalTime = nowArrivalTime

        interBurstLatency[src] = interBurst


def featureFromCentersAndMeanOfOptimal(src, data):
    for i in range(0, int(len(data.index) / 50)):
        # Inter-burst-latency --> Min : 1s / Max : 2m
        temp = pd.DataFrame(data[i * 50:(i + 1) * 50], columns=('x', 'y'))
        temp.loc[i * 50 + 50] = (50, ONE_SECONDS)
        temp.loc[i * 50 + 51] = (51, TWO_MENETES)

        # Min-Max scale and sort
        scaled_df = pd.DataFrame(scaler('minmax', temp), columns=('x', 'y'))
        scaled_df = scaled_df.sort_values(by='y').drop([0, 51], 0).reset_index(drop=True)
        scaled_df['x'] = scaled_df.index / 50.0

        # Clustering
        cluster_number = 3
        data_points = scaled_df.values
        kmeans = KMeans(n_clusters=cluster_number).fit(data_points)
        dbscan = DBSCAN(eps=0.05, min_samples=1).fit(data_points)

        # Points of clustering centers
        centers = np.sort(kmeans.cluster_centers_, axis=0)

        # Optimal mean
        scaled_df['label'] = dbscan.labels_

        dbscan_df = pd.DataFrame()
        dbscan_df['count'] = scaled_df.groupby(['label'])['y'].count()
        dbscan_df['mean'] = scaled_df.groupby(['label'])['y'].mean()
        dbscan_df = dbscan_df.sort_values(by=['count'], ascending=False).reset_index()

        scaledOptimalMean = float(dbscan_df.head(1)['mean']) * 2.0

        # Print result
        if i == 0:
            plt.title('Clustering (' + src + ')')
            plt.xlabel('(count)')
            plt.ylabel('(ms)')
            plt.ylim(0, 1)

            plt.scatter((scaled_df['x'] * 50), scaled_df['y'], c=kmeans.labels_.astype(float), s=50)
            plt.scatter((centers[:, 0] * 50), centers[:, 1], c='red', s=50)
            plt.show()

            print('>> Optimal Mean : ', scaledOptimalMean)
            print('--------------------------------------------------------------\n')

        # Create feature
        global feature_df
        global data_count
        feature = []

        feature.append(src)

        for j in range(cluster_number):
            for k in range(2):
                feature.append(centers[j][k])

        feature.append(scaledOptimalMean)

        feature_df.loc[data_count] = feature
        data_count += 1


def createFeatureFromInterBurstLatency(srcList, probeRequests):
    calculateInterBurstLatencyBySource(srcList, probeRequests)

    # Create data frame and remove outliers.
    isUpdated = False

    for src, values in interBurstLatency.items():
        if len(values) < 50:
            continue

        df = pd.DataFrame(columns=('x', 'y'))
        df['x'] = range(0, len(values))
        df['y'] = values

        # Remove outliers
        df = std_based_outlier(df).reset_index(drop=True)
        df['x'] = df.index

        # Create feature if number is more than certain number.
        if len(df.index) >= 50:
            print('>> [' + str(dt.datetime.now()) + ']')
            print('>> Success to create feature from', src)
            isUpdated = True
            featureFromCentersAndMeanOfOptimal(src, df)

    # Add feature data.
    if isUpdated is True:
        preTrainingSet_df = pd.read_csv("./data/TrainingSet.csv")
        newTrainingSet_df = pd.concat([preTrainingSet_df, feature_df]).drop_duplicates().reset_index(drop=True)

        newTrainingSet_df.to_csv("./data/TrainingSet.csv", index=False)
