from sklearn import svm
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.decomposition import PCA
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import classification_report

def iris():
    def Sort_dic(type):
        it = {b'Iris-setosa': 0, b'Iris-versicolor': 1, b'Iris-virginica': 2}
        return it[type]
    path = 'Iris.data'
    data = np.loadtxt(path, dtype=float, delimiter=',', converters={4: Sort_dic})

    print("Iris:")
    x, y = np.split(data, indices_or_sections=(4,), axis=1)
    x = x[:, 0:2]
    train_data, test_data, train_label, test_label = train_test_split(x, y, random_state=1, train_size=0.8, test_size=0.2)

    classifier = svm.SVC(C=5, kernel='rbf', gamma=20, decision_function_shape='ovr')
    classifier.fit(train_data, train_label.ravel())


    print("Training_set_score：", format(classifier.score(train_data, train_label), '.3f'))
    print("Testing_set_score：", format(classifier.score(test_data, test_label), '.3f'))

    x1_min = x[:, 0].min()
    x1_max = x[:, 0].max()
    x2_min = x[:, 1].min()
    x2_max = x[:, 1].max()
    x1, x2 = np.mgrid[x1_min:x1_max:200j, x2_min:x2_max:200j]
    grid_test = np.stack((x1.flat, x2.flat), axis=1)
    grid_value = classifier.predict(grid_test)
    grid_value = grid_value.reshape(x1.shape)
    light_camp = matplotlib.colors.ListedColormap(['#FFA0A0', '#A0FFA0', '#A0A0FF'])
    dark_camp = matplotlib.colors.ListedColormap(['r', 'g', 'b'])
    fig = plt.figure(figsize=(10, 5))
    fig.canvas.set_window_title('SVM -2 feature classification of Iris')
    plt.pcolormesh(x1, x2, grid_value, cmap=light_camp,shading='auto')
    plt.scatter(x[:, 0], x[:, 1], c=y[:, 0], s=30, cmap=dark_camp)
    plt.scatter(test_data[:, 0], test_data[:, 1], c=test_label[:, 0], s=30, edgecolors='white', zorder=2, cmap=dark_camp)
    plt.title('SVM -2 feature classification of Iris')
    plt.xlabel('length of calyx')
    plt.ylabel('width of calyx')
    plt.title('Iris')
    plt.xlim(x1_min, x1_max)
    plt.ylim(x2_min, x2_max)
    plt.show()

def agaricus():
    print('agaricus')
    mush_df = pd.read_csv('agaricus-lepiota.data')
    mush_df_encoded = pd.get_dummies(mush_df)
    X_mush = mush_df_encoded.iloc[:, 2:]
    y_mush = mush_df_encoded.iloc[:, 1]
    Xtrain, Xtest, ytrain, ytest = train_test_split(X_mush, y_mush,random_state=41)
    pca = PCA(n_components=50, whiten=True, random_state=42)
    svc = SVC(kernel='linear', class_weight='balanced')
    model = make_pipeline(pca, svc)
    param_grid = {'svc__C': [1, 5, 10, 50]}
    grid = GridSearchCV(model, param_grid)
    grid.fit(Xtrain, ytrain)
    model = grid.best_estimator_
    yfit = model.predict(Xtest)
    print(classification_report(ytest, yfit))

iris()
agaricus()