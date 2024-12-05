import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(layout="wide")

st.markdown(
    """
    <style>
    .main .block-container {
        max-width: 1200px;
        padding-left: 2rem;
        padding-right: 2rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Load your DataFrame
soccer_df = pd.read_csv('soccer_df.csv')

# Filter matches where Manchester United is the home team
home_matches = soccer_df[soccer_df['home_team'] == 'Manchester United']

# Filter matches where Manchester United is the away team
away_matches = soccer_df[soccer_df['away_team'] == 'Manchester United']

# Calculate goals scored by Manchester United as home team
home_matches['man_utd_goals'] = home_matches['home_score']

# Calculate goals scored by Manchester United as away team
away_matches['man_utd_goals'] = away_matches['away_score']

# Calculate goals allowed by Manchester United as home team
home_matches['goals_allowed'] = home_matches['away_score']

# Calculate goals allowed by Manchester United as away team
away_matches['goals_allowed'] = away_matches['home_score']

# Combine home and away matches
man_utd_matches = pd.concat([home_matches, away_matches])

# Determine match results
man_utd_matches['result'] = 'draw'
man_utd_matches.loc[man_utd_matches['home_team'] == 'Manchester United', 'result'] = man_utd_matches.apply(
    lambda row: 'win' if row['home_score'] > row['away_score'] else 'loss' if row['home_score'] < row['away_score'] else 'draw', axis=1)
man_utd_matches.loc[man_utd_matches['away_team'] == 'Manchester United', 'result'] = man_utd_matches.apply(
    lambda row: 'win' if row['away_score'] > row['home_score'] else 'loss' if row['away_score'] < row['home_score'] else 'draw', axis=1)

# Group by year and month and calculate the average goals scored per game
goals_per_game_by_month_year = man_utd_matches.groupby(['year', 'month']).agg(
    total_goals=('man_utd_goals', 'sum'),
    games_played=('man_utd_goals', 'count')
).reset_index()

# Calculate average goals scored per game
goals_per_game_by_month_year['average_goals_per_game'] = goals_per_game_by_month_year['total_goals'] / goals_per_game_by_month_year['games_played']

# Group by year and month and calculate the average goals allowed per game
goals_allowed_per_game_by_month_year = man_utd_matches.groupby(['year', 'month']).agg(
    total_goals_allowed=('goals_allowed', 'sum'),
    games_played=('goals_allowed', 'count')
).reset_index()

# Calculate average goals allowed per game
goals_allowed_per_game_by_month_year['average_goals_allowed_per_game'] = goals_allowed_per_game_by_month_year['total_goals_allowed'] / goals_allowed_per_game_by_month_year['games_played']

# Merge the two DataFrames on year and month
combined_df = pd.merge(goals_per_game_by_month_year[['year', 'month', 'average_goals_per_game']],
                       goals_allowed_per_game_by_month_year[['year', 'month', 'average_goals_allowed_per_game']],
                       on=['year', 'month'])

# Streamlit app
st.title('Manchester United Soccer Insights')

# Sidebar for user selection
tab_selection = st.sidebar.selectbox('Select Tab', ['Main', 'Line Graph', 'Pie Charts'])

if tab_selection == 'Line Graph':
    st.sidebar.header('Filter Options')

    # Section for selecting years
    st.sidebar.subheader('Year(s)')
    selected_years = [year for year in soccer_df['year'].unique() if st.sidebar.checkbox(str(year), value=True)]

    # Section for selecting months
    st.sidebar.subheader('Month(s)')
    selected_months = [month for month in soccer_df['month'].unique() if st.sidebar.checkbox(str(month), value=True)]

    # Filter the combined DataFrame based on user selection
    filtered_df = combined_df[(combined_df['year'].isin(selected_years)) & (combined_df['month'].isin(selected_months))]

    # Create the plot
    fig = go.Figure()

    # Add average goals scored per game
    fig.add_trace(go.Scatter(x=filtered_df['month'].astype(str) + '-' + filtered_df['year'].astype(str),
                             y=filtered_df['average_goals_per_game'],
                             mode='lines+markers',
                             name='Average Goals Scored',
                             line=dict(color='dodgerblue')))

    # Add average goals allowed per game
    fig.add_trace(go.Scatter(x=filtered_df['month'].astype(str) + '-' + filtered_df['year'].astype(str),
                             y=filtered_df['average_goals_allowed_per_game'],
                             mode='lines+markers',
                             name='Average Goals Allowed',
                             line=dict(color='indianred')))

    # Update layout
    fig.update_layout(title='Manchester United Average Goals Scored vs Allowed Per Game by Month and Year',
                      xaxis_title='Month-Year',
                      yaxis_title='Average Goals Per Game',
                      xaxis_tickangle=-45,
                      xaxis=dict(tickmode='linear'),  # Ensure all x-axis labels are shown
                      margin=dict(l=40, r=40, t=40, b=40),  # Adjust margins
                      font=dict(size=12))  # Adjust font size

    # Display the plot
    st.plotly_chart(fig, use_container_width=True)

     # Top 5 highest scoring months in terms of average goals per game
    top_5_highest_scoring_months = combined_df.nlargest(5, 'average_goals_per_game')

    # Create bar chart for top 5 highest scoring months
    fig_bar_highest = px.bar(top_5_highest_scoring_months,
                             x=top_5_highest_scoring_months['month'].astype(str) + '-' + top_5_highest_scoring_months['year'].astype(str),
                             y='average_goals_per_game',
                             labels={'x': 'Month-Year', 'average_goals_per_game': 'Average Goals Per Game'},
                             title='Top 5 Months with Highest Goals Scored (Average Goals Per Game)',
                             color_discrete_sequence=['dodgerblue'])

    # Display the bar chart
    st.plotly_chart(fig_bar_highest)

    # Top 5 months with highest goals allowed
    top_5_highest_goals_allowed = combined_df.nlargest(5, 'average_goals_allowed_per_game')

    # Create bar chart for top 5 months with highest goals allowed
    fig_bar_highest_allowed = px.bar(top_5_highest_goals_allowed,
                                     x=top_5_highest_goals_allowed['month'].astype(str) + '-' + top_5_highest_goals_allowed['year'].astype(str),
                                     y='average_goals_allowed_per_game',
                                     labels={'x': 'Month-Year', 'average_goals_allowed_per_game': 'Average Goals Allowed Per Game'},
                                     title='Top 5 Months with Highest Goals Allowed (Average Goals Allowed Per Game)',
                                     color_discrete_sequence=['indianred'])

    # Display the bar chart
    st.plotly_chart(fig_bar_highest_allowed)

elif tab_selection == 'Main':
    st.subheader('Soccer DataFrame')
    st.dataframe(soccer_df)

    # Convert percentage strings to numeric values
    soccer_df['Ball Possession'] = soccer_df['Ball Possession'].str.rstrip('%').astype('float') / 100.0
    soccer_df['Passes %'] = soccer_df['Passes %'].str.rstrip('%').astype('float') / 100.0


    # Heatmap for correlations
    st.subheader('Correlation Heatmap')
    corr = soccer_df[['home_score', 'away_score', 'Ball Possession', 'Total Shots', 'Shots on Goal', 'Total passes', 'Passes %', 'Points']].corr()
    fig_heatmap = px.imshow(corr, text_auto=True, width=1000, height=750)
    st.plotly_chart(fig_heatmap)

    # Create a box plot to compare expected goals and results
    st.subheader('Expected Goals vs Results')
    fig_box = px.box(man_utd_matches, x='result', y='expected_goals')
    st.plotly_chart(fig_box)

elif tab_selection == 'Pie Charts':
    st.sidebar.header('Filter Options')

    # Section for selecting year range
    selected_year_range = st.sidebar.slider('Select Year Range', 
                                            min_value=int(soccer_df['year'].min()), 
                                            max_value=int(soccer_df['year'].max()), 
                                            value=(int(soccer_df['year'].min()), int(soccer_df['year'].max())))

    # Filter the data based on the selected year range
    filtered_home_matches = man_utd_matches[(man_utd_matches['year'] >= selected_year_range[0]) & (man_utd_matches['year'] <= selected_year_range[1]) & (man_utd_matches['home_team'] == 'Manchester United')]
    filtered_away_matches = man_utd_matches[(man_utd_matches['year'] >= selected_year_range[0]) & (man_utd_matches['year'] <= selected_year_range[1]) & (man_utd_matches['away_team'] == 'Manchester United')]

    # Calculate the proportions of wins, losses, and draws for home matches
    home_result_counts = filtered_home_matches['result'].value_counts()
    home_result_proportions = home_result_counts / home_result_counts.sum()

    # Calculate the proportions of wins, losses, and draws for away matches
    away_result_counts = filtered_away_matches['result'].value_counts()
    away_result_proportions = away_result_counts / away_result_counts.sum()

    # Create the pie chart for home matches
    fig_pie_home = px.pie(values=home_result_proportions, names=home_result_proportions.index, 
                          title=f'Manchester United Home Match Results from {selected_year_range[0]} to {selected_year_range[1]}',
                          width=450, height=450)  # Adjust width and height

    # Create the pie chart for away matches
    fig_pie_away = px.pie(values=away_result_proportions, names=away_result_proportions.index, 
                          title=f'Manchester United Away Match Results from {selected_year_range[0]} to {selected_year_range[1]}',
                          width=450, height=450)  # Adjust width and height

    # Display the pie charts
    st.plotly_chart(fig_pie_home)
    st.plotly_chart(fig_pie_away)