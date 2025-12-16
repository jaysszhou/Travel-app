import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import json
import uuid
from itertools import combinations
from collections import defaultdict
import time
import hashlib
import random
import threading

# 页面配置
st.set_page_config(
    page_title="Travel-Together",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 自定义CSS样式
st.markdown("""
<style>
    /* 手机优化 */
    @media (max-width: 768px) {
        .block-container {
            padding: 1rem 0.5rem;
        }
        .stButton > button {
            width: 100%;
            margin: 2px 0;
        }
        .stTextInput > div > input {
            font-size: 16px;
        }
    }
    
    /* 通用样式 */
    .main-header {
        text-align: center;
        color: #1E88E5;
        padding: 1rem 0;
    }
    
    /* 多人协作提示 */
    .collaboration-notice {
        background: linear-gradient(45deg, #2196F3, #21CBF3);
        color: white;
        padding: 12px 20px;
        border-radius: 10px;
        margin: 10px 0;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        animation: slideIn 0.5s ease-out;
    }
    .collaboration-notice .icon {
        font-size: 24px;
        margin-right: 10px;
    }
    @keyframes slideIn {
        from { transform: translateY(-20px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }
    
    /* 用户指示器 - 清晰可见 */
    .user-indicator {
        display: inline-flex;
        align-items: center;
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 0.9em;
        margin: 5px;
        background-color: #ffffff;
        border: 2px solid #1E88E5;
        color: #1565c0;
        font-weight: 500;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .user-you {
        background: linear-gradient(45deg, #4CAF50, #8BC34A) !important;
        border-color: #2E7D32 !important;
        color: white !important;
        font-weight: bold;
    }
    
    /* 在线状态指示器 */
    .online-status {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 8px;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.2); }
        100% { transform: scale(1); }
    }
    .online {
        background-color: #4CAF50;
        box-shadow: 0 0 8px #4CAF50;
    }
    
    /* 同步状态指示 */
    .sync-indicator {
        font-size: 0.8em;
        color: #666;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 5px 0;
    }
    .sync-indicator .dot {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        margin-right: 5px;
    }
    .syncing {
        color: #FF9800;
    }
    .syncing .dot {
        background-color: #FF9800;
        animation: pulse 1s infinite;
    }
    .synced {
        color: #4CAF50;
    }
    .synced .dot {
        background-color: #4CAF50;
    }
    
    /* 自动更新通知 */
    .auto-update-notice {
        background-color: #e3f2fd;
        border-left: 4px solid #2196F3;
        padding: 10px 15px;
        margin: 10px 0;
        border-radius: 0 5px 5px 0;
        animation: fadeIn 0.5s ease-out;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateX(-10px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    /* 行程卡片样式 */
    .day-card {
        border-left: 4px solid #1E88E5;
        padding: 0.8rem 1rem;
        margin: 0.5rem 0;
        background-color: #e3f2fd;
        border-radius: 0 5px 5px 0;
        color: #333333 !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    .day-card:hover {
        transform: translateX(3px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    .day-card b {
        color: #1565c0 !important;
    }
    .day-card .time {
        color: #0d47a1 !important;
        font-weight: bold;
    }
    
    /* 编辑指示器 */
    .edit-indicator {
        font-size: 0.8em;
        color: #666;
        font-style: italic;
        margin-top: 5px;
        display: flex;
        align-items: center;
    }
    .edit-indicator::before {
        content: "✏️";
        margin-right: 5px;
    }
    
    /* 开销项目样式 */
    .expense-item {
        border-left: 4px solid #4CAF50;
        padding: 0.8rem;
        margin: 0.3rem 0;
        background-color: #e8f5e8;
        color: #333333 !important;
        border-radius: 0 5px 5px 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    .expense-item:hover {
        transform: translateX(3px);
        box-shadow: 0 3px 6px rgba(0,0,0,0.15);
    }
    .expense-item b {
        color: #2e7d32 !important;
    }
    .personal-expense {
        border-left-color: #FF9800;
        background-color: #fff3e0;
        color: #333333 !important;
    }
    .personal-expense b {
        color: #ef6c00 !important;
    }
    
    /* 最近更新标记 */
    .recent-update {
        animation: highlight 2s ease-out;
    }
    @keyframes highlight {
        0% { background-color: rgba(255, 255, 200, 0.8); }
        100% { background-color: inherit; }
    }
    
    /* 表格样式优化 */
    .stDataFrame {
        border-radius: 8px;
        overflow: hidden;
    }
    
    /* 状态标签 */
    .status-tag {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.85em;
        font-weight: bold;
        margin: 2px;
    }
    .status-paid {
        background-color: #e8f5e8;
        color: #2e7d32;
        border: 1px solid #4CAF50;
    }
    .status-owed {
        background-color: #fff3e0;
        color: #ef6c00;
        border: 1px solid #FF9800;
    }
    .status-balanced {
        background-color: #e3f2fd;
        color: #1565c0;
        border: 1px solid #2196F3;
    }
</style>
""", unsafe_allow_html=True)

# ========== 智能多人协作模块 ==========
class SmartCollaborativeManager:
    """智能多人协作管理器，自动后台同步"""
    
    def __init__(self):
        self.init_collaboration_state()
        self.setup_auto_sync()
    
    def init_collaboration_state(self):
        """初始化协作相关的session state"""
        # 房间/旅行团ID
        if 'room_id' not in st.session_state:
            st.session_state.room_id = hashlib.md5(str(time.time()).encode()).hexdigest()[:8].upper()
        
        # 用户识别 - 创建持久化的用户ID
        if 'user_id' not in st.session_state:
            # 使用UUID作为持久化的用户ID
            st.session_state.user_id = str(uuid.uuid4())
        
        # 存储用户在各个房间中的名字映射
        if 'user_room_names' not in st.session_state:
            st.session_state.user_room_names = {}
        
        # 在线用户列表
        if 'online_users' not in st.session_state:
            st.session_state.online_users = {}
        
        # 智能同步状态
        if 'sync_status' not in st.session_state:
            st.session_state.sync_status = {
                'last_sync': time.time(),
                'last_update_check': time.time(),
                'auto_sync_count': 0,
                'needs_attention': False
            }
        
        # 数据版本控制
        if 'data_version' not in st.session_state:
            st.session_state.data_version = {
                'number': 0,
                'timestamp': time.time(),
                'last_editor': st.session_state.user_name if 'user_name' in st.session_state else "未知"
            }
        
        # 最近更新记录
        if 'recent_updates' not in st.session_state:
            st.session_state.recent_updates = []
        
        # 基础数据初始化
        self.init_base_data()
    
    def init_base_data(self):
        """初始化基础数据"""
        if 'travelers' not in st.session_state:
            st.session_state.travelers = []
        
        if 'itinerary' not in st.session_state:
            st.session_state.itinerary = {}
        
        if 'expenses' not in st.session_state:
            st.session_state.expenses = {}
        
        if 'current_day' not in st.session_state:
            st.session_state.current_day = 1
        
        if 'total_days' not in st.session_state:
            st.session_state.total_days = 3
        
        if 'traveler_ids' not in st.session_state:
            st.session_state.traveler_ids = []
        
        if 'show_add_itinerary' not in st.session_state:
            st.session_state.show_add_itinerary = False
    
    def setup_auto_sync(self):
        """设置自动同步（后台运行）"""
        # 每30秒自动检查更新
        AUTO_SYNC_INTERVAL = 30
        
        current_time = time.time()
        last_check = st.session_state.sync_status['last_update_check']
        
        # 检查是否到了自动同步的时间
        if current_time - last_check > AUTO_SYNC_INTERVAL:
            st.session_state.sync_status['last_update_check'] = current_time
            self.perform_auto_sync()
    
    def get_or_create_user_name(self, room_id):
        """获取或创建用户在指定房间的名字"""
        # 生成用户在房间的唯一键
        user_room_key = f"{st.session_state.user_id}_{room_id}"
        
        # 如果用户已经有在这个房间的名字，直接返回
        if user_room_key in st.session_state.user_room_names:
            return st.session_state.user_room_names[user_room_key]
        
        # 否则，创建一个新的名字（旅行者X）
        # 获取当前房间所有用户已使用的编号
        used_numbers = set()
        for key, name in st.session_state.user_room_names.items():
            # 只检查同一房间的其他用户
            if key.endswith(f"_{room_id}") and name.startswith("旅行者"):
                try:
                    num = int(name[3:])  # 提取"旅行者"后面的数字
                    used_numbers.add(num)
                except:
                    pass
        
        # 找出最小未使用的编号
        next_num = 1
        while next_num in used_numbers:
            next_num += 1
        
        new_name = f"旅行者{next_num}"
        st.session_state.user_room_names[user_room_key] = new_name
        return new_name
    
    def update_user_activity(self):
        """更新用户活动时间"""
        current_time = time.time()
        
        # 获取用户在当前房间的名字
        user_name = self.get_or_create_user_name(st.session_state.room_id)
        
        # 更新session中的用户名
        st.session_state.user_name = user_name
        
        # 为用户分配一个颜色（基于用户ID，确保一致性）
        if 'user_color' not in st.session_state:
            # 使用用户ID的哈希值来生成一致的颜色
            color_hash = hashlib.md5(st.session_state.user_id.encode()).hexdigest()
            colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F']
            color_index = int(color_hash, 16) % len(colors)
            st.session_state.user_color = colors[color_index]
        
        user_key = f"{st.session_state.user_id}_{st.session_state.room_id}"
        
        st.session_state.online_users[user_key] = {
            'user_id': st.session_state.user_id,
            'user_name': st.session_state.user_name,
            'room_id': st.session_state.room_id,
            'last_active': current_time,
            'color': st.session_state.user_color
        }
        
        # 清理长时间不活跃的用户（5分钟）
        for key in list(st.session_state.online_users.keys()):
            if current_time - st.session_state.online_users[key]['last_active'] > 300:
                del st.session_state.online_users[key]
        
        # 确保当前用户在旅行者名单中
        if st.session_state.user_name not in st.session_state.travelers:
            st.session_state.travelers.append(st.session_state.user_name)
            st.session_state.traveler_ids.append(st.session_state.user_id[:8])  # 使用用户ID前8位
    
    def get_online_users(self, max_inactive=30):
        """获取在线用户列表"""
        current_time = time.time()
        online_users = []
        
        for user_key, user_info in st.session_state.online_users.items():
            if user_info['room_id'] == st.session_state.room_id:
                if current_time - user_info['last_active'] < max_inactive:
                    online_users.append(user_info)
        
        # 按最后活动时间排序
        online_users.sort(key=lambda x: x['last_active'], reverse=True)
        
        # 更新当前用户的活动时间
        self.update_user_activity()
        
        return online_users
    
    def increment_data_version(self, action, details):
        """增加数据版本"""
        st.session_state.data_version['number'] += 1
        st.session_state.data_version['timestamp'] = time.time()
        st.session_state.data_version['last_editor'] = st.session_state.user_name
        
        # 记录更新历史（最多保留10条）
        update_record = {
            'user': st.session_state.user_name,
            'action': action,
            'details': details,
            'timestamp': time.time(),
            'version': st.session_state.data_version['number']
        }
        
        st.session_state.recent_updates.insert(0, update_record)
        if len(st.session_state.recent_updates) > 10:
            st.session_state.recent_updates = st.session_state.recent_updates[:10]
        
        # 标记需要其他用户注意
        self.flag_needs_attention()
        
        return st.session_state.data_version['number']
    
    def flag_needs_attention(self):
        """标记需要其他用户注意更新"""
        for user_key, user_info in st.session_state.online_users.items():
            if user_info['room_id'] == st.session_state.room_id and user_info['user_id'] != st.session_state.user_id:
                # 在实际应用中，这里应该发送通知给其他用户
                # 这里我们只是标记状态
                st.session_state.sync_status['needs_attention'] = True
    
    def check_for_updates(self):
        """检查是否有更新（模拟）"""
        # 模拟检查：如果5秒内有其他用户更新，则提示
        current_time = time.time()
        last_editor_time = st.session_state.data_version.get('timestamp', 0)
        last_editor = st.session_state.data_version.get('last_editor', '未知')
        
        # 如果不是当前用户编辑的，并且是最近5秒内的更新
        if last_editor != st.session_state.user_name and (current_time - last_editor_time) < 5:
            return {
                'has_updates': True,
                'last_editor': last_editor,
                'time_since_update': current_time - last_editor_time
            }
        
        return {'has_updates': False}
    
    def perform_auto_sync(self):
        """执行自动同步（后台）"""
        update_check = self.check_for_updates()
        
        if update_check['has_updates']:
            # 标记同步状态
            st.session_state.sync_status['last_sync'] = time.time()
            st.session_state.sync_status['auto_sync_count'] += 1
            
            # 在实际应用中，这里应该从服务器获取并合并数据
            # 这里我们只是更新状态
            return True
        
        return False
    
    def get_sync_status_text(self):
        """获取同步状态文本"""
        last_sync_ago = int(time.time() - st.session_state.sync_status['last_sync'])
        
        if last_sync_ago < 5:
            return "🔄 刚刚同步"
        elif last_sync_ago < 30:
            return f"✅ {last_sync_ago}秒前同步"
        else:
            return f"⏳ {last_sync_ago}秒前同步"

# 初始化协作管理器
collab = SmartCollaborativeManager()

# 主标题
st.markdown("<h1 class='main-header'>✈️ Travel-Together 旅行结伴</h1>", unsafe_allow_html=True)

# ========== 智能协作状态栏 ==========
with st.container():
    col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
    
    with col1:
        # 显示协作状态
        online_users = collab.get_online_users()
        online_count = len(online_users)
        
        if online_count > 1:
            st.markdown(f"""
            <div class='collaboration-notice'>
                <span class='icon'>👥</span>
                <b>多人协作模式</b> - {online_count} 人正在共同编辑
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style='text-align: center; padding: 10px; background-color: #000000; border-radius: 10px;'>
                <span class='icon'>👤</span>
                <b>单人模式</b> - 分享旅行团ID邀请他人加入
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        # 房间ID显示
        room_id = st.text_input("旅行团ID", 
                               value=st.session_state.room_id,
                               help="分享此ID给同伴，加入同一旅行团",
                               key="room_id_input")
        # 如果房间ID发生变化，需要重新获取用户名
        if room_id != st.session_state.room_id:
            st.session_state.room_id = room_id
            # 房间变化时，确保更新用户名
            collab.update_user_activity()
    
    with col3:
        # 用户设置 - 显示当前用户名并允许修改
        current_user_name = st.session_state.user_name
        new_user_name = st.text_input("你的昵称", 
                                     value=current_user_name,
                                     key="user_name_input")
        
        # 如果用户修改了名字，更新到房间映射中
        if new_user_name != current_user_name and new_user_name:
            user_room_key = f"{st.session_state.user_id}_{st.session_state.room_id}"
            st.session_state.user_room_names[user_room_key] = new_user_name
            st.session_state.user_name = new_user_name
            
            # 更新旅行者名单
            if current_user_name in st.session_state.travelers:
                index = st.session_state.travelers.index(current_user_name)
                st.session_state.travelers[index] = new_user_name
            
            # 更新所有行程和开销中的参与者名字
            for day, items in st.session_state.itinerary.items():
                for item in items:
                    if 'participants' in item and current_user_name in item['participants']:
                        item['participants'] = [new_user_name if x == current_user_name else x for x in item['participants']]
                    if 'editor' in item and item['editor'] == current_user_name:
                        item['editor'] = new_user_name
            
            for day, expenses in st.session_state.expenses.items():
                for expense in expenses:
                    if 'payer' in expense and expense['payer'] == current_user_name:
                        expense['payer'] = new_user_name
                    if 'sharers' in expense and current_user_name in expense['sharers']:
                        expense['sharers'] = [new_user_name if x == current_user_name else x for x in expense['sharers']]
                    if 'editor' in expense and expense['editor'] == current_user_name:
                        expense['editor'] = new_user_name
            
            collab.increment_data_version("修改昵称", f"{current_user_name} -> {new_user_name}")
            st.rerun()
    
    with col4:
        # 同步状态指示器
        sync_text = collab.get_sync_status_text()
        st.markdown(f"""
        <div class='sync-indicator synced'>
            <span class='dot'></span>
            {sync_text}
        </div>
        """, unsafe_allow_html=True)

# 显示在线用户
st.markdown("### 👥 在线成员")
online_users = collab.get_online_users()
if online_users:
    # 创建列布局显示在线用户
    cols = st.columns(min(4, len(online_users)))
    
    for idx, user in enumerate(online_users):
        with cols[idx % len(cols)]:
            is_you = (user['user_id'] == st.session_state.user_id)
            user_class = "user-indicator user-you" if is_you else "user-indicator"
            
            st.markdown(f"""
            <div class='{user_class}' style='border-color: {user.get('color', '#1E88E5')};'>
                <span class='online-status online' style='background-color: {user.get('color', '#4CAF50')};'></span>
                <strong>{user['user_name']}{" (你)" if is_you else ""}</strong>
            </div>
            """, unsafe_allow_html=True)
else:
    st.info("等待其他成员加入...")

# ========== 自动后台同步提示 ==========
# 检查是否有最近更新
update_check = collab.check_for_updates()
if update_check.get('has_updates'):
    time_since = int(update_check['time_since_update'])
    
    # st.markdown(f"""
    # <div class='auto-update-notice'>
    #     <strong>🔄 数据已自动同步！</strong><br>
    #     刚刚由 <b>{update_check['last_editor']}</b> 更新了数据
    # </div>
    # """, unsafe_allow_html=True)

# 显示最近更新历史（简洁版）
if st.session_state.recent_updates and len(st.session_state.recent_updates) > 0:
    with st.expander("📝 最近活动", expanded=False):
        for update in st.session_state.recent_updates[:3]:  # 只显示最近3条
            time_ago = int(time.time() - update['timestamp'])
            if time_ago < 60:
                time_text = f"{time_ago}秒前"
            elif time_ago < 3600:
                time_text = f"{time_ago//60}分钟前"
            else:
                time_text = f"{time_ago//3600}小时前"
            
            st.caption(f"**{update['user']}** {update['action']}了 {update['details']} ({time_text})")

st.markdown("---")

# ========== 创建选项卡 ==========
tab1, tab2, tab3 = st.tabs(["👥 同行人员", "🗓️ 行程计划", "💰 开销账单"])

# ========== TAB 1: 同行人员 ==========
with tab1:
    st.header("同行人员管理")
    
    # 显示当前在线成员自动加入
    st.markdown("**👥 已加入的成员:**")
    for user in online_users:
        st.write(f"• {user['user_name']}")
    
    st.markdown("---")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.info(f"当前同行人数: {len(st.session_state.travelers)} 人")
    
    with col2:
        if st.button("➕ 添加人员", use_container_width=True, key="add_person_btn"):
            # 生成一个新的旅行者名字
            used_numbers = set()
            for traveler in st.session_state.travelers:
                if traveler.startswith("旅行者"):
                    try:
                        num = int(traveler[3:])
                        used_numbers.add(num)
                    except:
                        pass
            
            # 找出最小未使用的编号
            next_num = 1
            while next_num in used_numbers:
                next_num += 1
            
            new_traveler = f"旅行者{next_num}"
            st.session_state.travelers.append(new_traveler)
            st.session_state.traveler_ids.append(str(uuid.uuid4())[:8])
            collab.increment_data_version("添加人员", new_traveler)
            st.rerun()
    
    # 显示并编辑人员列表
    updated_travelers = []
    updated_traveler_ids = []
    
    for i, traveler in enumerate(st.session_state.travelers):
        cols = st.columns([3, 1])
        with cols[0]:
            traveler_id = st.session_state.traveler_ids[i] if i < len(st.session_state.traveler_ids) else str(uuid.uuid4())[:8]
            new_name = st.text_input(f"人员 {i+1} 姓名", 
                                   value=traveler,
                                   key=f"traveler_input_{traveler_id}")
            updated_travelers.append(new_name)
            updated_traveler_ids.append(traveler_id)
        with cols[1]:
            # 不能删除当前用户自己
            if len(st.session_state.travelers) > 1 and traveler != st.session_state.user_name:
                if st.button("❌", key=f"del_person_{traveler_id}"):
                    st.session_state.travelers.pop(i)
                    if i < len(st.session_state.traveler_ids):
                        st.session_state.traveler_ids.pop(i)
                    collab.increment_data_version("删除人员", traveler)
                    st.rerun()
            else:
                st.write("")  # 占位
    
    # 更新旅行者名单
    st.session_state.travelers = updated_travelers
    st.session_state.traveler_ids = updated_traveler_ids
    
    st.markdown("---")
    st.subheader("当前同行人员")
    for i, traveler in enumerate(st.session_state.travelers):
        is_current_user = traveler == st.session_state.user_name
        st.write(f"👤 **{i+1}. {traveler}{' (你)' if is_current_user else ''}**")

# ========== TAB 2: 行程计划 ==========
with tab2:
    st.header("行程计划")
    
    # 天数控制
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        days = st.slider("旅行天数", min_value=1, max_value=30, 
                        value=st.session_state.total_days, key="days_slider")
        st.session_state.total_days = days
    
    with col2:
        if st.button("◀️ 前一天", use_container_width=True, key="prev_day_btn"):
            if st.session_state.current_day > 1:
                st.session_state.current_day -= 1
    
    with col3:
        if st.button("后一天 ▶️", use_container_width=True, key="next_day_btn"):
            if st.session_state.current_day < st.session_state.total_days:
                st.session_state.current_day += 1
    
    # 显示当前天数
    st.markdown(f"### 📅 第 {st.session_state.current_day} 天")
    
    # 初始化当天的行程
    current_day_str = str(st.session_state.current_day)
    if current_day_str not in st.session_state.itinerary:
        st.session_state.itinerary[current_day_str] = []
    
    # ========== 显示当天的行程 ==========
    st.subheader("当日行程安排")
    
    if st.session_state.itinerary[current_day_str]:
        # 按时间排序
        sorted_items = sorted(st.session_state.itinerary[current_day_str], 
                            key=lambda x: x.get('time', '').split('-')[0])
        
        for idx, item in enumerate(sorted_items):
            with st.container():
                col1, col2 = st.columns([4, 1])
                with col1:
                    participants_text = ', '.join(item.get('participants', [])) if item.get('participants') else "所有人"
                    
                    # 检查是否为最近更新（30秒内）
                    is_recent = time.time() - item.get('edit_time', 0) < 30
                    recent_class = " recent-update" if is_recent else ""
                    
                    st.markdown(f"""
                    <div class='day-card{recent_class}'>
                        <span class='time'>🕐 {item.get('time', '未设置')}</span> - <b>{item.get('project', '未命名')}</b><br>
                        🚗 <b>交通</b>：{item.get('transport', '未填写')}<br>
                        📍 <b>地点</b>：{item.get('location', '未填写')}<br>
                        👥 <b>参与人员</b>：{participants_text}
                        <div class='edit-indicator'>由 {item.get('editor', '未知')} 添加</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    if st.button("删除", key=f"del_itinerary_{current_day_str}_{item.get('id', idx)}"):
                        st.session_state.itinerary[current_day_str] = [
                            i for i in st.session_state.itinerary[current_day_str] 
                            if i.get('id') != item.get('id')
                        ]
                        collab.increment_data_version("删除行程", item.get('project', ''))
                        st.rerun()
    else:
        st.info("暂无行程安排，请点击下方按钮添加行程项目。")
    
    st.markdown("---")
    
    # ========== 添加快捷时间段选择 ==========
    st.markdown("**常用时间段:**")
    time_slots = ["08:00-10:00", "10:00-12:00", "12:00-14:00", 
                 "14:00-16:00", "16:00-18:00", "18:00-20:00", "20:00-22:00"]
    
    cols = st.columns(len(time_slots))
    selected_time = None
    
    time_key = f"selected_time_{current_day_str}"
    if time_key not in st.session_state:
        st.session_state[time_key] = time_slots[0]
    
    for idx, time_slot in enumerate(time_slots):
        with cols[idx]:
            is_selected = (st.session_state.get(time_key) == time_slot)
            if st.button(time_slot, key=f"time_btn_{current_day_str}_{idx}", 
                        type="primary" if is_selected else "secondary"):
                st.session_state[time_key] = time_slot
                st.session_state.show_add_itinerary = True
                st.rerun()
    
    # ========== 添加行程的表单 ==========
    if st.session_state.show_add_itinerary or not st.session_state.itinerary[current_day_str]:
        with st.expander("✏️ 添加行程项目", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                time_range = st.text_input("时间段", 
                                         value=st.session_state.get(time_key, time_slots[0]), 
                                         key=f"time_input_{current_day_str}")
                project = st.text_input("具体项目", placeholder="例如：参观故宫", 
                                      key=f"project_input_{current_day_str}")
            with col2:
                transport = st.text_input("交通工具", placeholder="例如：地铁、步行", 
                                        key=f"transport_input_{current_day_str}")
                location = st.text_input("具体地点", placeholder="例如：北京市东城区", 
                                       key=f"location_input_{current_day_str}")
            
            participants = st.multiselect("相关人员", 
                                        st.session_state.travelers,
                                        default=[st.session_state.user_name],
                                        key=f"participants_select_{current_day_str}")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ 确认添加", type="primary", use_container_width=True, 
                           key=f"confirm_itinerary_{current_day_str}"):
                    if time_range and project:
                        new_item = {
                            'time': time_range,
                            'project': project,
                            'transport': transport,
                            'location': location,
                            'participants': participants,
                            'id': str(uuid.uuid4())[:8],
                            'editor': st.session_state.user_name,
                            'edit_time': time.time()
                        }
                        st.session_state.itinerary[current_day_str].append(new_item)
                        st.success("行程添加成功！")
                        collab.increment_data_version("添加行程", project)
                        st.session_state.show_add_itinerary = False
                        st.rerun()
            
            with col2:
                if st.button("❌ 取消", use_container_width=True, 
                           key=f"cancel_itinerary_{current_day_str}"):
                    st.session_state.show_add_itinerary = False
                    st.rerun()
    else:
        if st.button("➕ 添加新行程", type="primary", use_container_width=True,
                   key=f"add_new_itinerary_{current_day_str}"):
            st.session_state.show_add_itinerary = True
            st.rerun()

# ========== TAB 3: 开销账单 ==========
with tab3:
    st.header("旅行开销账单")
    
    # ========== 选择要查看/编辑的天数 ==========
    expense_day = st.selectbox("选择日期", 
                              range(1, st.session_state.total_days + 1),
                              key="expense_day_select_main")
    
    expense_day_str = str(expense_day)
    if expense_day_str not in st.session_state.expenses:
        st.session_state.expenses[expense_day_str] = []
    
    # ========== 实时账单汇总表格 ==========
    st.subheader("💰 实时账单汇总")
    
    def calculate_payment_summary():
        summary = {}
        for day_expenses in st.session_state.expenses.values():
            for expense in day_expenses:
                payer = expense.get('payer', '')
                if payer not in summary:
                    summary[payer] = {
                        'total_paid': 0.0,
                        'categories': defaultdict(float)
                    }
                
                summary[payer]['total_paid'] += expense.get('amount', 0.0)
                summary[payer]['categories'][expense.get('category', '其他')] += expense.get('amount', 0.0)
        
        return summary
    
    def calculate_simple_aa_summary():
        aa_expenses_by_group = defaultdict(list)
        
        for day_expenses in st.session_state.expenses.values():
            for expense in day_expenses:
                if expense.get('category') != '个人' and 'sharers' in expense:
                    sharers = list(expense.get('sharers', []))
                    payer = expense.get('payer', '')
                    
                    if payer not in sharers:
                        sharers.append(payer)
                    
                    sharers_key = tuple(sorted(sharers))
                    aa_expenses_by_group[sharers_key].append({
                        **expense,
                        'sharers': sharers
                    })
        
        aa_results = {}
        
        for sharers, expenses in aa_expenses_by_group.items():
            total_amount = sum(e.get('amount', 0.0) for e in expenses)
            num_sharers = len(sharers)
            average_per_person = total_amount / num_sharers if num_sharers > 0 else 0
            
            payments = {traveler: 0.0 for traveler in sharers}
            for expense in expenses:
                payer = expense.get('payer', '')
                payments[payer] += expense.get('amount', 0.0)
            
            differences = {}
            for traveler in sharers:
                differences[traveler] = payments[traveler] - average_per_person
            
            aa_results[sharers] = {
                'total_amount': total_amount,
                'average_per_person': average_per_person,
                'payments': payments,
                'differences': differences
            }
        
        return aa_results
    
    # 创建汇总表格
    payment_summary = calculate_payment_summary()
    aa_results = calculate_simple_aa_summary()
    
    summary_data = []
    for traveler in st.session_state.travelers:
        total_paid = payment_summary.get(traveler, {}).get('total_paid', 0.0)
        
        total_owed = 0.0
        for result in aa_results.values():
            if traveler in result['differences']:
                total_owed += result['differences'][traveler]
        
        net_amount = total_paid - total_owed
        
        category_stats = []
        if traveler in payment_summary:
            for category, amount in payment_summary[traveler]['categories'].items():
                category_stats.append(f"{category}:¥{amount:.1f}")
        
        summary_data.append({
            '姓名': traveler,
            '总支付金额': f"¥{total_paid:.2f}",
            '类别统计': ', '.join(category_stats) if category_stats else "无",
            '人均应付': f"¥{total_owed:.2f}" if total_owed != 0 else "¥0.00",
            '净额': f"应收¥{abs(net_amount):.2f}" if net_amount > 0.01 else 
                   f"应付¥{abs(net_amount):.2f}" if net_amount < -0.01 else "已平衡"
        })
    
    if summary_data:
        df_summary = pd.DataFrame(summary_data)
        st.dataframe(df_summary, use_container_width=True, hide_index=True)
    else:
        st.info("暂无开销记录")
    
    st.markdown("---")
    
    # ========== 显示当天的开销 ==========
    st.subheader(f"第 {expense_day} 天开销记录")
    total_day_expense = 0
    aa_total = 0
    
    if st.session_state.expenses[expense_day_str]:
        for expense_idx, expense in enumerate(st.session_state.expenses[expense_day_str]):
            is_personal = expense.get('category') == '个人'
            css_class = "personal-expense" if is_personal else "expense-item"
            
            # 检查是否为最近更新
            is_recent = time.time() - expense.get('edit_time', 0) < 30
            if is_recent:
                css_class += " recent-update"
            
            sharers_text = ""
            if not is_personal and 'sharers' in expense:
                sharers_count = len(expense['sharers'])
                all_travelers_count = len(st.session_state.travelers)
                if sharers_count == all_travelers_count:
                    sharers_text = "👥 全体分摊"
                else:
                    sharers_text = f"👥 {sharers_count}人分摊: {', '.join(expense['sharers'])}"
            
            with st.container():
                col1, col2 = st.columns([5, 1])
                with col1:
                    st.markdown(f"""
                    <div class='{css_class}'>
                        <b>🧾 {expense.get('item', '未命名')}</b> - 💰 <b>{expense.get('amount', 0):.2f}元</b><br>
                        🏷️ <b>类别</b>: {expense.get('category', '未分类')} | 
                        👤 <b>付款人</b>: {expense.get('payer', '未知')}<br>
                        {sharers_text}
                        <div class='edit-indicator'>由 {expense.get('editor', '未知')} 记录</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    if st.button("删除", key=f"del_expense_{expense_day_str}_{expense.get('id', expense_idx)}"):
                        st.session_state.expenses[expense_day_str] = [
                            e for e in st.session_state.expenses[expense_day_str] 
                            if e.get('id') != expense.get('id')
                        ]
                        collab.increment_data_version("删除开销", expense.get('item', ''))
                        st.rerun()
            
            total_day_expense += expense.get('amount', 0.0)
            if not is_personal:
                aa_total += expense.get('amount', 0.0)
        
        st.markdown(f"**当日总开销:** **¥{total_day_expense:.2f}**")
        st.markdown(f"**当日参与AA总金额:** **¥{aa_total:.2f}**")
    else:
        st.info("暂无开销记录")
    
    # ========== 添加开销的表单 ==========
    st.markdown("---")
    
    form_key_suffix = f"day{expense_day_str}"
    
    with st.expander("➕ 添加开销记录", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            payer = st.selectbox("付款人", 
                               st.session_state.travelers,
                               key=f"payer_select_{form_key_suffix}")
            item = st.text_input("具体项目", 
                               placeholder="例如：午餐、门票",
                               key=f"expense_item_input_{form_key_suffix}")
        with col2:
            category = st.selectbox("种类", 
                                  ["餐饮", "交通", "门票", "住宿", "购物", "个人"],
                                  key=f"category_select_{form_key_suffix}")
            amount = st.number_input("金额（元）", 
                                   min_value=0.0, 
                                   step=1.0,
                                   format="%.2f",
                                   key=f"amount_input_{form_key_suffix}")
        
        sharers = []
        if category != "个人":
            default_sharers = st.session_state.travelers.copy()
            sharers = st.multiselect("分摊人员（默认全选，付款人自动包含）",
                                   st.session_state.travelers,
                                   default=default_sharers,
                                   key=f"sharers_select_{form_key_suffix}")
            
            if payer not in sharers:
                sharers.append(payer)
                st.info(f"已自动将付款人 {payer} 添加到分摊人员中")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ 确认添加开销", type="primary", use_container_width=True,
                       key=f"confirm_expense_{form_key_suffix}"):
                if item and amount > 0:
                    new_expense = {
                        'payer': payer,
                        'item': item,
                        'category': category,
                        'amount': float(amount),
                        'day': expense_day,
                        'id': str(uuid.uuid4())[:8],
                        'editor': st.session_state.user_name,
                        'edit_time': time.time()
                    }
                    
                    if category != "个人":
                        if not sharers:
                            sharers = st.session_state.travelers.copy()
                            if payer not in sharers:
                                sharers.append(payer)
                        
                        new_expense['sharers'] = sharers
                    
                    st.session_state.expenses[expense_day_str].append(new_expense)
                    st.success("开销记录添加成功！")
                    collab.increment_data_version("添加开销", f"{item}: ¥{amount}")
                    st.rerun()
        
        with col2:
            if st.button("❌ 取消", use_container_width=True,
                       key=f"cancel_expense_{form_key_suffix}"):
                st.rerun()

# ========== 数据导出/导入功能 ==========
with st.sidebar:
    st.header("📊 数据管理")
    
    # 协作说明
    st.markdown("### 👥 多人协作说明")
    st.markdown("""
    1. **分享旅行团ID**给同伴
    2. 同伴输入相同ID加入
    3. **数据自动同步** (每30秒)
    4. 所有人的修改会实时合并
    """)
    
    # 显示当前协作状态
    online_users = collab.get_online_users()
    st.metric("在线人数", len(online_users))
    st.caption(f"数据版本: {st.session_state.data_version['number']}")
    
    st.markdown("---")
    
    # 导出数据
    if st.button("📥 导出数据", key="export_data_btn", use_container_width=True):
        data = {
            'room_id': st.session_state.room_id,
            'travelers': st.session_state.travelers,
            'itinerary': st.session_state.itinerary,
            'expenses': st.session_state.expenses,
            'total_days': st.session_state.total_days,
            'traveler_ids': st.session_state.traveler_ids,
            'data_version': st.session_state.data_version,
            'user_room_names': st.session_state.user_room_names,
            'user_id': st.session_state.user_id,
            'export_time': time.time(),
            'export_by': st.session_state.user_name
        }
        
        json_str = json.dumps(data, ensure_ascii=False, indent=2)
        st.download_button(
            label="下载JSON文件",
            data=json_str,
            file_name=f"travel_together_{st.session_state.room_id}_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
            mime="application/json",
            key="download_data_btn"
        )
    
    # 导入数据
    st.markdown("### 导入数据")
    uploaded_file = st.file_uploader("选择JSON文件", type=['json'], 
                                    help="导入之前导出的旅行数据", key="upload_data")
    
    if uploaded_file:
        try:
            data = json.load(uploaded_file)
            
            if st.checkbox("确认导入数据（这将覆盖当前数据）"):
                if st.button("开始导入", type="primary"):
                    st.session_state.travelers = data.get('travelers', st.session_state.travelers)
                    st.session_state.itinerary = data.get('itinerary', st.session_state.itinerary)
                    st.session_state.expenses = data.get('expenses', st.session_state.expenses)
                    st.session_state.total_days = data.get('total_days', st.session_state.total_days)
                    st.session_state.traveler_ids = data.get('traveler_ids', st.session_state.traveler_ids)
                    st.session_state.user_room_names = data.get('user_room_names', st.session_state.user_room_names)
                    
                    # 如果导入的数据包含用户ID，使用它
                    if 'user_id' in data:
                        st.session_state.user_id = data['user_id']
                    
                    imported_version = data.get('data_version', {})
                    if imported_version:
                        st.session_state.data_version = imported_version
                    
                    st.success("数据导入成功！")
                    st.rerun()
        except Exception as e:
            st.error(f"导入失败: {str(e)}")
    
    # 清空数据
    if st.button("🗑️ 清空数据", type="secondary", 
                use_container_width=True, key="clear_data_btn"):
        if st.checkbox("确认清空所有数据？"):
            current_room = st.session_state.room_id
            current_user_id = st.session_state.user_id
            current_user_name = st.session_state.user_name
            current_user_room_names = st.session_state.user_room_names
            
            # 重新初始化数据
            collab.init_base_data()
            
            st.session_state.room_id = current_room
            st.session_state.user_id = current_user_id
            st.session_state.user_room_names = current_user_room_names
            
            # 重新获取用户名
            collab.update_user_activity()
            
            st.session_state.data_version = {
                'number': 0,
                'timestamp': time.time(),
                'last_editor': st.session_state.user_name
            }
            
            st.success("数据已重置！")
            st.rerun()
    
    st.markdown("---")
    st.markdown("### 📖 使用说明")
    st.markdown("""
    **智能协作功能：**
    - ✅ 自动同步 (每30秒)
    - ✅ 实时在线用户显示
    - ✅ 更新自动合并
    - ✅ 无需手动操作
    
    **💡 提示：**
    - 数据自动保存在浏览器中
    - 定期导出备份重要数据
    - 清空数据不会清除房间ID
    
    **⚡ 后台运行：**
    - 同步完全自动化
    - 无复杂设置
    - 专注旅行规划
    """)

# ========== 页面底部状态栏 ==========
st.markdown("---")

# 计算页面统计信息
total_itinerary_items = sum(len(day_items) for day_items in st.session_state.itinerary.values())
total_expenses = sum(len(day_expenses) for day_expenses in st.session_state.expenses.values())
total_expense_amount = sum(
    expense.get('amount', 0) 
    for day_expenses in st.session_state.expenses.values() 
    for expense in day_expenses
)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("在线人数", len(online_users))
with col2:
    st.metric("行程项目", total_itinerary_items)
with col3:
    st.metric("开销记录", total_expenses)
with col4:
    st.metric("总开销", f"¥{total_expense_amount:.2f}")

# 页脚信息
st.markdown(f"""
<div style='text-align: center; color: #666; padding: 20px 0;'>
    <div>✈️ <b>Travel-Together 智能协作版</b></div>
    <div style='font-size: 0.9em; margin-top: 5px;'>
        旅行团ID: <code>{st.session_state.room_id}</code> | 
        自动同步: {collab.get_sync_status_text()} | 
        数据版本: {st.session_state.data_version['number']}
    </div>
</div>
""", unsafe_allow_html=True)

# ========== 后台自动同步 ==========
# 在页面加载时自动运行同步检查
collab.setup_auto_sync()