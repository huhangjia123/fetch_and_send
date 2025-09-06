import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import os
import json
import pandas as pd
import numpy as np

# 获取环境变量中的敏感信息
email_user = os.getenv('EMAIL_USER')
email_password = os.getenv('EMAIL_PASSWORD')
to_email = os.getenv('TO_EMAIL')

def fetch_financial_data():
    """
    使用AKShare获取实时金融数据
    """
    try:
        import akshare as ak
        
        # 获取上证指数实时行情
        sh_index_df = ak.stock_zh_index_spot()
        sh_index = sh_index_df[sh_index_df['代码'] == 'sh000001'].iloc[0]
        
        # 获取深证成指实时行情
        sz_index_df = ak.stock_zh_index_spot()
        sz_index = sz_index_df[sh_index_df['代码'] == 'sz399001'].iloc[0]
        
        # 获取美元兑人民币汇率
        forex_df = ak.currency_boc_sina()
        usd_cny = forex_df[forex_df['币种'] == '美元'].iloc[0]
        
        # 获取美国标普500指数（通过新浪财经）
        sp500_df = ak.stock_us_spot()
        sp500 = sp500_df[sp500_df['代码'] == '.INX'].iloc[0]
        
        # 组织数据
        data = {
            'domestic_market': {
                'SHANGHAI': {
                    'value': float(sh_index['最新价']),
                    'change': float(sh_index['涨跌额']),
                    'change_pct': float(sh_index['涨跌幅'])
                },
                'SZ_COMP': {
                    'value': float(sz_index['最新价']),
                    'change': float(sz_index['涨跌额']),
                    'change_pct': float(sz_index['涨跌幅'])
                },
                # 其他数据...
            },
            'global_markets': {
                'USD/CNY': {
                    'value': float(usd_cny['现汇卖出价']),
                    'change': 0,  # 需要计算
                    'change_pct': 0  # 需要计算
                },
                'S&P_500': {
                    'value': float(sp500['最新价']),
                    'change': float(sp500['涨跌额']),
                    'change_pct': float(sp500['涨跌幅'])
                }
                # 其他数据...
            }
            # 其他类别数据...
        }
        
        return data
        
    except Exception as e:
        print(f"获取金融数据时出错: {e}")
        # 可以考虑返回None或者部分数据
        return None

def generate_market_analysis(data):
    """
    生成市场分析和解读，按照新手投资者每日必看清单组织
    """
    if not data:
        return "今日无法获取市场数据，请手动检查数据源。"
    
    analysis = []
    
    # 1. 国内市场分析
    analysis.append("# 📊 国内市场分析（核心晴雨表）")
    
    sh_index = data['domestic_market']['SHANGHAI']
    sz_index = data['domestic_market']['SZ_COMP']
    rising = data['domestic_market']['RISING_STOCKS']
    falling = data['domestic_market']['FALLING_STOCKS']
    limit_up = data['domestic_market']['LIMIT_UP']
    limit_down = data['domestic_market']['LIMIT_DOWN']
    
    # 大盘指数分析
    if sh_index['change_pct'] > 0 and sz_index['change_pct'] > 0:
        analysis.append("✅ **大盘指数双双上涨** - 上证指数和深证成指均收涨，市场整体情绪积极。")
    elif sh_index['change_pct'] < 0 and sz_index['change_pct'] < 0:
        analysis.append("⚠️ **大盘指数双双下跌** - 市场整体表现疲软，需要关注下跌原因和后续走势。")
    else:
        analysis.append("🔸 **大盘指数分化** - 主要指数走势不一，显示市场内部结构分化。")
    
    # 涨跌家数分析
    rising_ratio = rising / (rising + falling) * 100
    if rising_ratio > 60:
        analysis.append("✅ **市场普涨格局** - 上涨家数占比超过60%，市场赚钱效应较好。")
    elif rising_ratio < 40:
        analysis.append("⚠️ **市场普跌格局** - 下跌家数占比较多，市场整体情绪偏谨慎。")
    else:
        analysis.append("🔸 **市场涨跌互现** - 上涨和下跌家数基本持平，市场呈现结构性行情。")
    
    # 涨跌停家数分析
    analysis.append(f"📈 **涨停家数**: {limit_up}家 | 📉 **跌停家数**: {limit_down}家")
    if limit_up > 50 and limit_down < 10:
        analysis.append("✅ **市场炒作热情高** - 涨停家数较多而跌停家数较少，显示市场风险偏好较强。")
    elif limit_up < 20 and limit_down > 20:
        analysis.append("⚠️ **市场恐慌情绪上升** - 跌停家数明显多于涨停家数，需要警惕市场风险。")
    
    # 2. 资金动向分析
    analysis.append("\n# 💰 资金动向分析（市场发动机）")
    
    northbound = data['capital_flows']['NORTHBOUND_NET']
    turnover = data['capital_flows']['TURNOVER']
    margin = data['capital_flows']['MARGIN_TRADING']
    
    # 北向资金分析
    if northbound > 30:
        analysis.append("✅ **北向资金大幅净流入** - '聪明钱'大幅流入，通常对市场有积极影响，特别是其重点布局的板块。")
    elif northbound < -30:
        analysis.append("⚠️ **北向资金大幅净流出** - 外资流出可能对市场构成压力，需要关注流出原因和持续性。")
    else:
        analysis.append("🔸 **北向资金小幅波动** - 外资流向对市场影响中性。")
    
    # 成交额分析
    if turnover > 10000:
        analysis.append("✅ **市场成交活跃** - 成交额超过万亿，显示市场参与度高，资金活跃。")
    elif turnover < 8000:
        analysis.append("⚠️ **市场成交萎缩** - 成交额较低，可能反映市场观望情绪浓厚。")
    
    # 融资融券分析
    analysis.append(f"📊 **两融余额**: {margin}亿元 - 杠杆资金水平{(margin-15000)/500:.1f}%")
    
    # 3. 全球市场分析
    analysis.append("\n# 🌍 全球市场分析（外部环境）")
    
    usd_cny = data['global_markets']['USD/CNY']
    usd_index = data['global_markets']['USD_INDEX']
    sp500 = data['global_markets']['S&P_500']
    a50 = data['global_markets']['A50_INDEX']
    vix = data['global_markets']['VIX']
    
    # 汇率分析
    if usd_index['change'] < 0 and usd_cny['change'] < 0:
        analysis.append("✅ **美元走弱，人民币相对走强** - 美元指数下跌，同时人民币对美元升值，这通常有利于A股市场，特别是那些有美元负债和进口依赖型企业。")
    elif usd_index['change'] > 0 and usd_cny['change'] > 0:
        analysis.append("⚠️ **美元走强，人民币承压** - 美元指数上涨带动人民币贬值，这可能对A股市场构成压力，特别是外资可能会流出。")
    
    # 美股影响分析
    if sp500['change_pct'] > 0.5:
        analysis.append("✅ **美股大幅上涨** - 隔夜美股表现强劲，特别是纳斯达克指数上涨明显，这对今日A股科技板块情绪有积极影响。")
    elif sp500['change_pct'] < -0.5:
        analysis.append("⚠️ **美股显著下跌** - 隔夜美股下跌可能对今日A股开盘造成压力，需要关注市场风险偏好变化。")
    
    # A50指数分析
    analysis.append(f"📈 **富时A50指数**: {a50['value']} ({a50['change_pct']:+.2f}%) - 作为A股先行指标，其表现对开盘有预示作用。")
    
    # 恐慌指数分析
    if vix['value'] < 18:
        analysis.append("✅ **市场恐慌指数较低** - VIX指数低于18，显示市场情绪稳定，风险偏好较高。")
    elif vix['value'] > 25:
        analysis.append("⚠️ **市场恐慌指数升高** - VIX指数超过25，显示市场担忧情绪上升，需要谨慎操作。")
    
    # 4. 政策与情绪分析
    analysis.append("\n# 📰 政策与情绪分析（方向盘与催化剂）")
    
    policy = data['policy_sentiment']['RECENT_POLICY']
    news = data['policy_sentiment']['KEY_NEWS']
    sectors = data['policy_sentiment']['SECTOR_PERFORMANCE']
    
    analysis.append(f"🏛️ **近期政策焦点**: {policy}")
    analysis.append(f"📢 **重要新闻**: {news}")
    
    # 板块表现分析
    analysis.append("📊 **板块表现**:")
    for sector, performance in sectors.items():
        sector_name = {
            'AI_CHIP': '人工智能芯片',
            'NEW_ENERGY': '新能源',
            'CONSUMER': '大消费'
        }.get(sector, sector)
        
        if performance > 2:
            analysis.append(f"  ✅ {sector_name}: +{performance:.2f}% - 表现强势，受政策或资金青睐")
        elif performance < -1:
            analysis.append(f"  ⚠️ {sector_name}: {performance:.2f}% - 表现疲软，需关注原因")
        else:
            analysis.append(f"  🔸 {sector_name}: {performance:+.2f}% - 表现平稳")
    
    # 投资建议
    analysis.append("\n# 💡 今日投资建议")
    analysis.append("1. **关注北向资金流向** - 密切跟踪外资动向，特别是其重点增持的板块")
    analysis.append("2. **注意板块轮动** - 市场可能在不同板块间轮动，避免追高")
    analysis.append("3. **控制仓位风险** - 在不确定性中保持适度仓位，留有进退空间")
    analysis.append("4. **关注政策受益板块** - 特别是人工智能、新能源等受政策支持的领域")
    
    analysis.append("\n---")
    analysis.append("**免责声明**: 本分析仅供参考，不构成投资建议。市场有风险，投资需谨慎。")
    
    return "\n".join(analysis)

def format_number(num):
    """格式化数字，保留两位小数并添加正负号"""
    return f"{num:+.2f}"

def create_email_html(data, analysis):
    """
    创建HTML格式的邮件内容，按照四个部分组织
    """
    today = datetime.now().strftime("%Y-%m-%d")
    
    # 先处理分析文本，将换行符替换为HTML换行标签
    analysis_html = analysis.replace('\n', '<br>')
    
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
            .section-title {{ font-size: 1.5em; color: #4a4a4a; margin-top: 30px; margin-bottom: 15px; padding-bottom: 10px; border-bottom: 2px solid #667eea; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📈 新手投资者每日必看市场报告</h1>
            <p>生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        </div>
    """
    
    # 1. 国内市场数据
    html_content += """
        <div class="section">
            <div class="section-title">📊 国内市场（核心晴雨表）</div>
            <table>
                <tr><th>指标</th><th>数值</th><th>涨跌</th><th>涨跌幅</th></tr>
    """
    domestic = data['domestic_market']
    for index in ['SHANGHAI', 'SZ_COMP', 'CHINEXT']:
        values = domestic[index]
        change_class = "positive" if values['change'] > 0 else "negative" if values['change'] < 0 else "neutral"
        change_sign = "+" if values['change'] > 0 else ""
        index_name = {
            'SHANGHAI': '上证指数',
            'SZ_COMP': '深证成指',
            'CHINEXT': '创业板指'
        }.get(index, index)
        html_content += f"""
            <tr>
                <td>{index_name}</td>
                <td>{values['value']}</td>
                <td class="{change_class}">{change_sign}{values['change']}</td>
                <td class="{change_class}">{change_sign}{values['change_pct']}%</td>
            </tr>
        """
    
    # 添加涨跌家数数据
    html_content += f"""
            <tr><td colspan="4"><hr></td></tr>
            <tr>
                <td>上涨家数</td>
                <td colspan="3" class="positive">{domestic['RISING_STOCKS']}家</td>
            </tr>
            <tr>
                <td>下跌家数</td>
                <td colspan="3" class="negative">{domestic['FALLING_STOCKS']}家</td>
            </tr>
            <tr>
                <td>涨停家数</td>
                <td colspan="3" class="positive">{domestic['LIMIT_UP']}家</td>
            </tr>
            <tr>
                <td>跌停家数</td>
                <td colspan="3" class="negative">{domestic['LIMIT_DOWN']}家</td>
            </tr>
    """
    html_content += "</table></div>"
    
    # 2. 资金动向数据
    html_content += """
        <div class="section">
            <div class="section-title">💰 资金动向（市场发动机）</div>
            <table>
                <tr><th>指标</th><th>数值</th><th>说明</th></tr>
    """
    capital = data['capital_flows']
    html_content += f"""
            <tr>
                <td>北向资金净流入</td>
                <td class="{'positive' if capital['NORTHBOUND_NET'] > 0 else 'negative'}">{capital['NORTHBOUND_NET']}亿元</td>
                <td>外资流向指标，正值表示净流入</td>
            </tr>
            <tr>
                <td>沪股通净流入</td>
                <td>{capital['NORTHBOUND_SH']}亿元</td>
                <td>外资在上海市场的流向</td>
            </tr>
            <tr>
                <td>深股通净流入</td>
                <td>{capital['NORTHBOUND_SZ']}亿元</td>
                <td>外资在深圳市场的流向</td>
            </tr>
            <tr>
                <td>两市成交额</td>
                <td>{capital['TURNOVER']}亿元</td>
                <td>市场活跃度指标</td>
            </tr>
            <tr>
                <td>融资融券余额</td>
                <td>{capital['MARGIN_TRADING']}亿元</td>
                <td>杠杆资金水平</td>
            </tr>
    """
    html_content += "</table></div>"
    
    # 3. 全球市场数据
    html_content += """
        <div class="section">
            <div class="section-title">🌍 全球市场（外部环境）</div>
            <table>
                <tr><th>指标</th><th>数值</th><th>涨跌</th><th>涨跌幅</th></tr>
    """
    global_markets = data['global_markets']
    for indicator in ['USD/CNY', 'USD_INDEX', 'S&P_500', 'NASDAQ', 'NIKKEI', 'A50_INDEX', 'VIX']:
        if indicator in global_markets:
            values = global_markets[indicator]
            change_class = "positive" if values['change'] > 0 else "negative" if values['change'] < 0 else "neutral"
            change_sign = "+" if values['change'] > 0 else ""
            indicator_name = {
                'USD/CNY': '美元/人民币',
                'USD_INDEX': '美元指数',
                'S&P_500': '标普500指数',
                'NASDAQ': '纳斯达克指数',
                'NIKKEI': '日经225指数',
                'A50_INDEX': '富时A50指数',
                'VIX': '恐慌指数(VIX)'
            }.get(indicator, indicator)
            html_content += f"""
                <tr>
                    <td>{indicator_name}</td>
                    <td>{values['value']}</td>
                    <td class="{change_class}">{change_sign}{values['change']}</td>
                    <td class="{change_class}">{change_sign}{values['change_pct']}%</td>
                </tr>
            """
    html_content += "</table></div>"
    
    # 4. 政策与情绪数据
    html_content += """
        <div class="section">
            <div class="section-title">📰 政策与情绪（方向盘与催化剂）</div>
            <table>
                <tr><th>类别</th><th>内容</th></tr>
                <tr>
                    <td>近期政策焦点</td>
                    <td>{}</td>
                </tr>
                <tr>
                    <td>重要新闻</td>
                    <td>{}</td>
                </tr>
            </table>
    """.format(data['policy_sentiment']['RECENT_POLICY'], data['policy_sentiment']['KEY_NEWS'])
    
    # 板块表现
    html_content += """
            <h3>📊 板块表现</h3>
            <table>
                <tr><th>板块</th><th>涨跌幅</th><th>表现评价</th></tr>
    """
    sectors = data['policy_sentiment']['SECTOR_PERFORMANCE']
    for sector, performance in sectors.items():
        sector_name = {
            'AI_CHIP': '人工智能芯片',
            'NEW_ENERGY': '新能源',
            'CONSUMER': '大消费'
        }.get(sector, sector)
        
        change_class = "positive" if performance > 0 else "negative" if performance < 0 else "neutral"
        change_sign = "+" if performance > 0 else ""
        
        if performance > 2:
            evaluation = "表现强势，受政策或资金青睐"
        elif performance < -1:
            evaluation = "表现疲软，需关注原因"
        else:
            evaluation = "表现平稳"
            
        html_content += f"""
            <tr>
                <td>{sector_name}</td>
                <td class="{change_class}">{change_sign}{performance}%</td>
                <td>{evaluation}</td>
            </tr>
        """
    html_content += "</table></div>"
    
    # 添加市场分析和解读
    html_content += f"""
        <div class="analysis">
            <div class="section-title">🧠 市场分析与解读</div>
            <div class="highlight">
                {analysis_html}
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
    email_subject = f"📈 新手投资者每日必看市场报告 ({today_str})"
    email_html_body = create_email_html(financial_data, market_analysis)

    # 发送邮件
    success = send_email(email_subject, email_html_body)
    if not success:
        raise Exception("邮件发送失败，请检查配置。")
    
    print("分析报告发送完成！")
    return True

if __name__ == '__main__':
    main()

