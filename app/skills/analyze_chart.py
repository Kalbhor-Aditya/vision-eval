from app.skills.base import BaseSkill


class AnalyzeChartSkill(BaseSkill):
    name = "analyze_chart"
    description = "Interpret charts, graphs, diagrams, tables — extract data, trends, and key insights"
    system_prompt = (
        "You are a data visualization analyst. Carefully examine the chart, graph, or table. "
        "Identify: chart type, axes/labels, key data points, trends, outliers, and the main insight "
        "the visualization communicates. Quote specific values when visible."
    )
