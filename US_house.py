import Quandl
import pandas as pd
import pickle
import matplotlib.pyplot as plt
from matplotlib import style
from sklearn import svm, preprocessing, cross_validation
style.use('fivethirtyeight')


api_key = 'fKxzNiU37CKbcX-_pj5i'

def state_list():
    fiddy_states = pd.read_html('https://simple.wikipedia.org/wiki/List_of_U.S._states')
    return fiddy_states[0][0][1:]

def grab_initial_state_data():
    states = state_list()
    main_df = pd.DataFrame()

    for abbv in states :
        query = "FMAC/HPI_"+str(abbv)
        df = Quandl.get(query, authtoken=api_key)
        df.rename(columns={'Value':str(abbv)}, inplace=True)
        df[abbv] = ((df[abbv] - df[abbv][0]) / df[abbv][0]) * 100.0


        if main_df.empty:
            main_df = df
        else :
            main_df = main_df.join(df)
#           main_df = pd.merge(main_df,df,right_index=True, left_index=True)

    print(main_df.head())

    pickle_out = open('fiddy_states3.pickle','wb')
    pickle.dump(main_df, pickle_out)
    pickle_out.close()

def HPI_Benchmark():
    query = "FMAC/HPI_USA"
    df =Quandl.get(query, authtoken=api_key)
    df.rename(columns={'Value':str("United States")}, inplace=True)
    df["United States"] = ((df["United States"] - df["United States"][0]) / df["United States"][0]) * 100.0
    return df

#grab_initial_state_data()

fig = plt.figure()
ax1 = plt.subplot2grid((2,1),(0,0))
ax2 = plt.subplot2grid((2,1),(1,0),sharex=ax1)


HPI_data = pd.read_pickle('fiddy_states3.pickle')

HPI_data['TX12MA'] = pd.rolling_mean(HPI_data['TX'],12)
HPI_data['TX12STD'] = pd.rolling_std(HPI_data['TX'],12)

print (HPI_data[['TX12MA','TX','TX12STD']].head())
#HPI_data.dropna(inplace=True)
#HPI_data.fillna(value=-99999,limit=10,inplace=True)
#print (HPI_data[['TX12MA','TX']].head())

HPI_data[['TX','TX12MA']].plot(ax = ax1)
HPI_data['TX12STD'].plot(ax = ax2)


plt.legend(loc=4)
plt.show()

