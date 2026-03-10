import streamlit as st
import pandas as pd
import plotly.express as px
from tmdbv3api import TMDb, Movie, TV

st.set_page_config(page_title="Netflix Data Explorer", layout="wide")

# Injecting a custom CSS
st.markdown("""
<style>
    /* Import Poppins font */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
        
    }

    /* Gallery card hover effect */
    .gallery-card {
        transition: transform 0.2s ease;
    }
    .gallery-card:hover {
        transform: scale(1.02);
    }

    /* Main background */
    .stApp {
        background-color: #F8FAFC !important;
    }

    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #1E3A5F !important;
    }
    section[data-testid="stSidebar"] * {
        color: white !important;
    }

    /* Metric cards */
    div[data-testid="stMetric"] {
        background-color: white;
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
    }

    /* Tabs styling */
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: white;
        border-radius: 20px;
        padding: 8px 20px;
        font-weight: 500;
        color: #1E3A5F;
        border: 2px solid #E2E8F0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.03);
        transition: all 0.2s ease;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #F8FAFC;
        border-color: #1E3A5F;
        box-shadow: 0 4px 8px rgba(0,0,0,0.05);
        cursor: pointer;
    }
    .stTabs [aria-selected="true"] {
    background-color: #E50914 !important;
    color: white !important;
    border-color: #E50914 !important;
    }

    /* Headers */
h1, h2, h3 {
    color: #1E3A5F !important;
    font-weight: 600;
}
h1 span.coral {
    color: #E50914 !important;
}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("<h1><span class='coral'>N</span>etflix Data Explorer</h1>", unsafe_allow_html=True)

# Gradient bar
st.markdown("""
<div style="background: linear-gradient(90deg, #1E3A5F 0%, #E50914 100%); 
            height: 4px; 
            border-radius: 2px; 
            margin: 10px 0 20px 0;">
</div>
""", unsafe_allow_html=True)

# Loading the CSV file
df = pd.read_csv("netflix_titles.csv")


# Getting unique values for filters (from the full dataset)
min_year = int(df['release_year'].min())
max_year = int(df['release_year'].max())

# Unique ratings (drop NaN)
all_ratings = sorted(df['rating'].dropna().unique())

# Unique countries (split and flatten)
all_countries = sorted(set(
    country.strip() for sublist in df['country'].dropna().str.split(', ')
    for country in sublist if country.strip()
))

# Unique genres (split and flatten)
all_genres = sorted(set(
    genre.strip() for sublist in df['listed_in'].dropna().str.split(', ') for genre in sublist
))


# Initializing TMDb
tmdb = TMDb()
tmdb.api_key = st.secrets["tmdb_api_key"]
tmdb.language = 'en'
movie_api = Movie()
tv_api = TV()


def get_poster(title, media_type='Movie'):
    """Fetch poster URL for a movie or TV show"""
    try:
        if media_type == 'Movie':
            results = movie_api.search(title)
        else:
            results = tv_api.search(title)

        if results and len(results) > 0:
            poster_path = results[0].poster_path
            if poster_path:
                return f"https://image.tmdb.org/t/p/w500{poster_path}"
    except:
        pass
    return None


# ---- Parse duration columns ----
def parse_duration(row):
    if row['type'] == 'Movie':
        try:
            return int(row['duration'].split()[0])
        except:
            return None
    else:
        return None

def parse_seasons(row):
    if row['type'] == 'TV Show':
        try:
            return int(row['duration'].split()[0])
        except:
            return None
    else:
        return None

df['duration_minutes'] = df.apply(parse_duration, axis=1)
df['duration_seasons'] = df.apply(parse_seasons, axis=1)
# ---------------------------------

# Sidebar filters
st.sidebar.header("Filters")

search_term = st.sidebar.text_input("🔎 Search by title or cast", "")

selected_type = st.sidebar.selectbox(
    "Select content type",
    options=['All', 'Movie', 'TV Show']
)

year_range = st.sidebar.slider(
    "Release year",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year)
)

selected_ratings = st.sidebar.multiselect(
    "Rating",
    options=all_ratings,
    default=[]
)

selected_countries = st.sidebar.multiselect(
    "Country",
    options=all_countries,
    default=[]
)

selected_genres = st.sidebar.multiselect(
    "Genre",
    options=all_genres,
    default=[]
)


# Apply all filters
filtered_df = df.copy()

if search_term:
    mask_title = filtered_df['title'].str.contains(search_term, case=False, na=False)
    mask_cast = filtered_df['cast'].str.contains(search_term, case=False, na=False)
    filtered_df = filtered_df[mask_title | mask_cast]

if selected_type != 'All':
    filtered_df = filtered_df[filtered_df['type'] == selected_type]

filtered_df = filtered_df[
    (filtered_df['release_year'] >= year_range[0]) &
    (filtered_df['release_year'] <= year_range[1])
]

if selected_ratings:
    filtered_df = filtered_df[filtered_df['rating'].isin(selected_ratings)]

if selected_countries:
    # Create mask on the full column, handling NaNs
    country_mask = filtered_df['country'].apply(
        lambda x: False if pd.isna(x) else any(country in x.split(', ') for country in selected_countries)
    )
    filtered_df = filtered_df[country_mask]

if selected_genres:
    genre_mask = filtered_df['listed_in'].apply(
        lambda x: False if pd.isna(x) else any(genre in x.split(', ') for genre in selected_genres)
    )
    filtered_df = filtered_df[genre_mask]

st.sidebar.write(f"Showing **{len(filtered_df)}** titles")


# ----- Create all figures -----
# 1. Release year trend
if not filtered_df.empty:
    year_counts = filtered_df['release_year'].value_counts().sort_index().reset_index()
    year_counts.columns = ['release_year', 'count']
    fig_year = px.line(year_counts, x='release_year', y='count',
                       title='Number of titles released per year')
else:
    fig_year = None

# 2. Top countries
if not filtered_df.empty:
    countries_exploded = filtered_df['country'].dropna().str.split(', ').explode()
    top_countries = countries_exploded.value_counts().head(10).reset_index()
    top_countries.columns = ['country', 'count']
    fig_countries = px.bar(top_countries, x='count', y='country',
                           orientation='h', title='Top 10 Producing Countries',
                           color='count', color_continuous_scale='Reds')
else:
    fig_countries = None

# 3. Ratings distribution
if not filtered_df.empty:
    rating_counts = filtered_df['rating'].value_counts().reset_index()
    rating_counts.columns = ['rating', 'count']
    fig_ratings = px.bar(rating_counts.head(15), x='count', y='rating',
                         orientation='h', title='Top 15 Ratings',
                         color='count', color_continuous_scale='Blues')
else:
    fig_ratings = None

# 4. Top genres
if not filtered_df.empty:
    genres_exploded = filtered_df['listed_in'].dropna().str.split(', ').explode()
    top_genres = genres_exploded.value_counts().head(10).reset_index()
    top_genres.columns = ['genre', 'count']
    fig_genres = px.bar(top_genres, x='count', y='genre',
                        orientation='h', title='Top 10 Genres',
                        color='count', color_continuous_scale='Greens')
else:
    fig_genres = None

# 5. Duration analysis (movies and TV shows)
movie_durs = filtered_df[filtered_df['type'] == 'Movie']['duration_minutes'].dropna()
if not movie_durs.empty:
    fig_movie_dur = px.histogram(movie_durs, nbins=30, title='Movie Runtime (minutes)')
else:
    fig_movie_dur = None

tv_seasons = filtered_df[filtered_df['type'] == 'TV Show']['duration_seasons'].dropna()
if not tv_seasons.empty:
    fig_tv_dur = px.histogram(tv_seasons, nbins=20, title='TV Show Seasons')
else:
    fig_tv_dur = None

# 6. World map of content production
if not filtered_df.empty:
    # Explode countries to handle multiple countries per title
    countries_exploded = filtered_df['country'].dropna().str.split(', ').explode()
    country_counts = countries_exploded.value_counts().reset_index()
    country_counts.columns = ['country', 'count']

    # Create choropleth map
    fig_map = px.choropleth(
        country_counts,
        locations='country',
        locationmode='country names',
        color='count',
        hover_name='country',
        color_continuous_scale='Reds',
        title='Number of titles by country',
        projection='natural earth'
    )
    fig_map.update_layout(margin=dict(l=0, r=0, t=30, b=0))
else:
    fig_map = None



# ----- Tabs layout -----
tab_gallery, tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "🎬 Gallery",
    "📅 Trends",
    "🌍 Countries",
    "🗺️ World Map",
    "🔞 Ratings",
    "🎭 Genres",
    "⏱️ Duration",
    "📋 Raw Data"
])

with tab_gallery:
    st.subheader("🎬 Featured Titles")

    if filtered_df.empty:
        st.info("No titles match your filter.")
    else:
        preview_count = st.slider("Number of previews", 3, 12, 6)
        sample_titles = filtered_df.sample(n=min(preview_count, len(filtered_df)))
        cols = st.columns(3)

        for i, (idx, row) in enumerate(sample_titles.iterrows()):
            with cols[i % 3]:
                # Get poster
                poster_url = get_poster(row['title'], row['type'])

                if poster_url:
                    poster_html = f'<img src="{poster_url}" style="width:100%; border-radius:8px; margin-bottom:10px;">'
                else:
                    poster_html = '<div style="font-size: 3rem; text-align: center;">🎬</div>'

                # YouTube search URL
                search_query = f"{row['title']} trailer"
                youtube_url = f"https://www.youtube.com/results?search_query={search_query.replace(' ', '+')}"

                st.markdown(f"""
                <div class="gallery-card" style="background-color: white; 
                            border-radius: 16px; 
                            padding: 20px; 
                            margin-bottom: 20px;
                            box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
                            border: 1px solid #E2E8F0;">
                    {poster_html}
                    <h4 style="color: #1E3A5F; margin: 10px 0 5px 0;">{row['title']}</h4>
                    <p style="color: #64748B; font-size: 0.9rem; margin-bottom: 10px;">
                        {row['type']} • {row['rating'] if pd.notna(row['rating']) else 'NR'} • {row['release_year']}
                    </p>
                    <p style="color: #475569; font-size: 0.85rem; margin-bottom: 15px;">
                        {row['description'][:120]}...
                    </p>
                    <a href="{youtube_url}" target="_blank" style="
                        background-color: #E50914;
                        color: white;
                        padding: 8px 16px;
                        border-radius: 20px;
                        text-decoration: none;
                        font-size: 0.9rem;
                        font-weight: 500;
                        display: inline-block;
                    ">▶ Watch Trailer</a>
                </div>
                """, unsafe_allow_html=True)

with tab1:
    if fig_year:
        st.plotly_chart(fig_year, width='stretch')
    else:
        st.info("No data available for the selected filters.")

with tab2:
    if fig_countries:
        st.plotly_chart(fig_countries, width='stretch')
    else:
        st.info("No data available for the selected filters.")

with tab3:  # World Map
    if fig_map:
        st.plotly_chart(fig_map, width='stretch')
    else:
        st.info("No data available for the selected filters.")

with tab4:  # Ratings
    if fig_ratings:
        st.plotly_chart(fig_ratings, width='stretch')
    else:
        st.info("No data available for the selected filters.")

with tab5:  # Genres
    if fig_genres:
        st.plotly_chart(fig_genres, width='stretch')
    else:
        st.info("No data available for the selected filters.")


with tab6:  # Duration
    col1, col2 = st.columns(2)
    with col1:
        if fig_movie_dur:
            st.plotly_chart(fig_movie_dur, width='stretch')
        else:
            st.info("No movie data with duration available.")
    with col2:
        if fig_tv_dur:
            st.plotly_chart(fig_tv_dur, width='stretch')
        else:
            st.info("No TV show data with seasons available.")

with tab7:  # Raw Data
    st.subheader("Raw Data Preview")
    st.dataframe(filtered_df.head(100))
    st.write(f"Total rows in filtered data: **{len(filtered_df)}**")

    if not filtered_df.empty:
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download filtered data as CSV",
            data=csv,
            file_name='netflix_filtered.csv',
            mime='text/csv'
        )
    else:
        st.info("No data to download.")