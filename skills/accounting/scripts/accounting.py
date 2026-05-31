#!/usr/bin/env python3
"""
记账核心脚本
处理收入、支出记录、分类汇总、查询等操作
"""

import sqlite3
import json
import os
import sys
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), 'accounting.db')

# 支出分类映射（预设分类，可动态扩展）
CATEGORY_KEYWORDS = {
    '饮食': ['吃饭', '外卖', '餐厅', '食物', '零食', '水果', '饮料', '买菜', '烹饪', '餐饮', '米面', '肉类', '蔬菜', '麦当劳', '肯德基', '汉堡', '披萨'],
    '娱乐': ['电影', '游戏', '音乐', '演出', '展览', '旅游', '电影', 'KTV', '酒吧', '娱乐', '综艺', '视频', '会员'],
    '学习': ['书', '课程', '培训', '学费', '文具', '学习', '教育', '考试', '资料', '订阅', '技术', '编程', '教程'],
    '交通': ['打车', '地铁', '公交', '火车', '飞机', '自驾', '停车', '油费', '高铁', '出行', '通勤', '租车'],
    '购物': ['衣服', '鞋子', '包', '化妆品', '电器', '日用品', '网购', '京东', '淘宝', '天猫', '购物', '消费'],
    '医疗': ['医院', '药品', '医生', '体检', '医疗', '牙科', '药店', '保健'],
    '住房': ['房租', '水电', '物业', '房贷', '装修', '家居'],
    '通讯': ['手机', '话费', '网络', '宽带', '流量'],
    '社交': ['请客', '送礼', '红包', '份子', '朋友', '聚会', '人情'],
    '运动': ['健身', '运动', '跑步', '游泳', '瑜伽', '体育'],
}

def get_conn():
    return sqlite3.connect(DB_PATH)

def init_db():
    """初始化数据库（删除旧库重建）"""
    # 删除旧库（如果存在）
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    
    conn = get_conn()
    c = conn.cursor()
    
    # 交易明细表（核心数据源，唯一数据源）
    c.execute('''
        CREATE TABLE transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT,
            description TEXT,
            date DATE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 周收支汇总表
    c.execute('''
        CREATE TABLE weekly_summary (
            year INTEGER NOT NULL,
            week INTEGER NOT NULL,
            week_start DATE NOT NULL,
            week_end DATE NOT NULL,
            total_income REAL DEFAULT 0,
            total_expense REAL DEFAULT 0,
            category_expenses TEXT DEFAULT '{}',
            PRIMARY KEY (year, week)
        )
    ''')
    
    # 月收支汇总表
    c.execute('''
        CREATE TABLE monthly_summary (
            year INTEGER NOT NULL,
            month INTEGER NOT NULL,
            total_income REAL DEFAULT 0,
            total_expense REAL DEFAULT 0,
            category_expenses TEXT DEFAULT '{}',
            PRIMARY KEY (year, month)
        )
    ''')
    
    # 年收支汇总表
    c.execute('''
        CREATE TABLE yearly_summary (
            year INTEGER NOT NULL,
            total_income REAL DEFAULT 0,
            total_expense REAL DEFAULT 0,
            category_expenses TEXT DEFAULT '{}',
            PRIMARY KEY (year)
        )
    ''')
    
    # 索引
    c.execute('CREATE INDEX IF NOT EXISTS idx_trans_date ON transactions(date)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_trans_type ON transactions(type)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_trans_cat ON transactions(category)')
    
    conn.commit()
    conn.close()

def get_week_info(date):
    """获取日期所在的周信息"""
    date = datetime.strptime(date, '%Y-%m-%d') if isinstance(date, str) else date
    year, week, weekday = date.isocalendar()
    week_start = date - timedelta(days=weekday - 1)
    week_end = date + timedelta(days=7 - weekday)
    return year, week, week_start.strftime('%Y-%m-%d'), week_end.strftime('%Y-%m-%d')

def compute_balance(date=None):
    """实时从 transactions 计算余额"""
    conn = get_conn()
    c = conn.cursor()
    
    if date:
        c.execute('''
            SELECT 
                COALESCE(SUM(CASE WHEN type='income' THEN amount ELSE 0 END), 0) as income,
                COALESCE(SUM(CASE WHEN type='expense' THEN amount ELSE 0 END), 0) as expense
            FROM transactions 
            WHERE date <= ?
        ''', (date,))
    else:
        c.execute('''
            SELECT 
                COALESCE(SUM(CASE WHEN type='income' THEN amount ELSE 0 END), 0) as income,
                COALESCE(SUM(CASE WHEN type='expense' THEN amount ELSE 0 END), 0) as expense
            FROM transactions
        ''')
    
    row = c.fetchone()
    conn.close()
    
    income = row[0] if row else 0
    expense = row[1] if row else 0
    return income - expense

def upsert_weekly_summary(c, year, week, week_start, week_end, amount, is_income, category=None):
    """插入或更新周汇总"""
    # 先尝试更新
    if is_income:
        c.execute('''
            INSERT INTO weekly_summary (year, week, week_start, week_end, total_income)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(year, week) DO UPDATE SET total_income = total_income + ?
        ''', (year, week, week_start, week_end, amount, amount))
    else:
        # 支出：更新总支出 + 更新分类
        c.execute('SELECT category_expenses FROM weekly_summary WHERE year=? AND week=?', (year, week))
        row = c.fetchone()
        cat_exp = json.loads(row[0]) if row and row[0] else {} if row else {}
        if category:
            cat_exp[category] = cat_exp.get(category, 0) + amount
        
        c.execute('''
            INSERT INTO weekly_summary (year, week, week_start, week_end, total_expense, category_expenses)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(year, week) DO UPDATE SET 
                total_expense = total_expense + ?,
                category_expenses = ?
        ''', (year, week, week_start, week_end, amount, json.dumps(cat_exp), amount, json.dumps(cat_exp)))

def upsert_monthly_summary(c, year, month, amount, is_income, category=None):
    """插入或更新月汇总"""
    if is_income:
        c.execute('''
            INSERT INTO monthly_summary (year, month, total_income)
            VALUES (?, ?, ?)
            ON CONFLICT(year, month) DO UPDATE SET total_income = total_income + ?
        ''', (year, month, amount, amount))
    else:
        c.execute('SELECT category_expenses FROM monthly_summary WHERE year=? AND month=?', (year, month))
        row = c.fetchone()
        cat_exp = json.loads(row[0]) if row and row[0] else {} if row else {}
        if category:
            cat_exp[category] = cat_exp.get(category, 0) + amount
        
        c.execute('''
            INSERT INTO monthly_summary (year, month, total_expense, category_expenses)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(year, month) DO UPDATE SET 
                total_expense = total_expense + ?,
                category_expenses = ?
        ''', (year, month, amount, json.dumps(cat_exp), amount, json.dumps(cat_exp)))

def upsert_yearly_summary(c, year, amount, is_income, category=None):
    """插入或更新年汇总"""
    if is_income:
        c.execute('''
            INSERT INTO yearly_summary (year, total_income)
            VALUES (?, ?)
            ON CONFLICT(year) DO UPDATE SET total_income = total_income + ?
        ''', (year, amount, amount))
    else:
        c.execute('SELECT category_expenses FROM yearly_summary WHERE year=?', (year,))
        row = c.fetchone()
        cat_exp = json.loads(row[0]) if row and row[0] else {} if row else {}
        if category:
            cat_exp[category] = cat_exp.get(category, 0) + amount
        
        c.execute('''
            INSERT INTO yearly_summary (year, total_expense, category_expenses)
            VALUES (?, ?, ?)
            ON CONFLICT(year) DO UPDATE SET 
                total_expense = total_expense + ?,
                category_expenses = ?
        ''', (year, amount, json.dumps(cat_exp), amount, json.dumps(cat_exp)))

def record_income(amount, description='', date=None):
    """记录收入（同一事务内写入 transactions + 三个汇总表）"""
    if date is None:
        date = datetime.now().strftime('%Y-%m-%d')
    
    conn = get_conn()
    c = conn.cursor()
    
    try:
        # 1. 写入 transactions
        c.execute(
            'INSERT INTO transactions (type, amount, category, description, date) VALUES (?, ?, ?, ?, ?)',
            ('income', amount, '收入', description or '工资/收入', date)
        )
        
        # 2. 更新周汇总
        dt = datetime.strptime(date, '%Y-%m-%d')
        year, week, week_start, week_end = get_week_info(dt)
        upsert_weekly_summary(c, year, week, week_start, week_end, amount, is_income=True)
        
        # 3. 更新月汇总
        upsert_monthly_summary(c, dt.year, dt.month, amount, is_income=True)
        
        # 4. 更新年汇总
        upsert_yearly_summary(c, dt.year, amount, is_income=True)
        
        conn.commit()
        current_balance = compute_balance()
        conn.close()
        return current_balance
        
    except Exception as e:
        conn.rollback()
        conn.close()
        raise e

def record_expense(amount, description='', date=None, category=None):
    """记录支出（同一事务内写入 transactions + 三个汇总表）"""
    if date is None:
        date = datetime.now().strftime('%Y-%m-%d')
    
    if category is None:
        # 如果没有传分类，返回 None 让调用者自己判断
        category = '其他'
    
    conn = get_conn()
    c = conn.cursor()
    
    try:
        # 1. 写入 transactions
        c.execute(
            'INSERT INTO transactions (type, amount, category, description, date) VALUES (?, ?, ?, ?, ?)',
            ('expense', amount, category, description, date)
        )
        
        # 2. 更新周汇总
        dt = datetime.strptime(date, '%Y-%m-%d')
        year, week, week_start, week_end = get_week_info(dt)
        upsert_weekly_summary(c, year, week, week_start, week_end, amount, is_income=False, category=category)
        
        # 3. 更新月汇总
        upsert_monthly_summary(c, dt.year, dt.month, amount, is_income=False, category=category)
        
        # 4. 更新年汇总
        upsert_yearly_summary(c, dt.year, amount, is_income=False, category=category)
        
        conn.commit()
        current_balance = compute_balance()
        conn.close()
        return current_balance
        
    except Exception as e:
        conn.rollback()
        conn.close()
        raise e

def get_balance(date=None):
    """获取指定日期的余额（实时计算）"""
    return compute_balance(date)

def get_monthly_report(year, month):
    """获取指定月份的收支报告"""
    conn = get_conn()
    c = conn.cursor()
    
    c.execute('SELECT total_income, total_expense, category_expenses FROM monthly_summary WHERE year=? AND month=?',
              (year, month))
    row = c.fetchone()
    
    if not row:
        conn.close()
        return None
    
    income, expense, cat_json = row
    categories = json.loads(cat_json) if cat_json else {}
    balance = income - expense
    
    # 获取该月支出明细
    start_date = f'{year}-{month:02d}-01'
    if month == 12:
        end_date = f'{year+1}-01-01'
    else:
        end_date = f'{year}-{month+1:02d}-01'
    
    c.execute('''SELECT description, amount, category, date FROM transactions 
                 WHERE type='expense' AND date>=? AND date<? ORDER BY date''',
              (start_date, end_date))
    expenses = c.fetchall()
    
    conn.close()
    
    return {
        'year': year,
        'month': month,
        'income': income,
        'expense': expense,
        'balance': balance,
        'category_expenses': categories,
        'expense_details': expenses
    }

def get_yearly_report(year):
    """获取指定年份的收支报告"""
    conn = get_conn()
    c = conn.cursor()
    
    c.execute('SELECT total_income, total_expense, category_expenses FROM yearly_summary WHERE year=?', (year,))
    row = c.fetchone()
    
    if not row:
        conn.close()
        return None
    
    income, expense, cat_json = row
    categories = json.loads(cat_json) if cat_json else {}
    balance = income - expense
    
    # 按月统计
    c.execute('''SELECT month, total_income, total_expense, category_expenses FROM monthly_summary 
                 WHERE year=? ORDER BY month''', (year,))
    monthly = []
    for m, inc, exp, cat in c.fetchall():
        cats = json.loads(cat) if cat else {}
        monthly.append({
            'month': m,
            'income': inc,
            'expense': exp,
            'balance': inc - exp,
            'categories': cats
        })
    
    conn.close()
    
    return {
        'year': year,
        'income': income,
        'expense': expense,
        'balance': balance,
        'category_expenses': categories,
        'monthly': monthly
    }

def get_weekly_report(year, week):
    """获取指定周的报告"""
    conn = get_conn()
    c = conn.cursor()
    
    c.execute('SELECT week_start, week_end, total_income, total_expense, category_expenses FROM weekly_summary WHERE year=? AND week=?',
              (year, week))
    row = c.fetchone()
    
    if not row:
        conn.close()
        return None
    
    week_start, week_end, income, expense, cat_json = row
    categories = json.loads(cat_json) if cat_json else {}
    
    conn.close()
    
    return {
        'year': year,
        'week': week,
        'week_start': week_start,
        'week_end': week_end,
        'income': income,
        'expense': expense,
        'balance': income - expense,
        'category_expenses': categories
    }

def get_recent_transactions(limit=10):
    """获取最近交易记录"""
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT type, amount, category, description, date FROM transactions ORDER BY id DESC LIMIT ?',
              (limit,))
    rows = c.fetchall()
    conn.close()
    return rows

def print_report(report):
    """格式化输出报告"""
    if not report:
        print("暂无数据")
        return
    
    if 'month' in report and 'week' not in report:
        # 月报
        print(f"\n{'='*50}")
        print(f"  📅 {report['year']}年{report['month']}月 收支报告")
        print(f"{'='*50}")
        print(f"  💰 收入: ¥{report['income']:.2f}")
        print(f"  💸 支出: ¥{report['expense']:.2f}")
        print(f"  💵 结余: ¥{report['balance']:.2f}")
        
        if report['category_expenses']:
            print(f"\n  📊 支出分类:")
            total_exp = report['expense'] or 1
            for cat, amt in sorted(report['category_expenses'].items(), key=lambda x: -x[1]):
                pct = amt / total_exp * 100
                bar = '█' * int(pct / 5) + '░' * (20 - int(pct / 5))
                print(f"    {cat}: ¥{amt:.2f} ({pct:.1f}%) {bar}")
        
        if report.get('expense_details'):
            print(f"\n  📝 支出明细:")
            for desc, amt, cat, date in report['expense_details'][-5:]:
                print(f"    [{date}] {desc}: ¥{amt:.2f} ({cat})")
    
    elif 'week' in report:
        # 周报
        print(f"\n{'='*50}")
        print(f"  📆 {report['year']}年第{report['week']}周 ({report['week_start']} ~ {report['week_end']})")
        print(f"{'='*50}")
        print(f"  💰 收入: ¥{report['income']:.2f}")
        print(f"  💸 支出: ¥{report['expense']:.2f}")
        print(f"  💵 结余: ¥{report['balance']:.2f}")
        
        if report['category_expenses']:
            print(f"\n  📊 支出分类:")
            total_exp = report['expense'] or 1
            for cat, amt in sorted(report['category_expenses'].items(), key=lambda x: -x[1]):
                pct = amt / total_exp * 100
                bar = '█' * int(pct / 5) + '░' * (20 - int(pct / 5))
                print(f"    {cat}: ¥{amt:.2f} ({pct:.1f}%) {bar}")
    
    elif 'year' in report and 'monthly' in report:
        # 年报
        print(f"\n{'='*50}")
        print(f"  🗓️ {report['year']}年 年度收支报告")
        print(f"{'='*50}")
        print(f"  💰 年度收入: ¥{report['income']:.2f}")
        print(f"  💸 年度支出: ¥{report['expense']:.2f}")
        print(f"  💵 年度结余: ¥{report['balance']:.2f}")
        
        if report['category_expenses']:
            print(f"\n  📊 支出分类:")
            total_exp = report['expense'] or 1
            for cat, amt in sorted(report['category_expenses'].items(), key=lambda x: -x[1]):
                pct = amt / total_exp * 100
                bar = '█' * int(pct / 5) + '░' * (20 - int(pct / 5))
                print(f"    {cat}: ¥{amt:.2f} ({pct:.1f}%) {bar}")
        
        print(f"\n  📅 月度明细:")
        for m in report['monthly']:
            print(f"    {m['month']}月: 收入¥{m['income']:.2f} 支出¥{m['expense']:.2f} 结余¥{m['balance']:.2f}")

def main():
    if len(sys.argv) < 2:
        print("用法: python3 accounting.py <命令> [参数]")
        print("\n命令:")
        print("  income <金额> [描述] [日期]     记录收入")
        print("  expense <金额> [描述] [分类] [日期]    记录支出")
        print("  balance [日期]                  查询余额")
        print("  month [年 月]                   月度报告")
        print("  year [年]                       年度报告")
        print("  week [年 周]                    周报告")
        print("  recent [条数]                   最近记录")
        print("  init                           初始化数据库")
        return
    
    cmd = sys.argv[1]
    
    if cmd == 'init':
        init_db()
        print("[OK] 数据库初始化完成（已重建）")
    
    elif cmd == 'income':
        amount = float(sys.argv[2])
        desc = sys.argv[3] if len(sys.argv) > 3 else ''
        date = sys.argv[4] if len(sys.argv) > 4 else None
        balance = record_income(amount, desc, date)
        print(f"[OK] 已记录收入 ¥{amount:.2f}，当前余额 ¥{balance:.2f}")
    
    elif cmd == 'expense':
        amount = float(sys.argv[2])
        desc = sys.argv[3] if len(sys.argv) > 3 else ''
        category = sys.argv[4] if len(sys.argv) > 4 else None
        date = sys.argv[5] if len(sys.argv) > 5 else None
        balance = record_expense(amount, desc, date, category)
        print(f"[OK] 已记录支出 ¥{amount:.2f}（{category}），当前余额 ¥{balance:.2f}")
    
    elif cmd == 'balance':
        date = sys.argv[2] if len(sys.argv) > 2 else None
        bal = get_balance(date)
        print(f"💵 当前余额: ¥{bal:.2f}")
    
    elif cmd == 'month':
        if len(sys.argv) > 3:
            year, month = int(sys.argv[2]), int(sys.argv[3])
        else:
            now = datetime.now()
            year, month = now.year, now.month
        report = get_monthly_report(year, month)
        print_report(report)
    
    elif cmd == 'year':
        year = int(sys.argv[2]) if len(sys.argv) > 2 else datetime.now().year
        report = get_yearly_report(year)
        print_report(report)
    
    elif cmd == 'week':
        if len(sys.argv) > 3:
            year, week = int(sys.argv[2]), int(sys.argv[3])
        else:
            now = datetime.now()
            year, week, _, _ = get_week_info(now.strftime('%Y-%m-%d'))
        report = get_weekly_report(year, week)
        print_report(report)
    
    elif cmd == 'recent':
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        rows = get_recent_transactions(limit)
        print(f"\n{'='*50}")
        print(f"  最近 {len(rows)} 条记录")
        print(f"{'='*50}")
        for t, a, cat, d, dt in rows:
            typ = '💰' if t == 'income' else '💸'
            print(f"  {typ} [{dt}] {d or cat}: ¥{a:.2f}")
    
    else:
        print(f"未知命令: {cmd}")

if __name__ == '__main__':
    main()