import requests
import pandas as pd
from datetime import datetime
import streamlit as st


def build_country_data(country):
	res = []
	keys = country.get('timeline').get('cases').keys()
	for key in keys:
		target_entry = {}
		target_entry['Report_Date'] = key
		country_name = country.get('country')
		if country.get('province') != None:
			country_name = country_name + '_' + country.get('province')
		target_entry[country_name + '_cases'] = country.get('timeline').get('cases').get(key)
		target_entry[country_name + '_deaths'] = country.get('timeline').get('deaths').get(key)
		target_entry[country_name + '_recovered'] = country.get('timeline').get('recovered').get(key)
		res.append(target_entry)
	return res

@st.cache
def build_covid19_data():
	request_str = 'https://corona.lmao.ninja/v2/historical?lastdays=all'
	response = requests.get(request_str)
	json_data = response.json() if response and response.status_code == 200 else None

	df = None
	for country in json_data:
		res = build_country_data(country)
		if df is None:
			df = pd.DataFrame(res)
			df.index = pd.DatetimeIndex(df['Report_Date'])
			df = df.drop('Report_Date', 1)
			df = df.sort_values(by=['Report_Date'])
		else:
			df_new = pd.DataFrame(res)
			df_new.index = pd.DatetimeIndex(df_new['Report_Date'])
			df_new = df_new.drop('Report_Date', 1)
			df_new = df_new.sort_values(by=['Report_Date'])
			df = df.merge(df_new, left_index=True, right_index=True)

	return df


df = build_covid19_data()
st.title("COVID-19 Visualization")
countries_list = list(set([i.split('_')[0] for i in df.columns]))
countries_list.sort()
select = st.sidebar.selectbox('Country',countries_list)
st.write(select)
df_n = df[[select+'_cases',select+'_recovered',select+'_deaths']]
df_n['active'] = df_n[select+'_cases']-df_n[select+'_recovered']-df_n[select+'_deaths']
df_n['daily'] = df[select+'_cases'].diff()
df_n['death'] = df[select+'_deaths'].diff()
st.dataframe(df_n)


option = st.multiselect('What you want to be plot?',[select+'_cases',select+'_recovered',select+'_deaths','daily','death','active'])
st.line_chart(df_n[option])
