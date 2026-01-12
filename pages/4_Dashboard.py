import sys
import pandas as pd
import numpy as np
import streamlit as st
import io

import openpyxl, yattag
from openpyxl import load_workbook
from functions_data import get_list
from functions_data import data_player

st.set_page_config(page_title='Dashboard', layout='wide')
st.markdown('# Competition Dashboard')

from menu import menu
menu()

@st.cache_data(ttl=600)
def load_data(sheets_url):
    xlsx_url = sheets_url.replace("/edit#gid=", "/export?format=xlsx&gid=")
    return pd.read_excel(xlsx_url)
df = load_data(st.secrets["matchdata"])
dx = load_data(st.secrets["timeline"])
db = load_data(st.secrets["playersfull"])
gk = load_data(st.secrets["keepers"])
xg = load_data(st.secrets["xgdata"])

from datetime import date
date = date.today().strftime("%Y-%m-%d")
dfx = df.copy()
dfx['Date'] = pd.to_datetime(dfx['Date'])
dfx['Month'] = dfx['Date'].dt.strftime('%B')
dfx = pd.merge(dfx, db, on='Player ID', how='left')

mlist = get_list(df)

try:
    comps, teams, players = st.tabs(['Competitions', 'Team Stats', 'Player Stats'])

    with comps:
      st.write('Hai')
    with teams:
      st.write('Hai')
    with players:
      col1, col2, col3, col4, col5 = st.columns(5)
      with col1:
        season = st.selectbox('Select Season', ['2025-26'], key='1')
        data = dfx.copy()
        team = st.multiselect('Select Teams', pd.unique(data['Team']), key='2')
        all_teams = st.checkbox('Select All Teams', key='3')
        if all_teams:
          team = pd.unique(data['Team'])
      with col2:
        temp = data[data['Team'].isin(team)]
        month = st.multiselect('Select Months', pd.unique(temp['Month']), key='4')
        all_months = st.checkbox('Select All Months', key='5')
        if all_months:
          month = pd.unique(temp['Month'])
        temp = temp[temp['Month'].isin(month)]
        gws = st.multiselect('Select Gameweeks', pd.unique(temp['Gameweek']), key='6')
        all_gws = st.checkbox('Select All Gameweeks', key='7')
        if all_gws:
          gws = pd.unique(temp['Gameweek'])
      with col3:
        temp = temp[temp['Gameweek'].isin(gws)]
        venue = st.multiselect('Select Venues', pd.unique(temp['Home/Away']), key='8')
        temp = temp[temp['Home/Away'].isin(venue)]
        nats = st.multiselect('Select Nationalities', pd.unique(temp['Nat. Status']), key='9')
      with col4:
        temp = temp[temp['Nat. Status'].isin(nats)]
        age_group = st.multiselect('Select Age Groups', pd.unique(temp['Age Group']), key='10')
        temp = temp[temp['Age Group'].isin(age_group)]
        positions = st.multiselect('Select Positions', pd.unique(temp['Position']), key='11')
        all_pos = st.checkbox('Select All Positions', key='12')
        if all_pos:
          positions = pd.unique(temp['Position'])
      with col5:
        temp = temp[temp['Position'].isin(positions)]
        mins = st.number_input('Input minimum mins. played', min_value=0, max_value=3060, step=90, key=13)
        metrik = st.multiselect('Select Metrics', mlist, key='14')
      cat = st.selectbox('Select Category', ['Total', 'per 90'], key='15')
      show_player_data = data_player(dfx, db, team, month, gws, venue,
                                     age_group, nats, positions, mins,
                                     metrik, cat)

      buffer = io.BytesIO()
      with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        show_player_data.to_excel(writer, sheet_name='Sheet1', index=False)
      download = st.download_button(label="Download data as Excel", data=buffer.getvalue(),
                                    file_name='player-data_downloaded ('+date+').xlsx',
                                    mime='application/vnd.ms-excel', key = 16)
      st.write(show_player_data)
except:
    st.write(db)
