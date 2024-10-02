import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import pandas as pd
import numpy as np
import time
import re

# список url календаря за каждый год
# 'https://www.khl.ru/calendar/160/00/', 'https://www.khl.ru/calendar/167/00/', 'https://www.khl.ru/calendar/185/00/', 'https://www.khl.ru/calendar/202/00/', 'https://www.khl.ru/calendar/222/00/', 'https://www.khl.ru/calendar/244/00/', 'https://www.khl.ru/calendar/266/00/', 'https://www.khl.ru/calendar/309/00/', 'https://www.khl.ru/calendar/405/00/', 'https://www.khl.ru/calendar/671/00/', 'https://www.khl.ru/calendar/851/00/', 'https://www.khl.ru/calendar/1045/00/', 'https://www.khl.ru/calendar/1097/00/', 'https://www.khl.ru/calendar/1154/00/', https://www.khl.ru/calendar/1217/00/

page_links_reg = ['https://www.khl.ru/calendar/1097/00/']
page_links_play_off = ['https://www.khl.ru/calendar/165/00/', 'https://www.khl.ru/calendar/168/00/', 'https://www.khl.ru/calendar/186/00/', 'https://www.khl.ru/calendar/203/00/', 'https://www.khl.ru/calendar/223/00/', 'https://www.khl.ru/calendar/245/00/', 'https://www.khl.ru/calendar/267/00/', 'https://www.khl.ru/calendar/310/00/', 'https://www.khl.ru/calendar/406/00/', 'https://www.khl.ru/calendar/472/00/', 'https://www.khl.ru/calendar/674/00/', 'https://www.khl.ru/calendar/854/00/', 'https://www.khl.ru/calendar/1046/00/', 'https://www.khl.ru/calendar/1098/00/', 'https://www.khl.ru/calendar/1155/00/']
page_links_expect = ['https://www.khl.ru/calendar/237/00/', 'https://www.khl.ru/calendar/265/00/']
page_last_link_reg = 'https://www.khl.ru/calendar/1217/00/'
page_last_link_play_off = 'https://www.khl.ru/calendar/1218/00/'

# собираю url на протокол каждого матча
section_names = []
for link in page_links_reg:
    response = requests.get(link, headers={'User-Agent': UserAgent().chrome})
    soup = BeautifulSoup(response.content, 'html.parser')
    sections = soup.findAll('a', attrs={'class': 'card-game__hover-link_small'})

    for i in sections:
        section_names.append(i.attrs['href'])
links = ['https://khl.ru' + element for element in section_names if 'protocol' in element]


#  -----------------Фун-ия подключения------------------
def connect(link):
    response = requests.get(link, headers={'User-Agent': UserAgent().chrome})
    count = 0
    while not response.ok:
        time.sleep(20)
        response = requests.get(link, headers={'User-Agent': UserAgent().chrome})
        count += 1
        if count == 2:
            break
    if count != 0:
        return None
    count = 0
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup


#  ----------------функция очистки-------------------
def stats_cleaner(data):
    data = [x.strip('\n').strip(' ') for x in data]
    return data


#  ================Получение статистики о матче=======================
def get_stat_match(id_match):
    '''
    input: id матча
    добавляет в data_match инфу о id, типе, дате, командах, тренерах, [p1, p2, overtime, Б], итоговый счёт
    output: команды участники
    '''
    type_match = 'reg'

    teams = []
    for string in soup_protocol.findAll('a', attrs={'class': 'preview-frame__club-nameClub'}, limit=2):
        string = string.get_text(strip=True)
        teams.append(string)

    trener = []
    for string in soup_protocol.findAll('p', attrs={'class': 'preview-frame__club-nameTrainer'}, limit=2):
        string = string.get_text(strip=True)
        trener.append(string)

    date = ""
    for string in soup_protocol.find('div', attrs={'class': 'card-infos__item-info'}).stripped_strings:
        date = string

    goals = str(soup_protocol.findAll('div', attrs={'class': 'previw-frame__center-value'}))
    goals_path = re.findall(r"([0-9][0-9]|[0-9])\:([0-9][0-9]|[0-9])", goals)
    path_g = []
    goal_1team = 0
    goal_2team = 0
    for item in goals_path:
        path_g.append(str(item[0]) + ':' + str(item[1]))
        goal_1team += int(item[0])
        goal_2team += int(item[1])
    final_point = str(goal_1team) + ":" + str(goal_2team)
    data_match.loc[len(data_match.index)] = [id_match, type_match, date, teams, trener, path_g, final_point]
    return teams

#  -----------------Фун-ия парсинга фолов----------------------
def get_stats_foul(id_match, teams, className):

    """
    input: id матча, команды, и имя_класс (div) содержащего информацию о фолах
    output: список фолов за игру вида [[id_матча, команда, вр. сов. фола, №игрока, игрок, время_штрафа, тип_наруш.], ...]
    """

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


#  -------------------Parsing stat goalkeeper-----------------------------
def get_stat_goalkeeper(id_match, teams, className):

    """
     input: id матча, команды, и имя_класса (div) содержащего информацию стат о вратарях
     output: список cстаты вратаря за игру вида [[id_матча, команда, тип_игрока, №, Игрок,
      И, В, П, ИБ, Бр, ПШ, ОБ, %ОБ, КН, Ш, А, И"0", Штр, ВП ], ...]
    """

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


#  -------------------Parsing stat defenders/forward-----------------------------
def get_stat_def_for(id_match, teams, className):

    """
    input: id матча, команды, и имя_класса (div) содержащего информацию стат о защитниках
    output: список cстаты вратаря за игру вида [[много данных)], ...]
    """

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
                  if char.contents[0] == '\n' or char.contents[0] == '\n-':
                    player.append(None)
                  else:
                    data = re.search(r'(?<=\n)\S+', char.contents[0])[0]
                    print(char.contents)
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


#  -------------------Pars step match----------------------
def get_step_match(id, data):
    """
    input: id матча, команды, и имя_класса (div) содержащего информацию стат о защитниках
    output: список cстаты вратаря за игру вида [[много данных)], ...]
    """
    event_list = data.findAll('div', attrs={'class': 'textBroadcast-item__wrap'})
    all_match_event = []
    for item in event_list[1:]:
        event_info = [id]
        time = item.findAll('time', attrs={'class': 'textBroadcast-item__left-time'})
        if len(time) != 0:
            match = re.findall(r"[0-9][0-9]|[0-9]:[0-9][0-9]|[0-9]", str(time[0]))
            if len(match) == 2:
                ev_time = str(match[0]) + ':' + str(match[1])
                event_info.append(ev_time)
            else:
                if len(match) != 0:
                    ev_time = str(match[0]) + ':00'
                    event_info.append(ev_time)
                else:
                    continue
        else:
            continue
        if len(item.findAll('p', attrs={'class': 'textBroadcast-item__right-text'})) != 0:
            if item.find('strong') is not None:
                event = item.find('strong').contents[0]
                match_event = re.search(r"(Удаление)|(Окончание \d периода)|(Изменение счета)", str(event))
                if match_event is not None:
                    event_info.append(match_event.group(0))
                else:
                    continue
                if match_event.group(0) == 'Удаление' or match_event.group(0) == 'Изменение счета':
                    text = item.find('p', attrs={'class': 'textBroadcast-item__right-text'})
                    textall = text.get_text()
                    if match_event.group(0) == 'Удаление':
                        list = textall.split('.')
                        team = re.search(r"\S+", list[1])
                        number = re.search(r"[1-9][0-9]|[1-9]", list[2])
                        part_name = re.findall(r"\S+", list[3])
                        name = part_name[0] + ' ' + part_name[1]
                        # print('=================', '\n', list, '\n', team, number, part_name, name, '\n', '==============')
                        foul = list[4]
                        data = [team.group(0), int(number.group(0)), name, foul, None]
                        event_info += data
                    else:
                        list = textall.split('\n')
                        team = re.search(r"\S+[^\.]", list[2])
                        number = re.search(r"[^\xa0]\d+", list[3])
                        part_name = re.findall(r"\S+", list[3])
                        name = part_name[1] + ' ' + part_name[2]
                        event2 = item.find('p', attrs={'class': 'textBroadcast-item__content-text'}).getText()
                        event2 = event2.replace("\n", "")
                        event2 = event2.replace("В", "")
                        event2 = event2.replace(" ", "")
                        event2 = event2.replace(".", "")
                        # print('!!!!!!!!!', '\n', item, '\n', event2)
                        # print('*********', '\n', list, '\n', '***********')
                        data = [team.group(0), int(number.group(0)), name, None, event2]
                        event_info += data
                        # print(list)
                else:
                    data = [None, None, None, None, None]
                    event_info += data
            else:
                continue
        else:
            continue
        print(event_info)
        all_match_event.append(event_info)
    return all_match_event


#  =======================Pars resume============================
def get_match_resume(id_match, link):
    """
    input: id матча и url
    output: стата из резюме
    """
    stats_resume = []
    print(link)
    soup_resume = connect(link.replace('protocol', 'resume'))
    if soup_resume is not None:
        print(link)
        stats_resume.append(id_match)
        statics_resume = soup_resume.findAll('p', attrs={'class':'roboto-condensed'})[1:21]
        for stat in statics_resume:
            clean_stat = stats_cleaner(stat.contents)
            if clean_stat != [''] and clean_stat != ['n/a'] and clean_stat != ['Всего']:
                stats_resume.append(clean_stat[0])
            elif clean_stat == 'n/a':
                stats_resume.append('')
            else:
                stats_resume.append('')
    return stats_resume


#  ========================Get dop date==========================
def get_dop_date(id_match):
    match_stats = []
    global soup_protocol
    if soup_protocol is not None:
        stat_team = soup_protocol.find('div', attrs={'class': 'fineTable-totalTable-wrapper col9'})
        match_stats = [id_match]
        print(link)
        if stat_team is not None:
            statistics_protocol = stat_team.find('div', attrs={'class': 'fineTable-totalTable d-none_768'})
            dop_stat = statistics_protocol.find('div', attrs={'class': 'fineTable-totalTable__line_blue'})
            dop_date = dop_stat.findAll('p', attrs={'class': 'fineTable-totalTable__line-text'})
            for obj in dop_date:
                clean_stats = stats_cleaner(obj.contents)
                if clean_stats != ['']:
                    match_stats.append(clean_stats[0])
                else:
                    match_stats.append(np.NaN)
    return match_stats


# -------------------Start parsing protocol----------------------------
all_match_stats = []  # статистика данных для каждого матча из протокола
data_match = pd.DataFrame(columns=['id_match', 'type_match', 'date', 'teams', 'trener', 'path_g', 'final_point'])  # stat match
data_foul = pd.DataFrame(columns=['id_match', 'team', 'time', 'number', 'name', 'foul_time', 'foul_name'])  # stat foul
data_gk = pd.DataFrame(columns=['id_match', 'team', 'type', 'number', 'name', 'И', 'В', 'П', 'ИБ', 'Бр', 'ПШ', 'ОБ', '%ОБ', 'КН', 'Ш', 'А', 'И0', 'Штр', 'ВП'])  # stat goalkeeper
data_def_for = pd.DataFrame(columns=['id_match', 'team', 'type', 'number', 'name', 'p', 'w', 'asist', 'point', 'plmi', 'pl', 'mi', 'foul_time', 'equal_point', 'big_point', 'lit_point', 'bul_point', 'win_point', 'bul_match', 'shot', 'per_shot', 'face-off', 'win_face-off', 'per_win_face-off', 'play_time', 'change', 'equal_time', 'change_in_equal', 'bigteam_time', 'change_in_bigteam', 'litteam_time', 'change_in_litteam', 'time_not_gk', 'change_not_gk', 'power_rec', 'block_shot', 'attack_time', 'intercept', 'inter_assist', 'puc_select', 'avg_speed', 'max_speed', 'dist'])
data_step_match = pd.DataFrame(columns=['id_match', 'time', 'event', 'team', 'number', 'player', 'foul', 'sost'])
data_stat_resume = pd.DataFrame(columns=['id_match', 'team_h', 'score_h', 'ppp_h', 'ppp_a', 'ppk_h', 'ppk_a', 'numa_h', 'numa_a', 'wt_h', 'wt_a', 'pt_h', 'pt_a', 'sog_h', 'sog_a', 'dist_h', 'dist_a', 'at_h', 'at_a', 'team_a', 'score_a'])
data_dop_stat = pd.DataFrame(columns=['id_match', 'bs_h', 'pm_h', 't_h', 'at_h', 'tot', 'bs_a', 'pm_a', 't_a', 'at_a'])
all_stats, matches_missing = [], []

print('start')
for link in links[::-1]:

    soup_protocol = connect(link)
    if soup_protocol is not None:
        match1 = re.findall(r"\d+", link)
        id_match = match1[-1]

        teams = get_stat_match(id_match)  # Основная информация о матче + команды
        dop_stat = get_dop_date(id_match)  # Доп. статистика для матча
        if len(dop_stat) < 2:
            continue

        df = pd.DataFrame([dop_stat], columns=['id_match', 'bs_h', 'pm_h', 't_h', 'at_h', 'tot', 'bs_a', 'pm_a', 't_a', 'at_a'])
        data_dop_stat = (data_dop_stat.copy() if df.empty else df.copy() if data_dop_stat.empty else pd.concat([data_dop_stat, df], ignore_index=True))
        print(df)

        stat_resume = get_match_resume(id_match, link)  # Резюме матча
        if len(stat_resume) < 2:
            continue
        df = pd.DataFrame([stat_resume], columns=['id_match', 'team_h', 'score_h', 'ppp_h', 'ppp_a', 'ppk_h', 'ppk_a', 'numa_h', 'numa_a', 'wt_h', 'wt_a', 'pt_h', 'pt_a', 'sog_h', 'sog_a', 'dist_h', 'dist_a', 'at_h', 'at_a', 'team_a', 'score_a'])
        data_stat_resume = (data_stat_resume.copy() if df.empty else df.copy() if data_stat_resume.empty else pd.concat([data_stat_resume, df], ignore_index=True))
        print(df)

        # часть статистики матча в его протоколе
        type_match = 'reg'
        match1 = re.findall(r"\d+", link)
        id_match = match1[-1]

        foul_stat = get_stats_foul(id_match, teams, 'fineTable-table_left')  # df - фолов
        df = pd.DataFrame(foul_stat, columns=['id_match', 'team', 'time', 'number', 'name', 'foul_time', 'foul_name'])
        data_foul = (data_foul.copy() if df.empty else df.copy() if data_foul.empty else pd.concat([data_foul, df], ignore_index=True))

        gk_stats = get_stat_goalkeeper(id_match, teams, 'fine-table_sm')  # df - вратарей
        df = pd.DataFrame(gk_stats, columns=['id_match', 'team', 'type', 'number', 'name', 'И', 'В', 'П', 'ИБ', 'Бр', 'ПШ', 'ОБ', '%ОБ', 'КН', 'Ш', 'А', 'И0', 'Штр', 'ВП'])
        data_gk = pd.concat([data_gk, df], ignore_index=True)

        def_for_stats = get_stat_def_for(id_match, teams, 'fine-table_lg')  # df - защ и нападающих
        df = pd.DataFrame(def_for_stats, columns=['id_match', 'team', 'type', 'number', 'name', 'p', 'w', 'asist', 'point', 'plmi', 'pl', 'mi', 'foul_time', 'equal_point', 'big_point', 'lit_point', 'bul_point', 'win_point', 'bul_match', 'shot', 'per_shot', 'face-off', 'win_face-off', 'per_win_face-off', 'play_time', 'change', 'equal_time', 'change_in_equal', 'bigteam_time', 'change_in_bigteam', 'litteam_time', 'change_in_litteam', 'time_not_gk', 'change_not_gk', 'power_rec', 'block_shot', 'attack_time', 'intercept', 'inter_assist', 'puc_select', 'avg_speed', 'max_speed', 'dist'])
        data_def_for = (data_def_for.copy() if df.empty else df.copy() if data_def_for.empty else pd.concat([data_def_for, df], ignore_index=True))


data = pd.DataFrame(all_stats, columns=['id_match', 'bs_h', 'pm_h', 't_h', 'at_h', 'tot', 'bs_a', 'pm_a', 't_a', 'at_a'])
data_dop_stat.to_csv(r'1097\dop_data.csv', index=False, mode='a', header=True)
data_stat_resume.to_csv(r'1097\data_resume.csv', index=False, mode='a', header=True)
data_match.to_csv(r'1097\new_test_match_stat.csv', index=False, mode='a', header=True)
data_foul.to_csv(r'1097\new_test_foul_stat.csv', index=False, mode='a', header=True)
data_gk.to_csv(r'1097\new_test_gk_stat.csv', index=False, mode='a', header=True)
data_def_for.to_csv(r'1097\new_test_def_for_stat.csv', index=False, mode='a', header=True)

# data_step_match.to_csv('test_data_step_match', index=False, mode='a', header=False)
