import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta, time
from database import init_db, get_db
from travel_logic import create_trip, get_trip_by_invite_code, get_trip_by_id, get_schedule_items, delete_schedule_item, add_activity, vote_for_item, finalize_proposal
import models

# --- Page Config ---
st.set_page_config(page_title="TravelSync - 多人協作旅遊規畫", layout="wide")

# --- Initialize Database ---
init_db()

# --- Session State Initialization ---
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "current_trip_id" not in st.session_state:
    st.session_state.current_trip_id = None

def render_schedule_item(item):
    """Render a single schedule item or proposal as a card."""
    with st.container(border=True):
        col1, col2, col3 = st.columns([1, 4, 1.5])
        
        # Time or Proposal status
        with col1:
            if item.is_proposal:
                st.warning("🗳️ 提案中")
            else:
                st.info(f"🕒 {item.start_time.strftime('%H:%M') if item.start_time else '未定'}")
        
        # Title and Notes
        with col2:
            st.markdown(f"**{item.title}**")
            if item.location:
                st.caption(f"📍 {item.location}")
            if item.note:
                st.markdown(f"> {item.note}")
            
            # Display votes for proposals
            if item.is_proposal:
                vote_count = len(item.votes)
                st.write(f"目前票數：{vote_count}")
                voters = ", ".join([v.user_name for v in item.votes])
                if voters:
                    st.caption(f"投票者：{voters}")
        
        # Actions
        with col3:
            if item.is_proposal:
                if st.button("➕ 投票", key=f"vote_{item.id}", use_container_width=True):
                    db = get_db()
                    if vote_for_item(db, item.id, st.session_state.user_name):
                        st.toast("投票成功！")
                        st.rerun()
                    else:
                        st.warning("您已經投過票了")
                
                if st.button("✅ 採納", key=f"final_{item.id}", use_container_width=True):
                    db = get_db()
                    finalize_proposal(db, item.id)
                    st.success("已採納為正式行程")
                    st.rerun()
            
            if st.button("🗑️ 刪除", key=f"del_{item.id}", use_container_width=True):
                db = get_db()
                if delete_schedule_item(db, item.id):
                    st.toast("已刪除項目")
                    st.rerun()

# --- Header ---
st.title("✈️ TravelSync")
st.markdown("---")

# --- Sidebar ---
with st.sidebar:
    st.header("👤 使用者設定")
    user_name = st.text_input("輸入您的暱稱", value=st.session_state.user_name)
    if user_name:
        st.session_state.user_name = user_name
        st.success(f"歡迎, {user_name}!")
    
    st.divider()
    
    st.header("🗺️ 行程管理")
    
    # Create Trip
    with st.expander("✨ 建立新行程"):
        trip_title = st.text_input("旅遊名稱", placeholder="例如：東京五日遊")
        col1, col2 = st.columns(2)
        start_date = col1.date_input("開始日期", min_value=date.today())
        end_date = col2.date_input("結束日期", min_value=start_date)
        
        if st.button("確認建立", key="btn_create_trip"):
            if not user_name:
                st.error("請先輸入暱稱")
            elif not trip_title:
                st.error("請輸入旅遊名稱")
            else:
                db = get_db()
                new_trip = create_trip(db, trip_title, start_date, end_date)
                st.session_state.current_trip_id = new_trip.id
                st.success(f"行程「{trip_title}」建立成功！")
                st.rerun()

    # Join Trip
    with st.expander("🔗 加入行程"):
        invite_code = st.text_input("輸入邀請碼")
        if st.button("確認加入", key="btn_join_trip"):
            if not user_name:
                st.error("請先輸入暱稱")
            else:
                db = get_db()
                trip = get_trip_by_invite_code(db, invite_code)
                if trip:
                    st.session_state.current_trip_id = trip.id
                    st.success(f"已成功加入「{trip.title}」")
                    st.rerun()
                else:
                    st.error("找不到該邀請碼對應的行程")

# --- Main Content ---
if not st.session_state.user_name:
    st.info("👋 請在側邊欄輸入暱稱以開始使用。")
elif not st.session_state.current_trip_id:
    st.info("📅 請選擇「建立新行程」或「加入現有行程」開始您的規劃。")
else:
    # --- Display Trip Content ---
    db = get_db()
    current_trip = get_trip_by_id(db, st.session_state.current_trip_id)
    
    if current_trip:
        st.header(f"📍 {current_trip.title}")
        st.caption(f"📅 日期：{current_trip.start_date} 至 {current_trip.end_date} | 🔑 邀請碼：`{current_trip.invite_code}`")
        
        # Day Tabs
        num_days = (current_trip.end_date - current_trip.start_date).days + 1
        tabs = st.tabs([f"第 {i+1} 天" for i in range(num_days)])
        
        for i, tab in enumerate(tabs):
            with tab:
                day_num = i + 1
                items = get_schedule_items(db, current_trip.id, day_num)
                
                if not items:
                    st.write("目前沒有行程項目。")
                else:
                    for item in items:
                        render_schedule_item(item)
                
                st.divider()
                
                # Add Item Form
                with st.expander(f"➕ 新增第 {day_num} 天行程項目"):
                    with st.form(key=f"form_add_{day_num}"):
                        new_title = st.text_input("景點名稱")
                        col_a, col_b = st.columns(2)
                        new_time = col_a.time_input("開始時間", value=None)
                        new_duration = col_b.number_input("停留時長 (分鐘)", min_value=1, value=60)
                        new_location = st.text_input("地點/地址")
                        new_note = st.text_area("備註")
                        is_prop = st.checkbox("這是一個提案 (開放投票)")
                        
                        if st.form_submit_button("新增到行程"):
                            if not new_title:
                                st.error("請輸入景點名稱")
                            else:
                                add_activity(
                                    db, current_trip.id, day_num, 
                                    new_title, new_time, new_duration, 
                                    new_location, new_note, is_prop
                                )
                                st.success("已新增！")
                                st.rerun()
    else:
        st.session_state.current_trip_id = None
        st.error("行程不存在。")
        st.rerun()
