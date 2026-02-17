import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime
import os
from src.infrastructure.database import FraudDatabase


class ReportGenerator:
    
    def __init__(self, database: FraudDatabase):
        self.db = database
        self.output_dir = 'data/reports'
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_incident_report(self) -> str:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        pdf_path = os.path.join(self.output_dir, f'fraud_incident_report_{timestamp}.pdf')
        
        doc = SimpleDocTemplate(pdf_path, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        title = Paragraph("Fraud Shield - Incident Analysis Report", title_style)
        story.append(title)
        story.append(Spacer(1, 0.3*inch))
        
        date_style = ParagraphStyle(
            'DateStyle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#7f8c8d'),
            alignment=TA_CENTER
        )
        report_date = Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", date_style)
        story.append(report_date)
        story.append(Spacer(1, 0.5*inch))
        
        stats = self.db.get_total_stats()
        
        summary_data = [
            ['Metric', 'Value'],
            ['Total Transactions Analyzed', f"{stats.get('total_analyzed', 0):,}"],
            ['Fraud Cases Detected', f"{stats.get('total_frauds', 0):,}"],
            ['Fraud Rate', f"{(stats.get('total_frauds', 0) / max(stats.get('total_analyzed', 1), 1) * 100):.2f}%"],
            ['Total Fraud Amount', f"${stats.get('total_fraud_amount', 0):,.2f}"],
            ['Average Confidence Score', f"{stats.get('avg_confidence', 0):.4f}"]
        ]
        
        summary_table = Table(summary_data, colWidths=[3.5*inch, 2.5*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecf0f1')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7'))
        ]))
        
        story.append(Paragraph("Executive Summary", styles['Heading2']))
        story.append(Spacer(1, 0.2*inch))
        story.append(summary_table)
        story.append(Spacer(1, 0.5*inch))
        
        chart_path = self._generate_fraud_chart()
        if os.path.exists(chart_path):
            story.append(Paragraph("Fraud Distribution Analysis", styles['Heading2']))
            story.append(Spacer(1, 0.2*inch))
            story.append(Image(chart_path, width=6*inch, height=3.5*inch))
            story.append(Spacer(1, 0.3*inch))
        
        story.append(PageBreak())
        
        recent_frauds = self.db.get_recent_frauds(limit=20)
        
        story.append(Paragraph("Recent Fraud Incidents", styles['Heading2']))
        story.append(Spacer(1, 0.2*inch))
        
        if recent_frauds:
            fraud_data = [['Transaction ID', 'User ID', 'Amount', 'Risk', 'Confidence']]
            
            for fraud in recent_frauds[:15]:
                fraud_data.append([
                    fraud['transaction_id'][:15] + '...',
                    fraud['user_id'][:12],
                    f"${fraud['amount']:.2f}",
                    fraud['risk_level'],
                    f"{fraud['confidence_score']:.3f}"
                ])
            
            fraud_table = Table(fraud_data, colWidths=[1.8*inch, 1.5*inch, 1.2*inch, 0.9*inch, 1*inch])
            fraud_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#fadbd8')),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#c0392b'))
            ]))
            
            story.append(fraud_table)
        else:
            story.append(Paragraph("No fraud incidents recorded yet.", styles['Normal']))
        
        story.append(Spacer(1, 0.5*inch))
        
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#95a5a6'),
            alignment=TA_CENTER
        )
        footer = Paragraph(
            "This report is confidential and intended for authorized personnel only.<br/>"
            "Fraud Shield v1.0 - Production Ready Anti-Fraud Engine",
            footer_style
        )
        story.append(footer)
        
        doc.build(story)
        return pdf_path
    
    def _generate_fraud_chart(self) -> str:
        hourly_data = self.db.get_fraud_count_by_hour()
        
        if not hourly_data:
            return ""
        
        hours = [int(item['hour']) for item in hourly_data]
        totals = [item['total'] for item in hourly_data]
        frauds = [item['fraud_count'] for item in hourly_data]
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
        
        ax1.bar(hours, totals, color='#3498db', alpha=0.7, label='Total')
        ax1.bar(hours, frauds, color='#e74c3c', alpha=0.9, label='Fraud')
        ax1.set_xlabel('Hour of Day')
        ax1.set_ylabel('Transaction Count')
        ax1.set_title('Transaction Volume by Hour')
        ax1.legend()
        ax1.grid(axis='y', alpha=0.3)
        
        fraud_rates = [(f/t*100 if t > 0 else 0) for f, t in zip(frauds, totals)]
        ax2.plot(hours, fraud_rates, marker='o', color='#e74c3c', linewidth=2)
        ax2.fill_between(hours, fraud_rates, alpha=0.3, color='#e74c3c')
        ax2.set_xlabel('Hour of Day')
        ax2.set_ylabel('Fraud Rate (%)')
        ax2.set_title('Fraud Rate Trend')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        chart_path = os.path.join(self.output_dir, 'temp_chart.png')
        plt.savefig(chart_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return chart_path
