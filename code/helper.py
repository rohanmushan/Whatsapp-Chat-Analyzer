from urlextract import URLExtract
from wordcloud import WordCloud
import pandas as pd
from collections import Counter
import emoji
from pathlib import Path

extract = URLExtract()

def fetch_stats(selected_user,df):
    print(f"DEBUG: fetch_stats called with selected_user={selected_user}")
    print(f"DEBUG: Original df shape: {df.shape}")
    print(f"DEBUG: df columns: {list(df.columns)}")
    print(f"DEBUG: df['user'].unique(): {df['user'].unique()}")
    
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
        print(f"DEBUG: After filtering for {selected_user}, df shape: {df.shape}")

    # fetch the number of messages
    num_messages = df.shape[0]
    print(f"DEBUG: num_messages = {num_messages}")

    # fetch the total number of words
    words = []
    for message in df['message'].astype(str):
        if message:
            words.extend(message.split())
    print(f"DEBUG: words count = {len(words)}")

    # fetch number of media messages
    num_media_messages = df[df['message'] == '<Media omitted>\n'].shape[0]
    print(f"DEBUG: num_media_messages = {num_media_messages}")

    # fetch number of links shared
    links = []
    for message in df['message'].astype(str):
        if message:
            links.extend(extract.find_urls(message))
    print(f"DEBUG: links count = {len(links)}")

    return num_messages,len(words),num_media_messages,len(links)

def most_busy_users(df):
    x = df['user'].value_counts().head()
    df = round((df['user'].value_counts() / df.shape[0]) * 100, 2).reset_index().rename(
        columns={'index': 'name', 'user': 'percent'})
    return x,df

def create_wordcloud(selected_user,df):

    stop_path = Path(__file__).resolve().parent / 'stop_hinglish.txt'
    stop_words_text = stop_path.read_text(encoding='utf-8') if stop_path.exists() else ''
    stop_words = set(w.strip() for w in stop_words_text.splitlines() if w.strip())

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    temp = df[df['user'] != 'group_notification'].copy()
    temp['message'] = temp['message'].astype(str)
    # filter out media/system messages and blanks
    temp = temp[~temp['message'].str.startswith('<Media omitted>')]
    temp = temp[temp['message'].str.strip() != '']

    def remove_stop_words(message):
        cleaned_words = []
        for word in message.lower().split():
            if word not in stop_words:
                cleaned_words.append(word)
        return " ".join(cleaned_words)

    if temp.empty:
        return None

    wc = WordCloud(width=500,height=500,min_font_size=10,background_color='white')
    temp['message'] = temp['message'].apply(remove_stop_words)
    text = temp['message'].str.cat(sep=" ")
    text = text.strip()
    if not text:
        return None
    df_wc = wc.generate(text)
    return df_wc

def most_common_words(selected_user,df):

    stop_path = Path(__file__).resolve().parent / 'stop_hinglish.txt'
    stop_words_text = stop_path.read_text(encoding='utf-8') if stop_path.exists() else ''
    stop_words = set(w.strip() for w in stop_words_text.splitlines() if w.strip())

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    temp = df[df['user'] != 'group_notification'].copy()
    temp['message'] = temp['message'].astype(str)
    temp = temp[~temp['message'].str.startswith('<Media omitted>')]
    temp = temp[temp['message'].str.strip() != '']

    words = []

    for message in temp['message']:
        for word in message.lower().split():
            if word not in stop_words:
                words.append(word)

    if not words:
        return pd.DataFrame(columns=[0,1])

    most_common_df = pd.DataFrame(Counter(words).most_common(20))
    return most_common_df

def emoji_helper(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    emojis = []
    # Support both older and newer emoji packages
    emoji_set = None
    try:
        emoji_set = set(emoji.UNICODE_EMOJI['en'])  # type: ignore[attr-defined]
    except Exception:
        try:
            emoji_set = set(emoji.EMOJI_DATA.keys())  # type: ignore[attr-defined]
        except Exception:
            emoji_set = set()

    for message in df['message'].astype(str):
        if message:
            emojis.extend([c for c in message if c in emoji_set])

    counts = Counter(emojis)
    if not counts:
        return pd.DataFrame(columns=[0,1])

    emoji_df = pd.DataFrame(counts.most_common(len(counts)))

    return emoji_df

def monthly_timeline(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    timeline = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()

    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline['month'][i] + "-" + str(timeline['year'][i]))

    timeline['time'] = time

    return timeline

def daily_timeline(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    daily_timeline = df.groupby('only_date').count()['message'].reset_index()

    return daily_timeline

def week_activity_map(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['day_name'].value_counts()

def month_activity_map(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['month'].value_counts()

def activity_heatmap(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    user_heatmap = df.pivot_table(index='day_name', columns='period', values='message', aggfunc='count').fillna(0)

    return user_heatmap


def time_activity_user_grid(selected_user, df):

    # Filter by selected user when not overall
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    if df.empty:
        return pd.DataFrame(columns=['user', 'day_name', 'hour', 'count'])

    # Define day order for consistent display
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    # Group to counts
    grouped = (
        df.groupby(['user', 'day_name', 'hour'])
          .size()
          .reset_index(name='count')
    )

    # Ensure categorical ordering and hour int
    grouped['day_name'] = pd.Categorical(grouped['day_name'], categories=day_order, ordered=True)
    grouped['hour'] = grouped['hour'].astype(int)

    # Fill missing day-hour combinations per user with zeros
    users = grouped['user'].unique()
    full_index = (
        pd.MultiIndex.from_product(
            [users, day_order, list(range(24))], names=['user', 'day_name', 'hour']
        )
    )
    grouped = grouped.set_index(['user', 'day_name', 'hour']).reindex(full_index, fill_value=0).reset_index()

    return grouped















