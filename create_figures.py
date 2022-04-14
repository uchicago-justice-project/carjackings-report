from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import altair as alt
from altair_theme import theme


def read_carjackings_csv(file_path):
    '''
    Read in carjackings data and set up variables used for creating plots
    :param file_path: pathlib.Path of the carjackings csv
    :returns pandas DataFrame of the carjackings data, with additional date and recovered boolean columns
    '''
    df = pd.read_csv(file_path)
    df.columns = [x.lower().replace(' ', '_') for x in df.columns]
    df['month-year'] = pd.to_datetime(df['incident_date/time']).dt.to_period('M').astype(str)
    df['year'] = pd.to_datetime(df['incident_date/time']).dt.year
    df['recovered'] = np.where(df['recovery_date'].isna(), 'Not Recovered', 'Recovered')
    for col in ['vehicle_make_descr', 'vehicle_model_descr']:
        df[col] = df[col].str.upper()
    df['make_model'] = df[['vehicle_make_descr', 'vehicle_model_descr']].astype(str).agg(' '.join, axis=1)
    return df

def get_group_counts(df, group_cols):
	'''
	Helper function to calculate group counts
	:param df: the pandas DataFrame to be grouped
	:param group_cols: list of strings, the columns to group by
	:returns pandas DataFrame of group counts
	'''
	group_counts = df.groupby(group_cols).size().unstack().reset_index()
	group_counts['n_carjackings'] = group_counts['Recovered'] + group_counts['Not Recovered']
	group_counts['proportion_recovered'] = group_counts['Recovered'] / group_counts['n_carjackings']
	return group_counts.fillna(0)


def add_footer_to_plot(chart,
					   footer_text):
	'''
	Helper function to add footer to altair chart
	:param chart: altair chart to add footer to
	:param footer_text: string, the footer text to add to chart
	:returns altair chart with added footer text
	'''
	return alt.concat(chart).properties(
		title=alt.TitleParams(footer_text,
		baseline='bottom',
		orient='bottom',
     	anchor='start',
     	fontSize=12, 
     	font="Raleway, sans-serif", 
     	fontWeight=200, dy=20)).configure_legend(labelLimit= 0) 

def save_chart(chart, 
			   fig_path, 
			   footer_text="Source: Chicago Police Department data, recieved by FOIA request"):
	'''
	Helper chart to save altair chart figure with added footer text
	:param chart: altair chart
	:param fig_path: pathlib.Path for output figure
	:param footer_text: string of footer text
	'''
	add_footer_to_plot(chart, footer_text).save(fig_path)    


if __name__=="__main__":

	root = Path().parent.absolute()
	data = root/"data"
	figures = root/"figures"

	alt.data_transformers.disable_max_rows()

	alt.themes.register("alt_theme", theme)
	alt.themes.enable("alt_theme")

	cj_df = read_carjackings_csv(data/"carjackings_raw_data_geocoded.csv")

	bar_chart = alt.Chart(cj_df).mark_bar().encode(
    				x=alt.X('year:O', title='Year'),
    				y=alt.Y('count()', title="Carjackings"),
    				color=alt.Color('recovered')
				).properties(width=300,height=400)

	save_chart(bar_chart, figures/"carjackings_bar_chart.png")


	line_chart = alt.Chart(get_group_counts(cj_df, ['year', 'recovered'])).mark_line(color="#06063c").encode(
    				x=alt.X('year:O', title='Year'),
    				y=alt.Y('proportion_recovered', title="% of carjacked cars recovered", axis=alt.Axis(format='.0%'), scale=alt.Scale(domain=[0, 1]))
    			).properties(width=500,height=400)

	save_chart(line_chart, figures/"carjackings_line_chart.png")


	month_chart = alt.Chart(get_group_counts(cj_df, ['month-year', 'recovered'])).mark_line(color="#06063c").encode(
    				x=alt.X('month-year:T', title='Month', axis=alt.Axis(format='%b-%Y')),
    				y=alt.Y('proportion_recovered', title="% of carjacked cars recovered", axis=alt.Axis(format='.0%'), scale=alt.Scale(domain=[0, 1]))
    			).properties(width=800,height=300)
	lines = alt.Chart(pd.DataFrame({'month-year': ['2021-01', '2020-04', '2021-03']})).mark_rule(color="#902727").encode(
				x=alt.X('month-year:T', axis=alt.Axis(format='%b-%Y')))

	save_chart((month_chart + lines), figures/"carjackings_monthly_chart.png")



