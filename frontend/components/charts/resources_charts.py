"""
Resource utilization and cost visualization components
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List, Optional

def render_resource_utilization(utilization_data: Dict, chart_type: str = "gauge") -> None:
    """
    Render resource utilization charts with multiple visualization options
    """
    if not utilization_data:
        st.info("📭 No resource utilization data available")
        return
    
    st.subheader("👥 Resource Utilization Analysis")
    
    # Chart type selector
    col1, col2 = st.columns([3, 1])
    with col2:
        chart_type = st.selectbox(
            "Chart Type",
            options=["gauge", "bar", "heatmap", "radar"],
            index=0
        )
    
    if chart_type == "gauge":
        render_utilization_gauges(utilization_data)
    elif chart_type == "bar":
        render_utilization_bars(utilization_data)
    elif chart_type == "heatmap":
        render_utilization_heatmap(utilization_data)
    elif chart_type == "radar":
        render_utilization_radar(utilization_data)

def render_utilization_gauges(utilization_data: Dict) -> None:
    """Render utilization as gauge charts"""
    num_resources = len(utilization_data)
    cols_per_row = 3
    rows = (num_resources + cols_per_row - 1) // cols_per_row
    
    fig = make_subplots(
        rows=rows, cols=cols_per_row,
        specs=[[{'type': 'indicator'} for _ in range(cols_per_row)] for _ in range(rows)],
        subplot_titles=list(utilization_data.keys())
    )
    
    for i, (resource, utilization) in enumerate(utilization_data.items()):
        row = i // cols_per_row + 1
        col = i % cols_per_row + 1
        
        # Determine color based on utilization level
        if utilization <= 0.7:
            color = "green"
        elif utilization <= 0.9:
            color = "orange"
        else:
            color = "red"
        
        fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=utilization * 100,
                title={'text': f"{resource}"},
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': color},
                    'steps': [
                        {'range': [0, 70], 'color': "lightgray"},
                        {'range': [70, 90], 'color': "yellow"},
                        {'range': [90, 100], 'color': "lightcoral"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                }
            ),
            row=row, col=col
        )
    
    fig.update_layout(
        height=300 * rows,
        title_text="Resource Utilization Gauges",
        template="plotly_white"
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_utilization_bars(utilization_data: Dict) -> None:
    """Render utilization as bar chart"""
    resources = list(utilization_data.keys())
    utilizations = [utilization_data[r] * 100 for r in resources]
    
    # Color coding
    colors = []
    for util in utilizations:
        if util <= 70:
            colors.append('#2ca02c')  # Green
        elif util <= 90:
            colors.append('#ff7f0e')  # Orange
        else:
            colors.append('#d62728')  # Red
    
    fig = go.Figure(data=[
        go.Bar(
            x=resources,
            y=utilizations,
            marker_color=colors,
            text=[f'{u:.1f}%' for u in utilizations],
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>Utilization: %{y:.1f}%<extra></extra>'
        )
    ])
    
    fig.update_layout(
        title="Resource Utilization (%)",
        xaxis_title="Resources",
        yaxis_title="Utilization %",
        yaxis_range=[0, 100],
        template="plotly_white",
        height=400
    )
    
    # Add reference lines
    fig.add_hline(y=70, line_dash="dash", line_color="green", annotation_text="Optimal")
    fig.add_hline(y=90, line_dash="dash", line_color="red", annotation_text="Critical")
    
    st.plotly_chart(fig, use_container_width=True)

def render_utilization_heatmap(utilization_data: Dict) -> None:
    """Render utilization as heatmap (for time-series data)"""
    # This would typically show utilization over time
    # For now, create a simple 2D representation
    st.info("Heatmap visualization requires time-series utilization data")
    
    # Create sample time-series data for demonstration
    dates = pd.date_range(start='2024-01-01', periods=30, freq='D')
    sample_data = []
    
    for resource, base_util in utilization_data.items():
        for date in dates:
            # Add some variation to base utilization
            variation = np.random.normal(0, 0.1)
            util = max(0, min(1, base_util + variation))
            sample_data.append({
                'Date': date,
                'Resource': resource,
                'Utilization': util * 100
            })
    
    heatmap_df = pd.DataFrame(sample_data)
    pivot_df = heatmap_df.pivot(index='Resource', columns='Date', values='Utilization')
    
    fig = px.imshow(
        pivot_df,
        title="Resource Utilization Heatmap Over Time",
        color_continuous_scale='RdYlGn_r',  # Red-Yellow-Green (reversed)
        aspect="auto"
    )
    
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

def render_utilization_radar(utilization_data: Dict) -> None:
    """Render utilization as radar chart"""
    categories = list(utilization_data.keys())
    values = [utilization_data[cat] * 100 for cat in categories]
    
    # Close the radar chart
    categories = categories + [categories[0]]
    values = values + [values[0]]
    
    fig = go.Figure(data=
        go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name='Resource Utilization',
            line=dict(color='blue'),
            fillcolor='rgba(0, 0, 255, 0.3)'
        )
    )
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )),
        showlegend=False,
        title="Resource Utilization Radar Chart",
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_cost_breakdown(cost_data: Dict, chart_type: str = "pie") -> None:
    """
    Render project cost breakdown analysis
    """
    if not cost_data:
        st.info("📭 No cost data available")
        return
    
    st.subheader("💰 Project Cost Analysis")
    
    if chart_type == "pie":
        render_cost_pie_chart(cost_data)
    elif chart_type == "treemap":
        render_cost_treemap(cost_data)
    elif chart_type == "waterfall":
        render_cost_waterfall(cost_data)

def render_cost_pie_chart(cost_data: Dict) -> None:
    """Render cost breakdown as pie chart"""
    labels = list(cost_data.keys())
    values = list(cost_data.values())
    total_cost = sum(values)
    
    fig = px.pie(
        values=values,
        names=labels,
        title=f"Project Cost Breakdown<br><sub>Total: ${total_cost:,.0f}</sub>",
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Amount: $%{value:,.0f}<br>Percentage: %{percent}<extra></extra>'
    )
    
    fig.update_layout(
        showlegend=False,
        annotations=[dict(
            text=f'${total_cost:,.0f}',
            x=0.5, y=0.5,
            font_size=16,
            showarrow=False
        )]
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_cost_treemap(cost_data: Dict) -> None:
    """Render cost breakdown as treemap"""
    # Prepare hierarchical data for treemap
    parents = []
    labels = []
    values = []
    
    for category, amount in cost_data.items():
        labels.append(category)
        values.append(amount)
        parents.append("")  # Root level
    
    fig = go.Figure(go.Treemap(
        labels=labels,
        parents=parents,
        values=values,
        textinfo="label+value+percent parent",
        hovertemplate='<b>%{label}</b><br>Amount: $%{value:,.0f}<br>Percentage: %{percentParent}<extra></extra>',
        marker=dict(colors=px.colors.qualitative.Set3)
    ))
    
    fig.update_layout(
        title="Project Cost Treemap",
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_cost_waterfall(cost_data: Dict) -> None:
    """Render cost breakdown as waterfall chart"""
    categories = list(cost_data.keys())
    amounts = list(cost_data.values())
    
    fig = go.Figure(go.Waterfall(
        name="Cost Breakdown",
        orientation="v",
        measure=["relative"] * len(categories),
        x=categories,
        y=amounts,
        text=[f"${amount:,.0f}" for amount in amounts],
        textposition="outside",
        connector={"line": {"color": "rgb(63, 63, 63)"}},
    ))
    
    fig.update_layout(
        title="Project Cost Waterfall Chart",
        showlegend=False,
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_resource_timeline(allocations_df: pd.DataFrame) -> None:
    """
    Render resource allocation timeline
    """
    if allocations_df.empty:
        st.info("📭 No resource allocation data available")
        return
    
    fig = px.timeline(
        allocations_df,
        x_start="StartDate",
        x_end="EndDate",
        y="ResourceName",
        color="ResourceType",
        title="Resource Allocation Timeline",
        hover_data=["TaskID", "UnitsUsed"]
    )
    
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(
        height=400,
        xaxis_title="Timeline",
        yaxis_title="Resources"
    )
    
    st.plotly_chart(fig, use_container_width=True)