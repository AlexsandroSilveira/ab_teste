import numpy as np
import pandas as pd
from flask import Flask, render_template, redirect, url_for, request

app = Flask( __name__ )

@app.route( '/home' )
def index():
    # get data
    df = pd.read_csv('data_experiment.csv')

    df['no_click'] = df['visit'] - df['click']
    click_array = df.groupby( 'group' ).sum().reset_index()[['click', 'no_click']].T.to_numpy()
    
    # thompson agent
    prob_reward = np.random.beta( click_array[0], click_array[1])

    if np.argmax(prob_reward) == 0:
        return render_template('pagina_azul.html')
    else:
        return render_template('pagina_vermelho.html')

@app.route( '/yes', methods=['POST'])
def yes_event():
    df = pd.read_csv('data_experiment.csv')
    if request.form['yescheckbox'] == 'red':
        visit = 1
        click = 1
        group = 'treatment'
    else:
        visit = 1
        click = 1
        group = 'control'
    
    df_raw = pd.DataFrame( {'click':click, 'visit':visit, 'group':group}, index=[0])
    df = pd.concat([df, df_raw])
    df.to_csv('data_experiment.csv', index=False)
    
    return redirect( url_for('index') )

@app.route( '/no', methods=['POST'])
def no_event():
    df = pd.read_csv('data_experiment.csv')
    if request.form['nocheckbox'] == 'red':
        visit = 1
        click = 0
        group = 'treatment'
    else:
        visit = 1
        click = 0
        group = 'control'
    
    df_raw = pd.DataFrame( {'click':click, 'visit':visit, 'group':group}, index=[0])
    df = pd.concat([df, df_raw])
    df.to_csv('data_experiment.csv', index=False)

    return redirect( url_for('index') )

if __name__ == '__main__':
    app.run()