# import streamlit as st
# import pandas as pd
# import calendar
# from datetime import datetime, timedelta
# import plotly.express as px
# import plotly.graph_objects as go
# import gspread
# from oauth2client.service_account import ServiceAccountCredentials
# import json

# # --- CONFIGURATION ---
# SHEET_NAME = "ProNutritionDB"
# WORKSHEET_LOGS = "Logs"
# WORKSHEET_TARGETS = "Targets"
# APP_NAME = "🥗 Pro Nutrition Tracker"

# # Global Defaults
# DEFAULT_CALS = 2000
# DEFAULT_PRO = 150
# DEFAULT_FIB = 30

# # Page Config
# st.set_page_config(page_title="Pro Nutrition Tracker", page_icon="🥗", layout="wide")

# # --- CSS STYLING ---
# st.markdown("""
#     <style>
#     .block-container { padding-top: 1rem; padding-bottom: 5rem; }
#     .app-header { text-align: center; font-size: 2.5rem; font-weight: 800; color: #667eea; margin-bottom: 20px; padding-top: 20px; }
    
#     /* METRICS & CARDS */
#     .metrics-container { display: flex; gap: 12px; overflow-x: auto; padding: 10px 0; -webkit-overflow-scrolling: touch; scrollbar-width: none; }
#     .metrics-container::-webkit-scrollbar { display: none; }
#     .metric-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-width: 100%; flex-shrink: 0; padding: 20px 16px; border-radius: 16px; box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15); text-align: center; color: white; position: relative; overflow: hidden; }
#     .metric-card::before { content: ''; position: absolute; top: -50%; right: -50%; width: 200%; height: 200%; background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%); pointer-events: none; }
#     .metric-card.cal { background: linear-gradient(135deg, #FF9800, #FF6F00); }
#     .metric-card.pro { background: linear-gradient(135deg, #66BB6A, #388E3C); }
#     .metric-card.fib { background: linear-gradient(135deg, #42A5F5, #1976D2); }
#     .metric-emoji { font-size: 2rem; margin-bottom: 8px; display: block; }
#     .metric-label { font-size: 1.8rem; font-weight: 700; text-transform: uppercase; opacity: 0.9; letter-spacing: 1px; margin-bottom: 8px; }
#     .metric-value { font-size: 2.2rem; font-weight: 900; margin: 8px 0; line-height: 1; }
#     .metric-delta { font-size: 1rem; opacity: 0.95; font-weight: 600; margin-top: 6px; }
    
#     /* MEALS */
#     .meal-header { padding: 12px 15px; border-radius: 8px; color: white; font-weight: bold; margin-top: 15px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center; font-size: 1.0rem; box-shadow: 0 2px 5px rgba(0,0,0,0.1); font-family: 'Segoe UI', sans-serif; }
#     .bg-breakfast { background: linear-gradient(90deg, #FF9966, #FF5E62); }
#     .bg-lunch { background: linear-gradient(90deg, #56ab2f, #a8e063); }
#     .bg-dinner { background: linear-gradient(90deg, #2193b0, #6dd5ed); }
#     .bg-snacks { background: linear-gradient(90deg, #DA4453, #89216B); }
    
#     /* FOOD CARDS & BUTTONS */
#     .food-card { background-color: white; border: 1px solid #eee; border-left: 5px solid #ddd; padding: 12px 15px; margin-bottom: 8px; border-radius: 8px; }
#     .food-name { font-size: 1.1rem; font-weight: 700; color: #2c3e50; margin-bottom: 4px; display: block; }
#     .food-macros { font-size: 0.85rem; color: #7f8c8d; font-weight: 500; }
#     .stButton button { padding: 0.25rem 0.5rem; font-size: 0.85rem; }
    
#     /* MOBILE RESPONSIVE */
#     @media (max-width: 768px) {
        
#         .metrics-container { gap: 10px; padding: 8px 0; }
#         .metric-card { min-width: 100%; padding: 18px 14px; border-radius: 14px; }
#         .metric-emoji { font-size: 1.6rem; margin-bottom: 6px; }
#         .metric-value { font-size: 1.6rem; }
#         .metric-label { font-size: 1.5rem; }
#         .metric-delta { font-size: 1rem; }
#         .food-name { font-size: 0.95rem; }
#         .food-macros { font-size: 0.75rem; }
#         .stButton button { padding: 0.3rem 0.4rem !important; min-width: 32px !important; height: 32px !important; font-size: 0.75rem !important; }
#         .meal-header { flex-direction: column; align-items: flex-start; gap: 5px; font-size: 0.9rem; padding: 10px 12px; }
#         div[data-testid="stMetricValue"] div { font-size: 1.5rem !important; }
#     }
#     @media (max-width: 600px) { h1 { margin-top: 12px; font-size: 1.6rem !important; } .app-header { font-size: 1.8rem; } }
#     @media (max-width: 480px) { .metric-card { min-width: 100%; padding: 16px 12px; } .metric-emoji { font-size: 2rem; } .metric-value { font-size: 1.6rem; } .metric-label { font-size: 1.3rem; } }
#     </style>
# """, unsafe_allow_html=True)

# # --- APP HEADER ---
# st.markdown(f"<div class='app-header'>{APP_NAME}</div>", unsafe_allow_html=True)

# # --- 🔒 SECURITY: STRICT USER IDENTIFICATION ---
# # 1. Try to get the real user from Streamlit Cloud
# user_email = st.context.headers.get("X-Streamlit-User-Email")

# if not user_email:
#     try:
#         user_email = st.experimental_user.email
#     except:
#         pass

# # 2. NO FALLBACKS: If user is not found, we use Session State (Manual Login)
# if 'manual_user_email' not in st.session_state:
#     st.session_state.manual_user_email = None

# if not user_email:
#     # If no Cloud Email, check if they manually logged in
#     if st.session_state.manual_user_email:
#         user_email = st.session_state.manual_user_email
#     else:
#         # SHOW LOGIN SCREEN
#         st.warning("⚠️ Could not detect Google Login automatically.")
#         with st.form("manual_login"):
#             st.markdown("### Please enter your email to continue:")
#             email_in = st.text_input("Email Address")
#             if st.form_submit_button("Login"):
#                 if "@" in email_in:
#                     st.session_state.manual_user_email = email_in
#                     st.rerun()
#                 else:
#                     st.error("Enter a valid email")
#         st.stop()

# CURRENT_USER = user_email

# # --- APP HEADER ---
# # st.markdown(f"<div class='app-header'>{APP_NAME}</div>", unsafe_allow_html=True)

# # # --- 🔒 SECURITY: GET CURRENT USER ---
# # user_email = st.context.headers.get("X-Streamlit-User-Email")

# # if not user_email:
# #     try:
# #         user_email = st.experimental_user.email
# #     except:
# #         pass

# # # FALLBACK: If user is not found, DO NOT STOP. Use a setup email.
# # if not user_email:
# #     user_email = "setup_admin@example.com"
# #     # st.warning("⚠️ No User ID found. Using 'setup_admin' to initialize app.")

# # CURRENT_USER = user_email


# # --- GOOGLE SHEETS CONNECTION FUNCTIONS ---

# @st.cache_resource
# def get_google_sheet():
#     """Connect to Google Sheets using st.secrets"""
#     # Scope for Google Drive/Sheets
#     scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    
#     # Load credentials from Streamlit Secrets
#     creds_dict = dict(st.secrets["gcp_service_account"])
#     creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
#     client = gspread.authorize(creds)
    
#     # Open the Sheet
#     try:
#         sheet = client.open(SHEET_NAME)
#         return sheet
#     except Exception as e:
#         st.error(f"Could not connect to Google Sheet. Check if shared with service account. Error: {e}")
#         return None

# def get_worksheet_data(worksheet_name, headers):
#     """Fetch data from a specific worksheet and return as DataFrame"""
#     sheet = get_google_sheet()
#     if not sheet: return pd.DataFrame(columns=headers)
    
#     try:
#         ws = sheet.worksheet(worksheet_name)
#         data = ws.get_all_records()
#         if not data:
#             return pd.DataFrame(columns=headers)
#         df = pd.DataFrame(data)
        
#         # Ensure numerical columns are numeric
#         if 'Calories' in df.columns:
#             df['Calories'] = pd.to_numeric(df['Calories'], errors='coerce').fillna(0)
#             df['Protein'] = pd.to_numeric(df['Protein'], errors='coerce').fillna(0)
#             df['Fiber'] = pd.to_numeric(df['Fiber'], errors='coerce').fillna(0)
#         return df
#     except gspread.WorksheetNotFound:
#         # Create it if it doesn't exist
#         ws = sheet.add_worksheet(title=worksheet_name, rows=1000, cols=10)
#         ws.append_row(headers)
#         return pd.DataFrame(columns=headers)

# def append_to_worksheet(worksheet_name, row_data):
#     sheet = get_google_sheet()
#     if sheet:
#         try:
#             ws = sheet.worksheet(worksheet_name)
#         except gspread.WorksheetNotFound:
#             # If it doesn't exist, create it!
#             ws = sheet.add_worksheet(title=worksheet_name, rows=1000, cols=10)
#             # If it's the Targets sheet, add headers
#             if worksheet_name == "Targets":
#                 ws.append_row(["Date", "Calories", "Protein", "Fiber"])
#             # If it's the Logs sheet, add headers
#             elif worksheet_name == "Logs":
#                 ws.append_row(["Date", "Meal", "Item", "Calories", "Protein", "Fiber"])
        
#         ws.append_row(row_data)
#         st.cache_data.clear()

# # --- BACKEND FUNCTIONS (REWRITTEN FOR SHEETS) ---

# def load_log():
#     df = get_worksheet_data(WORKSHEET_LOGS, ["Date", "Meal", "Item", "Calories", "Protein", "Fiber"])
#     if 'Date' in df.columns:
#         df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')
#     return df

# def save_entry(date_obj, meal, item, cals, pro, fib):
#     row = [
#         date_obj.strftime("%Y-%m-%d"),
#         meal,
#         item,
#         int(cals),
#         float(pro),
#         float(fib)
#     ]
#     append_to_worksheet(WORKSHEET_LOGS, row)
#     st.cache_data.clear() # Clear cache so new data shows up

# def update_entry(row_index, meal, item, cals, pro, fib):
#     # Note: Gspread rows are 1-indexed and row 1 is headers.
#     # So DataFrame index 0 corresponds to Sheet row 2.
#     sheet = get_google_sheet()
#     ws = sheet.worksheet(WORKSHEET_LOGS)
    
#     sheet_row_num = row_index + 2 
    
#     # Batch update is faster
#     ws.update(f"B{sheet_row_num}:F{sheet_row_num}", [[meal, item, int(cals), float(pro), float(fib)]])
#     st.cache_data.clear()

# def delete_entry(row_index):
#     sheet = get_google_sheet()
#     ws = sheet.worksheet(WORKSHEET_LOGS)
#     sheet_row_num = row_index + 2
#     ws.delete_rows(sheet_row_num)
#     st.cache_data.clear()

# def undo_last_entry():
#     sheet = get_google_sheet()
#     ws = sheet.worksheet(WORKSHEET_LOGS)
#     # Get total rows count
#     data = ws.get_all_values()
#     if len(data) > 1: # Don't delete header
#         ws.delete_rows(len(data))
#         st.toast("Last entry removed!")
#         st.cache_data.clear()

# # --- ANALYSIS FUNCTIONS ---
# def calculate_averages(df):
#     if df.empty:
#         return None, None, None, None
    
#     daily = df.groupby('Date')[['Calories', 'Protein', 'Fiber']].sum().reset_index()
#     daily['Date'] = pd.to_datetime(daily['Date'])
    
#     today = pd.to_datetime(datetime.now().date())
    
#     start_week = today - timedelta(days=7)
#     weekly = daily[(daily['Date'] >= start_week) & (daily['Date'] <= today)]
#     avg_week = weekly[['Calories', 'Protein', 'Fiber']].mean() if not weekly.empty else pd.Series([0,0,0], index=['Calories','Protein','Fiber'])
    
#     start_month = today - timedelta(days=30)
#     monthly = daily[(daily['Date'] >= start_month) & (daily['Date'] <= today)]
#     avg_month = monthly[['Calories', 'Protein', 'Fiber']].mean() if not monthly.empty else pd.Series([0,0,0], index=['Calories','Protein','Fiber'])
    
#     avg_year = daily[['Calories', 'Protein', 'Fiber']].mean()
    
#     return avg_week, avg_month, avg_year, daily

# # --- TARGET FUNCTIONS ---
# def load_targets():
#     df = get_worksheet_data(WORKSHEET_TARGETS, ["Date", "Calories", "Protein", "Fiber"])
#     if df.empty:
#         # Seed default
#         seed = ["2023-01-01", DEFAULT_CALS, DEFAULT_PRO, DEFAULT_FIB]
#         append_to_worksheet(WORKSHEET_TARGETS, seed)
#         return pd.DataFrame([seed], columns=["Date", "Calories", "Protein", "Fiber"])
#     return df

# def get_target_for_date(date_obj):
#     df = load_targets()
#     date_str = date_obj.strftime("%Y-%m-%d")
    
#     # Pandas filter
#     valid_targets = df[df['Date'] <= date_str]
#     if valid_targets.empty:
#         return DEFAULT_CALS, DEFAULT_PRO, DEFAULT_FIB
    
#     valid_targets = valid_targets.sort_values('Date', ascending=False)
#     latest = valid_targets.iloc[0]
#     return latest['Calories'], latest['Protein'], latest['Fiber']

# def save_smart_target(date_obj, cals, pro, fib, apply_future):
#     df = load_targets()
#     current_date_str = date_obj.strftime("%Y-%m-%d")
    
#     # In GSheets implementation, doing complex row insertion/restoration 
#     # is slow. We will simply append the new target.
#     # The get_target logic sorts by date anyway, so latest entry for a date wins.
    
#     row = [current_date_str, int(cals), int(pro), int(fib)]
    
#     # Check if target already exists for this exact date to update it instead of append
#     # (Optional optimization, but append is safer for now)
#     append_to_worksheet(WORKSHEET_TARGETS, row)
    
#     # If not apply future, we essentially need to re-assert the old target for tomorrow
#     if not apply_future:
#         tomorrow = date_obj + timedelta(days=1)
#         tomorrow_str = tomorrow.strftime("%Y-%m-%d")
        
#         # Find what the target was before today
#         past_targets = df[df['Date'] < current_date_str].sort_values('Date', ascending=False)
#         if not past_targets.empty:
#             restore_vals = past_targets.iloc[0]
#             row_restore = [
#                 tomorrow_str,
#                 int(restore_vals['Calories']),
#                 int(restore_vals['Protein']),
#                 int(restore_vals['Fiber'])
#             ]
#             append_to_worksheet(WORKSHEET_TARGETS, row_restore)

#     st.cache_data.clear()

# # --- STATE MANAGEMENT ---
# if 'selected_date' not in st.session_state:
#     st.session_state.selected_date = datetime.now().date()
# if 'edit_mode_index' not in st.session_state:
#     st.session_state.edit_mode_index = None

# # New State for Calendar Navigation
# if 'cal_month' not in st.session_state:
#     st.session_state.cal_month = datetime.now().month
# if 'cal_year' not in st.session_state:
#     st.session_state.cal_year = datetime.now().year

# # --- SIDEBAR (NAVIGATION) ---
# with st.sidebar:
#     st.header("📅 Navigator")
#     c1, c2, c3 = st.columns([1, 4, 1])
#     with c1:
#         if st.button("", icon=":material/arrow_back:", key="nav_prev"):
#             st.session_state.selected_date -= timedelta(days=1)
#             st.session_state.edit_mode_index = None
#             st.rerun()
#     with c2:
#         st.session_state.selected_date = st.date_input("Date", st.session_state.selected_date, label_visibility="collapsed")
#     with c3:
#         if st.button("", icon=":material/arrow_forward:", key="nav_next"):
#             st.session_state.selected_date += timedelta(days=1)
#             st.session_state.edit_mode_index = None
#             st.rerun()
            
#     # RESET BOTH DATE AND CALENDAR VIEW
#     if st.button("Return to Today", icon=":material/today:", width='stretch'):
#         now = datetime.now()
#         st.session_state.selected_date = now.date()
#         st.session_state.cal_month = now.month
#         st.session_state.cal_year = now.year
#         st.session_state.edit_mode_index = None
#         st.rerun()

#     st.divider()
#     with st.expander("🎯 Set Targets"):
#         st.caption(f"Targets for **{st.session_state.selected_date.strftime('%b %d')}**")
#         curr_c, curr_p, curr_f = get_target_for_date(st.session_state.selected_date)
        
#         with st.form("target_form"):
#             nc = st.number_input("Calories (Limit)", value=int(curr_c), step=50)
#             np = st.number_input("Protein (Min Goal)", value=int(curr_p), step=5)
#             nf = st.number_input("Fiber (Min Goal)", value=int(curr_f), step=5)
#             st.markdown("---")
#             apply_future = st.checkbox("Apply to future dates too?", value=True)
#             if st.form_submit_button("Save Targets", type="primary", icon=":material/save:", width='stretch'):
#                 save_smart_target(st.session_state.selected_date, nc, np, nf, apply_future)
#                 st.toast("Targets Updated!")
#                 st.rerun()
    
#     st.divider()
#     if st.button("Undo Last Food", icon=":material/undo:", width='stretch'):
#         undo_last_entry()
#         st.rerun()

# # --- MAIN PAGE ---
# current_date_str = st.session_state.selected_date.strftime("%Y-%m-%d")

# # Load Data
# df_log = load_log()
# df_today = df_log[df_log['Date'] == current_date_str].copy().reset_index(drop=True) 
# # Reset index is important for editing logic to match DataFrame index

# goal_cals, goal_pro, goal_fib = get_target_for_date(st.session_state.selected_date)
# ac = df_today['Calories'].sum()
# ap = df_today['Protein'].sum()
# af = df_today['Fiber'].sum()

# st.title(f"📊 {st.session_state.selected_date.strftime('%A, %b %d')}")

# # === MOBILE-OPTIMIZED METRICS (HORIZONTAL SCROLL) ===
# cals_left = int(goal_cals - ac)
# pro_delta = ap - goal_pro
# fib_delta = af - goal_fib

# c1, c2, c3 = st.columns(3)

# with c1:
#     st.markdown(f"""
#     <div class="metrics-container">
#         <div class="metric-card cal">
#             <div class="metric-emoji">🔥</div>
#             <div class="metric-label">Calories</div>
#             <div class="metric-value">{int(ac)}</div>
#             <div class="metric-delta">{cals_left} left</div>
#         </div>
#     </div>
#     """, unsafe_allow_html=True)

# with c2:
#     st.markdown(f"""
#     <div class="metrics-container">
#         <div class="metric-card pro">
#             <div class="metric-emoji">💪</div>
#             <div class="metric-label">Protein</div>
#             <div class="metric-value">{round(ap,1)}g</div>
#             <div class="metric-delta">{round(pro_delta,1)}g / {int(goal_pro)}g</div>
#         </div>
#     </div>
#     """, unsafe_allow_html=True)

# with c3:
#     st.markdown(f"""
#     <div class="metrics-container">
#         <div class="metric-card fib">
#             <div class="metric-emoji">🌾</div>
#             <div class="metric-label">Fiber</div>
#             <div class="metric-value">{round(af,1)}g</div>
#             <div class="metric-delta">{round(fib_delta,1)}g / {int(goal_fib)}g</div>
#         </div>
#     </div>
#     """, unsafe_allow_html=True)

# st.divider()

# # Add Food
# with st.expander("➕ Add Food Entry", expanded=False):
#     with st.form("add_food", clear_on_submit=True):
#         col_meal, col_name = st.columns([1, 3])
#         meal_in = col_meal.selectbox("Meal", ["Breakfast", "Lunch", "Snacks", "Dinner"])
#         name_in = col_name.text_input("Item Name", placeholder="e.g. 2 Eggs")
#         c1, c2, c3 = st.columns(3)
#         cal_in = c1.number_input("Calories", min_value=0, step=10)
#         pro_in = c2.number_input("Protein (g)", min_value=0.0, step=1.0)
#         fib_in = c3.number_input("Fiber (g)", min_value=0.0, step=1.0)
        
#         if st.form_submit_button("Add Entry", type="primary", icon=":material/add:", width='stretch'):
#             if not name_in.strip():
#                 st.error("⚠️ Item Name cannot be empty!")
#             else:
#                 save_entry(st.session_state.selected_date, meal_in, name_in, cal_in, pro_in, fib_in)
#                 st.rerun()

# # --- TABS ---
# tab1, tab2, tab3 = st.tabs(["📊 Visuals", "📝 Detailed Log", "📅 History & Trends"])

# # --- TAB 1: VISUALS ---
# with tab1:
#     if not df_today.empty:
#         c1, c2 = st.columns(2)
#         with c1:
#             st.subheader("🔥 Calorie Distribution")
#             fig = px.pie(df_today, values='Calories', names='Meal', hole=0.5,
#                          color='Meal',
#                          color_discrete_map={'Breakfast':'#FF9966', 'Lunch':'#56ab2f', 'Dinner':'#2193b0', 'Snacks':'#DA4453'})
#             fig.update_traces(textposition='inside', textinfo='percent+label')
#             st.plotly_chart(fig, width='stretch')
#         with c2:
#             st.subheader("💪 Protein & 🌾 Fiber")
#             chart_df = df_today.groupby('Meal')[['Protein', 'Fiber']].sum().reset_index()
#             chart_df = chart_df.melt(id_vars='Meal', value_vars=['Protein', 'Fiber'], var_name='Nutrient', value_name='Grams')
#             fig2 = px.bar(chart_df, x='Meal', y='Grams', color='Nutrient', barmode='group')
#             st.plotly_chart(fig2, width='stretch')
#     else:
#         st.info("No data for today. Add items to see charts.")

# # --- TAB 2: DETAILED LOG ---
# with tab2:
#     if not df_today.empty:
#         meal_order = ["Breakfast", "Lunch", "Dinner", "Snacks"]
#         css_classes = {"Breakfast": "bg-breakfast", "Lunch": "bg-lunch", "Dinner": "bg-dinner", "Snacks": "bg-snacks"}
        
#         # When using Google Sheets, we need the exact row index from the full dataset for editing
#         # But here we are iterating over filtered data. 
#         # We need to map back to the original sheet index if we want to delete/edit specific rows.
#         # Strategy: Use the Date+Meal+Item combo or just filter the main DF properly.
#         # Simpler Strategy: We will just search the main log for the matching entry in update_entry.
#         # NOTE: For simplicity in this demo, 'index' here refers to the df_today index.
#         # Since update_entry logic above assumes raw sheet index, we need to find the REAL index.
        
#         # Reload full log to get real indices
#         df_full = load_log()
        
#         for meal in meal_order:
#             meal_rows = df_today[df_today['Meal'] == meal]
#             m_cals = meal_rows['Calories'].sum()
#             m_pro = meal_rows['Protein'].sum()
#             m_fib = meal_rows['Fiber'].sum()
            
#             # Meal Header
#             st.markdown(f"""
#             <div class="meal-header {css_classes[meal]}">
#                 <span>{meal}</span>
#                 <span style="font-size:0.85em; opacity:0.95; font-weight:normal;">
#                     {int(m_cals)} Kcal &nbsp;|&nbsp; {int(m_pro)}g Protein &nbsp;|&nbsp; {int(m_fib)}g Fibers
#                 </span>
#             </div>
#             """, unsafe_allow_html=True)
            
#             if meal_rows.empty:
#                 st.caption("No items added.")
#                 continue

#             for idx, row in meal_rows.iterrows():
#                 # FIND REAL SHEET INDEX
#                 # We match based on Date, Meal, Item, and values to find the row in the Master DF
#                 # This is a bit hacky but safe for small personal datasets
#                 mask = (df_full['Date'] == current_date_str) & \
#                        (df_full['Meal'] == row['Meal']) & \
#                        (df_full['Item'] == row['Item']) & \
#                        (df_full['Calories'] == row['Calories'])
                
#                 real_indices = df_full[mask].index.tolist()
#                 if not real_indices:
#                     real_idx = -1
#                 else:
#                     real_idx = real_indices[0] # Take the first match
                
#                 unique_key = f"{meal}_{idx}_{real_idx}"

#                 # --- EDIT MODE ---
#                 if st.session_state.edit_mode_index == unique_key:
#                     with st.container():
#                         st.markdown(f"**Editing: {row['Item']}**")
#                         ec1, ec2, ec3, ec4 = st.columns([3, 1, 1, 1])
#                         e_item = ec1.text_input("Name", row['Item'], key=f"e_name_{unique_key}")
#                         e_cal = ec2.number_input("Calories", value=int(row['Calories']), key=f"e_cal_{unique_key}")
#                         e_pro = ec3.number_input("Protein", value=float(row['Protein']), key=f"e_pro_{unique_key}")
#                         e_fib = ec4.number_input("Fiber", value=float(row['Fiber']), key=f"e_fib_{unique_key}")
                        
#                         btn1, btn2 = st.columns([1, 4])
#                         if btn1.button("Save", key=f"save_{unique_key}", icon=":material/save:", width='stretch'):
#                             if real_idx != -1:
#                                 update_entry(real_idx, meal, e_item, e_cal, e_pro, e_fib)
#                                 st.session_state.edit_mode_index = None
#                                 st.rerun()
#                         if btn2.button("Cancel", key=f"cancel_{unique_key}", icon=":material/close:", width='stretch'):
#                             st.session_state.edit_mode_index = None
#                             st.rerun()
#                     st.divider()
                
#                 # --- DISPLAY MODE (MOBILE-FRIENDLY) ---
#                 else:
#                     col_text, col_edit, col_delete = st.columns([8, 1, 1])
                    
#                     with col_text:
#                         st.markdown(f"""
#                         <div style="margin-bottom: 2px;">
#                             <span class="food-name">{row['Item']}</span>
#                             <div class="food-macros">
#                                 {int(row['Calories'])} Kcal &nbsp;•&nbsp; {float(row['Protein'])}g Protein &nbsp;•&nbsp; {float(row['Fiber'])}g Fibers
#                             </div>
#                         </div>
#                         """, unsafe_allow_html=True)
                    
#                     with col_edit:
#                         if st.button("", key=f"edt_{unique_key}", icon=":material/edit:", help="Edit"):
#                             st.session_state.edit_mode_index = unique_key
#                             st.rerun()
                    
#                     with col_delete:
#                         if st.button("", key=f"del_{unique_key}", icon=":material/delete:", help="Delete"):
#                             if real_idx != -1:
#                                 delete_entry(real_idx)
#                                 st.rerun()
                    
#                     st.markdown("<hr style='margin: 5px 0px 10px 0px; opacity: 0.3;'>", unsafe_allow_html=True)
#     else:
#         st.info("No logs today.")

# # --- TAB 3: HISTORY & TRENDS ---
# with tab3:
#     st.subheader("📈 Statistics & Trends")
    
#     avg_week, avg_month, avg_all, daily_totals = calculate_averages(df_log)
    
#     if daily_totals is not None and not daily_totals.empty:
#         current_year = datetime.now().year
#         this_year_data = daily_totals[daily_totals['Date'].dt.year == current_year]
#         if not this_year_data.empty:
#             avg_curr_year = this_year_data[['Calories', 'Protein', 'Fiber']].mean()
#         else:
#             avg_curr_year = pd.Series([0, 0, 0], index=['Calories', 'Protein', 'Fiber'])

#         def get_vals(series):
#             if series is None or series.empty: return 0, 0, 0
#             return int(series['Calories']), int(series['Protein']), int(series['Fiber'])

#         w_c, w_p, w_f = get_vals(avg_week)
#         m_c, m_p, m_f = get_vals(avg_month)
#         y_c, y_p, y_f = get_vals(avg_curr_year)
#         o_c, o_p, o_f = get_vals(avg_all)

#         ac1, ac2, ac3, ac4 = st.columns(4)
#         with ac1: st.metric("7-Day Avg", f"{w_c} Kcal", f"{w_p}p / {w_f}f")
#         with ac2: st.metric("30-Day Avg", f"{m_c} Kcal", f"{m_p}p / {m_f}f")
#         with ac3: st.metric(f"{current_year} Avg", f"{y_c} Kcal", f"{y_p}p / {y_f}f")
#         with ac4: st.metric("All-Time Avg", f"{o_c} Kcal", f"{o_p}p / {o_f}f")
            
#         st.divider()

#         # Monthly Calendar View
#         st.subheader("🗓️ Monthly Calendar")

#         MIN_YEAR = 2023
#         MAX_YEAR = 2029

#         def next_month():
#             if st.session_state.cal_year == MAX_YEAR and st.session_state.cal_month == 12:
#                 return
#             if st.session_state.cal_month == 12:
#                 st.session_state.cal_month = 1
#                 st.session_state.cal_year += 1
#             else:
#                 st.session_state.cal_month += 1
        
#         def prev_month():
#             if st.session_state.cal_year == MIN_YEAR and st.session_state.cal_month == 1:
#                 return
#             if st.session_state.cal_month == 1:
#                 st.session_state.cal_month = 12
#                 st.session_state.cal_year -= 1
#             else:
#                 st.session_state.cal_month -= 1

#         col_prev, col_m, col_y, col_next = st.columns([1, 2, 2, 1])
        
#         with col_prev:
#             st.button("◀", on_click=prev_month, key="btn_prev_m", width='stretch')
#         with col_m:
#             selected_month_val = st.selectbox(
#                 "Month", 
#                 range(1, 13), 
#                 index=st.session_state.cal_month - 1, 
#                 format_func=lambda x: calendar.month_name[x],
#                 label_visibility="collapsed"
#             )
#             if selected_month_val != st.session_state.cal_month:
#                 st.session_state.cal_month = selected_month_val
#                 st.rerun()
#         with col_y:
#             selected_year_val = st.selectbox(
#                 "Year", 
#                 range(MIN_YEAR, MAX_YEAR + 1), 
#                 index=st.session_state.cal_year - MIN_YEAR, 
#                 label_visibility="collapsed"
#             )
#             if selected_year_val != st.session_state.cal_year:
#                 st.session_state.cal_year = selected_year_val
#                 st.rerun()
#         with col_next:
#             st.button("▶", on_click=next_month, key="btn_next_m", width='stretch')

#         # Draw Calendar
#         sel_year = st.session_state.cal_year
#         sel_month = st.session_state.cal_month
        
#         cal_obj = calendar.Calendar(firstweekday=0)
#         month_days = cal_obj.monthdayscalendar(sel_year, sel_month)
        
#         x_vals, y_vals, z_vals, text_vals = [], [], [], []
#         hover_cals, hover_pro, hover_fib = [], [], []
#         day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        
#         mask = (daily_totals['Date'].dt.year == sel_year) & (daily_totals['Date'].dt.month == sel_month)
#         month_data = daily_totals[mask].set_index('Date')

#         for week_idx, week in enumerate(month_days):
#             for day_idx, day_num in enumerate(week):
#                 x_vals.append(day_names[day_idx])
#                 y_vals.append(f"Week {week_idx+1}")
                
#                 if day_num == 0:
#                     z_vals.append(None)
#                     text_vals.append("")
#                     hover_cals.append("")
#                     hover_pro.append("")
#                     hover_fib.append("")
#                 else:
#                     date_key = pd.Timestamp(year=sel_year, month=sel_month, day=day_num)
#                     text_vals.append(str(day_num))
                    
#                     if date_key in month_data.index:
#                         row = month_data.loc[date_key]
#                         c, p, f = row['Calories'], row['Protein'], row['Fiber']
#                         z_vals.append(c) 
#                         hover_cals.append(int(c))
#                         hover_pro.append(int(p))
#                         hover_fib.append(int(f))
#                     else:
#                         z_vals.append(0) 
#                         hover_cals.append(0)
#                         hover_pro.append(0)
#                         hover_fib.append(0)

#         fig_cal = go.Figure(data=go.Heatmap(
#             x=x_vals, y=y_vals, z=z_vals,
#             text=text_vals, texttemplate="%{text}", 
#             textfont={"size": 14, "color": "gray"},
#             xgap=3, ygap=3,
#             colorscale=[[0, '#f8f9fa'], [0.01, '#e6fffa'], [1, '#319795']], 
#             showscale=False,
#             hovertemplate="<b>Date: %{x}, Day %{text}</b><br><br>🔥 Calories: %{customdata[0]}<br>💪 Protein: %{customdata[1]}g<br>🌾 Fiber: %{customdata[2]}g<extra></extra>",
#             customdata=list(zip(hover_cals, hover_pro, hover_fib))
#         ))
        
#         fig_cal.update_layout(
#             height=350,
#             margin=dict(l=0, r=0, t=30, b=0),
#             yaxis=dict(showgrid=False, zeroline=False, autorange="reversed", fixedrange=True), 
#             xaxis=dict(showgrid=False, zeroline=False, side="top", fixedrange=True), 
#             paper_bgcolor='rgba(0,0,0,0)',
#             plot_bgcolor='rgba(0,0,0,0)',
#             font=dict(family="Segoe UI")
#         )
#         st.plotly_chart(fig_cal, width='stretch')

#     else:
#         st.info("No historical data available yet. Start logging meals to see your stats!")

import streamlit as st
import pandas as pd
import calendar
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import hashlib

# --- CONFIGURATION ---
SHEET_NAME = "ProNutritionDB"
WORKSHEET_LOGS = "Logs"
WORKSHEET_TARGETS = "Targets"
WORKSHEET_USERS = "Users"
APP_NAME = "🥗 Pro Nutrition Tracker"

# Global Defaults
DEFAULT_CALS = 2000
DEFAULT_PRO = 150
DEFAULT_FIB = 30

st.set_page_config(page_title=APP_NAME, page_icon="🥗", layout="wide")

# --- CSS STYLING ---
st.markdown("""
    <style>
    .block-container { padding-top: 1rem; padding-bottom: 5rem; }
    .app-header { text-align: center; font-size: 2.5rem; font-weight: 800; color: #667eea; margin-bottom: 20px; padding-top: 20px; }
    
    /* METRICS & CARDS */
    .metrics-container { display: flex; gap: 12px; overflow-x: auto; padding: 10px 0; -webkit-overflow-scrolling: touch; scrollbar-width: none; }
    .metrics-container::-webkit-scrollbar { display: none; }
    .metric-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-width: 100%; flex-shrink: 0; padding: 20px 16px; border-radius: 16px; box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15); text-align: center; color: white; position: relative; overflow: hidden; }
    .metric-card::before { content: ''; position: absolute; top: -50%; right: -50%; width: 200%; height: 200%; background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%); pointer-events: none; }
    .metric-card.cal { background: linear-gradient(135deg, #FF9800, #FF6F00); }
    .metric-card.pro { background: linear-gradient(135deg, #66BB6A, #388E3C); }
    .metric-card.fib { background: linear-gradient(135deg, #42A5F5, #1976D2); }
    .metric-emoji { font-size: 2rem; margin-bottom: 8px; display: block; }
    .metric-label { font-size: 1.8rem; font-weight: 700; text-transform: uppercase; opacity: 0.9; letter-spacing: 1px; margin-bottom: 8px; }
    .metric-value { font-size: 2.2rem; font-weight: 900; margin: 8px 0; line-height: 1; }
    .metric-delta { font-size: 1rem; opacity: 0.95; font-weight: 600; margin-top: 6px; }
    
    /* MEALS */
    .meal-header { padding: 12px 15px; border-radius: 8px; color: white; font-weight: bold; margin-top: 15px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center; font-size: 1.0rem; box-shadow: 0 2px 5px rgba(0,0,0,0.1); font-family: 'Segoe UI', sans-serif; }
    .bg-breakfast { background: linear-gradient(90deg, #FF9966, #FF5E62); }
    .bg-lunch { background: linear-gradient(90deg, #56ab2f, #a8e063); }
    .bg-dinner { background: linear-gradient(90deg, #2193b0, #6dd5ed); }
    .bg-snacks { background: linear-gradient(90deg, #DA4453, #89216B); }
    
    /* FOOD CARDS & BUTTONS */
    .food-card { background-color: white; border: 1px solid #eee; border-left: 5px solid #ddd; padding: 12px 15px; margin-bottom: 8px; border-radius: 8px; }
    .food-name { font-size: 1.1rem; font-weight: 700; color: #2c3e50; margin-bottom: 4px; display: block; }
    .food-macros { font-size: 0.85rem; color: #7f8c8d; font-weight: 500; }
    .stButton button { padding: 0.25rem 0.5rem; font-size: 0.85rem; }
    
    /* MOBILE RESPONSIVE */
    @media (max-width: 768px) {
        .metrics-container { gap: 10px; padding: 8px 0; }
        .metric-card { min-width: 100%; padding: 18px 14px; border-radius: 14px; }
        .metric-emoji { font-size: 1.6rem; margin-bottom: 6px; }
        .metric-value { font-size: 1.6rem; }
        .metric-label { font-size: 1.5rem; }
        .metric-delta { font-size: 1rem; }
        .food-name { font-size: 0.95rem; }
        .food-macros { font-size: 0.75rem; }
        .stButton button { padding: 0.3rem 0.4rem !important; min-width: 32px !important; height: 32px !important; font-size: 0.75rem !important; }
        .meal-header { flex-direction: column; align-items: flex-start; gap: 5px; font-size: 0.9rem; padding: 10px 12px; }
        div[data-testid="stMetricValue"] div { font-size: 1.5rem !important; }
    }
    @media (max-width: 600px) { h1 { margin-top: 12px; font-size: 1.6rem !important; } .app-header { font-size: 1.8rem; } }
    @media (max-width: 480px) { .metric-card { min-width: 100%; padding: 16px 12px; } .metric-emoji { font-size: 2rem; } .metric-value { font-size: 1.6rem; } .metric-label { font-size: 1.3rem; } }
    </style>
""", unsafe_allow_html=True)

# --- APP HEADER ---
st.markdown(f"<div class='app-header'>{APP_NAME}</div>", unsafe_allow_html=True)

# --- GOOGLE SHEETS CONNECTION ---
@st.cache_resource
def get_google_sheet():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    try:
        sheet = client.open(SHEET_NAME)
        return sheet
    except Exception as e:
        st.error(f"Connection Error: {e}")
        return None

@st.cache_data(ttl=600)
def get_worksheet_df(worksheet_name, headers):
    sheet = get_google_sheet()
    if not sheet: return pd.DataFrame(columns=headers)
    try:
        ws = sheet.worksheet(worksheet_name)
        
        # AUTO-FIX: Check if sheet is empty and add headers
        all_vals = ws.get_all_values()
        if not all_vals:
            ws.append_row(headers)
            return pd.DataFrame(columns=headers)
            
        data = ws.get_all_records()
        if not data: return pd.DataFrame(columns=headers)
        df = pd.DataFrame(data)
        if 'Date' in df.columns:
            df['Date'] = df['Date'].astype(str)
        for col in ['Calories', 'Protein', 'Fiber']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        return df
    except gspread.WorksheetNotFound:
        # Create sheet if missing
        ws = sheet.add_worksheet(title=worksheet_name, rows=1000, cols=10)
        ws.append_row(headers)
        return pd.DataFrame(columns=headers)

def append_to_worksheet(worksheet_name, row_data):
    sheet = get_google_sheet()
    if sheet:
        try:
            ws = sheet.worksheet(worksheet_name)
        except gspread.WorksheetNotFound:
            ws = sheet.add_worksheet(title=worksheet_name, rows=1000, cols=10)
            if worksheet_name == WORKSHEET_LOGS:
                ws.append_row(["Email", "Date", "Meal", "Item", "Calories", "Protein", "Fiber"])
            elif worksheet_name == WORKSHEET_TARGETS:
                ws.append_row(["Email", "Date", "Calories", "Protein", "Fiber"])
        ws.append_row(row_data)
        st.cache_data.clear()

# --- 🔐 SECURITY & PASSWORD FUNCTIONS ---
def hash_password(password):
    """Converts a password into a secure hash"""
    return hashlib.sha256(str.encode(password)).hexdigest()

def verify_login(email, password):
    """Checks the Users sheet for a matching Email and Hashed Password"""
    df_users = get_worksheet_df(WORKSHEET_USERS, ["Email", "Password", "Name"])
    if df_users.empty: return False
    
    user_row = df_users[df_users['Email'] == email.strip()]
    if user_row.empty: return False
    
    stored_hash = str(user_row.iloc[0]['Password']).strip()
    input_hash = hash_password(password)

    # Support both hashed (new) and plain text (old/manual) passwords
    if stored_hash == input_hash: return True
    if stored_hash == password: return True 
    return False

def register_user(email, password, name):
    """Creates a new user row"""
    df_users = get_worksheet_df(WORKSHEET_USERS, ["Email", "Password", "Name"])
    if not df_users.empty and email.strip() in df_users['Email'].values:
        return False, "Email already registered!"
    
    new_hash = hash_password(password)
    append_to_worksheet(WORKSHEET_USERS, [email.strip(), new_hash, name.strip()])
    return True, "Account created! Please login."

def reset_password(email, new_password):
    """Updates the password in the Google Sheet"""
    sheet = get_google_sheet()
    if not sheet: return False, "Database Error"
    
    try:
        ws = sheet.worksheet(WORKSHEET_USERS)
    except gspread.WorksheetNotFound:
        return False, "Users sheet not found"
        
    cell = ws.find(email.strip())
    if not cell: return False, "Email not found in database!"
    
    new_hash = hash_password(new_password)
    ws.update_cell(cell.row, 2, new_hash)
    st.cache_data.clear()
    return True, "Password updated successfully!"

# === USER AUTHENTICATION LOGIC ===

# Initialize session state for user
if 'user_email' not in st.session_state:
    st.session_state.user_email = None

# Check if user is already logged in via URL params or session
if "user" in st.query_params and not st.session_state.user_email:
    st.session_state.user_email = st.query_params["user"]

# Try cloud header for Streamlit Cloud private apps
if not st.session_state.user_email:
    try:
        cloud_user = st.context.headers.get("X-Streamlit-User-Email")
        if cloud_user:
            st.session_state.user_email = cloud_user
    except:
        pass  # Headers not available in local environment

CURRENT_USER = st.session_state.user_email

# If no user logged in, show login screen
if not CURRENT_USER:    
    st.info("👋 Welcome! Please log in.")
        
    tab_login, tab_reg, tab_reset = st.tabs(["🔐 Login", "📝 Register", "🔄 Reset Password"])
        
    with tab_login:
        with st.form("login_form"):
            email_in = st.text_input("Email")
            pass_in = st.text_input("Password", type="password")
            remember = st.checkbox("Keep me logged in")
            
            if st.form_submit_button("Login", type="primary"):
                if verify_login(email_in, pass_in):
                    st.session_state.user_email = email_in.strip()
                    if remember:
                        st.query_params["user"] = email_in.strip()
                    st.rerun()
                else:
                    st.error("Invalid Email or Password.")

    with tab_reg:
        with st.form("reg_form"):
            new_email = st.text_input("New Email")
            new_name = st.text_input("Your Name")
            new_pass = st.text_input("New Password", type="password")
            if st.form_submit_button("Create Account"):
                if new_email and new_pass:
                    success, msg = register_user(new_email, new_pass, new_name)
                    if success: st.success(msg)
                    else: st.error(msg)
                else:
                    st.warning("Please fill all fields")

    with tab_reset:
        with st.form("reset_form"):
            r_email = st.text_input("Email Address")
            r_new = st.text_input("New Password", type="password")
            if st.form_submit_button("Update Password"):
                success, msg = reset_password(r_email, r_new)
                if success: st.success(msg)
                else: st.error(msg)
    
    st.stop()

# --- ONBOARDING LOGIC ---
def check_user_has_targets():
    df = get_worksheet_df(WORKSHEET_TARGETS, ["Email", "Date", "Calories", "Protein", "Fiber"])
    if df.empty or 'Email' not in df.columns: return False
    return not df[df['Email'] == CURRENT_USER].empty

def save_initial_targets(cals, pro, fib):
    today = datetime.now().strftime("%Y-%m-%d")
    append_to_worksheet(WORKSHEET_TARGETS, [CURRENT_USER, today, int(cals), int(pro), int(fib)])

if 'onboarding_complete' not in st.session_state:
    st.session_state.onboarding_complete = check_user_has_targets()

# ==========================================
# 🚀 SCREEN 1: ONBOARDING
# ==========================================
if not st.session_state.onboarding_complete:
    st.markdown("---")
    st.subheader(f"👋 Welcome {CURRENT_USER}!")
    st.write("Let's set your personal goals.")
    
    with st.container(border=True):
        col1, col2, col3 = st.columns(3)
        in_cal = col1.number_input("Daily Calories", value=DEFAULT_CALS, step=50)
        in_pro = col2.number_input("Protein (g)", value=DEFAULT_PRO, step=5)
        in_fib = col3.number_input("Fiber (g)", value=DEFAULT_FIB, step=5)
        
        st.markdown("<br>", unsafe_allow_html=True)
        c_save, c_skip = st.columns([2, 1])
        
        with c_save:
            if st.button("🚀 Save & Start", type="primary", width='stretch'):
                save_initial_targets(in_cal, in_pro, in_fib)
                st.session_state.onboarding_complete = True
                st.rerun()

        with c_skip:
            if st.button("Skip for now", width='stretch'):
                save_initial_targets(DEFAULT_CALS, DEFAULT_PRO, DEFAULT_FIB)
                st.session_state.onboarding_complete = True
                st.rerun()
    st.stop()

# ==========================================
# 🚀 SCREEN 2: MAIN DASHBOARD
# ==========================================

# --- DATA HELPERS ---
def load_log():
    df = get_worksheet_df(WORKSHEET_LOGS, ["Email", "Date", "Meal", "Item", "Calories", "Protein", "Fiber"])
    if not df.empty and 'Email' in df.columns:
        df = df[df['Email'] == CURRENT_USER]
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')
    return df

food_entry_expander = False
def save_entry(date_obj, meal, item, cals, pro, fib):
    append_to_worksheet(WORKSHEET_LOGS, [CURRENT_USER, date_obj.strftime("%Y-%m-%d"), meal, item, int(cals), float(pro), float(fib)])
    food_entry_expander = False

def update_entry(real_idx, meal, item, cals, pro, fib):
    sheet = get_google_sheet()
    ws = sheet.worksheet(WORKSHEET_LOGS)
    r = real_idx + 2
    ws.update(f"C{r}:G{r}", [[meal, item, int(cals), float(pro), float(fib)]])
    st.cache_data.clear()

def delete_entry(real_idx):
    sheet = get_google_sheet()
    ws = sheet.worksheet(WORKSHEET_LOGS)
    ws.delete_rows(real_idx + 2)
    st.cache_data.clear()

def get_target_for_date(date_obj):
    df = get_worksheet_df(WORKSHEET_TARGETS, ["Email", "Date", "Calories", "Protein", "Fiber"])
    if not df.empty and 'Email' in df.columns:
        df = df[df['Email'] == CURRENT_USER]
    date_str = date_obj.strftime("%Y-%m-%d")
    if not df.empty and 'Date' in df.columns:
        valid = df[df['Date'] <= date_str]
        if not valid.empty:
            latest = valid.sort_values('Date', ascending=False).iloc[0]
            return latest['Calories'], latest['Protein'], latest['Fiber']
    return DEFAULT_CALS, DEFAULT_PRO, DEFAULT_FIB

def save_smart_target(date_obj, cals, pro, fib):
    append_to_worksheet(WORKSHEET_TARGETS, [CURRENT_USER, date_obj.strftime("%Y-%m-%d"), int(cals), int(pro), int(fib)])

def calculate_averages(df):
    if df.empty: return None, None, None, None
    daily = df.groupby('Date')[['Calories', 'Protein', 'Fiber']].sum().reset_index()
    daily['Date'] = pd.to_datetime(daily['Date'])
    today = pd.to_datetime(datetime.now().date())
    
    start_week = today - timedelta(days=7)
    weekly = daily[(daily['Date'] >= start_week) & (daily['Date'] <= today)]
    avg_week = weekly[['Calories', 'Protein', 'Fiber']].mean() if not weekly.empty else pd.Series([0,0,0], index=['Calories','Protein','Fiber'])
    
    start_month = today - timedelta(days=30)
    monthly = daily[(daily['Date'] >= start_month) & (daily['Date'] <= today)]
    avg_month = monthly[['Calories', 'Protein', 'Fiber']].mean() if not monthly.empty else pd.Series([0,0,0], index=['Calories','Protein','Fiber'])
    
    avg_year = daily[['Calories', 'Protein', 'Fiber']].mean()
    return avg_week, avg_month, avg_year, daily

# --- STATE ---
if 'selected_date' not in st.session_state: 
    st.session_state.selected_date = datetime.now().date()
if 'edit_mode_index' not in st.session_state: 
    st.session_state.edit_mode_index = None
if 'cal_month' not in st.session_state: 
    st.session_state.cal_month = datetime.now().month
if 'cal_year' not in st.session_state: 
    st.session_state.cal_year = datetime.now().year

# --- SIDEBAR ---
with st.sidebar:
    users_df = get_worksheet_df(WORKSHEET_USERS, ["Email", "Password", "Name"])
    if not users_df.empty:
        user_info = users_df[users_df['Email'] == CURRENT_USER]
        if not user_info.empty:
            real_name = user_info.iloc[0]['Name']
            st.write(f"👤 **{real_name}**")
        else:
            st.write(f"👤 **{CURRENT_USER}**")
    
    if st.button("Logout", width='stretch'):
        st.session_state.user_email = None
        if "user" in st.query_params:
            del st.query_params["user"]
        st.rerun()
    
    st.divider()
    
    st.header("📅 Navigator")
    c1, c2, c3 = st.columns([1, 4, 1])
    if c1.button("◀", key="p"): 
        st.session_state.selected_date -= timedelta(days=1)
        st.session_state.edit_mode_index = None
        st.rerun()
    st.session_state.selected_date = c2.date_input("Date", st.session_state.selected_date, label_visibility="collapsed")
    if c3.button("▶", key="n"): 
        st.session_state.selected_date += timedelta(days=1)
        st.session_state.edit_mode_index = None
        st.rerun()
    
    if st.button("Return to Today", width='stretch'):
        st.session_state.selected_date = datetime.now().date()
        st.session_state.edit_mode_index = None
        st.rerun()

    st.divider()
    with st.expander("🎯 Update Targets"):
        curr_c, curr_p, curr_f = get_target_for_date(st.session_state.selected_date)
        with st.form("tgt"):
            nc = st.number_input("Cals", value=int(curr_c), step=50)
            np = st.number_input("Prot", value=int(curr_p), step=5)
            nf = st.number_input("Fib", value=int(curr_f), step=5)
            if st.form_submit_button("Save", width='stretch'):
                save_smart_target(st.session_state.selected_date, nc, np, nf)
                st.rerun()

# --- MAIN ---
current_date_str = st.session_state.selected_date.strftime("%Y-%m-%d")
df_log = load_log()
df_today = df_log[df_log['Date'] == current_date_str].copy().reset_index(drop=True)

goal_cals, goal_pro, goal_fib = get_target_for_date(st.session_state.selected_date)
ac = df_today['Calories'].sum()
ap = df_today['Protein'].sum()
af = df_today['Fiber'].sum()

st.subheader(f"📅 {st.session_state.selected_date.strftime('%b %d')}")
c1, c2, c3 = st.columns(3)
with c1: 
    st.markdown(f"""<div class="metrics-container"><div class="metric-card cal"><div class="metric-emoji">🔥</div><div class="metric-label">Calories</div><div class="metric-value">{int(ac)}</div><div class="metric-delta">{int(goal_cals - ac)} left</div></div></div>""", unsafe_allow_html=True)
with c2: 
    st.markdown(f"""<div class="metrics-container"><div class="metric-card pro"><div class="metric-emoji">💪</div><div class="metric-label">Protein</div><div class="metric-value">{round(ap,1)}g</div><div class="metric-delta">{round(ap - goal_pro,1)}g / {int(goal_pro)}g</div></div></div>""", unsafe_allow_html=True)
with c3: 
    st.markdown(f"""<div class="metrics-container"><div class="metric-card fib"><div class="metric-emoji">🌾</div><div class="metric-label">Fiber</div><div class="metric-value">{round(af,1)}g</div><div class="metric-delta">{round(af - goal_fib,1)}g / {int(goal_fib)}g</div></div></div>""", unsafe_allow_html=True)

st.divider()

# --- INPUT FORM ---
with st.expander("➕ Add Food Entry", expanded=food_entry_expander):
    with st.form("add_food", clear_on_submit=True, border=False):
        c_m, c_n = st.columns([1,3])
        meal_in = c_m.selectbox("Meal", ["Breakfast", "Lunch", "Snacks", "Dinner"], label_visibility="collapsed")
        name_in = c_n.text_input("Item Name", placeholder="e.g. 2 Eggs", label_visibility="collapsed")
        c1, c2, c3 = st.columns(3)
        cal_in = c1.number_input("Calories", step=10, help="Calories")
        pro_in = c2.number_input("Protein (g)", step=1.0, help="Protein")
        fib_in = c3.number_input("Fiber (g)", step=1.0, help="Fiber")
        
        if st.form_submit_button("Add Entry", type="primary"):
            if not name_in.strip():
                st.error("⚠️ Please enter a food name!")
            elif cal_in <= 0:
                st.error("⚠️ Calories must be greater than 0!")
            else:
                save_entry(st.session_state.selected_date, meal_in, name_in, cal_in, pro_in, fib_in)
                st.rerun()
                food_entry_expander = False


tab1, tab2, tab3 = st.tabs(["📊 Visuals", "📝 Detailed Log", "📅 History"])

with tab1:
    if not df_today.empty:
        c1, c2 = st.columns(2)
        with c1:
            fig = px.pie(df_today, values='Calories', names='Meal', hole=0.5, color='Meal', 
                        color_discrete_map={'Breakfast':'#FF9966', 'Lunch':'#56ab2f', 'Dinner':'#2193b0', 'Snacks':'#DA4453'})
            st.plotly_chart(fig, width='stretch')
        with c2:
            chart = df_today.groupby('Meal')[['Protein','Fiber']].sum().reset_index().melt('Meal')
            st.plotly_chart(px.bar(chart, x='Meal', y='value', color='variable', barmode='group'), width='stretch')
    else: 
        st.info("No data today")

# --- TAB 2: DETAILED LOG ---
with tab2:
    if not df_today.empty:
        meal_order = ["Breakfast", "Lunch", "Dinner", "Snacks"]
        css_classes = {"Breakfast": "bg-breakfast", "Lunch": "bg-lunch", "Dinner": "bg-dinner", "Snacks": "bg-snacks"}
        
        # When using Google Sheets, we need the exact row index from the full dataset for editing
        # But here we are iterating over filtered data. 
        # We need to map back to the original sheet index if we want to delete/edit specific rows.
        # Strategy: Use the Date+Meal+Item combo or just filter the main DF properly.
        # Simpler Strategy: We will just search the main log for the matching entry in update_entry.
        # NOTE: For simplicity in this demo, 'index' here refers to the df_today index.
        # Since update_entry logic above assumes raw sheet index, we need to find the REAL index.
        
        # Reload full log to get real indices
        df_full = load_log()
        
        for meal in meal_order:
            meal_rows = df_today[df_today['Meal'] == meal]
            m_cals = meal_rows['Calories'].sum()
            m_pro = meal_rows['Protein'].sum()
            m_fib = meal_rows['Fiber'].sum()
            
            # Meal Header
            st.markdown(f"""
            <div class="meal-header {css_classes[meal]}">
                <span>{meal}</span>
                <span style="font-size:0.85em; opacity:0.95; font-weight:normal;">
                    {int(m_cals)} Kcal &nbsp;|&nbsp; {int(m_pro)}g Protein &nbsp;|&nbsp; {int(m_fib)}g Fibers
                </span>
            </div>
            """, unsafe_allow_html=True)
            
            if meal_rows.empty:
                st.caption("No items added.")
                continue

            for idx, row in meal_rows.iterrows():
                # FIND REAL SHEET INDEX
                # We match based on Date, Meal, Item, and values to find the row in the Master DF
                # This is a bit hacky but safe for small personal datasets
                mask = (df_full['Date'] == current_date_str) & \
                       (df_full['Meal'] == row['Meal']) & \
                       (df_full['Item'] == row['Item']) & \
                       (df_full['Calories'] == row['Calories'])
                
                real_indices = df_full[mask].index.tolist()
                if not real_indices:
                    real_idx = -1
                else:
                    real_idx = real_indices[0] # Take the first match
                
                unique_key = f"{meal}_{idx}_{real_idx}"

                # --- EDIT MODE ---
                if st.session_state.edit_mode_index == unique_key:
                    with st.container():
                        st.markdown(f"**Editing: {row['Item']}**")
                        ec1, ec2, ec3, ec4 = st.columns([3, 1, 1, 1])
                        e_item = ec1.text_input("Name", row['Item'], key=f"e_name_{unique_key}")
                        e_cal = ec2.number_input("Calories", value=int(row['Calories']), key=f"e_cal_{unique_key}")
                        e_pro = ec3.number_input("Protein", value=float(row['Protein']), key=f"e_pro_{unique_key}")
                        e_fib = ec4.number_input("Fiber", value=float(row['Fiber']), key=f"e_fib_{unique_key}")
                        
                        btn1, btn2 = st.columns([1, 4])
                        if btn1.button("Save", key=f"save_{unique_key}", icon=":material/save:", width='stretch'):
                            if real_idx != -1:
                                update_entry(real_idx, meal, e_item, e_cal, e_pro, e_fib)
                                st.session_state.edit_mode_index = None
                                st.rerun()
                        if btn2.button("Cancel", key=f"cancel_{unique_key}", icon=":material/close:", width='stretch'):
                            st.session_state.edit_mode_index = None
                            st.rerun()
                    st.divider()
                
                # --- DISPLAY MODE (MOBILE-FRIENDLY) ---
                else:
                    col_text, col_edit, col_delete = st.columns([8, 1, 1])
                    
                    with col_text:
                        st.markdown(f"""
                        <div style="margin-bottom: 2px;">
                            <span class="food-name">{row['Item']}</span>
                            <div class="food-macros">
                                {int(row['Calories'])} Kcal &nbsp;•&nbsp; {float(row['Protein'])}g Protein &nbsp;•&nbsp; {float(row['Fiber'])}g Fibers
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col_edit:
                        if st.button("", key=f"edt_{unique_key}", icon=":material/edit:", help="Edit"):
                            st.session_state.edit_mode_index = unique_key
                            st.rerun()
                    
                    with col_delete:
                        if st.button("", key=f"del_{unique_key}", icon=":material/delete:", help="Delete"):
                            if real_idx != -1:
                                delete_entry(real_idx)
                                st.rerun()
                    
                    st.markdown("<hr style='margin: 5px 0px 10px 0px; opacity: 0.3;'>", unsafe_allow_html=True)
    else:
        st.info("No logs today.")

# --- TAB 3: HISTORY & TRENDS ---
with tab3:
    st.subheader("📈 Statistics & Trends")
    
    avg_week, avg_month, avg_all, daily_totals = calculate_averages(df_log)
    
    if daily_totals is not None and not daily_totals.empty:
        current_year = datetime.now().year
        this_year_data = daily_totals[daily_totals['Date'].dt.year == current_year]
        if not this_year_data.empty:
            avg_curr_year = this_year_data[['Calories', 'Protein', 'Fiber']].mean()
        else:
            avg_curr_year = pd.Series([0, 0, 0], index=['Calories', 'Protein', 'Fiber'])

        def get_vals(series):
            if series is None or series.empty: return 0, 0, 0
            return int(series['Calories']), int(series['Protein']), int(series['Fiber'])

        w_c, w_p, w_f = get_vals(avg_week)
        m_c, m_p, m_f = get_vals(avg_month)
        y_c, y_p, y_f = get_vals(avg_curr_year)
        o_c, o_p, o_f = get_vals(avg_all)

        ac1, ac2, ac3, ac4 = st.columns(4)
        with ac1: st.metric("7-Day Avg", f"{w_c} Kcal", f"{w_p}p / {w_f}f")
        with ac2: st.metric("30-Day Avg", f"{m_c} Kcal", f"{m_p}p / {m_f}f")
        with ac3: st.metric(f"{current_year} Avg", f"{y_c} Kcal", f"{y_p}p / {y_f}f")
        with ac4: st.metric("All-Time Avg", f"{o_c} Kcal", f"{o_p}p / {o_f}f")
            
        st.divider()

        # Monthly Calendar View
        st.subheader("🗓️ Monthly Calendar")

        MIN_YEAR = 2023
        MAX_YEAR = 2029

        def next_month():
            if st.session_state.cal_year == MAX_YEAR and st.session_state.cal_month == 12:
                return
            if st.session_state.cal_month == 12:
                st.session_state.cal_month = 1
                st.session_state.cal_year += 1
            else:
                st.session_state.cal_month += 1
        
        def prev_month():
            if st.session_state.cal_year == MIN_YEAR and st.session_state.cal_month == 1:
                return
            if st.session_state.cal_month == 1:
                st.session_state.cal_month = 12
                st.session_state.cal_year -= 1
            else:
                st.session_state.cal_month -= 1

        col_prev, col_m, col_y, col_next = st.columns([1, 2, 2, 1])
        
        with col_prev:
            st.button("◀", on_click=prev_month, key="btn_prev_m", width='stretch')
        with col_m:
            selected_month_val = st.selectbox(
                "Month", 
                range(1, 13), 
                index=st.session_state.cal_month - 1, 
                format_func=lambda x: calendar.month_name[x],
                label_visibility="collapsed"
            )
            if selected_month_val != st.session_state.cal_month:
                st.session_state.cal_month = selected_month_val
                st.rerun()
        with col_y:
            selected_year_val = st.selectbox(
                "Year", 
                range(MIN_YEAR, MAX_YEAR + 1), 
                index=st.session_state.cal_year - MIN_YEAR, 
                label_visibility="collapsed"
            )
            if selected_year_val != st.session_state.cal_year:
                st.session_state.cal_year = selected_year_val
                st.rerun()
        with col_next:
            st.button("▶", on_click=next_month, key="btn_next_m", width='stretch')

        # Draw Calendar
        sel_year = st.session_state.cal_year
        sel_month = st.session_state.cal_month
        
        cal_obj = calendar.Calendar(firstweekday=0)
        month_days = cal_obj.monthdayscalendar(sel_year, sel_month)
        
        x_vals, y_vals, z_vals, text_vals = [], [], [], []
        hover_cals, hover_pro, hover_fib = [], [], []
        day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        
        mask = (daily_totals['Date'].dt.year == sel_year) & (daily_totals['Date'].dt.month == sel_month)
        month_data = daily_totals[mask].set_index('Date')

        for week_idx, week in enumerate(month_days):
            for day_idx, day_num in enumerate(week):
                x_vals.append(day_names[day_idx])
                y_vals.append(f"Week {week_idx+1}")
                
                if day_num == 0:
                    z_vals.append(None)
                    text_vals.append("")
                    hover_cals.append("")
                    hover_pro.append("")
                    hover_fib.append("")
                else:
                    date_key = pd.Timestamp(year=sel_year, month=sel_month, day=day_num)
                    text_vals.append(str(day_num))
                    
                    if date_key in month_data.index:
                        row = month_data.loc[date_key]
                        c, p, f = row['Calories'], row['Protein'], row['Fiber']
                        z_vals.append(c) 
                        hover_cals.append(int(c))
                        hover_pro.append(int(p))
                        hover_fib.append(int(f))
                    else:
                        z_vals.append(0) 
                        hover_cals.append(0)
                        hover_pro.append(0)
                        hover_fib.append(0)

        fig_cal = go.Figure(data=go.Heatmap(
            x=x_vals, y=y_vals, z=z_vals,
            text=text_vals, texttemplate="%{text}", 
            textfont={"size": 14, "color": "gray"},
            xgap=3, ygap=3,
            colorscale=[[0, '#f8f9fa'], [0.01, '#e6fffa'], [1, '#319795']], 
            showscale=False,
            hovertemplate="<b>Date: %{x}, Day %{text}</b><br><br>🔥 Calories: %{customdata[0]}<br>💪 Protein: %{customdata[1]}g<br>🌾 Fiber: %{customdata[2]}g<extra></extra>",
            customdata=list(zip(hover_cals, hover_pro, hover_fib))
        ))
        
        fig_cal.update_layout(
            height=350,
            margin=dict(l=0, r=0, t=30, b=0),
            yaxis=dict(showgrid=False, zeroline=False, autorange="reversed", fixedrange=True), 
            xaxis=dict(showgrid=False, zeroline=False, side="top", fixedrange=True), 
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Segoe UI")
        )
        st.plotly_chart(fig_cal, width='stretch')

    else:
        st.info("No historical data available yet. Start logging meals to see your stats!")
