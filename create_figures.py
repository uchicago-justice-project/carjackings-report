from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import altair as alt
from altair_theme import theme


def read_carjackings_csv(file_path):
    '''
    '''
    df = pd.read_csv(file_path)
    df.columns = [x.lower().replace(' ', '_') for x in df.columns]
    df['month-year'] = pd.to_datetime(df['incident_date/time']).dt.to_period('M').astype(str)
    df['year'] = pd.to_datetime(df['incident_date/time']).dt.year
    df['recovered'] = np.where(df['recovery_date'].isna(), 'not_recovered', 'recovered')
    for col in ['vehicle_make_descr', 'vehicle_model_descr']:
        df[col] = df[col].str.upper()
    df['make_model'] = df[['vehicle_make_descr', 'vehicle_model_descr']].astype(str).agg(' '.join, axis=1)
    return df

def add_footer_to_plot(chart, footer_text):
	'''
	'''
	return alt.concat(chart).properties(
		title=alt.TitleParams(footer_text,
		baseline='bottom',
		orient='bottom',
     	anchor='start',
     	fontSize=12, 
     	font="Raleway, sans-serif", 
     	fontWeight=200, dy=20)).configure_legend(labelLimit= 0) 

def bar_chart(df, x, y, color):
	'''
	'''
	return alt.Chart(df).mark_bar().encode(
    		x=x,
    		y=y,
    		color=color
		).properties(width=300,height=400)

if __name__=="__main__":

	root = Path().parent.parent.absolute()
	data = root/"data"
	figures = root/"figures"

	alt.data_transformers.disable_max_rows()

	alt.themes.register("alt_theme", theme)
	alt.themes.enable("alt_theme")

	cj_df = read_carjackings_csv(data/"carjackings_raw_data_geocoded.csv")



alt.X('year:O', title='Year')
alt.Y('count', title="Carjackings")
alt.Color('recovered')