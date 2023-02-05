from matplotlib.animation import FuncAnimation
from matplotlib import pyplot as plt
from scipy import stats
import pandas as pd
import numpy as np

def bayesian_inference(data):
    N_mc = 10000
    proba_b_better_a = []
    expected_loss_a = []
    expected_loss_b = []
    for day in range(len(data)):
            
        u_a, var_a = stats.beta.stats( a= 1+ data.loc[day, 'acc_clicks_A'],
                                    b= 1 + (data.loc[day, 'acc_visits_A'] - data.loc[day, 'acc_clicks_A']),
                                    moments= 'mv')

        u_b, var_b = stats.beta.stats( a= 1+ data.loc[day, 'acc_clicks_B'],
                                    b= 1 + (data.loc[day, 'acc_visits_B'] - data.loc[day, 'acc_clicks_B']),
                                    moments= 'mv')

        # Amostras da distribuição normal A
        x_a = np.random.normal( loc = u_a,
                                scale = 1.25*np.sqrt( var_a ),
                                size = N_mc)

        # Amostras da distribuição normal B
        x_b = np.random.normal( loc = u_b,
                                scale = 1.25*np.sqrt( var_b ),
                                size = N_mc)

        #Distribuição beta da página A
        fa = stats.beta.pdf( x_a,
                            a = 1 + data.loc[day, 'acc_clicks_A'],
                            b = 1 + (data.loc[day, 'acc_visits_A'] - data.loc[day, 'acc_clicks_A']))

        #Distribuição beta da página B
        fb = stats.beta.pdf( x_b,
                            a = 1 + data.loc[day, 'acc_clicks_B'],
                            b = 1 + (data.loc[day, 'acc_visits_B'] - data.loc[day, 'acc_clicks_B']))

        #Distribuição normal da página A
        ga = stats.norm.pdf( x_a,
                            loc = u_a,
                            scale = 1.25*np.sqrt(var_a))

        #Distribuição normal da página B
        gb = stats.norm.pdf( x_b,
                            loc = u_b,
                            scale = 1.25*np.sqrt(var_b))

        # Beta/Normal
        y = (fa*fb) / (ga*gb)

        # Somente valores onde o B é maior do que A
        yb = y[x_b >= x_a]

        #probabilidade de B ser melhor que A
        p = ( 1 / N_mc)*np.sum(yb)

        # Erro ao assumir B melhor que A
        expected_loss_A = ( 1/N_mc ) * np.sum(((x_b - x_a)*y)[x_b >= x_a]) 
        expected_loss_B = ( 1/N_mc ) * np.sum(((x_a - x_b)*y)[x_a >= x_b]) 

        proba_b_better_a.append( p )
        expected_loss_a.append(expected_loss_A)
        expected_loss_b.append(expected_loss_B)

    return proba_b_better_a, expected_loss_a, expected_loss_b

def animate(i):
    data = pd.read_csv('../data_experiment.csv')

    #dtypes
    data['click'] = data['click'].astype(int)
    data['visit'] = data['visit'].astype(int)

    # pivot table
    data = data.drop(columns={' '})
    data = data.reset_index().rename(columns={"index": "day"})
    data = data.pivot(index='day', columns='group', values=['click', 'visit']).fillna(0)
    data.columns = ['click_control', 'click_treatment', 'visit_control', 'visit_treatment']
    data = data.reset_index( drop=True )

    data['acc_visits_A'] = np.cumsum(data['visit_control'])
    data['acc_visits_B'] = np.cumsum(data['visit_treatment'])

    data['acc_clicks_A'] = np.cumsum(data['click_control'])
    data['acc_clicks_B'] = np.cumsum(data['click_treatment'])

    #inference bayesion
    proba_b_better_a, expected_loss_a, expected_loss_b = bayesian_inference(data)

    x1 = np.arange( len(proba_b_better_a))
    
    plt.cla()
    plt.plot( x1, proba_b_better_a, label='Probability B better A')
    plt.plot( x1, expected_loss_a, label='Risk choosing A')
    plt.plot( x1, expected_loss_b, label='Risk choosing B')
    plt.legend(loc='upper right')
    plt.tight_layout()



ani = FuncAnimation(plt.gcf(), animate, interval=1000)

plt.tight_layout()
plt.show()