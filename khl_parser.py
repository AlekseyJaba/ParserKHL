# @title Импорт библиотек
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import pyparsing as pyp
import pandas as pd
import numpy as np
import time
import matplotlib.pyplot as plt
import seaborn as sns
import re

# from sklearn.preprocessing import MinMaxScaler, StandardScaler, Normalizer
# from sklearn.metrics import roc_auc_score, roc_curve, auc
# from sklearn.model_selection import GridSearchCV, KFold
# from sklearn.linear_model import LogisticRegression
# from sklearn.ensemble import RandomForestClassifier

# from xgboost import XGBClassifier
# from lightgbm import LGBMClassifier
# from catboost import CatBoostClassifier
# import warnings

# 'https://www.khl.ru/calendar/160/00/', 'https://www.khl.ru/calendar/167/00/', 'https://www.khl.ru/calendar/185/00/', 'https://www.khl.ru/calendar/202/00/', 'https://www.khl.ru/calendar/222/00/', 'https://www.khl.ru/calendar/244/00/', 'https://www.khl.ru/calendar/266/00/', 'https://www.khl.ru/calendar/309/00/', 'https://www.khl.ru/calendar/405/00/', 'https://www.khl.ru/calendar/671/00/', 'https://www.khl.ru/calendar/851/00/', 'https://www.khl.ru/calendar/1045/00/', 'https://www.khl.ru/calendar/1097/00/', 'https://www.khl.ru/calendar/1154/00/'
page_links_reg = ['https://www.khl.ru/calendar/160/00/', 'https://www.khl.ru/calendar/167/00/', 'https://www.khl.ru/calendar/185/00/', 'https://www.khl.ru/calendar/202/00/', 'https://www.khl.ru/calendar/222/00/', 'https://www.khl.ru/calendar/244/00/', 'https://www.khl.ru/calendar/266/00/']
page_links_play_off = ['https://www.khl.ru/calendar/165/00/', 'https://www.khl.ru/calendar/168/00/', 'https://www.khl.ru/calendar/186/00/', 'https://www.khl.ru/calendar/203/00/', 'https://www.khl.ru/calendar/223/00/', 'https://www.khl.ru/calendar/245/00/', 'https://www.khl.ru/calendar/267/00/', 'https://www.khl.ru/calendar/310/00/', 'https://www.khl.ru/calendar/406/00/', 'https://www.khl.ru/calendar/472/00/', 'https://www.khl.ru/calendar/674/00/', 'https://www.khl.ru/calendar/854/00/', 'https://www.khl.ru/calendar/1046/00/', 'https://www.khl.ru/calendar/1098/00/', 'https://www.khl.ru/calendar/1155/00/']
page_links_expect = ['https://www.khl.ru/calendar/237/00/', 'https://www.khl.ru/calendar/265/00/']
page_last_link_reg = 'https://www.khl.ru/calendar/1217/00/'
page_last_link_play_off = 'https://www.khl.ru/calendar/1218/00/'

section_names = []
for link in page_links_play_off:
    response = requests.get(link, headers={'User-Agent': UserAgent().chrome})
    soup = BeautifulSoup(response.content, 'html.parser')
    sections = soup.findAll('a', attrs={'class':'card-game__hover-link_small'})

    for i in sections:
        section_names.append(i.attrs['href'])

links = ['https://khl.ru' + element for element in section_names if 'protocol' in element]

#-----------------Фун-ия подключения------------------
def connect(link):
    response = requests.get(link, headers={'User-Agent': UserAgent().chrome})
    while not response.ok:
        time.sleep(15)
        response = requests.get(link, headers={'User-Agent': UserAgent().chrome})
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup

#-----------------Фун-ия парсинга фолов----------------------

def get_stats_foul(id_match, teams, className):
    '''
      на вход получает: id матча, команды, и сласс таблицы (div)
    содержащего информацию о фолах
      на выход список фолов за игру вида [[id_матча, команда, вр. сов. фола, №игрока, игрок, время_штрафа, тип_наруш.], ...]
    '''
    foul_stats = [] #статистика фолов за матч
    global soup_protocol
    for obj in soup_protocol.findAll('div', attrs={'class': className}):
        mass = obj.findAll('p', attrs={'class': 'fineTable-table__line-text'})
        flag = False
        if len(mass) > 4:
            for obj in mass[4:]:
                if obj.contents[0] != '\n':
                    flag = True
                    break
                else:
                    continue
        if className == 'fineTable-table_left':
            foul_team1 = [id_match, teams[0]]
        else:
            foul_team1 = [id_match, teams[1]]
        if flag:
            for obj in mass[4:]:
                con = obj.contents
                if con != ['\n']:
                  if len(con) == 1:
                    a = str(con[0])
                    if a == "\nкомандный штраф":
                        foul_team1.append(int(0))
                    match1 = re.search(r'[0-9][0-9]\:[0-5][0-9]', a)
                    match2 = re.search(r'[0-2][0-9]|[0-9]', a)
                    match3 = re.split(r'\n', a)
                    if match1 is not None:
                        foul_team1.append(match1[0])
                    elif match2 is not None:
                        foul_team1.append(int(match2[0]))
                    else:
                        foul_team1.append(str(match3[1]))
                  else:
                    if len(con) == 3:
                        a = str(con[1])
                        spl = re.split(r'\n', a)
                        match4 = re.search(r'[1-9][0-9]|[0-9]', str(spl[1]))
                        foul_team1.append(int(match4[0]))
                        match5 = re.search(r'[^\d\. ]\D+[^</a>]', str(spl[1]))
                        foul_team1.append(match5[0])
                    elif len(con) < 6:
                        a = str(con[0]) + str(con[2]) + str(con[3])
                        spl = re.split(r'\n', a)
                        match4 = re.search(r'[1-9][0-9]|[0-9]', str(spl[2]))
                        foul_team1.append(int(match4[0]))
                        match5 = re.search(r'[^\d\. ]\D+[^</a>]', str(spl[2]))
                        foul_team1.append(match5[0])
                    else:
                        a = str(con[1])
                        spl = re.split(r'\n', a)
                        match4 = re.search(r'[1-9][0-9]|[0-9]', str(spl[1]))
                        foul_team1.append(int(match4[0]))
                        match5 = re.search(r'[^\d\. ]\D+[^</a>]', str(spl[1]))
                        foul_team1.append(match5[0])
                else:
                    continue
                if len(foul_team1) == 7:
                  foul_stats.append(foul_team1)
                  if className == 'fineTable-table_left':
                      foul_team1 = [id_match, teams[0]]
                  else:
                      foul_team1 = [id_match, teams[1]]
                else:
                  continue
        else:
            foul_stats.append(foul_team1 + [None, None, None, None, None])
    return foul_stats

#-------------------Parsing stat goalkeeper-----------------------------

def get_stat_goalkeeper(id_match, teams, className):
    '''
      на вход получает: id матча, команды, и сласс таблицы (div)
    содержащего информацию о фолах
      на выход список фолов за игру вида [[id_матча, команда, тип_игрока, №, Игрок,
      И, В, П, ИБ, Бр, ПШ, ОБ, %ОБ, КН, Ш, А, И"0", Штр, ВП ], ...]
    '''
    global soup_protocol
    stats_goalkeeper = []
    Mass = soup_protocol.findAll('div', attrs={'class': className})
    k = 0
    for stgk in Mass:
      gk_mass = stgk.findAll('tr')
      for gk in gk_mass[1:]:
          characters = gk.findAll('p')
          number = re.findall(r"[1-9][0-9]|[0-9]", characters[0].contents[0])
          name = re.findall(r">\D+<", str(characters[1].contents[1]))
          if k == 0:
            player = [id_match, teams[0], 'gk', int(number[0]), name[0][1:-1]]
          else:
            player = [id_match, teams[1], 'gk', int(number[0]), name[0][1:-1]]
          for char in characters[2:]:
              if char.contents[0] != '\n':
                  data = re.findall(r"(?<=\n)\S+", char.contents[0])[0]
                  if data == '-':
                    player.append(None)
                  elif re.search(r"[0-9][0-9]|[0-9]:[0-9][0-9]|[0-9]", data) != None:
                    player.append(data)
                  elif re.search(r"\d+\.\d+", data) != None:
                    player.append(float(data))
                  else:
                    player.append(int(data))
              else:
                  player.append(None)
          stats_goalkeeper.append(player)
      k += 1
    return stats_goalkeeper

#-------------------Parsing stat defenders/forward-----------------------------

def get_stat_def_for(id_match, teams, className):
    global soup_protocol
    stats_def_for = []
    Mass = soup_protocol.findAll('div', attrs={'class': className})
    k = 0
    for stdf in Mass:
      df_mass = stdf.findAll('tr')
      for df in df_mass[1:]:
          characters = df.findAll('p')
          number = re.findall(r'[1-9][0-9]|[0-9]', characters[0].contents[0])
          name = re.findall(r'>\D+<', str(characters[1].contents[1]))
          if k <=1:
              if k%2 == 0:
                  player = [id_match, teams[0], 'def', int(number[0]), name[0][1:-1]]
              else:
                  player = [id_match, teams[0], 'for', int(number[0]), name[0][1:-1]]
          else:
              if k%2 == 0:
                  player = [id_match, teams[1], 'def', int(number[0]), name[0][1:-1]]
              else:
                  player = [id_match, teams[1], 'for', int(number[0]), name[0][1:-1]]
          if len(characters) != 38:
              for char in characters[2:-3]:
                  if char.contents[0] != '\n':
                      data = re.search(r'(?<=\n)\S+', char.contents[0])[0]
                      if data == '-':
                        player.append(None)
                      elif re.search(r'[0-9][0-9]|[0-9]:[0-9][0-9]|[0-9]', data) != None:
                        player.append(data)
                      elif re.search(r'\d+\.\d+', data) != None:
                        player.append(float(data))
                      else:
                        player.append(int(data))
                  else:
                      player.append(None)
              player.append(None)
              for char in characters[-3:]:
                  if char.contents[0] == '\n':
                    player.append(None)
                  else:
                    data = re.search(r'(?<=\n)\S+', char.contents[0])[0]
                    player.append(float(data))
              stats_def_for.append(player)
          else:
              # print('------------')
              i = 0
              for char in characters[2:-3]:
                  i += 1
                  if char.contents[0] != '\n':
                      data = re.search(r'(?<=\n)\S+', char.contents[0])[0]
                      if data == '-':
                        player.append(None)
                      elif re.search(r'[0-9][0-9]|[0-9]:[0-9][0-9]|[0-9]', data) != None:
                        player.append(data)
                      elif re.search(r'\d+\.\d+', data) != None:
                        player.append(float(data))
                      else:
                        player.append(int(data))
                  else:
                      player.append(None)
                  if i == 32:
                      player.append(None)
                      player.append(None)
              for char in characters[-3:]:
                  if char.contents[0] == '\n' or char.contents[0] == '\n-':
                    player.append(None)
                  else:
                    data = re.search(r'(?<=\n)\S+', char.contents[0])[0]
                    player.append(float(data))
              stats_def_for.append(player)
      k += 1
    return stats_def_for


#-------------------Start parsing protocol----------------------------
all_match_stats = [] # статистика данных для каждого матча из протокола
data_match = pd.DataFrame(columns=['id_match', 'type_match', 'date', 'teams', 'trener', 'path_g', 'final_point']) # stat match
data_foul = pd.DataFrame(columns=['id_match', 'team', 'time', 'number', 'name', 'foul_time', 'foul_name']) # stat foul
data_gk = pd.DataFrame(columns=['id_match', 'team', 'type', 'number', 'name', 'И', 'В', 'П', 'ИБ', 'Бр', 'ПШ', 'ОБ', '%ОБ', 'КН', 'Ш', 'А', 'И0', 'Штр', 'ВП']) # stat goalkeeper
data_def_for = pd.DataFrame(columns=['id_match', 'team', 'type', 'number', 'name', 'И', 'Ш', 'А', 'О', '+/-', '+', '-', 'Штр', 'ШР', 'ШБ', 'ШМ', 'ШО', 'ШП', 'РБ', 'БВ', '%БВ', 'Вбр', 'ВВбр', '%Вбр', 'ВП', 'См', 'ВПР', 'СмР', 'ВПБ', 'СмБ', 'ВПМ', 'СмМ', 'ВППВ', 'СмПВ', 'СПр', 'БлБ', 'ВВА', 'ОТБ', 'ПХТ', 'ФоП', 'СрС', 'МС', 'ПД'])
all_gk_stats = []
all_def_for_stats = []

for link in links:
    type_match = 'play-off'
    soup_protocol = connect(link) #забираю данные из протокола
    id_match = int(re.findall(r"(\d+)/protocol", link)[0])
    # linelink = 'https://text.khl.ru/text/' + str(id_match) + '.html#play-by-play'
    # soup_line = connect(linelink)
    # line_date = soup_line.findAll('div', attrs={'class':''})
    # print(link,'\n',linelink)
    print(link)
    light_data = soup_protocol.findAll('div', attrs={'class': 'preview-frame summary__preview-frame'})
    if light_data == []:
        continue
    else:
        print('+')
    teams = []
    for string in soup_protocol.findAll('a', attrs={'class': 'preview-frame__club-nameClub'}, limit=2):
      string = string.get_text(strip=True)
      teams.append(string)
    trener = []
    for string in soup_protocol.findAll('p', attrs={'class': 'preview-frame__club-nameTrainer'}, limit=2):
      string = string.get_text(strip=True)
      trener.append(string)

    goals = str(soup_protocol.findAll('div', attrs={'class':'previw-frame__center-value'}))
    goals_path = re.findall(r"([0-9][0-9]|[0-9])\:([0-9][0-9]|[0-9])", goals)
    path_g = []
    final_point = ''
    goal_1team = 0
    goal_2team = 0
    for item in goals_path:
        path_g.append(str(item[0]) + ':' + str(item[1]))
        goal_1team += int(item[0])
        goal_2team += int(item[1])
    final_point = str(goal_1team) + ":" + str(goal_2team)

    date = ""
    for string in soup_protocol.find('div', attrs={'class': 'card-infos__item-info'}).stripped_strings:
        date = string

    pd.set_option('display.max_columns', 50)

    foul_stat = get_stats_foul(id_match, teams, 'fineTable-table_left')

    df = pd.DataFrame(foul_stat, columns=['id_match', 'team', 'time', 'number', 'name', 'foul_time', 'foul_name'])
    data_foul = (data_foul.copy() if df.empty else df.copy() if data_foul.empty else pd.concat([data_foul, df], ignore_index=True))
    foul_stat = get_stats_foul(id_match, teams, 'fineTable-table_right')

    df = pd.DataFrame(foul_stat, columns=['id_match', 'team', 'time', 'number', 'name', 'foul_time', 'foul_name'])
    data_foul = (data_foul.copy() if df.empty else df.copy() if data_foul.empty else pd.concat([data_foul, df], ignore_index=True))

    gk_stats = get_stat_goalkeeper(id_match, teams, 'fine-table_sm')
    df = pd.DataFrame(gk_stats, columns=['id_match', 'team', 'type', 'number', 'name', 'И', 'В', 'П', 'ИБ', 'Бр', 'ПШ', 'ОБ', '%ОБ', 'КН', 'Ш', 'А', 'И0', 'Штр', 'ВП'])
    data_gk = pd.concat([data_gk, df], ignore_index=True)

    def_for_stats = get_stat_def_for(id_match, teams, 'fine-table_lg')
    df = pd.DataFrame(def_for_stats, columns=['id_match', 'team', 'type', 'number', 'name', 'И', 'Ш', 'А', 'О', '+/-', '+', '-', 'Штр', 'ШР', 'ШБ', 'ШМ', 'ШО', 'ШП', 'РБ', 'БВ', '%БВ', 'Вбр', 'ВВбр', '%Вбр', 'ВП', 'См', 'ВПР', 'СмР', 'ВПБ', 'СмБ', 'ВПМ', 'СмМ', 'ВППВ', 'СмПВ', 'СПр', 'БлБ', 'ВВА', 'ОТБ', 'ПХТ', 'ФоП', 'СрС', 'МС', 'ПД'])
    data_def_for = (data_def_for.copy() if df.empty else df.copy() if data_def_for.empty else pd.concat([data_def_for, df], ignore_index=True))


    data_match.loc[len(data_match.index)] = [id_match, type_match, date, teams, trener, path_g, final_point]


pd.set_option('display.max_columns', 50)


print(data_match, '\n=======\n', data_foul, '\n=======\n', data_gk, '\n=======\n', data_def_for)

data_match.to_csv('test_match_stat_22-23', index=False, mode='a', header=False)
data_foul.to_csv('test_foul_stat_22-23', index=False, mode='a', header=False)
data_gk.to_csv('test_gk_stat_22-23', index=False, mode='a', header=False)
data_def_for.to_csv('test_def_for_stat_22-23', index=False, mode='a', header=False)
