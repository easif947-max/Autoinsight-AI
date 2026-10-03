import pandas as pd
import plotly.express as px
import plotly.io as pio
import json
from typing import Dict, Any
from crewai.tools import tool

@tool("Plotly Chart Configurator")
def generate_plotly_chart_config(
    file_path: str,
    chart_type: str,
    x_axis: str,
    y_axis: str = "",
    title: str = "Data Visualization"
) -> str:
    """
    Generates a native Plotly chart figure configuration JSON string.
    
    Args:
        file_path (str): CSV file path.
        chart_type (str): Type of chart ('bar', 'scatter', 'line', 'histogram', 'box').
        x_axis (str): Column name for X-axis.
        y_axis (str, optional): Column name for Y-axis. Defaults to "".
        title (str, optional): Title of the chart. Defaults to "Data Visualization".
        
    Returns:
        str: JSON string representing Plotly figure specification.
    """
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        return json.dumps({"error": f"Failed to load CSV file: {str(e)}"})

    if x_axis not in df.columns:
        return json.dumps({"error": f"Column '{x_axis}' not found in dataset."})

    fig = None
    chart_type_clean = chart_type.lower().strip()

    try:
        if chart_type_clean == "bar":
            if y_axis and y_axis in df.columns:
                fig = px.bar(df, x=x_axis, y=y_axis, title=title, template="plotly_white")
            else:
                value_counts = df[x_axis].value_counts().reset_index()
                value_counts.columns = [x_axis, "count"]
                fig = px.bar(value_counts, x=x_axis, y="count", title=title, template="plotly_white")

        elif chart_type_clean == "scatter":
            if y_axis and y_axis in df.columns:
                fig = px.scatter(df, x=x_axis, y=y_axis, title=title, template="plotly_white")
            else:
                return json.dumps({"error": "Scatter plot requires a valid y_axis column."})

        elif chart_type_clean == "line":
            if y_axis and y_axis in df.columns:
                fig = px.line(df, x=x_axis, y=y_axis, title=title, template="plotly_white")
            else:
                return json.dumps({"error": "Line plot requires a valid y_axis column."})

        elif chart_type_clean == "histogram":
            fig = px.histogram(df, x=x_axis, title=title, template="plotly_white")

        elif chart_type_clean == "box":
            if y_axis and y_axis in df.columns:
                fig = px.box(df, x=x_axis, y=y_axis, title=title, template="plotly_white")
            else:
                fig = px.box(df, y=x_axis, title=title, template="plotly_white")

        else:
            return json.dumps({"error": f"Unsupported chart type: {chart_type}"})

        # Return serialized Plotly JSON figure spec
        fig_json = pio.to_json(fig)
        return json.dumps({
            "status": "success",
            "chart_type": chart_type_clean,
            "title": title,
            "plotly_json": json.loads(fig_json)
        })

    except Exception as e:
        return json.dumps({"error": f"Chart generation failed: {str(e)}"})
