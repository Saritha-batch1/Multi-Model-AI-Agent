from jinja2 import Template
from datetime import datetime
from models import FinalReport
from milestone1 import DataIngestionEngine
from milestone2 import AnalysisEngine
from milestone3 import SynthesisEngine

class ReportGenerator:
    def generate_html_report(self, report_data: FinalReport) -> str:
        html_template = Template("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Blood Analysis Report</title>
            <style>
                body { font-family: sans-serif; margin: 20px; background-color: #f4f7f6; color: #333; }
                .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
                h1 { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
                h2 { color: #16a085; margin-top: 30px; }
                table { width: 100%; border-collapse: collapse; margin-top: 15px; }
                th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
                th { background-color: #ecf0f1; }
                .High { color: #e74c3c; font-weight: bold; }
                .Normal { color: #27ae60; }
                .Low { color: #f39c12; font-weight: bold; }
                .risk-score { font-size: 24px; font-weight: bold; color: #c0392b; text-align: center; margin: 20px 0; }
                .rec-card { background: #e8f6f3; border-left: 5px solid #1abc9c; padding: 10px; margin-bottom: 10px; }
                .footer { margin-top: 40px; font-size: 0.8em; color: #7f8c8d; text-align: center; border-top: 1px solid #eee; padding-top: 10px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Blood Test Analysis Report</h1>
                <div class="header-info">
                    <div>
                        <strong>Patient:</strong> {{ report.patient_context.gender }}, {{ report.patient_context.age }} years<br>
                        <strong>Diet:</strong> {{ report.patient_context.dietary_preferences|join(', ') }}
                    </div>
                    <div style="text-align: right;">
                        <strong>Date:</strong> {{ report.generated_at }}<br>
                        <strong>Risk Score:</strong> {{ report.analysis.risk_score }}/10 ({% if report.analysis.risk_score < 3 %}Low{% elif report.analysis.risk_score < 6 %}Moderate{% else %}High{% endif %})
                    </div>
                </div>

                {% if report.summary %}
                <div class="summary-box" style="background: #fdf2f2; border: 1px solid #f5c6cb; padding: 15px; border-radius: 4px; margin-bottom: 20px;">
                    <strong>AI Summary:</strong> {{ report.summary }}
                </div>
                {% endif %}

                <h2>Blood Parameters</h2>
                <table>
                    <tr>
                        <th>Parameter</th>
                        <th>Value</th>
                        <th>Unit</th>
                        <th>Status</th>
                    </tr>
                    {% for p in report.parameters %}
                    <tr>
                        <td>{{ p.name }}</td>
                        <td>{{ p.value }}</td>
                        <td>{{ p.unit }}</td>
                        <td class="{{ p.flag }}">{{ p.flag }}</td>
                    </tr>
                    {% endfor %}
                </table>

                <h2>Recommendations</h2>
                {% for rec in report.recommendations %}
                <div class="rec-card">
                    <strong>[{{ rec.category }}]</strong> {{ rec.text }}
                </div>
                {% endfor %}
                <div class="footer">
                    <strong>Disclaimer:</strong> Powered by Groq AI. Not medical advice.
                </div>
            </div>
        </body>
        </html>
        """)
        return html_template.render(report=report_data)

class BloodTestOrchestrator:
    def __init__(self, ingestor: DataIngestionEngine):
        self.ingestor = ingestor
        self.analyzer = AnalysisEngine()
        self.synthesizer = SynthesisEngine()
        self.reporter = ReportGenerator()

    def run_analysis_from_source(self, source_data, context):
        # source_data can be a file path (string) or a dict (json)
        params = self.ingestor.parse_parameters(source_data, context)
        analysis = self.analyzer.analyze_patterns(params, context)
        summary = self.synthesizer.generate_findings_summary(analysis, context)
        recommendations = self.synthesizer.generate_recommendations(params, context)

        final_report = FinalReport(
            patient_context=context,
            parameters=params,
            analysis=analysis,
            recommendations=recommendations,
            summary=summary,
            generated_at=datetime.now().strftime("%Y-%m-%d %H:%M")
        )

        html_content = self.reporter.generate_html_report(final_report)
        with open("report.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        return final_report