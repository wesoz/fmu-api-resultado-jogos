import pandas as pd #Porcessamento de dados 
from flask import Flask, jsonify, request

app = Flask(__name__)

# Ler e monstarar os dados 
results = pd.read_csv('results.csv')

#Transformar as colunas

#Converter a coluna Date, para o um argumeto de tempo e data, em outras palavaras dividir date, para dia, mês e ano
results['date'] = pd.to_datetime(results['date'])

#Criando colunas de dia, mês e ano
results['year'] = results['date'].apply(lambda x : x.year)
results['month'] = results['date'].apply(lambda x: x.month)
results['day'] = results['date'].apply(lambda x: x.day)

#Criando as colunas de vitória, derrota e empate
results['home_team_wins'] = (results['home_score'] - results['away_score']) > 0
results['away_team_wins'] = (results['home_score'] - results['away_score']) < 0 
results['draw'] = (results['home_score'] - results['away_score']) == 0

#Dividindo o so times da casa e visitantes em variaveis com uma lista de valores únicos

#Unique = mostra os valores unicos que estão na base de dados, na sua ordem não em outro formato 

home_teams = results['home_team'].unique()
away_teams = results['away_team'].unique()

#Dividindo os torneios, cidades e paises em variaveis com uma lista de valores unicos

tournaments = results['tournament'].unique()
cities = results['city'].unique()
countries = results['country'].unique()

#Filtrando resultados de duas seleções especificas

def get_results_of_two_countries(results_, country1, country2):
    results_of_two_countries = results.loc[((results.home_team == country1) & (results.away_team == country2))
                                          | ((results.home_team == country2) & (results.away_team == country1)), :]
    return results_of_two_countries

#Filtra os resultados dos confrontos das duas seleções

# print(get_results_of_two_countries(results, 'England', 'Italy'))

#Função que ira retornar as probabildades historicas de vitorias, derrotas e empates entre duas seleções

def get_hist_proba_of_two_countries(results_, country1, country2):
    probas = dict()
    # obtendo resultados dos paises que vão se enfrentar 
    temp = get_results_of_two_countries(results_, country1, country2)
    temp = temp[['home_team', 'away_team', 'home_team_wins', 'away_team_wins',  'draw']]
    temp = temp.groupby(['home_team', 'away_team']).sum()
    
    probas['result'] = {'Win' : 0, 'Loose' : 0, 'Draw' : 0, 'Games' : 0 }
    temp
    
    if len(temp) == 2: # jogos feitos pelas as seleções
        probas['result']['Win'] = temp.loc[(country1, country2)]['home_team_wins'] + temp.loc[(country2, country1)]['away_team_wins']
        probas['result']['Loose'] = temp.loc[(country1, country2)]['away_team_wins'] + temp.loc[(country2, country1)]['home_team_wins']
        probas['result']['Draw'] = temp.loc[(country1, country2)]['draw'] + temp.loc[(country2, country1)]['draw']
        n_games = probas['result']['Win'] + probas['result']['Loose'] + probas['result']['Draw']
        
        if n_games > 0 :
            probas['result']['Win'] = probas['result']['Win']/n_games
            probas['result']['Loose'] = probas['result']['Loose']/n_games
            probas['result']['Draw'] = probas['result']['Draw']/n_games
            probas['result']['Games'] = n_games
            
    
    if len(temp) == 1: # jogos de uma unica seleção 
        if (country1, country2) in temp.index: #Todos os jogos do country1 serão usados como index para o temp
            probas['result']['Win'] = temp.loc[(country1, country2)]['home_team_wins']
            probas['result']['Loose'] = temp.loc[(country1, country2)]['away_team_wins']
            probas['result']['Draw'] = temp.loc[(country1, country2)]['draw']
            n_games = probas['result']['Win'] + probas['result']['Loose'] + probas['result']['Draw']
        
            if n_games > 0 :
                probas['result']['Win'] = probas['result']['Win']/n_games
                probas['result']['Loose'] = probas['result']['Loose']/n_games
                probas['result']['Draw'] = probas['result']['Draw']/n_games
                probas['result']['Games'] = n_games
        
        else: ##Todos os jogos do country2 serão usados como index para o temp
            probas['result']['Win'] = temp.loc[(country2, country1)]['away_team_wins']
            probas['result']['Loose'] = temp.loc[(country2, country1)]['home_team_wins']
            probas['result']['Draw'] = temp.loc[(country2, country1)]['draw']
            n_games = probas['result']['Win'] + probas['result']['Loose'] + probas['result']['Draw']
        
            if n_games > 0 :
                probas['result']['Win'] = probas['result']['Win']/n_games
                probas['result']['Loose'] = probas['result']['Loose']/n_games
                probas['result']['Draw'] = probas['result']['Draw']/n_games
                probas['result']['Games'] = n_games
        
    probas['result']['Games'] = int(probas['result']['Games'])
                                                    
    return probas

@app.route("/")
def healthcheck():
  return "API está online"

@app.route("/resultado")
def getResultado():
  timeA = request.args.get('timea', default = 'Argentina', type = str)
  timeB = request.args.get('timeb', default = 'Brazil', type = str)
  resultado = get_hist_proba_of_two_countries(results, timeA, timeB)
  return jsonify(resultado)


app.run(host='0.0.0.0')