import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import json
import uuid
from itertools import combinations
from collections import defaultdict

# 页面配置
st.set_page_config(
    page_title="Travel-Together",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 自定义CSS样式，优化手机显示
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
            font-size: 16px; /* 防止手机自动缩放 */
        }
    }
    
    /* 通用样式 */
    .main-header {
        text-align: center;
        color: #1E88E5;
        padding: 1rem 0;
    }
    
    /* 行程卡片样式 - 修复显示问题 */
    .day-card {
        border-left: 4px solid #1E88E5;
        padding: 0.8rem 1rem;
        margin: 0.5rem 0;
        background-color: #e3f2fd;
        border-radius: 0 5px 5px 0;
        color: #333333 !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .day-card b {
        color: #1565c0 !important;
    }
    .day-card .time {
        color: #0d47a1 !important;
        font-weight: bold;
    }
    
    /* 开销项目样式 - 修复显示问题 */
    .expense-item {
        border-left: 4px solid #4CAF50;
        padding: 0.8rem;
        margin: 0.3rem 0;
        background-color: #e8f5e8;
        color: #333333 !important;
        border-radius: 0 5px 5px 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
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
    
    /* 表格样式优化 */
    .stDataFrame {
        border-radius: 8px;
        overflow: hidden;
    }
    
    /* 状态标签 */
    .status-tag {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.8em;
        font-weight: bold;
        margin: 2px;
    }
    .status-paid {
        background-color: #e8f5e8;
        color: #2e7d32;
    }
    .status-owed {
        background-color: #fff3e0;
        color: #ef6c00;
    }
    .status-balanced {
        background-color: #e3f2fd;
        color: #1565c0;
    }
</style>
""", unsafe_allow_html=True)

# 初始化session state
def init_session_state():
    if 'travelers' not in st.session_state:
        # 默认4人
        st.session_state.travelers = ['旅行者1', '旅行者2', '旅行者3', '旅行者4']
    
    if 'itinerary' not in st.session_state:
        st.session_state.itinerary = {}
    
    if 'expenses' not in st.session_state:
        st.session_state.expenses = {}
    
    if 'current_day' not in st.session_state:
        st.session_state.current_day = 1
    
    if 'total_days' not in st.session_state:
        st.session_state.total_days = 3
    
    # 用于控制添加行程表单的显示
    if 'show_add_itinerary' not in st.session_state:
        st.session_state.show_add_itinerary = False
        
    # 为每个旅行者生成唯一的ID
    if 'traveler_ids' not in st.session_state:
        st.session_state.traveler_ids = [str(uuid.uuid4())[:8] for _ in st.session_state.travelers]

init_session_state()

# 主标题
st.markdown("<h1 class='main-header'>✈️ Travel-Together 旅行结伴</h1>", unsafe_allow_html=True)

# 创建选项卡
tab1, tab2, tab3 = st.tabs(["👥 同行人员", "🗓️ 行程计划", "💰 开销账单"])

# ========== TAB 1: 同行人员 ==========
with tab1:
    st.header("同行人员管理")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.info(f"当前同行人数: {len(st.session_state.travelers)} 人")
    
    with col2:
        if st.button("➕ 添加人员", use_container_width=True, key="add_person_btn"):
            new_traveler = f"旅行者{len(st.session_state.travelers)+1}"
            st.session_state.travelers.append(new_traveler)
            st.session_state.traveler_ids.append(str(uuid.uuid4())[:8])
    
    # 显示并编辑人员列表
    updated_travelers = []
    for i, traveler in enumerate(st.session_state.travelers):
        cols = st.columns([3, 1])
        with cols[0]:
            traveler_id = st.session_state.traveler_ids[i]
            new_name = st.text_input(f"人员 {i+1} 姓名", 
                                   value=traveler,
                                   key=f"traveler_input_{traveler_id}")
            updated_travelers.append(new_name)
        with cols[1]:
            if len(st.session_state.travelers) > 1:
                if st.button("❌", key=f"del_person_{traveler_id}"):
                    st.session_state.travelers.pop(i)
                    st.session_state.traveler_ids.pop(i)
                    st.rerun()
    
    # 更新旅行者名单
    st.session_state.travelers = updated_travelers
    
    st.markdown("---")
    st.subheader("当前同行人员")
    for i, traveler in enumerate(st.session_state.travelers):
        st.write(f"👤 {i+1}. {traveler}")

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
                            key=lambda x: x['time'].split('-')[0])
        
        for idx, item in enumerate(sorted_items):
            with st.container():
                col1, col2 = st.columns([4, 1])
                with col1:
                    participants_text = ', '.join(item['participants']) if item['participants'] else "所有人"
                    st.markdown(f"""
                    <div class='day-card'>
                        <span class='time'>🕐 {item['time']}</span> - <b>{item['project']}</b><br>
                        🚗 <b>交通</b>：{item['transport'] or '未填写'}<br>
                        📍 <b>地点</b>：{item['location'] or '未填写'}<br>
                        👥 <b>参与人员</b>：{participants_text}
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    if st.button("删除", key=f"del_itinerary_{current_day_str}_{item['id']}"):
                        st.session_state.itinerary[current_day_str] = [
                            i for i in st.session_state.itinerary[current_day_str] 
                            if i['id'] != item['id']
                        ]
                        st.rerun()
    else:
        st.info("暂无行程安排，请点击下方按钮添加行程项目。")
    
    st.markdown("---")
    
    # ========== 添加快捷时间段选择 ==========
    st.markdown("**常用时间段:**")
    time_slots = ["08:00-10:00", "10:00-12:00", "12:00-14:00", 
                 "14:00-16:00", "16:00-18:00", "18:00-20:00", "20:00-22:00"]
    
    # 创建按钮选择时间段
    cols = st.columns(len(time_slots))
    selected_time = None
    
    # 从session state获取当前选择的时间段
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
    
    # ========== 添加行程的表单（默认隐藏） ==========
    if st.session_state.show_add_itinerary or not st.session_state.itinerary[current_day_str]:
        with st.expander("✏️ 添加行程项目", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                # 使用选择的时间段
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
            
            # 选择相关人员
            participants = st.multiselect("相关人员", 
                                        st.session_state.travelers,
                                        default=st.session_state.travelers,
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
                            'id': str(uuid.uuid4())[:8]
                        }
                        st.session_state.itinerary[current_day_str].append(new_item)
                        st.success("行程添加成功！")
                        st.session_state.show_add_itinerary = False
                        st.rerun()
            
            with col2:
                if st.button("❌ 取消", use_container_width=True, 
                           key=f"cancel_itinerary_{current_day_str}"):
                    st.session_state.show_add_itinerary = False
                    st.rerun()
    else:
        # 显示添加行程按钮
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
    
    # 计算每个人的支付总额和类别统计
    def calculate_payment_summary():
        summary = {}
        for day_expenses in st.session_state.expenses.values():
            for expense in day_expenses:
                payer = expense['payer']
                if payer not in summary:
                    summary[payer] = {
                        'total_paid': 0.0,
                        'categories': defaultdict(float)
                    }
                
                summary[payer]['total_paid'] += expense['amount']
                summary[payer]['categories'][expense['category']] += expense['amount']
        
        return summary
    
    # 简化版AA计算函数
    def calculate_simple_aa_summary():
        """
        简化版AA计算，确保付款人总是参与分摊
        """
        aa_expenses_by_group = defaultdict(list)
        
        for day_expenses in st.session_state.expenses.values():
            for expense in day_expenses:
                if expense['category'] != '个人' and 'sharers' in expense:
                    # 确保付款人在分摊人员中
                    sharers = list(expense['sharers'])
                    payer = expense['payer']
                    
                    # 如果付款人不在分摊人员中，自动添加
                    if payer not in sharers:
                        sharers.append(payer)
                    
                    sharers_key = tuple(sorted(sharers))
                    aa_expenses_by_group[sharers_key].append({
                        **expense,
                        'sharers': sharers  # 更新后的分摊人员
                    })
        
        # 计算每组的分摊结果
        aa_results = {}
        
        for sharers, expenses in aa_expenses_by_group.items():
            total_amount = sum(e['amount'] for e in expenses)
            num_sharers = len(sharers)
            average_per_person = total_amount / num_sharers if num_sharers > 0 else 0
            
            # 计算每人支付总额
            payments = {traveler: 0.0 for traveler in sharers}
            for expense in expenses:
                payer = expense['payer']
                payments[payer] += expense['amount']
            
            # 计算每人差额
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
    # 使用简化版AA计算
    aa_results = calculate_simple_aa_summary()
    
    # 创建DataFrame
    summary_data = []
    for traveler in st.session_state.travelers:
        total_paid = payment_summary.get(traveler, {}).get('total_paid', 0.0)
        
        # 计算人均应付和差额
        total_owed = 0.0
        for result in aa_results.values():
            if traveler in result['differences']:
                total_owed += result['differences'][traveler]
        
        # 计算净支付/应收
        net_amount = total_paid - total_owed
        
        # 获取类别统计
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
    aa_total = 0  # 参与AA的总金额
    
    if st.session_state.expenses[expense_day_str]:
        for expense_idx, expense in enumerate(st.session_state.expenses[expense_day_str]):
            # 判断是否为个人消费
            is_personal = expense['category'] == '个人'
            css_class = "personal-expense" if is_personal else "expense-item"
            
            # 获取分摊人信息
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
                        <b>🧾 {expense['item']}</b> - 💰 <b>{expense['amount']:.2f}元</b><br>
                        🏷️ <b>类别</b>: {expense['category']} | 
                        👤 <b>付款人</b>: {expense['payer']}<br>
                        {sharers_text}
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    if st.button("删除", key=f"del_expense_{expense_day_str}_{expense['id']}"):
                        st.session_state.expenses[expense_day_str] = [
                            e for e in st.session_state.expenses[expense_day_str] 
                            if e['id'] != expense['id']
                        ]
                        st.rerun()
            
            total_day_expense += expense['amount']
            if not is_personal:
                aa_total += expense['amount']
        
        st.markdown(f"**当日总开销:** **¥{total_day_expense:.2f}**")
        st.markdown(f"**当日参与AA总金额:** **¥{aa_total:.2f}**")
    else:
        st.info("暂无开销记录")
    
    # ========== 添加开销的表单 ==========
    st.markdown("---")
    
    # 创建一个唯一的表单ID
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
        
        # 选择分摊人（如果不是个人消费）
        sharers = []
        if category != "个人":
            # 默认包含付款人
            default_sharers = st.session_state.travelers.copy()
            
            sharers = st.multiselect("分摊人员（默认全选，付款人自动包含）",
                                   st.session_state.travelers,
                                   default=default_sharers,
                                   key=f"sharers_select_{form_key_suffix}")
            
            # 确保付款人在分摊人员中
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
                        'id': str(uuid.uuid4())[:8]
                    }
                    
                    # 添加分摊人信息
                    if category != "个人":
                        # 确保分摊人员不为空
                        if not sharers:
                            sharers = st.session_state.travelers.copy()
                            if payer not in sharers:
                                sharers.append(payer)
                        
                        new_expense['sharers'] = sharers
                    
                    st.session_state.expenses[expense_day_str].append(new_expense)
                    st.success("开销记录添加成功！")
                    st.rerun()
        
        with col2:
            if st.button("❌ 取消", use_container_width=True,
                       key=f"cancel_expense_{form_key_suffix}"):
                st.rerun()
    
    # ========== AA计算功能 ==========
    st.markdown("---")
    st.subheader("📊 AA费用计算")
    
    if st.button("计算AA分摊方案", use_container_width=True, type="primary", key="calculate_aa_main_btn"):
        if len(st.session_state.travelers) == 0:
            st.error("请先添加同行人员")
        else:
            # 收集所有参与AA的开销
            aa_expenses_by_group = defaultdict(list)
            
            for day_expenses in st.session_state.expenses.values():
                for expense in day_expenses:
                    if expense['category'] != '个人' and 'sharers' in expense:
                        # 确保付款人在分摊人员中
                        sharers = list(expense['sharers'])
                        payer = expense['payer']
                        
                        if payer not in sharers:
                            sharers.append(payer)
                        
                        sharers_key = tuple(sorted(sharers))
                        aa_expenses_by_group[sharers_key].append({
                            **expense,
                            'sharers': sharers
                        })
            
            if not aa_expenses_by_group:
                st.warning("暂无需要AA的开销记录")
            else:
                # 计算每组的分摊结果
                all_transactions = []
                
                for sharers, expenses in aa_expenses_by_group.items():
                    st.markdown(f"### 👥 分摊组: {', '.join(sharers)}")
                    
                    total_amount = sum(e['amount'] for e in expenses)
                    num_sharers = len(sharers)
                    average_per_person = total_amount / num_sharers if num_sharers > 0 else 0
                    
                    # 计算每人支付金额
                    payments = {traveler: 0.0 for traveler in sharers}
                    for expense in expenses:
                        payments[expense['payer']] += expense['amount']
                    
                    # 计算差额
                    differences = {}
                    for traveler in sharers:
                        differences[traveler] = payments[traveler] - average_per_person
                    
                    # 显示该组汇总
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("组内总金额", f"¥{total_amount:.2f}")
                    with col2:
                        st.metric("组内人均", f"¥{average_per_person:.2f}")
                    with col3:
                        st.metric("参与人数", num_sharers)
                    
                    # 显示每人支付情况
                    st.markdown("**每人支付情况:**")
                    for traveler in sharers:
                        paid = payments[traveler]
                        diff = differences[traveler]
                        
                        cols = st.columns(4)
                        with cols[0]:
                            st.write(f"**{traveler}**")
                        with cols[1]:
                            st.write(f"支付: ¥{paid:.2f}")
                        with cols[2]:
                            st.write(f"应付: ¥{average_per_person:.2f}")
                        with cols[3]:
                            if diff > 0.01:
                                st.markdown(f'<span class="status-tag status-paid">应收¥{diff:.2f}</span>', 
                                          unsafe_allow_html=True)
                            elif diff < -0.01:
                                st.markdown(f'<span class="status-tag status-owed">应付¥{abs(diff):.2f}</span>', 
                                          unsafe_allow_html=True)
                            else:
                                st.markdown('<span class="status-tag status-balanced">已平衡</span>', 
                                          unsafe_allow_html=True)
                    
                    # 生成该组的转账方案
                    st.markdown("**💸 组内转账方案:**")
                    
                    # 分离收款人和付款人
                    creditors = [(p, diff) for p, diff in differences.items() if diff > 0.01]
                    debtors = [(p, abs(diff)) for p, diff in differences.items() if diff < -0.01]
                    
                    transactions = []
                    i, j = 0, 0
                    
                    while i < len(creditors) and j < len(debtors):
                        creditor, credit_amt = creditors[i]
                        debtor, debt_amt = debtors[j]
                        
                        amount = min(credit_amt, debt_amt)
                        
                        if amount > 0.01:
                            transactions.append({
                                'from': debtor,
                                'to': creditor,
                                'amount': amount,
                                'group': sharers
                            })
                            all_transactions.append({
                                'from': debtor,
                                'to': creditor,
                                'amount': amount,
                                'group': sharers
                            })
                        
                        # 更新余额
                        creditors[i] = (creditor, credit_amt - amount)
                        debtors[j] = (debtor, debt_amt - amount)
                        
                        if creditors[i][1] < 0.01:
                            i += 1
                        if debtors[j][1] < 0.01:
                            j += 1
                    
                    # 显示该组转账方案
                    if transactions:
                        for t in transactions:
                            st.info(f"**{t['from']}** → **{t['to']}**: ¥{t['amount']:.2f}")
                    else:
                        st.success("✅ 组内费用已平衡，无需转账")
                    
                    st.markdown("---")
                
                # 显示整体转账总结
                if all_transactions:
                    st.markdown("### 📋 总体转账总结")
                    
                    total_transfer = sum(t['amount'] for t in all_transactions)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("总转账金额", f"¥{total_transfer:.2f}")
                    with col2:
                        st.metric("总转账笔数", len(all_transactions))
                    
                    # 按人汇总
                    st.markdown("**按人汇总:**")
                    person_summary = defaultdict(lambda: {'pay': 0.0, 'receive': 0.0})
                    
                    for t in all_transactions:
                        person_summary[t['from']]['pay'] += t['amount']
                        person_summary[t['to']]['receive'] += t['amount']
                    
                    for person in st.session_state.travelers:
                        pay = person_summary[person]['pay']
                        receive = person_summary[person]['receive']
                        if pay > 0 or receive > 0:
                            cols = st.columns(4)
                            with cols[0]:
                                st.write(f"**{person}**")
                            with cols[1]:
                                if pay > 0:
                                    st.write(f"需支付: ¥{pay:.2f}")
                            with cols[2]:
                                if receive > 0:
                                    st.write(f"应收款: ¥{receive:.2f}")
                            with cols[3]:
                                net = receive - pay
                                if net > 0.01:
                                    st.markdown(f'<span class="status-tag status-paid">净收入¥{net:.2f}</span>', 
                                              unsafe_allow_html=True)
                                elif net < -0.01:
                                    st.markdown(f'<span class="status-tag status-owed">净支出¥{abs(net):.2f}</span>', 
                                              unsafe_allow_html=True)
                                else:
                                    st.markdown('<span class="status-tag status-balanced">已平衡</span>', 
                                              unsafe_allow_html=True)

# ========== 数据导出/导入功能 ==========
with st.sidebar:
    st.header("数据管理")
    
    # 导出数据
    if st.button("📥 导出所有数据", key="export_data_btn"):
        data = {
            'travelers': st.session_state.travelers,
            'itinerary': st.session_state.itinerary,
            'expenses': st.session_state.expenses,
            'total_days': st.session_state.total_days
        }
        st.download_button(
            label="下载数据文件",
            data=json.dumps(data, ensure_ascii=False, indent=2),
            file_name=f"travel_together_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
            mime="application/json",
            key="download_data_btn"
        )
    
    # 导入数据
    uploaded_file = st.file_uploader("导入数据", type=['json'], key="upload_data")
    if uploaded_file:
        try:
            data = json.load(uploaded_file)
            st.session_state.travelers = data.get('travelers', st.session_state.travelers)
            st.session_state.itinerary = data.get('itinerary', st.session_state.itinerary)
            st.session_state.expenses = data.get('expenses', st.session_state.expenses)
            st.session_state.total_days = data.get('total_days', st.session_state.total_days)
            st.success("数据导入成功！")
            st.rerun()
        except:
            st.error("数据文件格式错误")
    
    # 清空数据
    if st.button("🗑️ 清空所有数据", type="secondary", key="clear_data_btn"):
        st.session_state.travelers = ['旅行者1', '旅行者2', '旅行者3', '旅行者4']
        st.session_state.itinerary = {}
        st.session_state.expenses = {}
        st.session_state.total_days = 3
        st.session_state.current_day = 1
        st.session_state.traveler_ids = [str(uuid.uuid4())[:8] for _ in st.session_state.travelers]
        st.success("数据已重置！")
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 📖 使用说明")
    st.markdown("""
    **👥 同行人员**
    - 添加/删除成员，自定义姓名
    
    **🗓️ 行程计划**
    - 按天安排，每天可添加多个项目
    - 点击时间按钮快速选择时间段
    
    **💰 开销账单**
    - 实时显示每个人的支付情况
    - 记录每日开销，可选分摊人员
    - "个人"消费不参与AA
    - AA计算支持分组分摊
    
    💡 **提示**: 数据保存在浏览器中，请定期导出备份
    """)

# 页脚
st.markdown("---")
st.markdown("<div style='text-align: center; color: #666;'>Travel-Together ✈️ 让结伴旅行更简单</div>", 
           unsafe_allow_html=True)