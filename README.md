# 🎬 Netflix Data Explorer

An interactive web application to explore the Netflix catalog using Streamlit.  
Filter movies and TV shows by year, country, rating, genre, and search keywords.  
View data through charts, a world map, and a gallery with real posters and trailer links.


🔗 Try it live: [Streamlit Cloud](https://netflix-data-explorer-ji8ejqgext58hpvtpwkmae.streamlit.app/)

## ✨ Features

- **Interactive Filters**: Type, year range, rating, country, genre, and text search.
- **Gallery View**: Browse titles in a Netflix‑style card layout with posters and "Watch Trailer" buttons.
- **Data Visualizations**:
  - Content release trends over time
  - Top 10 producing countries (bar chart)
  - World map of content production
  - Rating distribution
  - Most common genres
  - Movie runtime and TV show seasons histograms
- **Raw Data Preview** with CSV download option.

## 📁 Dataset

The dataset used is the [Netflix Movies and TV Shows](https://www.kaggle.com/datasets/shivamb/netflix-shows) from Kaggle.  
It contains information about titles, directors, cast, countries, release year, rating, duration, and genres.

## 🛠️ Technologies Used

- Python 3.9+
- Streamlit
- Pandas
- Plotly Express
- TMDBv3API (for fetching posters)
