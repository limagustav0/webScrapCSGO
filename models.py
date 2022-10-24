import sqlalchemy
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, Integer, String, Float
from urllib.request import urlopen, urlretrieve, Request
from bs4 import BeautifulSoup
import pandas as pd


url = 'https://www.hltv.org/stats/players?startDate=2022-01-01&endDate=2022-12-31'
headers ={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36"}
req = Request(url,headers=headers)
response = urlopen(req)
html = response.read()
soup = BeautifulSoup(html,'html.parser')


numPlayers = soup.findAll('td',class_='playerCol')
numPlayers1 = range(int(len(numPlayers)))
nomePlayers = soup.find('td',class_='playerCol').getText()
nacionalidade = soup.find_all('td', attrs={'class': 'teamCol'})
mapasJogados = soup.find('td',class_='statsDetail').getText()
rounds = soup.find('td',class_='statsDetail gtSmartphone-only').getText()
killDeathDiff = soup.find('td',class_='kdDiffCol won').getText()
rating = soup.find('td',class_='ratingCol').getText()


Nacionalidade = []
for lista in soup.find_all('td', attrs={'class': 'playerCol'}):
    nacaoPlayer = lista.find("img")['title']
    Nacionalidade.append(nacaoPlayer)


players = []
for c in soup.find_all('td', attrs={'class': 'playerCol'}):
    players.append(c.text)


status = []
for c in soup.find_all('td', attrs={'class': 'statsDetail'}):
    try:
        status.append(int(c.text))
    except:
        status.append(float(c.text))


KD=[]
for c in status:
    if type(c) == float:
        KD.append(c)

for c in KD:
    status.remove(c)

multiplos = [num for num in range(0,len(status)) if num % 2 == 0]

maps=[]
for c in multiplos:
    maps.append(status[c])

for c in maps:
    status.remove(c)

kdiff = []
for c in soup.find_all('td', attrs={'class': 'kdDiffCol'}):
    try:
        kdiff.append(int(c.text[1:]))
    except:
        kdiff.append('sem info')


time = []
for lista in soup.find_all('td', attrs={'class': 'teamCol'}):
    timePlayer = lista.find("img")['title']
    time.append(timePlayer)

rating = []
for lista in soup.find_all('td', attrs={'class': 'ratingCol'}):
    ratingPlayer = float(lista.text)
    rating.append(ratingPlayer)

times_anteriores = []

modelo = soup.find_all('span' , attrs='gtSmartphone-only')

for lista in range(0, len(players)):
    lista_times = []
    for c in modelo[lista]:
        try:
            lista_times.append(c.find("img")['title'])
        except:
            pass
    times_anteriores.append(lista_times)

main_df = pd.DataFrame(list(zip(Nacionalidade,players,time,maps,status,kdiff,KD,rating)),columns=[['Nacionalidade', 'Jogadores', 'Time', 'Maps', 'Rounds', 'KDiff', 'KD', 'Rating']])



# jogadores = []
# for c in range(0,len(players)):
#     dicionario = {}
#     dicionario['id'] = players[c].lower()
#     dicionario['nacionalidade'] = Nacionalidade[c].lower()
#     dicionario['time'] = time[c].lower()
#     dicionario['times_anteriores'] = times_anteriores[c]
#     dicionario['maps'] = maps[c]
#     dicionario['rounds'] = status[c]
#     dicionario['kdiff'] = kdiff[c]
#     dicionario['kd'] = KD[c]
#     dicionario['rating'] = rating[c]
#     jogadores.append(dicionario)



engine = sqlalchemy.create_engine('sqlite:///HLTV.db', echo=True)

Base = declarative_base()

class player_status(Base):
    __tablename__ = 'player_status'
    id_jogador = Column(Integer, primary_key = True)
    Nacionalidade = Column(String(150))
    Jogadores = Column(String(150))
    Time = Column(String(120))
    Maps = Column(String(150))
    Rounds = Column(Integer)
    KDiff = Column(Integer)
    KD = Column(Float)
    Rating = Column(Float)
    
    # def __repr__(self):
    #     return "<player_status{nacionalidade={}, time={}, times_anteriores={}, maps={}, rounds={}, kdiff={}, kd={}, rating={}}>".format(
    #         self.id,self.nacionalidade, self.time, self.maps, self.rounds, self.kdiff, self.kd, self.rating
    #     )
    

Base.metadata.create_all(engine)

main_df.to_sql(con=engine, name=player_status.__tablename__ , index=False, if_exists='append')

Session = sessionmaker(bind=engine)

session = Session()

session.add(player)

session.commit()

query_user = session.query(player_status).filter_by(name='fallen').first()

print(query_user)