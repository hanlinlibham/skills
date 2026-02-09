"""
Report Generator
报告生成和通知推送
"""

import os
import json
import smtplib
from datetime import datetime
from typing import List, Dict, Any
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

import pandas as pd


class ReportGenerator:
    """
    报告生成器
    
    生成 Excel/Markdown 报告，并支持飞书/邮件推送
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化报告生成器
        
        Parameters:
        -----------
        config : dict
            配置信息，包含通知设置
        """
        self.config = config or {}
        self.today = datetime.now()
        self.today_str = self.today.strftime('%Y%m%d')
        
    def to_excel(self, anomalies: List[Dict[str, Any]], output_dir: str = 'output') -> str:
        """
        生成 Excel 报告
        
        Parameters:
        -----------
        anomalies : list of dict
            异常资产列表
        output_dir : str
            输出目录
            
        Returns:
        --------
        str : 生成的文件路径
        """
        if not anomalies:
            return ""
        
        os.makedirs(output_dir, exist_ok=True)
        
        df = pd.DataFrame(anomalies)
        df = df.sort_values('z_score', key=abs, ascending=False)
        
        file_path = os.path.join(output_dir, f"asset_anomaly_report_{self.today_str}.xlsx")
        df.to_excel(file_path, index=False, sheet_name='异常波动资产')
        
        print(f"✅ Excel 报告已生成: {file_path}")
        return file_path
    
    def to_markdown(self, anomalies: List[Dict[str, Any]]) -> str:
        """
        生成 Markdown 报告
        
        Parameters:
        -----------
        anomalies : list of dict
            异常资产列表
            
        Returns:
        --------
        str : Markdown 格式的报告文本
        """
        if not anomalies:
            return "# 资产异常波动报告\n\n✅ 今日未发现异常资产。\n"
        
        lines = [
            "# 📊 资产异常波动报告",
            "",
            f"**报告时间**: {self.today.strftime('%Y-%m-%d %H:%M')}",
            f"**异常资产数**: {len(anomalies)} 个",
            "",
            "---",
            "",
            "## 异常汇总",
            "",
            "| 资产 | 类别 | 涨跌幅 | Z值 | 方向 |",
            "|-----|-----|-------:|----:|:----:|",
        ]
        
        for item in anomalies:
            direction = "🚀 大涨" if item['z_score'] > 0 else "📉 大跌"
            lines.append(
                f"| {item['name']} | {item['category']} | "
                f"{item['today_return']:+.2f}% | {item['z_score']:+.2f} | {direction} |"
            )
        
        lines.extend([
            "",
            "---",
            "",
            "*报告由 Asset Monitor 自动生成*",
        ])
        
        return '\n'.join(lines)
    
    def to_text(self, anomalies: List[Dict[str, Any]]) -> str:
        """
        生成纯文本报告（适合飞书/微信推送）
        
        Parameters:
        -----------
        anomalies : list of dict
            异常资产列表
            
        Returns:
        --------
        str : 纯文本格式的报告
        """
        if not anomalies:
            return "📊 资产异常监控\n\n✅ 今日未发现异常资产，所有资产均在正常波动范围内。"
        
        lines = [
            "📊 资产异常波动报告",
            f"报告时间: {self.today.strftime('%Y-%m-%d')}",
            "",
            f"共发现 {len(anomalies)} 个异常资产:",
            "",
        ]
        
        for i, item in enumerate(anomalies, 1):
            emoji = "🚀" if item['z_score'] > 0 else "📉"
            lines.append(
                f"{i}. {emoji} {item['name']} ({item['category']})\n"
                f"   涨跌幅: {item['today_return']:+.2f}% | Z值: {item['z_score']:+.2f} | {item['direction']}"
            )
        
        return '\n'.join(lines)
    
    def send_feishu(self, content_or_file: str, webhook: str = None) -> bool:
        """
        发送飞书通知
        
        Parameters:
        -----------
        content_or_file : str
            文本内容或文件路径
        webhook : str, optional
            飞书 webhook URL，默认从配置读取
            
        Returns:
        --------
        bool : 是否发送成功
        """
        webhook = webhook or self.config.get('feishu', {}).get('webhook')
        if not webhook:
            print("⚠️ 未配置飞书 webhook")
            return False
        
        try:
            import urllib.request
            
            # 判断是文件还是文本
            if os.path.exists(content_or_file):
                # 发送文件
                # 注意：飞书 webhook 直接发送文件需要上传到飞书服务器
                # 这里简化处理，发送文本摘要
                content = f"📊 资产异常报告已生成\n文件: {content_or_file}"
            else:
                content = content_or_file
            
            data = json.dumps({
                "msg_type": "text",
                "content": {"text": content}
            }).encode('utf-8')
            
            req = urllib.request.Request(webhook, data=data, method='POST')
            req.add_header('Content-Type', 'application/json')
            
            with urllib.request.urlopen(req, timeout=10) as response:
                result = json.loads(response.read().decode('utf-8'))
                if result.get('code') == 0:
                    print("✅ 飞书推送成功")
                    return True
                else:
                    print(f"❌ 飞书推送失败: {result}")
                    return False
                    
        except Exception as e:
            print(f"❌ 飞书推送失败: {e}")
            return False
    
    def send_email(self, 
                   file_path: str, 
                   recipients: List[str] = None,
                   subject: str = None) -> bool:
        """
        发送邮件报告
        
        Parameters:
        -----------
        file_path : str
            附件文件路径
        recipients : list, optional
            收件人列表，默认从配置读取
        subject : str, optional
            邮件主题
            
        Returns:
        --------
        bool : 是否发送成功
        """
        email_config = self.config.get('email', {})
        recipients = recipients or email_config.get('recipients', [])
        
        if not recipients:
            print("⚠️ 未配置邮件收件人")
            return False
        
        sender = email_config.get('sender', 'itseekqq@gmail.com')
        password = email_config.get('password', '')
        smtp_server = email_config.get('smtp_server', 'smtp.gmail.com')
        smtp_port = email_config.get('smtp_port', 587)
        
        subject = subject or f"资产异常波动报告 {self.today_str}"
        
        try:
            msg = MIMEMultipart()
            msg['From'] = sender
            msg['To'] = ', '.join(recipients)
            msg['Subject'] = subject
            
            body = f"附件为今日资产异常波动监控报告。\n\n报告时间: {self.today.strftime('%Y-%m-%d %H:%M')}"
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # 添加附件
            if os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    attachment = MIMEBase('application', 'octet-stream')
                    attachment.set_payload(f.read())
                encoders.encode_base64(attachment)
                filename = os.path.basename(file_path)
                attachment.add_header(
                    'Content-Disposition',
                    f'attachment; filename= "{filename}"'
                )
                msg.attach(attachment)
            
            # 发送
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(sender, password)
            server.sendmail(sender, recipients, msg.as_string())
            server.quit()
            
            print(f"✅ 邮件发送成功: {', '.join(recipients)}")
            return True
            
        except Exception as e:
            print(f"❌ 邮件发送失败: {e}")
            return False
