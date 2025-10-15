import streamlit as st
import preprocessor,helper
import matplotlib.pyplot as plt
import seaborn as sns

# Page config and global styles
st.set_page_config(page_title="WhatsApp Chat Analyzer", page_icon="🗨️", layout="wide")

# Top bar: Dark mode toggle (with icon)
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = True

top_left, top_spacer, top_right = st.columns([0.6, 0.25, 0.15])
with top_right:
    toggle_label = "Light Mode" if st.session_state.dark_mode else "Dark Mode"
    st.toggle(toggle_label, key="dark_mode", label_visibility="visible")

# Compute theme variables from toggle
is_dark = bool(st.session_state.dark_mode)
bg = "#0b1220" if is_dark else "#ffffff"
panel = "#111827" if is_dark else "#f8fafc"
panel2 = "#1f2937" if is_dark else "#eef2ff"
text = "#e2e8f0" if is_dark else "#0f172a"
muted = "#94a3b8" if is_dark else "#475569"

st.markdown(
    f"""
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
      @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');
      
      :root {{ 
        --bg: {bg}; 
        --panel: {panel}; 
        --panel-2: {panel2}; 
        --text: {text}; 
        --muted: {muted}; 
        --gradient1: linear-gradient(135deg, #7c3aed 0%, #2563eb 100%);
        --gradient2: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        --gradient3: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        --gradient4: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        --shadow: 0 20px 40px rgba(0,0,0,0.1);
        --shadow-lg: 0 25px 50px rgba(0,0,0,0.15);
      }}

      /* Global Styles */
      .stApp {{ 
        background: var(--bg);
        background-image: radial-gradient(circle at 20% 80%, rgba(120, 119, 198, 0.3) 0%, transparent 50%),
                         radial-gradient(circle at 80% 20%, rgba(255, 119, 198, 0.3) 0%, transparent 50%),
                         radial-gradient(circle at 40% 40%, rgba(120, 219, 255, 0.2) 0%, transparent 50%);
      }}
      
      html, body, [class*="css"] {{
        font-family: 'Poppins', 'Inter', ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial !important;
        font-size: 15px;
        line-height: 1.6;
      }}

      /* Toggle visibility and sizing */
      .stToggle label {{
        color: var(--text) !important;
        font-weight: 600;
        font-size: 1.6rem;
      }}
      .stToggle [data-baseweb="switch"] {{
        transform: scale(3.0);
        transform-origin: right center;
      }}
      /* Switch track (unchecked) */
      .stToggle [data-baseweb="switch"] > div {{
        background: var(--panel-2) !important;
        border: 1px solid rgba(0,0,0,0.15);
      }}
      /* Switch track (checked) */
      .stToggle [data-baseweb="switch"][aria-checked="true"] > div {{
        background: var(--gradient1) !important;
        border-color: transparent;
      }}
      /* Knob */
      .stToggle [data-baseweb="switch"] > div > div {{
        background: #ffffff !important;
      }}
      
      h1, h2, h3, h4, h5, h6 {{ 
        color: var(--text) !important; 
        font-weight: 700;
        letter-spacing: -0.025em;
      }}
      
      p, .stMarkdown, .stText, .stCaption, .stSelectbox, .stFileUploader {{ 
        color: var(--text) !important; 
      }}

      /* Enhanced Buttons */
      .stButton>button {{
        background: var(--gradient1);
        color: #fff;
        border: 0;
        border-radius: 12px;
        padding: 12px 24px;
        font-weight: 600;
        font-size: 14px;
        
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
      }}
      
      
      
      .stButton>button:hover {{
        
      }}
      
      .stButton>button:hover:before {{
        left: 100%;
      }}

      /* Enhanced Metric Cards */
      .metric-card {{
        padding: 24px 20px;
        border-radius: 20px;
        background: linear-gradient(135deg, var(--panel) 0%, var(--panel-2) 100%);
        border: 1px solid rgba(255,255,255,0.1);
        
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
      }}
      
      .metric-card:before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: var(--gradient1);
      }}
      
      .metric-card:hover {{
        border-color: rgba(255,255,255,0.2);
      }}
      
      .metric-label {{
        color: var(--muted);
        font-size: 0.85rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
      }}
      
      .metric-value {{
        color: var(--text);
        font-size: 2.2rem;
        font-weight: 800;
        line-height: 1;
      }}
      
      .metric-icon {{
        font-size: 1.2rem;
        margin-right: 8px;
      }}

      /* Enhanced Section Headers */
      .section-title {{
        margin: 16px 0 24px 0;
        padding: 16px 24px;
        border-radius: 16px;
        background: var(--gradient1);
        color: #ffffff;
        display: inline-block;
        font-weight: 700;
        font-size: 1.1rem;
        position: relative;
        overflow: hidden;
      }}
      
      

      /* Enhanced Hero Card */
      .hero-card {{
        background: linear-gradient(135deg, var(--panel) 0%, var(--panel-2) 100%);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 24px;
        padding: 32px;
        
        position: relative;
        overflow: hidden;
        
      }}
      
      
      
      .hero-title {{
        color: var(--text);
        font-size: 2.2rem;
        font-weight: 800;
        margin-bottom: 12px;
        position: relative;
        z-index: 1;
      }}
      
      .hero-sub {{
        color: var(--muted);
        font-size: 1.1rem;
        margin-bottom: 20px;
        position: relative;
        z-index: 1;
      }}

      /* Enhanced Tabs */
      .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
        background: rgba(255,255,255,0.05);
        padding: 8px;
        border-radius: 16px;
        
      }}
      
      .stTabs [data-baseweb="tab"] {{
        background: transparent;
        border: 1px solid rgba(255,255,255,0.1);
        color: var(--text);
        padding: 12px 20px;
        border-radius: 12px;
        font-weight: 600;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
      }}
      
      .stTabs [aria-selected="true"] {{
        background: var(--gradient1);
        color: #ffffff;
        border-color: transparent;
        transform: translateY(-2px);
      }}

      /* Enhanced Empty State */
      .empty-card {{
        background: rgba(255,255,255,0.05);
        border: 2px dashed rgba(255,255,255,0.2);
        border-radius: 16px;
        padding: 32px;
        color: var(--muted);
        text-align: center;
        
        transition: all 0.3s ease;
      }}
      
      .empty-card:hover {{
        border-color: rgba(255,255,255,0.3);
        background: rgba(255,255,255,0.08);
      }}

      /* Enhanced Footer */
      .app-footer {{
        color: var(--muted);
        text-align: center;
        padding: 20px 0;
        border-top: 1px solid rgba(255,255,255,0.1);
        background: rgba(0,0,0,0.1);
        
      }}
      
      .app-footer a {{
        color: #c4b5fd;
        text-decoration: none;
        font-weight: 600;
        transition: all 0.3s ease;
      }}
      
      .app-footer a:hover {{
        color: var(--text);
      }}

      /* Animations */
      @keyframes shimmer {{
        0% {{ left: -100%; }}
        100% {{ left: 100%; }}
      }}
      
      @keyframes float {{
        0%, 100% {{ transform: translateY(0px) rotate(0deg); }}
        50% {{ transform: translateY(-20px) rotate(180deg); }}
      }}
      
      @keyframes fadeInUp {{
        from {{
          opacity: 0;
          transform: translateY(30px);
        }}
        to {{
          opacity: 1;
          transform: translateY(0);
        }}
      }}
      
      .metric-card {{
        animation: fadeInUp 0.6s ease-out;
      }}
      
      .metric-card:nth-child(1) {{ animation-delay: 0.1s; }}
      .metric-card:nth-child(2) {{ animation-delay: 0.2s; }}
      .metric-card:nth-child(3) {{ animation-delay: 0.3s; }}
      .metric-card:nth-child(4) {{ animation-delay: 0.4s; }}

      /* File Uploader Enhancement */
      .stFileUploader {{
        border-radius: 16px;
        overflow: hidden;
      }}
      
      .stFileUploader > div {{
        background: rgba(255,255,255,0.05);
        border: 2px dashed rgba(255,255,255,0.2);
        border-radius: 16px;
        padding: 24px;
        transition: all 0.3s ease;
      }}
      
      .stFileUploader > div:hover {{
        border-color: rgba(255,255,255,0.4);
        background: rgba(255,255,255,0.08);
      }}

      /* Selectbox Enhancement */
      .stSelectbox > div {{
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.2);
        border-radius: 12px;
        
      }}

      /* Scrollbar Styling */
      ::-webkit-scrollbar {{
        width: 8px;
      }}
      
      ::-webkit-scrollbar-track {{
        background: rgba(255,255,255,0.1);
        border-radius: 4px;
      }}
      
      ::-webkit-scrollbar-thumb {{
        background: var(--gradient1);
        border-radius: 4px;
      }}
      
      ::-webkit-scrollbar-thumb:hover {{
        background: var(--gradient2);
      }}
    </style>
    """,
    unsafe_allow_html=True,
)


st.markdown("""
<div class='hero-card'>
    <div class='hero-title'>🗨️ WhatsApp Chat Analyzer</div>
    <div class='hero-sub'>Transform your WhatsApp conversations into beautiful insights with advanced analytics, sentiment analysis, and interactive visualizations.</div>
    <div style='margin-top: 16px; display: flex; gap: 12px; flex-wrap: wrap;'>
        <span style='background: rgba(255,255,255,0.1); padding: 6px 12px; border-radius: 20px; font-size: 0.85rem; color: var(--text);'>📊 Analytics</span>
        <span style='background: rgba(255,255,255,0.1); padding: 6px 12px; border-radius: 20px; font-size: 0.85rem; color: var(--text);'>📈 Visualizations</span>
        <span style='background: rgba(255,255,255,0.1); padding: 6px 12px; border-radius: 20px; font-size: 0.85rem; color: var(--text);'>🎯 Insights</span>
    </div>
</div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Upload exported chat (.txt)", help="Export a chat from WhatsApp and upload the .txt file here")
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")
    df = preprocessor.preprocess(data)

    # fetch unique users
    user_list = df['user'].unique().tolist()
    if 'group_notification' in user_list:
        user_list.remove('group_notification')
    user_list.sort()
    user_list.insert(0,"Overall")

    col_sel, col_btn = st.columns([3,1])
    with col_sel:
        selected_user = st.selectbox("Analyze messages for",user_list, help="View metrics for a specific participant or overall")
    with col_btn:
        analyze_clicked = st.button("Refresh Analysis", type="primary", help="Regenerate insights for the selected scope")

    # Auto-analyze when file is uploaded or user changes
    if 'last_analyzed_user' not in st.session_state:
        st.session_state.last_analyzed_user = None
    
    should_analyze = (analyze_clicked or 
                     st.session_state.last_analyzed_user != selected_user or 
                     st.session_state.last_analyzed_user is None)
    
    if should_analyze:
        st.session_state.last_analyzed_user = selected_user
        
        # Debug information
        st.write("🔍 Debug Info:")
        st.write(f"DataFrame shape: {df.shape}")
        st.write(f"Columns: {list(df.columns)}")
        st.write(f"First few rows:")
        st.dataframe(df.head())
        st.write(f"User list: {user_list}")
        st.write(f"Selected user: {selected_user}")
        
        # Header
        st.markdown("<h2 class='section-title'>Overview</h2>", unsafe_allow_html=True)

        # Tabs
        tab_overview, tab_timeline, tab_activity, tab_users, tab_words, tab_emojis = st.tabs([
            "Overview", "Timeline", "Activity", "Users", "Words", "Emojis"
        ])

        # Stats Area as metric cards
        num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user,df)
        with tab_overview:
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.markdown("<div class='metric-card'><div class='metric-label'>💬 Messages</div><div class='metric-value'>"+str(num_messages)+"</div></div>", unsafe_allow_html=True)
            with c2:
                st.markdown("<div class='metric-card'><div class='metric-label'>📝 Words</div><div class='metric-value'>"+str(words)+"</div></div>", unsafe_allow_html=True)
            with c3:
                st.markdown("<div class='metric-card'><div class='metric-label'>🖼️ Media</div><div class='metric-value'>"+str(num_media_messages)+"</div></div>", unsafe_allow_html=True)
            with c4:
                st.markdown("<div class='metric-card'><div class='metric-label'>🔗 Links</div><div class='metric-value'>"+str(num_links)+"</div></div>", unsafe_allow_html=True)

        # Timeline Tab
        with tab_timeline:
            st.markdown("<h3 class='section-title'>Timeline</h3>", unsafe_allow_html=True)
            timeline = helper.monthly_timeline(selected_user,df)
            if timeline is not None and not timeline.empty:
                fig,ax = plt.subplots()
                ax.plot(timeline['time'], timeline['message'],color='#22c55e')
                plt.xticks(rotation='vertical')
                st.pyplot(fig)
            else:
                st.info("No monthly activity to display.")

            daily_timeline = helper.daily_timeline(selected_user, df)
            if daily_timeline is not None and not daily_timeline.empty:
                fig, ax = plt.subplots()
                ax.plot(daily_timeline['only_date'], daily_timeline['message'], color='#a78bfa')
                plt.xticks(rotation='vertical')
                st.pyplot(fig)
            else:
                st.info("No daily activity to display.")

        # Activity Tab
        with tab_activity:
            st.markdown("<h3 class='section-title'>Activity</h3>", unsafe_allow_html=True)
            col1,col2 = st.columns(2)
            with col1:
                st.subheader("Most Busy Day")
                busy_day = helper.week_activity_map(selected_user,df)
                if busy_day is not None and not busy_day.empty:
                    fig,ax = plt.subplots()
                    ax.bar(busy_day.index,busy_day.values,color='#f59e0b')
                    plt.xticks(rotation='vertical')
                    st.pyplot(fig)
                else:
                    st.info("No weekly activity to display.")
            with col2:
                st.subheader("Most Busy Month")
                busy_month = helper.month_activity_map(selected_user, df)
                if busy_month is not None and not busy_month.empty:
                    fig, ax = plt.subplots()
                    ax.bar(busy_month.index, busy_month.values,color='#38bdf8')
                    plt.xticks(rotation='vertical')
                    st.pyplot(fig)
                else:
                    st.info("No monthly activity breakdown to display.")

            st.subheader("Weekly Activity Map")
            user_heatmap = helper.activity_heatmap(selected_user,df)
            if user_heatmap is not None and not user_heatmap.empty:
                fig,ax = plt.subplots()
                ax = sns.heatmap(user_heatmap, cmap="crest")
                st.pyplot(fig)
            else:
                st.info("No heatmap data to display.")

        # Users Tab
        with tab_users:
            st.markdown("<h3 class='section-title'>Users</h3>", unsafe_allow_html=True)
            if selected_user == 'Overall':
                x,new_df = helper.most_busy_users(df)
                fig, ax = plt.subplots()
                col1, col2 = st.columns(2)
                with col1:
                    ax.bar(x.index, x.values,color='#ef4444')
                    plt.xticks(rotation='vertical')
                    st.pyplot(fig)
                with col2:
                    st.dataframe(new_df)
            else:
                st.info("Switch to 'Overall' to view most busy users.")

        # Words Tab
        with tab_words:
            st.markdown("<h3 class='section-title'>Words</h3>", unsafe_allow_html=True)
            df_wc = helper.create_wordcloud(selected_user,df)
            if df_wc is not None:
                fig,ax = plt.subplots()
                ax.imshow(df_wc)
                ax.axis('off')
                st.pyplot(fig)
            else:
                st.info("Not enough text to generate a wordcloud.")

            most_common_df = helper.most_common_words(selected_user,df)
            if most_common_df is not None and not most_common_df.empty:
                fig,ax = plt.subplots()
                ax.barh(most_common_df[0],most_common_df[1], color="#60a5fa")
                plt.xticks(rotation='vertical')
                st.pyplot(fig)
            else:
                st.info("No common words to display.")

        # Emojis Tab
        with tab_emojis:
            st.markdown("<h3 class='section-title'>Emojis</h3>", unsafe_allow_html=True)
            emoji_df = helper.emoji_helper(selected_user,df)
            if emoji_df is not None and not emoji_df.empty:
                col1,col2 = st.columns(2)
                with col1:
                    st.dataframe(emoji_df)
                with col2:
                    top_counts = emoji_df[1].head()
                    if top_counts.sum() > 0:
                        fig,ax = plt.subplots()
                        ax.pie(top_counts,labels=emoji_df[0].head(),autopct="%0.2f")
                        st.pyplot(fig)
                    else:
                        st.info("No emoji usage to chart.")
            else:
                st.info("No emojis found in the selected conversation.")
    else:
        st.markdown("<div class='empty-card'>Click 'Refresh Analysis' to generate insights for the selected user.</div>", unsafe_allow_html=True)
else:
    st.markdown("""
    <div class='empty-card'>
        <div style='font-size: 3rem; margin-bottom: 16px;'>📁</div>
        <h3 style='color: #e2e8f0; margin-bottom: 12px; font-weight: 600;'>Ready to Analyze Your Chat?</h3>
        <p style='margin-bottom: 20px; line-height: 1.6;'>Upload an exported WhatsApp chat .txt file to unlock powerful insights including:</p>
        <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px; text-align: left;'>
            <div style='display: flex; align-items: center; gap: 8px;'>
                <span style='font-size: 1.2rem;'>📊</span>
                <span>Message Statistics</span>
            </div>
            <div style='display: flex; align-items: center; gap: 8px;'>
                <span style='font-size: 1.2rem;'>📈</span>
                <span>Activity Timelines</span>
            </div>
            <div style='display: flex; align-items: center; gap: 8px;'>
                <span style='font-size: 1.2rem;'>🔥</span>
                <span>Most Active Users</span>
            </div>
            <div style='display: flex; align-items: center; gap: 8px;'>
                <span style='font-size: 1.2rem;'>☁️</span>
                <span>Word Clouds</span>
            </div>
            <div style='display: flex; align-items: center; gap: 8px;'>
                <span style='font-size: 1.2rem;'>😊</span>
                <span>Emoji Analysis</span>
            </div>
            <div style='display: flex; align-items: center; gap: 8px;'>
                <span style='font-size: 1.2rem;'>🌡️</span>
                <span>Activity Heatmaps</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("<div class='app-footer'>Made with ❤️ using Streamlit · Need help? See README</div>", unsafe_allow_html=True)

