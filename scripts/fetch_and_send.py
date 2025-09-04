import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import os
import json
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup

# 获取环境变量中的敏感信息
email_user = os.getenv('EMAIL_USER')
email_password = os.getenv('EMAIL_PASSWORD')
to_email = os.getenv('TO_EMAIL')

def fetch_financial_data():
    """
    获取更全面的金融数据（包括实际数据和市场解读）
    """
    try:
        # 这里使用模拟数据，实际应用中应从API获取真实数据
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        
        # 模拟更多金融市场数据
        data = {
            # 汇率数据
            'exchange_rates': {
                'USD/CNY': {'value': 7.1986, 'change': -0.0023, 'change_pct': -0.03},
                'EUR/CNY': {'value': 7.8234, 'change': 0.0125, 'change_pct': 0.16},
                'JPY/CNY': {'value': 0.0482, 'change': -0.0002, 'change_pct': -0.41},
                'GBP/CNY': {'value': 9.1234, 'change': 0.0234, 'change_pct': 0.26}
            },
            
            # 大宗商品
            'commodities': {
                'Gold': {'value': 1987.50, 'change': 15.30, 'change_pct': 0.78},
                'Oil_Brent': {'value': 85.67, 'change': -1.23, 'change_pct': -1.42},
                'Copper': {'value': 8430, 'change': 120, 'change_pct': 1.44}
            },
            
            # 全球股指
            'global_indices': {
                'SHANGHAI': {'value': 3204.56, 'change': -14.50, 'change_pct': -0.45},
                'SZ_COMP': {'value': 10234.12, 'change': 12.30, 'change_pct': 0.12},
                'S&P_500': {'value': 4550.43, 'change': 40.12, 'change_pct': 0.89},
                'NASDAQ': {'value': 14271.42, 'change': 125.34, 'change_pct': 0.89},
                'NIKKEI': {'value': 33168.27, 'change': -234.56, 'change_pct': -0.70}
            },
            
            # 债券收益率
            'bond_yields': {
                'US_10Y': {'value': 4.23, 'change': 0.05, 'change_pct': 1.20},
                'CN_10Y': {'value': 2.67, 'change': -0.02, 'change_pct': -0.74}
            },
            
            # 市场情绪指标
            'market_sentiment': {
                'VIX': {'value': 17.23, 'change': -1.20, 'change_pct': -6.51},
                'USD_INDEX': {'value': 98.10, 'change': -0.30, 'change_pct': -0.30}
            },
            
            # 宏观经济数据（最新发布）
            'macro_economics': {
                'CPI_YoY': {'value': 2.5, 'previous': 2.8, 'forecast': 2.6},
                'PMI': {'value': 51.2, 'previous': 50.8, 'forecast': 51.0}
            }
        }
        
        return data
    except Exception as e:
        print(f"获取金融数据时出错: {e}")
        return None

def generate_market_analysis(data):
    """
    生成市场分析和解读
    """
    if not data:
        return "今日无法获取市场数据，请手动检查数据源。"
    
    analysis = []
    
    # 美元指数和人民币汇率分析
    usd_cny = data['exchange_rates']['USD/CNY']
    usd_index = data['market_sentiment']['USD_INDEX']
    
    analysis.append("## 📊 人民币汇率与美元指数分析")
    if usd_index['change'] < 0 and usd_cny['change'] < 0:
        analysis.append("✅ **美元走弱，人民币相对走强** - 美元指数下跌，同时人民币对美元升值，这通常有利于A股市场，特别是那些有美元负债和进口依赖型企业。")
    elif usd_index['change'] > 0 and usd_cny['change'] > 0:
        analysis.append("⚠️ **美元走强，人民币承压** - 美元指数上涨带动人民币贬值，这可能对A股市场构成压力，特别是外资可能会流出。")
    else:
        analysis.append("🔸 **汇率走势分化** - 美元指数和人民币汇率出现不同方向变动，需要关注其他影响因素。")
    
    # 美股对A股影响分析
    sp500_change = data['global_indices']['S&P_500']['change_pct']
    analysis.append("\n## 🌍 全球市场影响")
    if sp500_change > 0.5:
        analysis.append("✅ **美股大幅上涨** - 隔夜美股表现强劲，特别是纳斯达克指数上涨明显，这对今日A股科技板块情绪有积极影响。")
    elif sp500_change < -0.5:
        analysis.append("⚠️ **美股显著下跌** - 隔夜美股下跌可能对今日A股开盘造成压力，需要关注市场风险偏好变化。")
    else:
        analysis.append("🔸 **美股波动有限** - 隔夜美股波动不大，对A股影响中性，市场将更多关注内部因素。")
    
    # 大宗商品影响分析
    oil_change = data['commodities']['Oil_Brent']['change_pct']
    copper_change = data['commodities']['Copper']['change_pct']
    analysis.append("\n## ⛽ 大宗商品市场信号")
    if oil_change > 1 and copper_change > 1:
        analysis.append("✅ **大宗商品普涨** - 原油和铜价同时上涨，反映全球需求预期改善，对周期股和资源股有利。")
    elif oil_change < -1 and copper_change < -1:
        analysis.append("⚠️ **大宗商品走弱** - 原油和铜价下跌，可能反映需求担忧，能源和材料板块可能承压。")
    else:
        analysis.append(f"🔸 **商品走势分化** - 原油{oil_change:.2f}%，铜{copper_change:.2f}%，反映不同商品供需面差异。")
    
    # 债券市场分析
    us_10y = data['bond_yields']['US_10Y']['value']
    cn_10y = data['bond_yields']['CN_10Y']['value']
    analysis.append("\n## 📈 债券收益率分析")
    if us_10y > 4.2:
        analysis.append("⚠️ **美债收益率处于高位** - 美国10年期国债收益率超过4.2%，可能限制成长股估值，特别是科技板块。")
    else:
        analysis.append("✅ **美债收益率相对稳定** - 对成长股估值压力有限。")
    
    # 市场情绪指标
    vix = data['market_sentiment']['VIX']['value']
    analysis.append("\n## 😊 市场情绪指标")
    if vix < 18:
        analysis.append("✅ **市场恐慌指数较低** - VIX指数低于18，显示市场情绪稳定，风险偏好较高。")
    elif vix > 25:
        analysis.append("⚠️ **市场恐慌指数升高** - VIX指数超过25，显示市场担忧情绪上升，需要谨慎操作。")
    else:
        analysis.append("🔸 **市场情绪中性** - VIX指数在正常波动范围内。")
    
    # 宏观经济数据影响
    cpi = data['macro_economics']['CPI_YoY']['value']
    pmi = data['macro_economics']['PMI']['value']
    analysis.append("\n## 📊 宏观经济数据解读")
    if cpi < data['macro_economics']['CPI_YoY']['forecast']:
        analysis.append("✅ **通胀压力缓解** - CPI数据低于预期，为货币政策提供更多空间，对股市偏利好。")
    if pmi > 50:
        analysis.append("✅ **制造业保持扩张** - PMI保持在荣枯线以上，显示经济仍在扩张区间。")
    
    # 投资建议摘要
    analysis.append("\n## 💡 今日操作建议")
    analysis.append("1. **关注汇率敏感板块** - 人民币升值利好航空、造纸等板块")
    analysis.append("2. **跟踪外资流向** - 密切关注北向资金动向")
    analysis.append("3. **注意板块轮动** - 周期股与成长股可能出现分化")
    analysis.append("4. **控制仓位风险** - 在不确定性中保持适度仓位")
    
    analysis.append("\n---")
    analysis.append("**免责声明**: 本分析仅供参考，不构成投资建议。市场有风险，投资需谨慎。")
    
    return "\n".join(analysis)

def create_email_html(data, analysis):
    """
    创建HTML格式的邮件内容
    """
    today = datetime.now().strftime("%Y-%m-%d")
    
    html_content = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 900px; margin: 0 auto; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
            .section {{ margin-bottom: 25px; padding: 15px; border: 1px solid #e0e0e0; border-radius: 8px; }}
            .section h2 {{ color: #4a4a4a; border-bottom: 2px solid #667eea; padding-bottom: 8px; }}
            table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
            th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background-color: #f8f9fa; }}
            .positive {{ color: #28a745; font-weight: bold; }}
            .negative {{ color: #dc3545; font-weight: bold; }}
            .neutral {{ color: #6c757d; }}
            .analysis {{ background-color: #f8f9fa; padding: 20px; border-radius: 8px; }}
            .highlight {{ background-color: #fff3cd; padding: 15px; border-radius: 6px; border-left: 4px solid #ffc107; }}
            .footer {{ text-align: center; margin-top: 30px; color: #6c757d; font-size: 14px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📈 每日金融市场简报与解读</h1>
            <p>生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        </div>
    """
    
    # 汇率数据表格
    html_content += """
        <div class="section">
            <h2>💱 汇率市场</h2>
            <table>
                <tr><th>货币对</th><th>汇率</th><th>涨跌</th><th>涨跌幅</th></tr>
    """
    for pair, values in data['exchange_rates'].items():
        change_class = "positive" if values['change'] < 0 else "negative" if values['change'] > 0 else "neutral"
        change_sign = "+" if values['change'] > 0 else ""
        html_content += f"""
            <tr>
                <td>{pair}</td>
                <td>{values['value']}</td>
                <td class="{change_class}">{change_sign}{values['change']}</td>
                <td class="{change_class}">{change_sign}{values['change_pct']}%</td>
            </tr>
        """
    html_content += "</table></div>"
    
    # 全球股指表格
    html_content += """
        <div class="section">
            <h2>🌍 全球主要股指</h2>
            <table>
                <tr><th>指数</th><th>点位</th><th>涨跌</th><th>涨跌幅</th></tr>
    """
    for index, values in data['global_indices'].items():
        change_class = "positive" if values['change'] > 0 else "negative" if values['change'] < 0 else "neutral"
        change_sign = "+" if values['change'] > 0 else ""
        html_content += f"""
            <tr>
                <td>{index}</td>
                <td>{values['value']}</td>
                <td class="{change_class}">{change_sign}{values['change']}</td>
                <td class="{change_class}">{change_sign}{values['change_pct']}%</td>
            </tr>
        """
    html_content += "</table></div>"
    
    # 大宗商品和债券数据
    html_content += """
        <div class="section">
            <h2>📦 大宗商品与债券</h2>
            <table>
                <tr><th>品种</th><th>价格</th><th>涨跌</th><th>涨跌幅</th></tr>
    """
    # 添加大宗商品
    for commodity, values in data['commodities'].items():
        change_class = "positive" if values['change'] > 0 else "negative" if values['change'] < 0 else "neutral"
        change_sign = "+" if values['change'] > 0 else ""
        html_content += f"""
            <tr>
                <td>{commodity}</td>
                <td>{values['value']}</td>
                <td class="{change_class}">{change_sign}{values['change']}</td>
                <td class="{change_class}">{change_sign}{values['change_pct']}%</td>
            </tr>
        """
    # 添加债券收益率
    for bond, values in data['bond_yields'].items():
        change_class = "positive" if values['change'] < 0 else "negative" if values['change'] > 0 else "neutral"
        change_sign = "+" if values['change'] > 0 else ""
        html_content += f"""
            <tr>
                <td>{bond}</td>
                <td>{values['value']}%</td>
                <td class="{change_class}">{change_sign}{values['change']}</td>
                <td class="{change_class}">{change_sign}{values['change_pct']}%</td>
            </tr>
        """
    html_content += "</table></div>"
    
    # 市场情绪指标
    html_content += """
        <div class="section">
            <h2>📊 市场情绪指标</h2>
            <table>
                <tr><th>指标</th><th>数值</th><th>涨跌</th><th>涨跌幅</th></tr>
    """
    for indicator, values in data['market_sentiment'].items():
        change_class = "positive" if values['change'] < 0 else "negative" if values['change'] > 0 else "neutral"
        change_sign = "+" if values['change'] > 0 else ""
        html_content += f"""
            <tr>
                <td>{indicator}</td>
                <td>{values['value']}</td>
                <td class="{change_class}">{change_sign}{values['change']}</td>
                <td class="{change_class}">{change_sign}{values['change_pct']}%</td>
            </tr>
        """
    html_content += "</table></div>"
    
    # 添加市场分析和解读
    html_content += f"""
        <div class="analysis">
            <h2>🧠 市场分析与解读</h2>
            <div class="highlight">
                {analysis.replace('\n', '<br>')}
            </div>
        </div>
    """
    
    html_content += """
        <div class="footer">
            <p>⚠️ 免责声明: 本报告仅供参考，不构成投资建议。市场有风险，投资需谨慎。</p>
            <p>📧 本邮件由GitHub Actions自动生成并发送</p>
        </div>
    </body>
    </html>
    """
    
    return html_content

def send_email(subject, html_content):
    """
    使用QQ邮箱SMTP发送邮件
    """
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = email_user
        msg['To'] = to_email

        # 添加HTML内容
        part_html = MIMEText(html_content, 'html')
        msg.attach(part_html)

        # 连接QQ邮箱SMTP服务器并发送
        server = smtplib.SMTP('smtp.qq.com', 587)
        server.starttls()
        server.login(email_user, email_password)
        server.sendmail(email_user, to_email, msg.as_string())
        server.quit()

        print("邮件发送成功！")
        return True
    except Exception as e:
        print(f"发送邮件时出错: {e}")
        return False

def main():
    """主函数，协调数据获取和邮件发送"""
    print("开始获取金融数据并生成分析报告...")

    # 获取数据
    financial_data = fetch_financial_data()
    
    if not financial_data:
        print("无法获取金融数据")
        return False

    # 生成市场分析
    market_analysis = generate_market_analysis(financial_data)
    
    # 生成邮件内容
    today_str = datetime.now().strftime("%Y-%m-%d")
    email_subject = f"📈 每日金融市场简报与解读 ({today_str})"
    email_html_body = create_email_html(financial_data, market_analysis)

    # 发送邮件
    success = send_email(email_subject, email_html_body)
    if not success:
        raise Exception("邮件发送失败，请检查配置。")
    
    print("分析报告发送完成！")
    return True

if __name__ == '__main__':
    main()
