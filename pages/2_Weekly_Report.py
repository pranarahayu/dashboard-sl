import sys
import pandas as pd
import numpy as np
import streamlit as st
import io

import openpyxl, yattag
from openpyxl import load_workbook

from functions_plot import create_chart
from functions_plot import goal_plot
from functions_data import standings
from functions_data import get_wdl
from functions_data import standings_chart
from functions_data import goal_func
from functions_data import det_goal
from functions_data import top_act
from functions_data import gendata
from functions_data import findata

st.set_page_config(page_title='Weekly Report', layout='wide')
st.markdown('# Weekly Report')

from menu import menu
menu()

@st.cache_data(ttl=600)
def load_data(sheets_url):
    xlsx_url = sheets_url.replace("/edit#gid=", "/export?format=xlsx&gid=")
    return pd.read_excel(xlsx_url)
df = load_data(st.secrets["matchdata"])
db = load_data(st.secrets["dbase"])
#df2 = load_data(st.secrets["timeline"])

col1, col2 = st.columns(2)
with col1:
    gw = st.selectbox('Select GW', pd.unique(df['Gameweek']), key='2')
    temp = df[df['Gameweek']<=gw].reset_index(drop=True)
with col2:
    teamz = st.multiselect('Select Teams', pd.unique(temp['Team']), key='1')
    all_tms = st.checkbox('Select All Teams', key='3')
if all_tms:
    teamz = temp['Team'].unique().tolist()

datas = findata(temp, db, gw)
stands = standings(temp)
s_chart = standings_chart(temp)
cht = create_chart(teamz, s_chart)
wdl = get_wdl(temp, stands)
gl = goal_func(temp)
gp = goal_plot(gl, gw)
g, og, gav, pg = det_goal(gl, temp)

st.subheader('Weekly Results')
st.write(datas)
st.subheader('Standings #'+str(gw))
st.write(stands)
st.subheader('Week-wise Standings')
st.pyplot(cht)
st.subheader('Weeks-wise Results')
st.write(wdl)
st.subheader('Weeks-wise Goals')
col1, col2, col3, col4= st.columns(4)
with col1:
    st.metric(label="Goals", value=g)
with col2:
    st.metric(label="Own Goals", value=og)
with col3:
    st.metric(label="Penalty Goals", value=pg)
with col4:
    st.metric(label="Goal Average", value=gav)
st.pyplot(gp)

act = st.selectbox('Select Action', ['Goals','Goal','Assist','Create Chance','Tackle','Intercept','Save'], key='4')
tops = top_act(temp, act)
st.write(tops.head(5))
