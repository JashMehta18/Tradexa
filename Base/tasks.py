from celery import shared_task
from yahoo_fin.stock_info import *
from threading import Thread
import queue
from channels.layers import get_channel_layer
import asyncio
import simplejson as json
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import numpy as np
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.layers import LSTM
from numpy import array
from sklearn.preprocessing import MinMaxScaler
import tensorflow as tf
# %matplotlib inline

companies = ['TCS.NS', 'WIPRO.NS', 'HDFCBANK.NS', 'BAJFINANCE.NS', 'INFY.NS', 'SUZLON.NS', 'JPPOWER.NS']
# path = '/content/drive/MyDrive/LY-Project Data/'
path ='./assets/Model/'

def get_data():
    # get daily data and store it in the csv files
    data = yf.download(  # or pdr.get_data_yahoo(...
        # tickers list or string as well
        tickers = "TCS.NS WIPRO.NS INFY.NS HDFCBANK.NS BAJFINANCE.NS SUZLON.NS JPPOWER.NS",
        # tickers = "INFY.NS",

        # use "period" instead of start/end
        # valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
        # (optional, default is '1mo')
        period = "1d",  #yesterday
        # start = '2022-03-28',
        # end = '2022-03-30',

        # group by ticker (to access via data['SPY'])
        # (optional, default is 'column')
        group_by = 'ticker',

        # adjust all OHLC automatically
        # (optional, default is False)
        auto_adjust = True,

        # download pre/post regular market hours data
        # (optional, default is False)
        prepost = True,

        # use threads for mass downloading? (True/False/Integer)
        # (optional, default is True)
        threads = True,

        # proxy URL scheme use use when downloading?
        # (optional, default is None)
        proxy = None
    )
    print(data)
    for c in companies:
        df = pd.read_csv(path + c +'.csv')
        if 'Adj Close' in df.columns:
            print(c)
            df = df.drop(['Adj Close'], axis=1)
        # data[c].reset_index()['Date'] = data[c].reset_index()['Date'].dt.to_pydatetime()
        # print(df.loc[len(df.index)-1])
        # print(data[c].reset_index())
        # print(data)
        df = df.append(data[c].reset_index())
        # print(df.columns)
        df.to_csv(path + c + '.csv', index=False)

def create_dataset(dataset, time_step=1):
	dataX, dataY = [], []
	for i in range(len(dataset)-time_step-1):
		a = dataset[i:(i+time_step), 0]   ###i=0, 0,1,2,3-----99   100 
		dataX.append(a)
		dataY.append(dataset[i + time_step, 0])
	return np.array(dataX), np.array(dataY)

def create_new_model():
    model=Sequential()
    model.add(LSTM(32,return_sequences=True,input_shape=(100,1)))
    model.add(Dropout(0.25))
    model.add(LSTM(64,return_sequences=True))
    model.add(Dropout(0.25))
    model.add(LSTM(50))
    # model.add(Dropout(0.25))
    model.add(Dense(32)) 
    model.add(Dense(1))

    model.compile(loss='mean_squared_error', optimizer='adam')
    return model


def daily_predict():
    # create a dict
    # 1. read data from csv
    # 2. take the last 100 close values shape(1,100)
    # 3. apply min max scaler (copy from above)
    # 4. create model
    # 5. load weights
    # 6. copy the prediction code from above
    # 7. scaler.inverse_transform
    # 8. then thats the final o/p and save it in the csv file
    # get_data()
    ''' iterating through the companies '''
    for company in companies:
        df = pd.read_csv(path + company + '.csv')
        df_close=df.reset_index()['Close']
        # print(df_close)
        # print(company)
        # break
        scaler=MinMaxScaler(feature_range=(0,1))
        df_close=scaler.fit_transform(np.array(df_close).reshape(-1,1))
        x_input = df_close[len(df_close)-100:].reshape(1,-1)
        # print(df_close)
        # print(x_input.shape)
        # print(x_input)
        # model = create_model()
        # break
        print('loading model...')
        model = load_model(path + company +'_model')
        print('load successful')
        temp_input = list(x_input)
        temp_input = temp_input[0].tolist()
        # x_input = df_close.copy()
        lst_output=[]
        n_steps=100
        i=0
        print('predicting..')
        while(i<7):
            
            if(len(temp_input)>100):
                #print(temp_input)
                x_input=np.array(temp_input[1:])
                print("{} day input {}".format(i,x_input))
                x_input=x_input.reshape(1,-1)
                x_input = x_input.reshape((1, n_steps, 1))
                #print(x_input)
                yhat = model.predict(x_input, verbose=0)
                print("{} day output {}".format(i,yhat))
                temp_input.extend(yhat[0].tolist())
                temp_input=temp_input[1:]
                #print(temp_input)
                lst_output.extend(yhat.tolist())
                i=i+1
            else:
                x_input = x_input.reshape((1, n_steps,1))
                yhat = model.predict(x_input, verbose=0)
                print(yhat[0])
                temp_input.extend(yhat[0].tolist())
                print(len(temp_input))
                lst_output.extend(yhat.tolist())
                i=i+1

        print(lst_output)
        arr = scaler.inverse_transform(lst_output)
        # print(company.replace('.','_'))
        tempdf1 = pd.DataFrame(['Day 1', 'Day 2', 'Day 3', 'Day 4', 'Day 5', 'Day 6', 'Day 7'], columns=['Days'])
        tempdf2 = pd.DataFrame(scaler.inverse_transform(lst_output), columns=['predictions'])
        save_out = pd.concat([tempdf1, tempdf2], axis=1)
        print(save_out)
        # save_out.to_csv(path + company +'_predictions.csv')
        # model.save('/content/drive/MyDrive/LY-Project Data/'+ company + '.h5', save_format='h5')
        # break
        
def train_all():
    for company in companies:
        df = pd.read_csv(path + company + '.csv')
        df_close=df.reset_index()['Close']
        print(df_close.shape)
        scaler=MinMaxScaler(feature_range=(0,1))
        df_close=scaler.fit_transform(np.array(df_close).reshape(-1, 1))
        print(df_close.shape)
        # model = create_model()
        # model = load_model(path + company.replace('.','_') + '.h5')
        training_size=int(len(df_close)*0.90)
        test_size=len(df_close)-training_size
        train_data,test_data=df_close[0:training_size,:],df_close[training_size:len(df_close),:1]
        
        time_step = 100
        X_train, y_train = create_dataset(train_data, time_step)
        X_test, ytest = create_dataset(test_data, time_step)
        print(X_train, y_train, X_test, ytest)

        X_train =X_train.reshape(X_train.shape[0],X_train.shape[1] , 1)
        X_test = X_test.reshape(X_test.shape[0],X_test.shape[1] , 1)
        # model = create_model()
        model = create_new_model()
        
        # print(model.summary())
        model.fit(X_train,y_train,validation_data=(X_test,ytest),epochs=100,batch_size=64,verbose=1)
        model.save(path + company+'_model')

        # print(company.replace('.','_'))
        # break

@shared_task(bind = True)
def test_task(self):
    daily_predict()

    return "****Testing Task Called*****"

@shared_task(bind = True)
def update_stock(self, stockpicker):
    data = {}
    available_stocks = tickers_nifty50()
    for i in stockpicker:
        if i in available_stocks:
            pass
        else:
            stockpicker.remove(i)

    n_threads = len(stockpicker)
    thread_list = []
    que = queue.Queue()

    for i in range(n_threads):
        thread = Thread(target = lambda q, arg1: q.put({stockpicker[i]: json.loads(json.dumps(get_quote_table(arg1), ignore_nan = True))}), args = (que, stockpicker[i]))
        thread_list.append(thread)
        thread_list[i].start()

    for thread in thread_list:
        thread.join()

    while not que.empty():
        result = que.get()
        data.update(result)

    # send data to group
    channel_layer = get_channel_layer()
    loop = asyncio.new_event_loop()

    asyncio.set_event_loop(loop)

    loop.run_until_complete(channel_layer.group_send("stock_track", {
        'type': 'send_stock_update',
        'message': data,
    }))

    return "***Done***"