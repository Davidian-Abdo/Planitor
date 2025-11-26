"""
Enhanced chart rendering utilities with professional styling
"""
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class ProfessionalChartRenderer:
    """
    Professional chart renderer with construction industry styling
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.colors = {
            'primary': '#2c3e50',
            'secondary': '#3498db',
            'success': '#27ae60',
            'warning': '#f39c12',
            'danger': '#e74c3c',
            'info': '#17a2b8'
        }
    
    def create_professional_scurve(self, analysis_df: pd.DataFrame) -> go.Figure:
        """Create professional S-curve with enhanced styling"""
        fig = go.Figure()
        
        # Planned progress (smooth curve)
        fig.add_trace(go.Scatter(
            x=analysis_df['Date'],
            y=analysis_df['PlannedProgress'],
            mode='lines',
            name='Planned Progress',
            line=dict(color=self.colors['primary'], width=4, shape='spline'),
            fill='tozeroy',
            fillcolor='rgba(52, 152, 219, 0.1)',
            hovertemplate=(
                '<b>Planned Progress</b><br>'
                'Date: %{x|%Y-%m-%d}<br>'
                'Progress: %{y:.1%}<extra></extra>'
            )
        ))
        
        # Actual progress
        fig.add_trace(go.Scatter(
            x=analysis_df['Date'],
            y=analysis_df['CumulativeActual'],
            mode='lines+markers',
            name='Actual Progress',
            line=dict(color=self.colors['success'], width=3, dash='dot'),
            marker=dict(size=6, color=self.colors['success']),
            hovertemplate=(
                '<b>Actual Progress</b><br>'
                'Date: %{x|%Y-%m-%d}<br>'
                'Progress: %{y:.1%}<extra></extra>'
            )
        ))
        
        fig.update_layout(
            title=dict(
                text='📈 Progress S-Curve Analysis',
                x=0.5,
                font=dict(size=20, color=self.colors['primary'])
            ),
            xaxis_title="Date",
            yaxis_title="Cumulative Progress",
            yaxis_tickformat='.0%',
            hovermode='x unified',
            template="plotly_white",
            height=500,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            plot_bgcolor='rgba(248,249,250,1)',
            paper_bgcolor='white'
        )
        
        return fig
    
    def create_resource_utilization_dashboard(self, utilization_data: Dict) -> go.Figure:
        """Create professional resource utilization dashboard"""
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Resource Utilization', 'Utilization Distribution', 
                          'Over-utilization Alert', 'Performance Metrics'),
            specs=[[{"type": "bar"}, {"type": "pie"}],
                   [{"type": "indicator"}, {"type": "indicator"}]],
            vertical_spacing=0.15,
            horizontal_spacing=0.1
        )
        
        # Bar chart for utilization
        resources = list(utilization_data.keys())
        utilizations = [utilization_data[r] * 100 for r in resources]
        
        colors = [self.colors['success'] if u <= 80 
                 else self.colors['warning'] if u <= 95 
                 else self.colors['danger'] for u in utilizations]
        
        fig.add_trace(
            go.Bar(
                x=resources,
                y=utilizations,
                marker_color=colors,
                hovertemplate='<b>%{x}</b><br>Utilization: %{y:.1f}%<extra></extra>'
            ), row=1, col=1
        )
        
        # Pie chart for utilization distribution
        utilization_ranges = {
            'Optimal (≤80%)': len([u for u in utilizations if u <= 80]),
            'High (81-95%)': len([u for u in utilizations if 80 < u <= 95]),
            'Critical (>95%)': len([u for u in utilizations if u > 95])
        }
        
        fig.add_trace(
            go.Pie(
                labels=list(utilization_ranges.keys()),
                values=list(utilization_ranges.values()),
                marker=dict(colors=[self.colors['success'], self.colors['warning'], self.colors['danger']])
            ), row=1, col=2
        )
        
        # Overall utilization indicator
        avg_utilization = np.mean(utilizations)
        fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=avg_utilization,
                title={'text': "Avg Utilization"},
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': self.colors['primary']},
                    'steps': [
                        {'range': [0, 80], 'color': 'lightgray'},
                        {'range': [80, 95], 'color': 'yellow'},
                        {'range': [95, 100], 'color': 'red'}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                }
            ), row=2, col=1
        )
        
        # Over-utilized resources count
        over_utilized = len([u for u in utilizations if u > 95])
        fig.add_trace(
            go.Indicator(
                mode="number",
                value=over_utilized,
                title={'text': "Critical Resources"},
                number={'font': {'color': self.colors['danger'] if over_utilized > 0 else self.colors['success']}}
            ), row=2, col=2
        )
        
        fig.update_layout(
            height=600,
            title_text="🏗️ Resource Utilization Dashboard",
            showlegend=False,
            template="plotly_white"
        )
        
        return fig
    
    def create_cost_breakdown_chart(self, cost_data: Dict) -> go.Figure:
        """Create professional cost breakdown chart"""
        labels = list(cost_data.keys())
        values = list(cost_data.values())
        total_cost = sum(values)
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.4,
            hovertemplate='<b>%{label}</b><br>Amount: $%{value:,.0f}<br>Percentage: %{percent}<extra></extra>',
            textinfo='label+percent',
            textposition='inside',
            marker=dict(colors=px.colors.qualitative.Set3)
        )])
        
        fig.update_layout(
            title=dict(
                text=f'💰 Project Cost Breakdown<br><sub>Total: ${total_cost:,.0f}</sub>',
                x=0.5,
                font=dict(size=18, color=self.colors['primary'])
            ),
            showlegend=False,
            annotations=[dict(
                text=f'${total_cost:,.0f}',
                x=0.5, y=0.5,
                font_size=20,
                showarrow=False
            )]
        )
        
        return fig
    
    def create_progress_deviation_chart(self, analysis_df: pd.DataFrame) -> go.Figure:
        """Create professional progress deviation analysis"""
        fig = go.Figure()
        
        # Deviation area
        fig.add_trace(go.Scatter(
            x=analysis_df['Date'],
            y=analysis_df['ProgressDeviation'],
            fill='tozeroy',
            mode='lines',
            name='Progress Deviation',
            line=dict(color=self.colors['warning'], width=2),
            fillcolor='rgba(243, 156, 18, 0.3)',
            hovertemplate=(
                '<b>Deviation</b><br>'
                'Date: %{x|%Y-%m-%d}<br>'
                'Deviation: %{y:.3f}<extra></extra>'
            )
        ))
        
        # Zero reference line
        fig.add_hline(
            y=0, 
            line_dash="dash", 
            line_color="red", 
            opacity=0.7,
            annotation_text="Planned Progress"
        )
        
        fig.update_layout(
            title=dict(
                text='📊 Progress Deviation Analysis',
                x=0.5,
                font=dict(size=18, color=self.colors['primary'])
            ),
            xaxis_title="Date",
            yaxis_title="Deviation (Actual - Planned)",
            hovermode='x unified',
            template="plotly_white",
            height=400
        )
        
        return fig

# Convenience functions
def create_professional_scurve(analysis_df: pd.DataFrame) -> go.Figure:
    renderer = ProfessionalChartRenderer()
    return renderer.create_professional_scurve(analysis_df)

def create_resource_dashboard(utilization_data: Dict) -> go.Figure:
    renderer = ProfessionalChartRenderer()
    return renderer.create_resource_utilization_dashboard(utilization_data)