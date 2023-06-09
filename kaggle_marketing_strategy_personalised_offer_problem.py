# -*- coding: utf-8 -*-
"""Kaggle-Marketing_Strategy-Personalised_Offer-Problem.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1so4Ur-2-qkDz8IXjF9l4YQv2aJk3exwk
"""

# This Python 3 environment comes with many helpful analytics libraries installed
# It is defined by the kaggle/python Docker image: https://github.com/kaggle/docker-python
# For example, here's several helpful packages to load

import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)

# Input data files are available in the read-only "../input/" directory
# For example, running this (by clicking run or pressing Shift+Enter) will list all files under the input directory

import os
for dirname, _, filenames in os.walk('/kaggle/input'):
    for filename in filenames:
        print(os.path.join(dirname, filename))

# You can write up to 20GB to the current directory (/kaggle/working/) that gets preserved as output when you create a version using "Save & Run All" 
# You can also write temporary files to /kaggle/temp/, but they won't be saved outside of the current session

sample_data = pd.read_csv("/kaggle/input/marketing-strategy-personalised-offer/sample.csv")
data = pd.read_csv("/kaggle/input/marketing-strategy-personalised-offer/train_data.csv")
test_data = pd.read_csv("/kaggle/input/marketing-strategy-personalised-offer/test_data.csv")

"""# **About Data**"""

null_col = data.isna().sum().loc[data.isna().sum() > 0].index

data.drop(["car"],axis= 1, inplace= True)
data.rename(columns={'visit restaurant with rating (avg)':'Rating'},inplace = True)

data.dropna(axis=0,inplace= True)

y = data["Offer Accepted"]
data.drop(["Offer Accepted"],axis=1, inplace= True)

cat_columns = list(data.select_dtypes('object').columns)
num_columns = list(data.select_dtypes('int64').columns)

orignal_data = data.copy()

cat_columns

num_columns

data.info()

data.describe()

"""# **EDA and Plots**"""

data[num_columns].hist(figsize=(15, 20));

data[["temperature", "Travel Time"]].hist(figsize=(15,20));

import plotly.express as px

px.scatter_matrix(data[["Rating","temperature", "Travel Time"]])

corr = data[["Cooks regularly","has Children","Rating","temperature",
    "Travel Time","Prefer home food"]].corr()

px.imshow(corr)

"""# **Working on Data**"""

orignal_data.shape

data.shape

from sklearn.preprocessing import MaxAbsScaler, MinMaxScaler
minmax = MinMaxScaler()

from sklearn.preprocessing import OneHotEncoder
onehot = OneHotEncoder(sparse = False)

from sklearn.impute import SimpleImputer
simp = SimpleImputer(strategy="most_frequent")

num_columns

ecat = onehot.fit_transform(orignal_data[cat_columns])
enum = minmax.fit_transform(orignal_data[num_columns])

orignal_data[cat_columns]

"""### **Working on y**"""

'''
yl = []
for i in y:
    if i == 'Yes':
        yl.append(1)
    else:
        yl.append(0)
        '''

'''
for i in range(len(y)):
    y[i] = yl[i]
    '''

"""# **Data for Modeling**"""

X = np.concatenate((enum,ecat),axis= 1)

from sklearn.model_selection import train_test_split
x_train,x_test,y_train,y_test =train_test_split(X,y, test_size= 0.2,random_state=42,shuffle= False)

x_train

y_train

y_train.replace(('Yes','No'),(1,0),inplace = True)

y_train

x_test

y_test.replace(('Yes','No'),(1,0),inplace = True)

y_test

"""# **Test Data Modification**"""

test_data.drop(["car"],axis= 1, inplace= True)
test_data.rename(columns={'visit restaurant with rating (avg)':'Rating'},inplace = True)

null_col_test = test_data.isna().sum().loc[test_data.isna().sum() > 0].index

from sklearn.impute import SimpleImputer
test_data[null_col_test] = pd.DataFrame(
    simp.fit_transform(test_data[null_col_test]),columns= data[null_col_test].columns)

ecat_test = onehot.fit_transform(test_data[cat_columns])
enum_test = minmax.fit_transform(test_data[num_columns])
X_test = np.concatenate((enum_test,ecat_test), axis= 1)

"""# **Model Fitting**

### **Random Forest**
"""

from sklearn.ensemble import RandomForestClassifier
rf = RandomForestClassifier()

rf.fit(x_train, y_train)

rf.score(x_test,y_test)

"""**Hyperparameter tuning @randomforest**"""

#stop

para = {'n_estimators':[10,25,50,75,100,1000],
        'max_depth':[2,5,10,15],
        'min_samples_split':[2,3,4]}

from sklearn.model_selection import GridSearchCV
gsv_rf = GridSearchCV(rf,para, scoring='f1_micro', cv = 5)

gsv_rf.fit(x_train, y_train)
gsv_rf.score(x_test,y_test)

gsv_rf.best_params_

"""### **XGBoost**"""

from xgboost import XGBClassifier
xgb = XGBClassifier(random_state = 11)

data = pd.DataFrame(simp.fit_transform(data), columns = data.columns)

l = []
for i in data.columns:
  try:
    data[i] = data[i].astype('int')
  except Exception as e:
    l.append(i)

xgb.fit(x_train,y_train)

xgb.score(x_test,y_test)

"""**Hyperparameter tuning @XGBoost**"""

'''
params = {'learning_rate':[0.01,0.1,0.2,0.3],
          'max_depth':[3,5,7,8,10],
          'gamma':[0.1,0.2],
          'min_child_weight':[1,3,5]}
          '''

#gsv_xgb = GridSearchCV(xgb,params,scoring ='f1_micro',cv = 5)

#gsv_xgb.fit(x_train,y_train)

#gsv_xgb.score(x_test,y_test)

"""# **Final Model Selected after Grid search CV**"""

final_model = RandomForestClassifier(max_depth = 15, min_samples_split = 4, n_estimators = 1000)
final_model.fit(x_train,y_train)

from sklearn.metrics import classification_report
print(classification_report(y_test,final_model.predict(x_test)))

final_model.score(x_test,y_test)

"""# **Output of Model Selection**"""

y_pred = final_model.predict(X_test)
preds_csv = pd.DataFrame({
    'id': range(len(y_pred)),
    'Offer Accepted':y_pred
})

preds_csv['Offer Accepted'].replace((1,0),('Yes','No'),inplace = True)

preds_csv

preds_csv.to_csv("MLP_Project_sub_Term-3.csv",index= False)

#End