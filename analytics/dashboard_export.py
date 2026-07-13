import json
import logging
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))
from analytics.reports import KPIReportGenerator
from analytics.trend_analysis import TrendAnalyzer
from analytics.anomaly_detection import AnomalyDetector
from analytics.insights import InsightGenerator

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class DashboardExporter:
    """Orchestrator that generates and exports all JSONs for the dashboard."""
    
    def __init__(self, output_dir: str = "data/processed/analytics"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def export_all(self):
        logging.info("Starting Dashboard JSON Export...")
        
        # Initialize modules
        kpi_gen = KPIReportGenerator()
        trend_analyzer = TrendAnalyzer()
        anomaly_detector = AnomalyDetector()
        insight_gen = InsightGenerator()
        
        # 1. KPIs
        kpis = kpi_gen.generate_kpis()
        self._save_json(kpis, "kpi_summary.json")
        
        # Update SQLite top rankings
        kpi_gen.generate_top_rankings()
        
        # 2. Trends
        trends = trend_analyzer.analyze_trends()
        self._save_json(trends, "trend_analysis.json")
        
        # 3. Correlations
        correlations = trend_analyzer.get_correlations()
        self._save_json(correlations, "correlations.json")
        
        # 4. Anomalies
        anomalies = anomaly_detector.detect_anomalies()
        self._save_json(anomalies, "anomalies.json")
        
        # 5. Insights
        insights = insight_gen.generate_insights()
        self._save_json(insights, "insights.json")
        
        logging.info("Dashboard Exports Complete! Ready for Streamlit.")

    def _save_json(self, data, filename):
        path = self.output_dir / filename
        with open(path, 'w') as f:
            json.dump(data, f, indent=4)
        logging.info(f"Saved {filename}")

if __name__ == "__main__":
    exporter = DashboardExporter()
    exporter.export_all()
