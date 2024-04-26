import pandas as pd
import streamlit as st
from PIL import Image

import folium
from streamlit_folium import folium_static

image = Image.open('airbnb_landscape.png')

@st.cache_data
def get_data():
    url = 'https://cis102.guihang.org/data/AB_NYC_2019.csv'
    return pd.read_csv(url)
df = get_data()

df = df.rename(columns = {'name' : 'Info',
                           'host_name' : 'Host Name',
                           'neighbourhood_group' : 'Borough',
                           'neighbourhood' : 'Neighbourhood',
                           'room_type' : 'Room Type',
                           'number_of_reviews' : 'Number of Reviews'})

df['Price'] = '$' + df['price'].astype(str)



st.image(image, use_column_width='auto')

st.header('Check Out Our Listings: ')



cols = ['Price', 'Info', 'Borough', 'Neighbourhood', 'Room Type', 'Host Name']
selected_columns = st.multiselect("", df.columns.tolist(), default=cols)

st.dataframe(df[selected_columns].head(10))

st.write('---')

st.subheader('Or Browse Our Selection: ')

boroughs = df['Borough'].unique()
selected_borough = st.selectbox('Select a Borough: ', boroughs)

borough_df = df[df['Borough'] == selected_borough]

neighbourhoods = borough_df['Neighbourhood'].unique()
selected_neighbourhoods_multi = st.multiselect('Select Neighbourhood(s): ', neighbourhoods)

if selected_neighbourhoods_multi:
    final_df = borough_df[borough_df['Neighbourhood'].isin(selected_neighbourhoods_multi)]
else:
    final_df = borough_df


min_price = int(final_df['price'].min())
max_price = int(final_df['price'].max())

value_slider = st.slider(
    "Price range: ",
    min_value = min_price,
    max_value = max_price,
    value = (min_price, max_price),
    format = '$%.2f'
)

price_filtered_df = final_df[(final_df['price'] >= value_slider[0]) & (final_df['price'] <= value_slider[1])]
st.dataframe(price_filtered_df[selected_columns].head(10))

num = len(price_filtered_df)

selected_neighbourhoods_str = ', '.join(selected_neighbourhoods_multi)

st.write(f'There are a total of  {num} rentals found in {selected_neighbourhoods_str} {selected_borough}'
         f' priced between \${value_slider[0]:,.2f} and \${value_slider[1]:,.2f}.')

st.write('---')

start_location = price_filtered_df[['latitude', 'longitude']].mean().to_list()
bnb_map = folium.Map(location = start_location, zoom_start = 12)

entries = min(50, len(price_filtered_df))

for i in range (entries):
    entry = price_filtered_df.iloc[i]
    folium.Marker(
        [entry['latitude'], entry['longitude']],
        popup=f"Host Name: {entry['Host Name']} <br><br>Neighbourhood: {entry['Neighbourhood']} <br><br>Room Type: {entry['Room Type']} <br><br>Info: {entry['Info']} <br><br> Price: ${entry['price']}",
        tooltip=f"Price: ${entry['price']}"
    ).add_to(bnb_map)

folium_static(bnb_map)
