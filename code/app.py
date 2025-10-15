import streamlit as st
import preprocessor,helper
import matplotlib.pyplot as plt
import seaborn as sns
import altair as alt
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
import tempfile
import pandas as pd

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
        padding: 0;
        border-radius: 0;
        background: transparent;
        color: var(--text);
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
        background: transparent;
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
        background: transparent;
        color: var(--text);
        border-color: rgba(255,255,255,0.1);
        transform: none;
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
    
    # Always render analysis UI every rerun so interactions (checkboxes/buttons) work
    should_analyze = True
    
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
            col_left, col_right = st.columns(2)
            # Monthly timeline (left)
            with col_left:
                timeline = helper.monthly_timeline(selected_user, df)
                if timeline is not None and not timeline.empty:
                    fig, ax = plt.subplots(figsize=(8, 5))
                    ax.plot(timeline['time'], timeline['message'], color='#22c55e', linewidth=1.6)
                    plt.xticks(rotation='vertical')
                    plt.tight_layout()
                    st.pyplot(fig, width='content')
                else:
                    st.info("No monthly activity to display.")
            
            # Daily timeline (right)
            with col_right:
                daily_timeline = helper.daily_timeline(selected_user, df)
                if daily_timeline is not None and not daily_timeline.empty:
                    fig, ax = plt.subplots(figsize=(8, 5))
                    ax.plot(daily_timeline['only_date'], daily_timeline['message'], color='#a78bfa', linewidth=1.6)
                    plt.xticks(rotation='vertical')
                    plt.tight_layout()
                    st.pyplot(fig, width='content')
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
                    fig,ax = plt.subplots(figsize=(6,3.2))
                    ax.bar(busy_day.index,busy_day.values,color='#f59e0b')
                    plt.xticks(rotation='vertical')
                    st.pyplot(fig, width='content')
                else:
                    st.info("No weekly activity to display.")
            with col2:
                st.subheader("Most Busy Month")
                busy_month = helper.month_activity_map(selected_user, df)
                if busy_month is not None and not busy_month.empty:
                    fig, ax = plt.subplots(figsize=(6,3.2))
                    ax.bar(busy_month.index, busy_month.values,color='#38bdf8')
                    plt.xticks(rotation='vertical')
                    st.pyplot(fig, width='content')
                else:
                    st.info("No monthly activity breakdown to display.")

            st.subheader("Weekly Activity Map")
            user_heatmap = helper.activity_heatmap(selected_user,df)
            if user_heatmap is not None and not user_heatmap.empty:
                fig,ax = plt.subplots(figsize=(6.5,3.6))
                ax = sns.heatmap(user_heatmap, cmap="mako", cbar_kws={"label": "Messages"})
                ax.set_xlabel("Hour Period")
                ax.set_ylabel("Day of Week")
                st.pyplot(fig, width='content')
            else:
                st.info("No heatmap data to display.")

            st.subheader("Time-based Activity Heatmap by Participant")
            grid_df = helper.time_activity_user_grid(selected_user, df)
            if grid_df is not None and not grid_df.empty:
                # Build interactive Altair heatmap: Day vs Hour, colored by count, tooltip with details
                # If Overall, facet by user; if single user, just show one heatmap labeled
                base = alt.Chart(grid_df)

                heat = base.mark_rect().encode(
                    x=alt.X('hour:O', title='Hour of Day'),
                    y=alt.Y('day_name:O', sort=['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'], title='Day of Week'),
                    color=alt.Color('count:Q', scale=alt.Scale(scheme='inferno'), title='Messages'),
                    tooltip=[
                        alt.Tooltip('user:N', title='Participant'),
                        alt.Tooltip('day_name:N', title='Day'),
                        alt.Tooltip('hour:O', title='Hour'),
                        alt.Tooltip('count:Q', title='Messages')
                    ]
                ).properties(width=520, height=220)

                if selected_user == 'Overall':
                    chart = heat.facet(
                        row=alt.Row('user:N', title='Participant', header=alt.Header(labelAngle=0)),
                    ).resolve_scale(color='shared')
                else:
                    # Add a title for clarity
                    chart = heat.properties(title=f"{selected_user} — Messages by Day and Hour")

                st.altair_chart(chart.configure_axis(
                    labelColor='#e2e8f0', titleColor='#e2e8f0'
                ).configure_legend(
                    labelColor='#e2e8f0', titleColor='#e2e8f0'
                ))
            else:
                st.info("No time-based activity data to display.")

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
                fig,ax = plt.subplots(figsize=(6.5,3.8))
                ax.imshow(df_wc)
                ax.axis('off')
                st.pyplot(fig, width='content')
            else:
                st.info("Not enough text to generate a wordcloud.")

            most_common_df = helper.most_common_words(selected_user,df)
            if most_common_df is not None and not most_common_df.empty:
                fig,ax = plt.subplots(figsize=(6.5,3.8))
                ax.barh(most_common_df[0],most_common_df[1], color="#60a5fa")
                plt.xticks(rotation='vertical')
                st.pyplot(fig, width='content')
            else:
                st.info("No common words to display.")

        # Emojis Tab
        with tab_emojis:
            st.markdown("<h3 class='section-title'>Emojis</h3>", unsafe_allow_html=True)
            emoji_df = helper.emoji_helper(selected_user,df)
            if emoji_df is not None and not emoji_df.empty:
                # Ensure proper column names
                try:
                    emoji_df.columns = ['emoji', 'count']
                except Exception:
                    pass

                # Prepare display table with requested headers (no serial number)
                emoji_df = emoji_df.reset_index(drop=True)
                display_df = (
                    emoji_df[[ 'emoji', 'count' ]]
                    .rename(columns={
                        'emoji': 'emojis',
                        'count': 'no of time occured'
                    })
                )

                col1, col2 = st.columns(2)
                with col1:
                    st.dataframe(display_df, height=520)
                with col2:
                    # Use Altair (browser fonts) so emojis render correctly
                    top_n = 10 if len(emoji_df) >= 10 else len(emoji_df)
                    top_df = emoji_df.head(top_n)
                    if not top_df.empty and top_df['count'].sum() > 0:
                        bar = (
                            alt.Chart(top_df)
                              .mark_bar()
                              .encode(
                                  y=alt.Y('emoji:N', sort='-x', title='Emojis'),
                                  x=alt.X('count:Q', title='No. of times occurred'),
                                  tooltip=[
                                      alt.Tooltip('emoji:N', title='Emoji'),
                                      alt.Tooltip('count:Q', title='Count')
                                  ]
                              )
                              .properties(width=380, height=520)
                        )
                        text = (
                            alt.Chart(top_df)
                              .mark_text(align='left', dx=3, color='#e2e8f0')
                              .encode(
                                  y=alt.Y('emoji:N', sort='-x'),
                                  x='count:Q',
                                  text='count:Q'
                              )
                        )
                        st.altair_chart((bar + text).configure_axis(
                            labelColor='#e2e8f0', titleColor='#e2e8f0'
                        ).configure_legend(
                            labelColor='#e2e8f0', titleColor='#e2e8f0'
                        ))
                    else:
                        st.info("No emoji usage to chart.")
            else:
                st.info("No emojis found in the selected conversation.")

        # Report Generation Section
        st.markdown("<h3 class='section-title'>Report</h3>", unsafe_allow_html=True)
        anonymize = st.checkbox("Anonymize participant names in report", value=False)
        if st.button("Download Full Report as PDF"):
            # Prepare filtered dataframe according to selected_user
            if selected_user != 'Overall':
                filtered_df = df[df['user'] == selected_user].copy()
            else:
                filtered_df = df.copy()

            # Optional anonymization mapping
            anon_map = {}
            if anonymize:
                unique_users = [u for u in filtered_df['user'].unique() if u != 'group_notification']
                anon_map = {u: f"User {i+1}" for i, u in enumerate(unique_users)}
                filtered_df['user'] = filtered_df['user'].apply(lambda u: anon_map.get(u, u))

            # Utility: convert matplotlib fig to reportlab image flowable
            def fig_to_flowable(fig, max_width=480):
                buf = BytesIO()
                fig.savefig(buf, format='png', bbox_inches='tight', dpi=180)
                plt.close(fig)
                buf.seek(0)
                img = ImageReader(buf)
                rl_img = RLImage(img)
                # scale keeping aspect ratio
                iw, ih = rl_img.drawWidth, rl_img.drawHeight
                if iw > max_width:
                    scale = max_width / iw
                    rl_img.drawWidth = iw * scale
                    rl_img.drawHeight = ih * scale
                return rl_img

            # Compose report
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
            styles = getSampleStyleSheet()
            title_style = styles['Title']
            h_style = styles['Heading2']
            body = styles['BodyText']

            flow = []

            # Cover Page
            chat_name = uploaded_file.name if uploaded_file is not None else 'WhatsApp Chat'
            date_min = str(filtered_df['date'].min().date()) if not filtered_df.empty else '-'
            date_max = str(filtered_df['date'].max().date()) if not filtered_df.empty else '-'
            total_msgs = int(filtered_df.shape[0])

            flow.append(Paragraph("WhatsApp Chat Analysis Report", title_style))
            flow.append(Spacer(1, 12))
            flow.append(Paragraph(f"Chat: {chat_name}", body))
            flow.append(Paragraph(f"Scope: {selected_user}", body))
            flow.append(Paragraph(f"Date range: {date_min} to {date_max}", body))
            flow.append(Paragraph(f"Total messages analyzed: {total_msgs}", body))
            flow.append(Paragraph(f"Generated on: <u>{pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}</u>", body))
            flow.append(PageBreak())

            # Executive Summary (basic heuristics)
            try:
                busiest_day = filtered_df['day_name'].value_counts().idxmax() if not filtered_df.empty else '-'
                busiest_user = filtered_df[filtered_df['user']!='group_notification']['user'].value_counts().idxmax() if not filtered_df.empty else '-'
            except Exception:
                busiest_day, busiest_user = '-', '-'
            flow.append(Paragraph("Executive Summary", h_style))
            flow.append(Paragraph(f"- Peak activity day: {busiest_day}", body))
            flow.append(Paragraph(f"- Most frequent sender: {busiest_user}", body))
            flow.append(Spacer(1, 12))

            # Message Statistics chart
            num_messages, words_count, num_media_messages, num_links = helper.fetch_stats(selected_user, df)
            fig, ax = plt.subplots(figsize=(5, 3))
            stats_labels = ['Messages', 'Words', 'Media', 'Links']
            stats_values = [num_messages, words_count, num_media_messages, num_links]
            ax.bar(stats_labels, stats_values, color=['#7c3aed','#2563eb','#22c55e','#f59e0b'])
            ax.set_title('Message Statistics')
            flow.append(fig_to_flowable(fig))
            flow.append(Spacer(1, 6))

            # Timeline charts
            tl = helper.monthly_timeline(selected_user, df)
            if tl is not None and not tl.empty:
                fig, ax = plt.subplots(figsize=(6, 3.2))
                ax.plot(tl['time'], tl['message'], color='#2563eb')
                ax.set_title('Monthly Timeline')
                ax.tick_params(axis='x', labelrotation=60)
                flow.append(fig_to_flowable(fig))
                flow.append(Spacer(1, 6))

            dl = helper.daily_timeline(selected_user, df)
            if dl is not None and not dl.empty:
                fig, ax = plt.subplots(figsize=(6, 3.2))
                ax.plot(dl['only_date'], dl['message'], color='#a78bfa')
                ax.set_title('Daily Timeline')
                fig.autofmt_xdate()
                flow.append(fig_to_flowable(fig))
                flow.append(Spacer(1, 6))

            # Activity heatmap (day vs period)
            hm = helper.activity_heatmap(selected_user, df)
            if hm is not None and not hm.empty:
                fig, ax = plt.subplots(figsize=(6, 3.2))
                sns.heatmap(hm, cmap='mako', ax=ax, cbar_kws={'label':'Messages'})
                ax.set_title('Weekly Activity Heatmap')
                flow.append(fig_to_flowable(fig))
                flow.append(Spacer(1, 6))

            # Most active participants (Overall only)
            if selected_user == 'Overall':
                x, new_df = helper.most_busy_users(df)
                if not x.empty:
                    disp_index = [anon_map.get(idx, idx) if anonymize else idx for idx in x.index]
                    fig, ax = plt.subplots(figsize=(5.5, 3.2))
                    ax.bar(disp_index, x.values, color='#ef4444')
                    ax.set_title('Most Active Participants')
                    ax.tick_params(axis='x', labelrotation=60)
                    flow.append(fig_to_flowable(fig))
                    flow.append(Spacer(1, 6))

            # Top emojis
            e_df = helper.emoji_helper(selected_user, df)
            if e_df is not None and not e_df.empty:
                try:
                    e_df.columns = ['emoji','count']
                except Exception:
                    pass
                top_e = e_df.head(10)
                fig, ax = plt.subplots(figsize=(5, 3.2))
                ax.barh(top_e['emoji'][::-1], top_e['count'][::-1], color='#60a5fa')
                ax.set_title('Top Emojis')
                flow.append(fig_to_flowable(fig))
                flow.append(Spacer(1, 6))

            # Most common words
            mc_df = helper.most_common_words(selected_user, df)
            if mc_df is not None and not mc_df.empty:
                fig, ax = plt.subplots(figsize=(5.5, 3.2))
                ax.barh(mc_df[0][::-1], mc_df[1][::-1], color='#22c55e')
                ax.set_title('Most Common Words')
                flow.append(fig_to_flowable(fig))
                flow.append(PageBreak())

            # Appendix: Basic tables
            flow.append(Paragraph('Appendix: Summary Tables', h_style))
            # Summary metrics table
            metrics_data = [
                ['Metric', 'Value'],
                ['Total Messages', str(total_msgs)],
                ['Total Words', str(words_count)],
                ['Media Messages', str(num_media_messages)],
                ['Links Shared', str(num_links)],
            ]
            t = Table(metrics_data, hAlign='LEFT')
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.grey),
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ]))
            flow.append(t)

            # Build PDF
            doc.build(flow)
            buffer.seek(0)
            st.download_button(
                label="Download Full Report as PDF",
                data=buffer,
                file_name=f"chat_report_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.pdf",
                mime="application/pdf"
            )
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
st.markdown("<div class='app-footer'>Made with ❤️ using Streamlit · All Rights Reserved ©2025 Rohan Mushan</div>", unsafe_allow_html=True)

