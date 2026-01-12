import os
import pandas as pd
import glob
from datetime import date
import numpy as np

metrik = ['Name','Team','MoP','Non-penalty goals','Non-penalty xG','NPxG/Shot','Shots','Shot on target ratio','Conversion ratio','Chances created','Assists',
          'Passes-to-box','Through passes','Passes to final 3rd','Progressive passes','Long passes','Pass accuracy','Successful crosses',
          'Successful dribbles','Offensive duel won ratio','Tackles','Intercepts','Recoveries','Blocks','Clearances','Aerial duel won ratio',
          'Defensive duel won ratio','Passes','Passes received','Clean sheets','Shots on target faced','xGOT against','Goals conceded','Goals prevented',
          'Save ratio','Sweepers','Crosses claimed']

jamet = ['Name','Team','MoP','Non-penalty goals','Shots','Chances created','Assists','Through passes','Progressive passes',
         'Long passes','Successful crosses','Successful dribbles','Tackles','Intercepts','Recoveries','Blocks','Clearances',
         'Total Pass','Aerial Duels','Offensive Duel','Offensive Duel - Won','Defensive Duel','Defensive Duel - Won','Goal',
         'Shot on','Pass','Aerial Won','Penalty','Passes','Clean sheets','Sweepers','Crosses claimed']

posdict = {'gk':{'position':'Goalkeeper',
                 'metrics':['Name','Passes','Pass accuracy','Long passes','Progressive passes','Passes received','Clean sheets','Shots on target faced',
                            'xGOT against','Goals conceded','Goals prevented','Save ratio','Sweepers','Crosses claimed','Intercepts']},
           'cb':{'position':'Center Back',
                 'metrics':['Name','Non-penalty goals','Shots',
                            'Passes to final 3rd','Progressive passes','Long passes','Pass accuracy',
                            'Tackles','Intercepts','Recoveries','Blocks','Clearances','Aerial duel won ratio','Defensive duel won ratio']},
           'fb':{'position':'Fullback',
                 'metrics':['Name','Non-penalty goals','Non-penalty xG','Shots','Chances created','Assists',
                            'Passes-to-box','Through passes','Passes to final 3rd','Progressive passes','Pass accuracy','Successful dribbles','Successful crosses','Offensive duel won ratio',
                            'Tackles','Intercepts','Recoveries','Blocks','Clearances','Aerial duel won ratio','Defensive duel won ratio']},
           'cm':{'position':'Midfielder',
                 'metrics':['Name','Non-penalty goals','Non-penalty xG','NPxG/Shot','Shots','Shot on target ratio','Chances created','Assists',
                            'Passes-to-box','Through passes','Passes to final 3rd','Progressive passes','Long passes','Pass accuracy','Successful dribbles','Offensive duel won ratio',
                            'Tackles','Intercepts','Recoveries','Clearances','Defensive duel won ratio']},
           'cam/w':{'position':'Attacking 10/Winger',
                    'metrics':['Name','Non-penalty goals','Non-penalty xG','NPxG/Shot','Shots','Shot on target ratio','Conversion ratio','Chances created','Assists',
                               'Passes-to-box','Through passes','Passes to final 3rd','Progressive passes','Pass accuracy','Successful dribbles','Offensive duel won ratio',
                               'Tackles','Intercepts','Recoveries','Defensive duel won ratio']},
           'fw':{'position':'Forward',
                 'metrics':['Name','Non-penalty goals','Non-penalty xG','NPxG/Shot','Shots','Shot on target ratio','Conversion ratio','Chances created','Assists',
                            'Passes-to-box','Through passes','Progressive passes','Pass accuracy','Successful dribbles','Offensive duel won ratio',
                            'Tackles','Intercepts','Recoveries','Aerial duel won ratio','Defensive duel won ratio']}}

def standings(data):
  uk = data.copy()
  uk = uk[['Match', 'Result']]
  uk = uk.groupby(['Match', 'Result'], as_index=False).nunique()

  uk['Home'] = uk['Match'].str.split(' -').str[0]
  uk['Away'] = uk['Match'].str.split('- ').str[1]
  uk['FTHG'] = uk['Result'].str.split(' -').str[0]
  uk['FTAG'] = uk['Result'].str.split('- ').str[1]
  uk['FTHG'] = uk['FTHG'].astype(int)
  uk['FTAG'] = uk['FTAG'].astype(int)

  uk =  uk[['Home', 'Away', 'FTHG', 'FTAG']]

  df_results = uk.copy()
  teams = set(df_results['Home']).union(set(df_results['Away']))
  stats = {team: {'P': 0, 'W': 0, 'D': 0, 'L': 0, 'GF': 0, 'GA': 0, 'Pts': 0} for team in teams}

  def update_stats(team, played, win, draw, loss, gf, ga, pts):
    stats[team]['P'] += played
    stats[team]['W'] += win
    stats[team]['D'] += draw
    stats[team]['L'] += loss
    stats[team]['GF'] += gf
    stats[team]['GA'] += ga
    stats[team]['Pts'] += pts

  for index, row in df_results.iterrows():
    home = row['Home']
    away = row['Away']
    fthg = row['FTHG']
    ftag = row['FTAG']

    if fthg > ftag:
      update_stats(home, 1, 1, 0, 0, fthg, ftag, 3)
      update_stats(away, 1, 0, 0, 1, ftag, fthg, 0)
    elif ftag > fthg:
      update_stats(home, 1, 0, 0, 1, fthg, ftag, 0)
      update_stats(away, 1, 1, 0, 0, ftag, fthg, 3)
    else:
      update_stats(home, 1, 0, 1, 0, fthg, ftag, 1)
      update_stats(away, 1, 0, 1, 0, ftag, fthg, 1)

  df_standings = pd.DataFrame.from_dict(stats, orient='index').reset_index().rename(columns={'index': 'Team'})
  df_standings['GD'] = df_standings['GF'] - df_standings['GA']

  def calculate_h2h_stats(tied_teams, df_all_results):
    h2h_matches = df_all_results[
        (df_all_results['Home'].isin(tied_teams)) &
        (df_all_results['Away'].isin(tied_teams))
    ].copy()

    h2h_stats = {team: {'H2H_Pts': 0, 'H2H_GF': 0, 'H2H_GA': 0} for team in tied_teams}

    for _, row in h2h_matches.iterrows():
        home, away, fthg, ftag = row['Home'], row['Away'], row['FTHG'], row['FTAG']

        pts_home, pts_away = (3, 0) if fthg > ftag else ((0, 3) if ftag > fthg else (1, 1))

        h2h_stats[home]['H2H_Pts'] += pts_home
        h2h_stats[away]['H2H_Pts'] += pts_away

        h2h_stats[home]['H2H_GF'] += fthg
        h2h_stats[home]['H2H_GA'] += ftag
        h2h_stats[away]['H2H_GF'] += ftag
        h2h_stats[away]['H2H_GA'] += fthg

    df_h2h = pd.DataFrame.from_dict(h2h_stats, orient='index').reset_index().rename(columns={'index': 'Team'})
    df_h2h['H2H_GD'] = df_h2h['H2H_GF'] - df_h2h['H2H_GA']
    return df_h2h

  def custom_sort(df_standings, df_all_results):
    df_grouped = df_standings.groupby('Pts')
    sorted_groups = []

    for pts in sorted(df_grouped.groups.keys(), reverse=True):
      group = df_grouped.get_group(pts).copy()

      if len(group) > 1:
        tied_teams = group['Team'].tolist()
        df_h2h = calculate_h2h_stats(tied_teams, df_all_results)

        df_tied = pd.merge(group, df_h2h, on='Team', how='left')

        df_tied_sorted = df_tied.sort_values(by=['H2H_Pts', 'H2H_GD', 'H2H_GF', 'GD', 'GF'], ascending=False)

        sorted_groups.append(df_tied_sorted[df_standings.columns])
      else:
        group_sorted = group.sort_values(by=['GD', 'GF'], ascending=False)
        sorted_groups.append(group_sorted)

    return pd.concat(sorted_groups).reset_index(drop=True)

  df_final_standings = custom_sort(df_standings, df_results)

  df_final_standings = df_final_standings[['Team', 'P', 'W', 'D', 'L', 'GF', 'GA', 'GD', 'Pts']]
  df_final_standings.insert(0, 'Pos', range(1, 1 + len(df_final_standings)))

  return df_final_standings

def standings_chart(data):
  uk = data.copy()
  uk = uk[['Match', 'Result','Gameweek']]
  uk = uk.groupby(['Match', 'Result', 'Gameweek'], as_index=False).nunique()

  uk['Home'] = uk['Match'].str.split(' -').str[0]
  uk['Away'] = uk['Match'].str.split('- ').str[1]
  uk['FTHG'] = uk['Result'].str.split(' -').str[0]
  uk['FTAG'] = uk['Result'].str.split('- ').str[1]
  uk['FTHG'] = uk['FTHG'].astype(int)
  uk['FTAG'] = uk['FTAG'].astype(int)

  uk =  uk[['Home', 'Away', 'FTHG', 'FTAG', 'Gameweek']]

  df_results = uk.copy()
  teams = sorted(list(set(df_results['Home']).union(set(df_results['Away']))))
  max_gameweek = df_results['Gameweek'].max()
  num_teams = len(teams)

  def calculate_h2h_stats(tied_teams, df_all_results):
    h2h_matches = df_all_results[
        (df_all_results['Home'].isin(tied_teams)) &
        (df_all_results['Away'].isin(tied_teams))
        ].copy()

    h2h_stats = {team: {'H2H_Pts': 0, 'H2H_GF': 0, 'H2H_GA': 0} for team in tied_teams}

    for _, row in h2h_matches.iterrows():
      home, away, fthg, ftag = row['Home'], row['Away'], row['FTHG'], row['FTAG']
      pts_home, pts_away = (3, 0) if fthg > ftag else ((0, 3) if ftag > fthg else (1, 1))

      if home in tied_teams:
        h2h_stats[home]['H2H_Pts'] += pts_home
        h2h_stats[home]['H2H_GF'] += fthg
        h2h_stats[home]['H2H_GA'] += ftag
      if away in tied_teams:
        h2h_stats[away]['H2H_Pts'] += pts_away
        h2h_stats[away]['H2H_GF'] += ftag
        h2h_stats[away]['H2H_GA'] += fthg

    df_h2h = pd.DataFrame.from_dict(h2h_stats, orient='index').reset_index().rename(columns={'index': 'Team'})
    df_h2h['H2H_GD'] = df_h2h['H2H_GF'] - df_h2h['H2H_GA']
    return df_h2h

  def custom_sort(df_current_standings, df_matches_so_far):
    df_current_standings['GD'] = df_current_standings['GF'] - df_current_standings['GA']

    df_grouped = df_current_standings.groupby('Pts')
    sorted_groups = []

    for pts in sorted(df_grouped.groups.keys(), reverse=True):
      group = df_grouped.get_group(pts).copy()

      if len(group) > 1:
        tied_teams = group['Team'].tolist()
        df_h2h = calculate_h2h_stats(tied_teams, df_matches_so_far)
        df_tied = pd.merge(group, df_h2h, on='Team', how='left')

        df_tied[['H2H_Pts', 'H2H_GF', 'H2H_GA', 'H2H_GD']] = df_tied[['H2H_Pts', 'H2H_GF', 'H2H_GA', 'H2H_GD']].fillna(0)
        df_tied_sorted = df_tied.sort_values(by=['H2H_Pts', 'H2H_GD', 'H2H_GF', 'GD', 'GF'], ascending=False,kind='mergesort')

        sorted_groups.append(df_tied_sorted[df_current_standings.columns])
      else:
        group_sorted = group.sort_values(by=['GD', 'GF'], ascending=False)
        sorted_groups.append(group_sorted)

    return pd.concat(sorted_groups).reset_index(drop=True)

  position_history = {team: [] for team in teams}
  initial_stats = {team: {'P': 0, 'W': 0, 'D': 0, 'L': 0, 'GF': 0, 'GA': 0, 'Pts': 0} for team in teams}
  df_current_stats = pd.DataFrame.from_dict(initial_stats, orient='index').reset_index().rename(columns={'index': 'Team'})

  for gw in range(1, max_gameweek + 1):
    df_matches_so_far = df_results[df_results['Gameweek'] <= gw]
    gw_stats = {team: {'P': 0, 'W': 0, 'D': 0, 'L': 0, 'GF': 0, 'GA': 0, 'Pts': 0} for team in teams}

    for _, row in df_matches_so_far.iterrows():
      home, away, fthg, ftag = row['Home'], row['Away'], row['FTHG'], row['FTAG']

      if fthg > ftag:
        gw_stats[home]['P'] += 1; gw_stats[home]['W'] += 1; gw_stats[home]['GF'] += fthg; gw_stats[home]['GA'] += ftag; gw_stats[home]['Pts'] += 3
        gw_stats[away]['P'] += 1; gw_stats[away]['L'] += 1; gw_stats[away]['GF'] += ftag; gw_stats[away]['GA'] += fthg
      elif ftag > fthg:
        gw_stats[home]['P'] += 1; gw_stats[home]['L'] += 1; gw_stats[home]['GF'] += fthg; gw_stats[home]['GA'] += ftag
        gw_stats[away]['P'] += 1; gw_stats[away]['W'] += 1; gw_stats[away]['GF'] += ftag; gw_stats[away]['GA'] += fthg; gw_stats[away]['Pts'] += 3
      else:
        gw_stats[home]['P'] += 1; gw_stats[home]['D'] += 1; gw_stats[home]['GF'] += fthg; gw_stats[home]['GA'] += ftag; gw_stats[home]['Pts'] += 1
        gw_stats[away]['P'] += 1; gw_stats[away]['D'] += 1; gw_stats[away]['GF'] += ftag; gw_stats[away]['GA'] += fthg; gw_stats[away]['Pts'] += 1

    df_gw_standings = pd.DataFrame.from_dict(gw_stats, orient='index').reset_index().rename(columns={'index': 'Team'})
    df_gw_standings['GD'] = df_gw_standings['GF'] - df_gw_standings['GA']

    df_ranked_standings = custom_sort(df_gw_standings, df_matches_so_far)
    df_ranked_standings['Pos'] = range(1, num_teams + 1)

    for _, row in df_ranked_standings.iterrows():
      position_history[row['Team']].append(row['Pos'])

  gameweek_index = [f"GW {gw}" for gw in range(1, max_gameweek + 1)]
  df_position_history = pd.DataFrame(position_history, index=gameweek_index)

  df_position_history = df_position_history.T
  latest_gameweek_col = f"GW {max_gameweek}"
  df_position_history = df_position_history.sort_values(by=latest_gameweek_col, ascending=True)
  df_position_history.index.name = 'Team'
  df_position_history.reset_index(inplace=True)

  return df_position_history

def get_radar(data1, data2, data3, pos, player):
  df1 = data1.copy()
  df2 = data2.copy()
  df3 = data3.copy()

  if (pos=='Forward'):
    temp1 = df1[posdict['fw']['metrics']]
    temp2 = df2[posdict['fw']['metrics']]
    temp3 = df3[posdict['fw']['metrics']]
  elif (pos=='Winger') or (pos=='Attacking Midfielder'):
    temp1 = df1[posdict['cam/w']['metrics']]
    temp2 = df2[posdict['cam/w']['metrics']]
    temp3 = df3[posdict['cam/w']['metrics']]
  elif (pos=='Midfielder'):
    temp1 = df1[posdict['cm']['metrics']]
    temp2 = df2[posdict['cm']['metrics']]
    temp3 = df3[posdict['cm']['metrics']]
  elif (pos=='Side Back'):
    temp1 = df1[posdict['fb']['metrics']]
    temp2 = df2[posdict['fb']['metrics']]
    temp3 = df3[posdict['fb']['metrics']]
  elif (pos=='Center Back'):
    temp1 = df1[posdict['cb']['metrics']]
    temp2 = df2[posdict['cb']['metrics']]
    temp3 = df3[posdict['cb']['metrics']]
  elif (pos=='Goalkeeper'):
    temp1 = df1[posdict['gk']['metrics']]
    temp2 = df2[posdict['gk']['metrics']]
    temp3 = df3[posdict['gk']['metrics']]

  auxdata1 = temp1[temp1['Name']==player]
  auxdata2 = temp2[temp2['Name']==player]
  auxdata3 = temp3[temp3['Name']==player]
  auxt1 = auxdata1.transpose().reset_index()
  auxt2 = auxdata2.transpose().reset_index()
  auxt3 = auxdata3.transpose().reset_index()

  new_header = auxt1.iloc[0]
  auxt1 = auxt1[1:].reset_index(drop=True)
  auxt1.columns = new_header
  auxt1 = auxt1.rename(columns={'Name':'Metrics', player:'Percentile'})

  auxt2 = auxt2[1:].reset_index(drop=True)
  auxt2.columns = new_header
  auxt2 = auxt2.rename(columns={'Name':'Metrics', player:'per 90'})

  auxt3 = auxt3[1:].reset_index(drop=True)
  auxt3.columns = new_header
  auxt3 = auxt3.rename(columns={'Name':'Metrics', player:'Total'})

  auxt4 = pd.merge(auxt3, auxt2, on='Metrics', how='left')
  auxt = pd.merge(auxt4, auxt1, on='Metrics', how='left')
  return auxt

def proses_tl(data):
  dfx = data.copy()
  dfx = dfx[dfx['Act Zone'].notna()]
  dfx = dfx[dfx['Pas Zone'].notna()]
  dfx = dfx[['Act Name', 'Action', 'Act Zone', 'Pas Zone']]
  dfx = dfx[(dfx['Action']=='passing')].reset_index(drop=True)

  vv = dfx[dfx['Pas Zone'].str.contains("6B|6C|6D")]
  vv = vv[vv['Act Zone'].str.contains("1|2|3|4|5|6A|6E")].reset_index(drop=True)
  vv = vv[['Act Name','Action']].rename(columns={'Act Name':'Name','Action':'Passes-to-box'})
  vv = vv.groupby(['Name'], as_index=False).count()

  yy = dfx[dfx['Pas Zone'].str.contains("5|6")]
  yy = yy[yy['Act Zone'].str.contains("1|2|3|4")].reset_index(drop=True)
  yy = yy[['Act Name','Action']].rename(columns={'Act Name':'Name','Action':'Passes to final 3rd'})
  yy = yy.groupby(['Name'], as_index=False).count()

  dz = pd.merge(vv, yy, on='Name', how='outer')
  dz.fillna(0, inplace=True)

  return dz

def proses_tl2(data):
  dfx = data.copy()
  dfx = dfx[dfx['Act Zone'].notna()]
  dfx = dfx[dfx['Pas Zone'].notna()]
  dfx = dfx[['Pas Name', 'Action']].rename(columns={'Pas Name':'Name','Action':'Passes received'})
  dfx = dfx[(dfx['Passes received']=='passing')].reset_index(drop=True)
  yy = dfx.groupby(['Name'], as_index=False).count()
  yy.fillna(0, inplace=True)

  return yy

def get_sum90(report, tl, xg, db, gk, min):
  df = report.copy()
  df2 = tl.copy()
  db = db.copy()
  gk = gk.copy()

  dxg = xg.copy()
  dxg = dxg[['Name','xG']]
  dxg = dxg.groupby(['Name'], as_index=False).sum()

  df['Non-penalty goals'] = df['Goal']
  df['Shots'] = df['Shot on']+df['Shot off']+df['Shot Blocked']
  df['Chances created'] = df['Create Chance']
  df['Assists'] = df['Assist']
  df['Through passes'] = df['Pass - Through Pass']
  df['Progressive passes'] = df['Pass - Progressive Pass']
  df['Long passes'] = df['Pass - Long Ball']
  df['Successful crosses'] = df['Cross']
  df['Successful dribbles'] = df['Dribble']
  df['Tackles'] = df['Tackle']
  df['Intercepts'] = df['Intercept']
  df['Recoveries'] = df['Recovery']
  df['Blocks'] = df['Block']+df['Block Cross']
  df['Clearances'] = df['Clearance']
  df['Passes'] = df['Pass']
  df['Clean sheets'] = df['Cleansheet']
  df['Sweepers'] = df['Keeper - Sweeper']
  df['Crosses claimed'] = df['Cross Claim']

  df['Total Pass'] = df['Pass']+df['Pass Fail']
  df['Aerial Duels'] = df['Aerial Won']+df['Aerial Lost']
  df['Offensive Duel - Won'] = df['Offensive Duel - Won']+df['Fouled']+df['Dribble']
  df['Offensive Duel - Lost'] = df['Offensive Duel - Lost']+df['Loose Ball - Tackle']+df['Dribble Fail']
  df['Defensive Duel - Won'] = df['Defensive Duel - Won']+df['Tackle']
  df['Defensive Duel - Lost'] = df['Defensive Duel - Lost']+df['Foul']+df['Dribbled Past']
  df['Offensive Duel'] = df['Offensive Duel - Won']+df['Offensive Duel - Lost']
  df['Defensive Duel'] = df['Defensive Duel - Won']+df['Defensive Duel - Lost']
  df['Penalty'] = df['Penalty Goal']-df['Penalty Missed']

  df_data = df[jamet]
  df_sum = df_data.groupby(['Name','Team'], as_index=False).sum()
  df_sum = pd.merge(df_sum, dxg, on='Name', how='outer')

  df_sum['Non-penalty xG'] = round(df_sum['xG']-(df_sum['Penalty']*0.593469436750998),2)
  df_sum['NPxG/Shot'] = round(df_sum['Non-penalty xG']/(df_sum['Shots']-df_sum['Penalty']),2)
  df_sum['Conversion ratio'] = round(df_sum['Goal']/df_sum['Shots'],2)
  df_sum['Shot on target ratio'] = round(df_sum['Shot on']/df_sum['Shots'],2)
  df_sum['Pass accuracy'] = round(df_sum['Pass']/df_sum['Total Pass'],2)
  df_sum['Aerial duel won ratio'] = round(df_sum['Aerial Won']/df_sum['Aerial Duels'],2)
  df_sum['Offensive duel won ratio'] = round(df_sum['Offensive Duel - Won']/df_sum['Offensive Duel'],2)
  df_sum['Defensive duel won ratio'] = round(df_sum['Defensive Duel - Won']/df_sum['Defensive Duel'],2)

  temp = proses_tl(df2)
  df_sum = pd.merge(df_sum, temp, on='Name', how='outer')

  temp2 = proses_tl2(df2)
  df_sum = pd.merge(df_sum, temp2, on='Name', how='outer')

  gk = gk[['Name','Save','Penalty Save','Total Shots','Goals Conceded',
           'xGOTA','Goals Prevented']]
  gk['Save ratio'] = round((gk['Save']+gk['Penalty Save'])/gk['Total Shots'],2)
  gk['Shots on target faced'] = gk['Total Shots']
  gk['xGOT against'] = gk['xGOTA']
  gk['Goals conceded'] = gk['Goals Conceded']
  gk['Goals prevented'] = gk['Goals Prevented']
  gk = gk[['Name','Save ratio','Shots on target faced','xGOT against','Goals conceded','Goals prevented']]

  df_sum = pd.merge(df_sum, gk, on='Name', how='outer')

  df_sum.replace([np.inf, -np.inf], 0, inplace=True)
  df_sum.fillna(0, inplace=True)

  temp = df_sum.drop(['Name','Team'], axis=1)

  def p90_Calculator(variable_value):
    p90_value = round((((variable_value/temp['MoP']))*90),2)
    return p90_value
  p90 = temp.apply(p90_Calculator)

  p90['Name'] = df_sum['Name']
  p90['Team'] = df_sum['Team']
  p90['MoP'] = df_sum['MoP']
  p90['NPxG/Shot'] = df_sum['NPxG/Shot']
  p90['Conversion ratio'] = df_sum['Conversion ratio']
  p90['Shot on target tatio'] = df_sum['Shot on target ratio']
  p90['Pass accuracy'] = df_sum['Pass accuracy']
  p90['Aerial duel won ratio'] = df_sum['Aerial duel won ratio']
  p90['Offensive duel won ratio'] = df_sum['Offensive duel won ratio']
  p90['Defensive duel won ratio'] = df_sum['Defensive duel won ratio']
  p90['Save ratio'] = df_sum['Save ratio']

  p90 = p90[metrik]
  p90['Name'] = p90['Name'].str.strip()

  pos = db[['Name','Position']]
  data_full = pd.merge(p90, pos, on='Name', how='left')
  data_full = data_full.loc[(data_full['MoP']>=min)].reset_index(drop=True)

  return data_full, df_sum

def get_pct(data):
  data_full = data.copy()
  df4 = data_full.groupby('Position', as_index=False)
  midfielder = df4.get_group('Midfielder')
  goalkeeper = df4.get_group('Goalkeeper')
  forward = df4.get_group('Forward')
  att_10 = df4.get_group('Attacking Midfielder')
  center_back = df4.get_group('Center Back')
  fullback = df4.get_group('Side Back')
  winger = df4.get_group('Winger')

  #calculating the average stats per position
  #winger
  temp = winger.copy()
  winger = winger.drop(['Name','Position','Team'], axis=1)
  winger.loc['mean'] = round((winger.mean()),2)
  winger['Name'] = temp['Name']
  winger['Position'] = temp['Position']
  winger['Team'] = temp['Team']
  values1 = {"Name": 'Average W', "Position": 'Winger', "Team": 'League Average'}
  winger = winger.fillna(value=values1)

  #fb
  temp = fullback.copy()
  fullback = fullback.drop(['Name','Position','Team'], axis=1)
  fullback.loc['mean'] = round((fullback.mean()),2)
  fullback['Name'] = temp['Name']
  fullback['Position'] = temp['Position']
  fullback['Team'] = temp['Team']
  values2 = {"Name": 'Average FB', "Position": 'Side Back', "Team": 'League Average'}
  fullback = fullback.fillna(value=values2)

  #cb
  temp = center_back.copy()
  center_back = center_back.drop(['Name','Position','Team'], axis=1)
  center_back.loc['mean'] = round((center_back.mean()),2)
  center_back['Name'] = temp['Name']
  center_back['Position'] = temp['Position']
  center_back['Team'] = temp['Team']
  values3 = {"Name": 'Average CB', "Position": 'Center Back', "Team": 'League Average'}
  center_back = center_back.fillna(value=values3)

  #cam
  temp = att_10.copy()
  att_10 = att_10.drop(['Name','Position','Team'], axis=1)
  att_10.loc['mean'] = round((att_10.mean()),2)
  att_10['Name'] = temp['Name']
  att_10['Position'] = temp['Position']
  att_10['Team'] = temp['Team']
  values4 = {"Name": 'Average CAM', "Position": 'Attacking Midfielder', "Team": 'League Average'}
  att_10 = att_10.fillna(value=values4)

  #forward
  temp = forward.copy()
  forward = forward.drop(['Name','Position','Team'], axis=1)
  forward.loc['mean'] = round((forward.mean()),2)
  forward['Name'] = temp['Name']
  forward['Position'] = temp['Position']
  forward['Team'] = temp['Team']
  values5 = {"Name": 'Average FW', "Position": 'Forward', "Team": 'League Average'}
  forward = forward.fillna(value=values5)

  #gk
  temp = goalkeeper.copy()
  goalkeeper = goalkeeper.drop(['Name','Position','Team',], axis=1)
  goalkeeper.loc['mean'] = round((goalkeeper.mean()),2)
  goalkeeper['Name'] = temp['Name']
  goalkeeper['Position'] = temp['Position']
  goalkeeper['Team'] = temp['Team']
  values6 = {"Name": 'Average GK', "Position": 'Goalkeeper', "Team": 'League Average'}
  goalkeeper = goalkeeper.fillna(value=values6)

  #cm
  temp = midfielder.copy()
  midfielder = midfielder.drop(['Name','Position','Team'], axis=1)
  midfielder.loc['mean'] = round((midfielder.mean()),2)
  midfielder['Name'] = temp['Name']
  midfielder['Position'] = temp['Position']
  midfielder['Team'] = temp['Team']
  values7 = {"Name": 'Average CM', "Position": 'Midfielder', "Team": 'League Average'}
  midfielder = midfielder.fillna(value=values7)

  #percentile rank
  rank_cm = round(((midfielder.rank(pct=True))*100),0).astype(int)
  rank_gk = round(((goalkeeper.rank(pct=True))*100),0).astype(int)
  rank_fw = round(((forward.rank(pct=True))*100),0).astype(int)
  rank_cam = round(((att_10.rank(pct=True))*100),0).astype(int)
  rank_cb = round(((center_back.rank(pct=True))*100),0).astype(int)
  rank_fb = round(((fullback.rank(pct=True))*100),0).astype(int)
  rank_w = round(((winger.rank(pct=True))*100),0).astype(int)

  #adding Name and Position back
  rank_cm['Name'] = midfielder['Name']
  rank_gk['Name'] = goalkeeper['Name']
  rank_fw['Name'] = forward['Name']
  rank_cam['Name'] = att_10['Name']
  rank_cb['Name'] = center_back['Name']
  rank_fb['Name'] = fullback['Name']
  rank_w['Name'] = winger['Name']

  rank_cm['Position'] = midfielder['Position']
  rank_gk['Position'] = goalkeeper['Position']
  rank_fw['Position'] = forward['Position']
  rank_cam['Position'] = att_10['Position']
  rank_cb['Position'] = center_back['Position']
  rank_fb['Position'] = fullback['Position']
  rank_w['Position'] = winger['Position']

  rank_cm['Team'] = midfielder['Team']
  rank_gk['Team'] = goalkeeper['Team']
  rank_fw['Team'] = forward['Team']
  rank_cam['Team'] = att_10['Team']
  rank_cb['Team'] = center_back['Team']
  rank_fb['Team'] = fullback['Team']
  rank_w['Team'] = winger['Team']

  rank_cm['MoP'] = midfielder['MoP']
  rank_gk['MoP'] = goalkeeper['MoP']
  rank_fw['MoP'] = forward['MoP']
  rank_cam['MoP'] = att_10['MoP']
  rank_cb['MoP'] = center_back['MoP']
  rank_fb['MoP'] = fullback['MoP']
  rank_w['MoP'] = winger['MoP']

  rank_liga = pd.concat([rank_cm, rank_gk, rank_fw, rank_cam, rank_cb, rank_fb, rank_w]).reset_index(drop=True)
  rank_liga['MoP'] = rank_liga['MoP'].astype(int)

  return rank_liga

def get_wdl(data1, data2):
  df = data1.copy()
  temp = data2[['Pos','Team']]

  uk = df[['Team', 'Match', 'Result', 'Gameweek']]
  uk = uk.groupby(['Team', 'Match', 'Result', 'Gameweek'], as_index=False).nunique()

  uk['Home'] = uk['Match'].str.split(' -').str[0]
  uk['Away'] = uk['Match'].str.split('- ').str[1]
  uk['FTHG'] = uk['Result'].str.split(' -').str[0]
  uk['FTAG'] = uk['Result'].str.split('- ').str[1]
  uk['FTHG'] = uk['FTHG'].astype(int)
  uk['FTAG'] = uk['FTAG'].astype(int)
  uk['GW'] = uk['Gameweek']
  uk['Rslt'] = 'S'
  uk['AR'] = 'W'

  for i in range(len(uk)):
    if (uk['FTHG'][i] > uk['FTAG'][i]):
      uk['Rslt'][i] = 'W'
      uk['AR'][i] = 'L'
    elif (uk['FTHG'][i] < uk['FTAG'][i]):
      uk['Rslt'][i] = 'L'
      uk['AR'][i] = 'W'
    else:
      uk['Rslt'][i] = 'D'
      uk['AR'][i] = 'D'

  for i in range(len(uk)):
    if (uk['Home'][i]!=uk['Team'][i]) and (uk['Rslt'][i]=='W'):
      uk['Rslt'][i] = 'L'
    elif (uk['Home'][i]!=uk['Team'][i]) and (uk['Rslt'][i]=='L'):
      uk['Rslt'][i] = 'W'

  uk = uk[['Team', 'GW', 'Rslt']]
  uk = uk.sort_values(by='GW').reset_index(drop=True)

  dx = uk.copy()
  data = pd.DataFrame()
  team = dx['Team'].unique().tolist()
  state = dx['GW'].unique().tolist()
  data['Team'] = team
  for s in state:
    data[s] = 0
  for i in range(len(data)):
    for j in range(len(dx)):
      if (dx['Team'][j] == data['Team'][i]):
        data[dx['GW'][j]][i] = dx['Rslt'][j]

  data = pd.merge(temp, data, on='Team', how='left')
          
  def bg_col(val):
    if val == 'W':
      color = '#7ed957'
    elif val == 'L':
      color = '#d9577e'
    elif val == 'D':
      color = '#a6a6a6'
    else:
      color = 'white'
    return 'background-color: %s' % color
  uk = data.style.applymap(bg_col)

  return uk

def add_og(data):
  df = data.copy()
  dfog = df[['Match', 'Gameweek', 'Team', 'Opponent', 'Own Goal']]
  dfog = dfog.groupby(['Match', 'Gameweek', 'Team', 'Opponent'], as_index=False).sum()
  dfog['Team'] = dfog['Opponent']
  dfog['Goal - Own Goal'] = dfog['Own Goal']
  df_clean = dfog[['Team', 'Gameweek', 'Goal - Own Goal']]
  df_clean = df_clean.groupby(['Team','Gameweek'], as_index=False).sum()
  return df_clean

def goal_func(datas):
  df = datas.copy()
  temp = add_og(df)
  data = df[['Team','Gameweek','Goal','Penalty Goal']]
  data = data.groupby(['Team','Gameweek'], as_index=False).sum()
  data = pd.merge(data, temp, on=['Team','Gameweek'], how='left')
  data = data.fillna(0)
  data['Goals'] = data['Goal']+data['Goal - Own Goal']+data['Penalty Goal']
  data = data[['Gameweek','Goals']]
  data = data.groupby(['Gameweek'], as_index=False).sum()
  return data

def det_goal(data1, data2):
  df1 = data1.copy()
  df2 = data2.copy()
  goal = df1['Goals'].sum()
  og = df2['Own Goal'].sum()
  gavg = round(goal/(df2['Match'].nunique()), 2)
  pg = df2['Penalty Goal'].sum()

  return goal, og, gavg, pg

def top_act(data, aksi):
  df = data.copy()
  df['Goals'] = df['Goal']+df['Penalty Goal']
  df = df[['Name','Team','MoP',aksi]]
  df = df.groupby(['Name','Team'], as_index=False).sum()
  df[aksi+' per 90'] = round(df[aksi]/df['MoP']*90, 2)
  df = df.sort_values(by=[aksi], ascending=False).reset_index(drop=True)
  return df

def gendata(data1, data2):
  #fin = pd.DataFrame()
  #gw_list = gw
  df = data1.copy()
  #df = df[df['Gameweek'].isin(gw)]
  #mac = df['Match'].unique().tolist()
  db = data2.copy()

  st = ['Match','Result','Gameweek','Date','Venue']
  st_data = df[st]
  st_data = st_data.groupby('Match', as_index=False).first()
  st_data['Home Team'] = st_data['Match'].str.split(' - ').str[0]
  st_data['Away Team'] = st_data['Match'].str.split(' - ').str[1]
  st_data['Home Score'] = st_data['Result'].str.split(' - ').str[0]
  st_data['Away Score'] = st_data['Result'].str.split(' - ').str[1]
  st_data['Date'] = pd.to_datetime(st_data['Date'])
  st_data['Match Date'] = st_data['Date'].dt.date
  st_data['KO Time'] = st_data['Date'].dt.time
  st_data['Day'] = st_data['Date'].dt.day_name()
  st_data['Week'] = ''
  for i in range(len(st_data)):
    if st_data['Gameweek'][i] < 10:
      st_data['Week'][i] = 'W-0'+str(st_data['Gameweek'][i])
    else:
      st_data['Week'][i] = 'W-'+str(st_data['Gameweek'][i])
  st_data = st_data[['Match','Home Team','Away Team','Home Score','Away Score','Week','Day','Match Date','KO Time','Venue']].rename(columns={'Match Date':'Date'})

  nu = ['Match','Home/Away','Shot on','Shot off','Shot Blocked','Pass','Pass Fail',
        'Corner','Tackle','Offside','Own Goal','Foul','Yellow Card','Red Card']
  bp = ['Match','Home/Away','Ball Possession']
  bp_data = df[bp]
  nu_data = df[nu]
  nu_data = nu_data.groupby(['Match','Home/Away'], as_index=False).sum()
  bp_data = bp_data.groupby(['Match','Home/Away'], as_index=False).max()

  db = db[['Name','Nationality']]
  da = df[['Match','Home/Away','Name','Starter/Subs']]
  da = da[da['Starter/Subs']=='Starter'].reset_index(drop=True)
  da = pd.merge(da, db, on='Name', how='left')
  da['Status'] = 'Lokal'
  for i in range(len(da)):
    if da['Nationality'][i] != 'Indonesia':
      da['Status'][i] = 'Asing'
  da = da[['Match','Home/Away','Status']]
  da = da[da['Status']=='Asing'].reset_index(drop=True)
  da = da.groupby(['Match','Home/Away'], as_index=False).count()

  nu_data = pd.merge(nu_data, bp_data, on=['Match','Home/Away'], how='left')
  nu_data = pd.merge(nu_data, da, on=['Match','Home/Away'], how='left')

  nu_data['Shots'] = nu_data['Shot on']+nu_data['Shot off']+nu_data['Shot Blocked']
  nu_data['Shot on Target Ratio'] = nu_data['Shot on']/nu_data['Shots']
  hnu_data = nu_data[nu_data['Home/Away']=='Home'].reset_index(drop=True).drop(['Home/Away'], axis=1)
  hnu_data = hnu_data.rename(columns={'Shot on':'Shots on Target - Home','Shots':'Shots - Home','Shot on Target Ratio':'Shot on Target Ratio - Home',
                                      'Ball Possession':'Ball Possession (%) - Home','Pass':'Successful Passes - Home',
                                      'Pass Fail':'Passes Failed - Home','Corner':'Corner Kicks - Home','Tackle':'Successful Tackles - Home',
                                      'Offside':'Offsides - Home','Own Goal':'Own Goals - Home','Foul':'Fouls Commited - Home',
                                      'Yellow Card':'Yellow Cards - Home','Red Card':'Red Cards - Home','Status':'Starter Asing - Home'})

  anu_data = nu_data[nu_data['Home/Away']=='Away'].reset_index(drop=True).drop(['Home/Away'], axis=1)
  anu_data = anu_data.rename(columns={'Shot on':'Shots on Target - Away','Shots':'Shots - Away','Shot on Target Ratio':'Shot on Target Ratio - Away',
                                      'Ball Possession':'Ball Possession (%) - Away','Pass':'Successful Passes - Away',
                                      'Pass Fail':'Passes Failed - Away','Corner':'Corner Kicks - Away','Tackle':'Successful Tackles - Away',
                                      'Offside':'Offsides - Away','Own Goal':'Own Goals - Away','Foul':'Fouls Commited - Away',
                                      'Yellow Card':'Yellow Cards - Away','Red Card':'Red Cards - Away','Status':'Starter Asing - Away'})

  nu_data = pd.merge(hnu_data, anu_data, on=['Match'], how='left')
  metriks = ['Match','Starter Asing - Home','Starter Asing - Away','Shots on Target - Home','Shots on Target - Away','Shots - Home',
             'Shots - Away','Shot on Target Ratio - Home','Shot on Target Ratio - Away',
             'Ball Possession (%) - Home','Ball Possession (%) - Away','Successful Passes - Home','Successful Passes - Away',
             'Passes Failed - Home','Passes Failed - Away','Corner Kicks - Home','Corner Kicks - Away','Successful Tackles - Home',
             'Successful Tackles - Away','Offsides - Home','Offsides - Away','Own Goals - Home','Own Goals - Away','Fouls Commited - Home',
             'Fouls Commited - Away','Yellow Cards - Home','Yellow Cards - Away','Red Cards - Home','Red Cards - Away']
  nu_data = nu_data[metriks]

  datas = pd.merge(st_data, nu_data, on=['Match'], how='left')
  #fin = pd.concat([fin, datas], ignore_index=True)

  return datas

def findata(data1, data2, gw):
  #gw_list = gw
  df = data1.copy()
  db = data2.copy()
  df = df[df['Gameweek']==gw].reset_index(drop=True)
  mac = df['Match'].unique().tolist()
  fin = pd.DataFrame()
  for i in mac:
    data = df[df['Match']==i]
    temp = gendata(data, db)
    fin = pd.concat([fin, temp], ignore_index=True)
  return fin

def get_list(data):
  df = data.copy()
  df['Shots'] = df['Shot on']+df['Shot off']+df['Shot Blocked']
  df['Goals'] = df['Penalty Goal']+df['Goal']
  df['Goals Contribution'] = df['Goals']+df['Assist']
  df['Shots - Inside Box'] = df['Shot on - Inside Box']+df['Shot off - Inside Box']+df['Shot Blocked - Inside Box']
  df['Shots - Outside Box'] = df['Shot on - Outside Box']+df['Shot off - Outside Box']+df['Shot Blocked - Outside Box']
  df['Goals - Inside Box'] = df['Penalty Goal']+df['Goal - Inside Box']
  df['Goals - Open Play'] = df['Goal - Open Play']+df['Goal - Counter Attack']
  df['Goals - Set Pieces'] = df['Goal - Set-Piece Free Kick']+df['Goal - Throw in']+df['Goal - Corner Kick']
  df['Total Pass'] = df['Pass']+df['Pass Fail']
  df['Chances Created'] = df['Key Pass']+df['Assist']
  df['Crosses'] = df['Cross']+df['Cross Fail']
  df['Dribbles'] = df['Dribble']+df['Dribble Fail']
  df['Tackles'] = df['Tackle']+df['Tackle Fail']
  df['Saves'] = df['Save']+df['Penalty Save']
  df['Blocks'] = df['Block']+df['Block Cross']
  df['Aerial Duels'] = df['Aerial Won']+df['Aerial Lost']
  df['Errors'] = df['Error Goal - Error Led to Chance'] + df['Error Goal - Error Led to Goal']
  df['Conversion Ratio'] = round(df['Goals']/df['Shots'],2)
  df['Shot on Target Ratio'] = round(df['Shot on']/df['Shots'],2)
  df['Successful Cross Ratio'] = round(df['Cross']/df['Crosses'],2)
  df['Pass Accuracy'] = round(df['Pass']/df['Total Pass'],2)
  df['Aerial Won Ratio'] = round(df['Aerial Won']/df['Aerial Duels'],2)

  jatuh = ['Player ID','Team','MoP','Goals Contribution','Goals','Assist','Red Card','Yellow Card',
           'Chances Created','Key Pass','Goal','Penalty Goal','Goal - Open Play','Goals - Set Pieces',
           'Goals - Inside Box','Goal - Outside Box','Goal - Left Foot','Goal - Right Foot','Goal - Header',
           'Goal - Other Bodies Part','Shots','Shot on','Shot off','Shot Blocked','Shot on Target Ratio','Conversion Ratio',
           'Total Pass','Pass','Pass Accuracy','Crosses','Cross','Successful Cross Ratio','Dribbles',
           'Tackles','Tackle','Recovery','Clearance','Intercept','Errors','Blocks','Aerial Duels','Aerial Won',
           'Aerial Won Ratio','Foul','Fouled','Saves']

  df = df[jatuh]

  metrik = list(df)
  return metrik

def data_player(data1, data2, team, month, gw, venue, age, nat, pos, mins, metrik, cat):
  df = data1.copy()
  df = pd.merge(df, data2, on='Player ID', how='left')
  db = data2[['Player ID','Nickname']]
  dbx = data2.copy()
  gw_list = gw
  vn_list = venue
  mn_list = month
  ag_list = age
  nt_list = nat
  ps_list = pos
  mt_list = metrik
  tm_list = team

  df = df[df['Team'].isin(tm_list)]
  df = df[df['Home/Away'].isin(vn_list)]
  df = df[df['Gameweek'].isin(gw_list)]
  df = df[df['Month'].isin(mn_list)]
  df = df[df['Age Group'].isin(ag_list)]
  df = df[df['Position'].isin(ps_list)]
  df = df[df['Nat. Status'].isin(nt_list)]

  df['Shots'] = df['Shot on']+df['Shot off']+df['Shot Blocked']
  df['Goals'] = df['Penalty Goal']+df['Goal']
  df['Goals Contribution'] = df['Goals']+df['Assist']
  df['Shots - Inside Box'] = df['Shot on - Inside Box']+df['Shot off - Inside Box']+df['Shot Blocked - Inside Box']
  df['Shots - Outside Box'] = df['Shot on - Outside Box']+df['Shot off - Outside Box']+df['Shot Blocked - Outside Box']
  df['Goals - Inside Box'] = df['Penalty Goal']+df['Goal - Inside Box']
  df['Goals - Open Play'] = df['Goal - Open Play']+df['Goal - Counter Attack']
  df['Goals - Set Pieces'] = df['Goal - Set-Piece Free Kick']+df['Goal - Throw in']+df['Goal - Corner Kick']
  df['Total Pass'] = df['Pass']+df['Pass Fail']
  df['Chances Created'] = df['Key Pass']+df['Assist']
  df['Crosses'] = df['Cross']+df['Cross Fail']
  df['Dribbles'] = df['Dribble']+df['Dribble Fail']
  df['Tackles'] = df['Tackle']+df['Tackle Fail']
  df['Saves'] = df['Save']+df['Penalty Save']
  df['Blocks'] = df['Block']+df['Block Cross']
  df['Aerial Duels'] = df['Aerial Won']+df['Aerial Lost']
  df['Errors'] = df['Error Goal - Error Led to Chance'] + df['Error Goal - Error Led to Goal']

  jatuh = ['No','Team ID','Position (in match)','Gameweek','Opponent','Match','Home/Away','Venue',
           'Date','Result','Starter/Subs','Subs','Player Rating','Ball Possession','Pass Team','Kick In',
           'Fantasy Assist','Fantasy Assist - Penalty','Fantasy Assist - Free kick','Fantasy Assist - Goal by rebound',
           'Fantasy Assist - Own goal by pass/cross','Fantasy Assist - Own goal by rebound','Nationality',
           'Nat. Status','Age Group','Age','DoB','Month','Name_x','Name_y']

  df = df.drop(jatuh, axis=1)
  df = df.groupby(['Player ID','Team'], as_index=False).sum()

  # Ensure all columns to be processed are numeric after groupby.sum()
  for col in df.columns.drop(['Player ID', 'Team']):
      df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

  df['Conversion Ratio'] = round(df['Goals']/df['Shots'],2)
  df['Shot on Target Ratio'] = round(df['Shot on']/df['Shots'],2)
  df['Successful Cross Ratio'] = round(df['Cross']/df['Crosses'],2)
  df['Pass Accuracy'] = round(df['Pass']/df['Total Pass'],2)
  df['Aerial Won Ratio'] = round(df['Aerial Won']/df['Aerial Duels'],2)

  temp = dbx[['Player ID', 'Nickname', 'Age', 'Position', 'Nationality']]
  dfx = pd.merge(df, temp, on='Player ID', how='left')
  #dfx = df.copy()
  datafull = dfx[dfx['MoP'] >= mins].reset_index(drop=True)
  datafull = datafull[mt_list]
  fintot = pd.merge(db, datafull, on='Player ID', how='right')

  df_for_p90 = df[df['MoP'] > 0].reset_index(drop=True)
  mop_series_for_p90 = df_for_p90['MoP']

  def p90_Calculator(variable_value, mop_data):
    p90_value = round(((variable_value/mop_data)*90),2)
    return p90_value

  temp2 = df_for_p90.drop(['Player ID', 'Team'], axis=1)
  p90 = temp2.apply(p90_Calculator, args=(mop_series_for_p90,))
  p90['Player ID'] = df_for_p90['Player ID']
  p90['Team'] = df_for_p90['Team']
  p90['MoP'] = df_for_p90['MoP']
  p90['Conversion Ratio'] = df_for_p90['Conversion Ratio']
  p90['Shot on Target Ratio'] = df_for_p90['Shot on Target Ratio']
  p90['Successful Cross Ratio'] = df_for_p90['Successful Cross Ratio']
  p90['Pass Accuracy'] = df_for_p90['Pass Accuracy']
  p90['Aerial Won Ratio'] = df_for_p90['Aerial Won Ratio']

  p902 = pd.merge(p90, temp, on='Player ID', how='left')
  #p902 = p90.copy()
  data90 = p902[p902['MoP'] >= mins].reset_index(drop=True)
  data90 = data90[mt_list]

  fin90 = pd.merge(db, data90, on='Player ID', how='right')

  if (cat=='per 90'):
    return fin90.drop_duplicates(subset=['Player ID']).reset_index(drop=True)
  elif (cat=='Total'):
    return fintot.drop_duplicates(subset=['Player ID']).reset_index(drop=True)        
