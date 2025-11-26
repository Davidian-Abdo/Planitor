"""
Performance metrics and KPI visualization components
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple

def render_performance_metrics(performance_data: Dict) -> None:
    """
    Render key performance indicators (KPIs) for construction projects
    """
    st.subheader("🎯 Project Performance Metrics")
    
    # Create KPI cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        schedule_performance = performance_data.get('schedule_performance', 0)
        st.metric(
            "Schedule Performance", 
            f"{schedule_performance:.1f}%",
            delta="Ahead" if schedule_performance > 100 else "On Track" if schedule_performance == 100 else "Behind"
        )
    
    with col2:
        cost_performance = performance_data.get('cost_performance', 0)
        st.metric(
            "Cost Performance",
            f"{cost_performance:.1f}%", 
            delta="Under Budget" if cost_performance > 100 else "On Budget" if cost_performance == 100 else "Over Budget"
        )
    
    with col3:
        quality_score = performance_data.get('quality_score', 0)
        st.metric(
            "Quality Score",
            f"{quality_score:.1f}%",
            delta="Excellent" if quality_score >= 90 else "Good" if quality_score >= 80 else "Needs Improvement"
        )
    
    with col4:
        safety_index = performance_data.get('safety_index', 0)
        st.metric(
            "Safety Index",
            f"{safety_index:.1f}",
            delta="Excellent" if safety_index >= 95 else "Good" if safety_index >= 85 else "Review Needed"
        )

def render_kpi_dashboard(kpi_data: Dict) -> None:
    """
    Render comprehensive KPI dashboard with multiple visualizations
    """
    if not kpi_data:
        st.info("📭 No KPI data available for dashboard")
        return
    
    # Create comprehensive KPI dashboard
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            '📈 Performance Trends',
            '🎯 KPI Scorecard',
            '⚖️ Performance Balance',
            '📊 Metric Distribution'
        ),
        specs=[
            [{"type": "xy"}, {"type": "indicator"}],
            [{"type": "bar"}, {"type": "pie"}]
        ],
        vertical_spacing=0.15
    )
    
    # Performance trends (top left)
    if 'trend_data' in kpi_data:
        trend_df = kpi_data['trend_data']
        for column in ['Schedule_Performance', 'Cost_Performance', 'Quality_Score']:
            if column in trend_df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=trend_df['Date'],
                        y=trend_df[column],
                        name=column.replace('_', ' '),
                        mode='lines+markers'
                    ), row=1, col=1
                )
    
    # Overall performance indicator (top right)
    overall_score = kpi_data.get('overall_performance', 0)
    fig.add_trace(
        go.Indicator(
            mode="gauge+number",
            value=overall_score,
            title={'text': "Overall Performance"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 70], 'color': "red"},
                    {'range': [70, 85], 'color': "yellow"},
                    {'range': [85, 100], 'color': "green"}
                ],
                'threshold': {
                    'line': {'color': "black", 'width': 4},
                    'thickness': 0.75,
                    'value': 85
                }
            }
        ), row=1, col=2
    )
    
    # Performance balance (bottom left)
    categories = ['Schedule', 'Cost', 'Quality', 'Safety', 'Productivity']
    scores = [
        kpi_data.get('schedule_performance', 0),
        kpi_data.get('cost_performance', 0), 
        kpi_data.get('quality_score', 0),
        kpi_data.get('safety_index', 0),
        kpi_data.get('productivity_index', 0)
    ]
    
    fig.add_trace(
        go.Bar(
            x=categories,
            y=scores,
            marker_color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'],
            text=[f'{s:.1f}%' for s in scores],
            textposition='auto'
        ), row=2, col=1
    )
    
    # Performance distribution (bottom right)
    performance_levels = {
        'Excellent (90-100%)': len([s for s in scores if s >= 90]),
        'Good (80-89%)': len([s for s in scores if 80 <= s < 90]),
        'Fair (70-79%)': len([s for s in scores if 70 <= s < 80]),
        'Needs Improvement (<70%)': len([s for s in scores if s < 70])
    }
    
    fig.add_trace(
        go.Pie(
            labels=list(performance_levels.keys()),
            values=list(performance_levels.values()),
            hole=0.3
        ), row=2, col=2
    )
    
    fig.update_layout(
        height=700,
        title_text="🏗️ Construction Project KPI Dashboard",
        showlegend=True,
        template="plotly_white"
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_earned_value_analysis(ev_data: Dict) -> None:
    """
    Render Earned Value Management (EVM) analysis
    """
    if not ev_data:
        st.info("📭 No earned value data available")
        return
    
    st.subheader("💰 Earned Value Management Analysis")
    
    # Calculate EVM metrics
    pv = ev_data.get('planned_value', 0)  # Planned Value
    ev = ev_data.get('earned_value', 0)    # Earned Value  
    ac = ev_data.get('actual_cost', 0)     # Actual Cost
    
    # EVM formulas
    cv = ev - ac  # Cost Variance
    sv = ev - pv  # Schedule Variance
    cpi = ev / ac if ac > 0 else 0  # Cost Performance Index
    spi = ev / pv if pv > 0 else 0  # Schedule Performance Index
    
    # Display EVM metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Cost Variance (CV)", f"${cv:,.0f}", delta_color="inverse")
    
    with col2:
        st.metric("Schedule Variance (SV)", f"${sv:,.0f}", delta_color="inverse")
    
    with col3:
        st.metric("Cost Performance Index (CPI)", f"{cpi:.2f}")
    
    with col4:
        st.metric("Schedule Performance Index (SPI)", f"{spi:.2f}")
    
    # EVM chart
    fig = go.Figure()
    
    # Add EVM curves
    if 'evm_curve' in ev_data:
        curve_data = ev_data['evm_curve']
        fig.add_trace(go.Scatter(
            x=curve_data['date'], y=curve_data['pv'], 
            name='Planned Value (PV)', line=dict(color='blue')
        ))
        fig.add_trace(go.Scatter(
            x=curve_data['date'], y=curve_data['ev'], 
            name='Earned Value (EV)', line=dict(color='green')
        ))
        fig.add_trace(go.Scatter(
            x=curve_data['date'], y=curve_data['ac'], 
            name='Actual Cost (AC)', line=dict(color='red')
        ))
    
    fig.update_layout(
        title="Earned Value Management Analysis",
        xaxis_title="Time",
        yaxis_title="Value ($)",
        template="plotly_white",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # EVM interpretation
    render_evm_interpretation(cv, sv, cpi, spi)

def render_evm_interpretation(cv: float, sv: float, cpi: float, spi: float) -> None:
    """Render EVM performance interpretation"""
    st.subheader("📋 Performance Interpretation")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Cost Performance:**")
        if cpi > 1:
            st.success(f"✅ Under Budget (CPI = {cpi:.2f})")
        elif cpi == 1:
            st.info(f"📊 On Budget (CPI = {cpi:.2f})")
        else:
            st.error(f"❌ Over Budget (CPI = {cpi:.2f})")
        
        st.write("**Schedule Performance:**")
        if spi > 1:
            st.success(f"✅ Ahead of Schedule (SPI = {spi:.2f})")
        elif spi == 1:
            st.info(f"📊 On Schedule (SPI = {spi:.2f})")
        else:
            st.error(f"❌ Behind Schedule (SPI = {spi:.2f})")
    
    with col2:
        st.write("**Variance Analysis:**")
        if cv > 0:
            st.success(f"✅ Cost Variance: +${cv:,.0f} (Favorable)")
        else:
            st.error(f"❌ Cost Variance: ${cv:,.0f} (Unfavorable)")
        
        if sv > 0:
            st.success(f"✅ Schedule Variance: +${sv:,.0f} (Favorable)")
        else:
            st.error(f"❌ Schedule Variance: ${sv:,.0f} (Unfavorable)")

def render_risk_heatmap(risk_data: pd.DataFrame) -> None:
    """
    Render risk assessment heatmap
    """
    if risk_data.empty:
        st.info("📭 No risk assessment data available")
        return
    
    fig = px.scatter(
        risk_data,
        x='probability',
        y='impact',
        size='severity',
        color='category',
        hover_data=['description', 'mitigation'],
        title="Risk Assessment Heatmap",
        labels={
            'probability': 'Probability',
            'impact': 'Impact',
            'severity': 'Severity',
            'category': 'Risk Category'
        }
    )
    
    # Add risk quadrants
    fig.add_hline(y=5, line_dash="dash", line_color="red")
    fig.add_vline(x=5, line_dash="dash", line_color="red")
    
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)