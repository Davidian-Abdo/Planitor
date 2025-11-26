"""
Progress tracking and performance visualization components
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta

def render_schedule_metrics(schedule_results) -> None:
    """
    Render comprehensive schedule performance metrics
    """
    if not schedule_results:
        st.warning("No schedule results available for metrics")
        return
    
    st.subheader("📊 Schedule Performance Metrics")
    
    # Calculate key metrics
    total_tasks = len(schedule_results.tasks)
    scheduled_tasks = len([t for t in schedule_results.tasks if hasattr(schedule_results, 'schedule') and t.id in schedule_results.schedule])
    project_duration = getattr(schedule_results, 'project_duration', 0)
    total_cost = getattr(schedule_results, 'total_cost', 0)
    resource_utilization = getattr(schedule_results, 'resource_utilization', {})
    
    # Display metrics in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        completion_rate = (scheduled_tasks / total_tasks * 100) if total_tasks > 0 else 0
        st.metric(
            "Completion Rate", 
            f"{completion_rate:.1f}%",
            delta=f"{scheduled_tasks}/{total_tasks} tasks"
        )
    
    with col2:
        st.metric("Project Duration", f"{project_duration} days")
    
    with col3:
        st.metric("Estimated Cost", f"${total_cost:,.0f}")
    
    with col4:
        avg_utilization = np.mean(list(resource_utilization.values())) * 100 if resource_utilization else 0
        st.metric(
            "Avg Resource Utilization", 
            f"{avg_utilization:.1f}%",
            delta="Optimal: 70-85%" if avg_utilization < 70 else "High" if avg_utilization > 85 else "Good"
        )

def render_progress_dashboard(analysis_df: pd.DataFrame, show_filters: bool = True) -> None:
    """
    Render comprehensive progress dashboard with S-curves and analytics
    """
    if analysis_df is None or analysis_df.empty:
        st.info("📭 No progress data available for dashboard")
        return
    
    try:
        # Filters
        if show_filters:
            col1, col2 = st.columns(2)
            with col1:
                date_range = st.date_input(
                    "Analysis Period",
                    value=[analysis_df['Date'].min(), analysis_df['Date'].max()],
                    min_value=analysis_df['Date'].min(),
                    max_value=analysis_df['Date'].max()
                )
            with col2:
                show_trend_line = st.checkbox("Show Trend Line", value=True)
        
        # Create dashboard with multiple charts
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                '📈 Progress S-Curve Analysis',
                '📊 Progress Deviation',
                '🎯 Performance Indicators', 
                '📅 Weekly Progress Trend'
            ),
            specs=[
                [{"colspan": 2}, None],
                [{"type": "indicator"}, {"type": "xy"}]
            ],
            vertical_spacing=0.12,
            horizontal_spacing=0.1
        )
        
        # S-Curve (top row - spans both columns)
        fig.add_trace(
            go.Scatter(
                x=analysis_df['Date'],
                y=analysis_df['PlannedProgress'],
                name='Planned',
                line=dict(color='#1f77b4', width=4, shape='spline'),
                fill='tozeroy',
                fillcolor='rgba(31, 119, 180, 0.1)',
                hovertemplate='<b>Planned</b><br>Date: %{x|%Y-%m-%d}<br>Progress: %{y:.1%}<extra></extra>'
            ), row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=analysis_df['Date'],
                y=analysis_df['CumulativeActual'],
                name='Actual',
                line=dict(color='#2ca02c', width=3, dash='dot'),
                marker=dict(size=6, color='#2ca02c'),
                hovertemplate='<b>Actual</b><br>Date: %{x|%Y-%m-%d}<br>Progress: %{y:.1%}<extra></extra>'
            ), row=1, col=1
        )
        
        # Progress Deviation (bottom left)
        fig.add_trace(
            go.Scatter(
                x=analysis_df['Date'],
                y=analysis_df['ProgressDeviation'],
                name='Deviation',
                line=dict(color='#ff7f0e', width=2),
                fill='tozeroy',
                fillcolor='rgba(255, 127, 14, 0.2)',
                hovertemplate='<b>Deviation</b><br>Date: %{x|%Y-%m-%d}<br>Deviation: %{y:.3f}<extra></extra>'
            ), row=2, col=1
        )
        
        # Add zero reference line
        fig.add_hline(y=0, line_dash="dash", line_color="red", row=2, col=1)
        
        # Performance indicator (bottom right - gauge)
        current_deviation = analysis_df['ProgressDeviation'].iloc[-1]
        deviation_percent = (current_deviation / analysis_df['PlannedProgress'].iloc[-1] * 100) if analysis_df['PlannedProgress'].iloc[-1] > 0 else 0
        
        fig.add_trace(
            go.Indicator(
                mode="gauge+number+delta",
                value=deviation_percent,
                delta={'reference': 0},
                title={'text': "Progress Deviation %"},
                gauge={
                    'axis': {'range': [-50, 50]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [-50, -10], 'color': "red"},
                        {'range': [-10, 10], 'color': "lightgray"},
                        {'range': [10, 50], 'color': "green"}
                    ],
                    'threshold': {
                        'line': {'color': "black", 'width': 4},
                        'thickness': 0.75,
                        'value': 0
                    }
                }
            ), row=2, col=2
        )
        
        # Update layout
        fig.update_layout(
            height=700,
            showlegend=True,
            template="plotly_white",
            title_text="🏗️ Construction Progress Dashboard",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        # Update axes
        fig.update_yaxes(title_text="Progress", tickformat=".0%", row=1, col=1)
        fig.update_yaxes(title_text="Deviation", row=2, col=1)
        fig.update_xaxes(title_text="Date", row=1, col=1)
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Additional metrics below the chart
        render_progress_insights(analysis_df)
        
    except Exception as e:
        st.error(f"❌ Error rendering progress dashboard: {e}")

def render_progress_insights(analysis_df: pd.DataFrame) -> None:
    """Render progress insights and recommendations"""
    if analysis_df.empty:
        return
    
    latest = analysis_df.iloc[-1]
    current_deviation = latest['ProgressDeviation']
    current_deviation_pct = latest['DeviationPercentage']
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if current_deviation > 0:
            st.success(f"🎉 **Ahead of Schedule**: +{current_deviation:.3f} ({current_deviation_pct:.1f}%)")
        elif current_deviation < 0:
            st.error(f"⚠️ **Behind Schedule**: {current_deviation:.3f} ({current_deviation_pct:.1f}%)")
        else:
            st.info("📅 **On Schedule**: No deviation from plan")
    
    with col2:
        total_deviation = analysis_df['ProgressDeviation'].sum()
        st.metric("Cumulative Deviation", f"{total_deviation:.3f}")
    
    with col3:
        volatility = analysis_df['ProgressDeviation'].std()
        st.metric("Schedule Volatility", f"{volatility:.3f}")

def render_milestone_tracking(milestones: List[Dict]) -> None:
    """
    Render milestone tracking and completion status
    """
    if not milestones:
        st.info("No milestones defined for tracking")
        return
    
    # Convert to DataFrame
    milestone_df = pd.DataFrame(milestones)
    
    # Calculate completion status
    current_date = datetime.now().date()
    milestone_df['Status'] = milestone_df['date'].apply(
        lambda x: 'Completed' if pd.to_datetime(x).date() < current_date else 'Upcoming'
    )
    milestone_df['Days_Until'] = (pd.to_datetime(milestone_df['date']).dt.date - current_date).dt.days
    
    # Create milestone tracking chart
    fig = px.timeline(
        milestone_df,
        x_start="date",
        x_end="date",
        y="name",
        color="Status",
        title="🎯 Project Milestones",
        hover_data=["description", "Days_Until"]
    )
    
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(showlegend=True)
    
    st.plotly_chart(fig, use_container_width=True)