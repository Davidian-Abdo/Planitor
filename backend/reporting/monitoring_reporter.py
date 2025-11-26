"""
Progress monitoring and S-curve analysis reporter
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import logging

logger = logging.getLogger(__name__)


class MonitoringReporter:
    """
    Professional monitoring reporter for construction progress tracking
    Generates S-curves, progress deviation charts, and performance analytics
    """
    
    def __init__(self, reference_schedule: pd.DataFrame, actual_progress: pd.DataFrame):
        self.reference_schedule = reference_schedule.copy()
        self.actual_progress = actual_progress.copy()
        self.analysis_df = None
        self.logger = logging.getLogger(__name__)
        
        # Validate and preprocess data
        self._validate_input_data()
        self._preprocess_data()

    def _validate_input_data(self) -> None:
        """Validate input dataframes"""
        required_ref_columns = {"TaskID", "Start", "End"}
        required_act_columns = {"Date", "Progress"}
        
        ref_columns = set(self.reference_schedule.columns)
        act_columns = set(self.actual_progress.columns)
        
        missing_ref = required_ref_columns - ref_columns
        missing_act = required_act_columns - act_columns
        
        if missing_ref:
            raise ValueError(f"Reference schedule missing columns: {missing_ref}")
        if missing_act:
            raise ValueError(f"Actual progress missing columns: {missing_act}")

    def _preprocess_data(self) -> None:
        """Preprocess and clean input data"""
        # Convert dates
        self.reference_schedule["Start"] = pd.to_datetime(self.reference_schedule["Start"])
        self.reference_schedule["End"] = pd.to_datetime(self.reference_schedule["End"])
        self.actual_progress["Date"] = pd.to_datetime(self.actual_progress["Date"])
        
        # Normalize progress to 0-1 range if needed
        if self.actual_progress["Progress"].max() > 1.0:
            self.actual_progress["Progress"] = self.actual_progress["Progress"] / 100.0
        
        # Sort by date
        self.actual_progress = self.actual_progress.sort_values("Date")

    def compute_analysis(self) -> pd.DataFrame:
        """
        Compute comprehensive progress analysis including S-curve and deviations
        Returns analysis DataFrame
        """
        try:
            # Create timeline from project start to end
            project_start = self.reference_schedule["Start"].min()
            project_end = self.reference_schedule["End"].max()
            timeline = pd.date_range(project_start, project_end, freq="D")
            
            # Calculate planned progress (S-curve)
            planned_curve = self._calculate_planned_progress(timeline)
            
            # Calculate actual progress
            actual_curve = self._calculate_actual_progress(timeline)
            
            # Combine and compute deviations
            self.analysis_df = pd.merge(planned_curve, actual_curve, on="Date", how="outer")
            self.analysis_df = self.analysis_df.fillna(method="ffill").fillna(0)
            
            # Compute metrics
            self.analysis_df["ProgressDeviation"] = (
                self.analysis_df["CumulativeActual"] - self.analysis_df["PlannedProgress"]
            )
            self.analysis_df["DeviationPercentage"] = (
                self.analysis_df["ProgressDeviation"] / self.analysis_df["PlannedProgress"]
            ).replace([np.inf, -np.inf], 0) * 100
            
            self.logger.info("✅ Progress analysis computed successfully")
            return self.analysis_df
            
        except Exception as e:
            self.logger.error(f"❌ Failed to compute progress analysis: {e}")
            raise

    def _calculate_planned_progress(self, timeline: pd.DatetimeIndex) -> pd.DataFrame:
        """Calculate planned progress S-curve"""
        planned_data = []
        total_tasks = len(self.reference_schedule)
        
        for date in timeline:
            # Count tasks that should be completed by this date
            completed_tasks = len(self.reference_schedule[self.reference_schedule["End"] <= date])
            progress = completed_tasks / total_tasks if total_tasks > 0 else 0
            
            planned_data.append({
                "Date": date,
                "PlannedProgress": progress
            })
        
        return pd.DataFrame(planned_data)

    def _calculate_actual_progress(self, timeline: pd.DatetimeIndex) -> pd.DataFrame:
        """Calculate actual progress from reported data"""
        # Resample actual progress to daily frequency
        actual_daily = self.actual_progress.set_index("Date").resample("D").mean()
        actual_daily = actual_daily.reset_index()
        
        # Calculate cumulative actual progress
        actual_daily["CumulativeActual"] = actual_daily["Progress"].cumsum()
        actual_daily["CumulativeActual"] = actual_daily["CumulativeActual"].clip(upper=1.0)
        
        # Merge with timeline to ensure all dates are covered
        timeline_df = pd.DataFrame({"Date": timeline})
        actual_curve = pd.merge(timeline_df, actual_daily, on="Date", how="left")
        actual_curve = actual_curve.fillna(method="ffill").fillna(0)
        
        return actual_curve[["Date", "CumulativeActual"]]

    def generate_scurve_chart(self) -> go.Figure:
        """
        Generate professional S-curve chart
        """
        if self.analysis_df is None:
            self.compute_analysis()
        
        fig = go.Figure()
        
        # Planned progress line
        fig.add_trace(go.Scatter(
            x=self.analysis_df["Date"],
            y=self.analysis_df["PlannedProgress"],
            mode='lines',
            name='Planned Progress',
            line=dict(color='#1f77b4', width=3),
            hovertemplate='<b>Planned</b><br>Date: %{x|%Y-%m-%d}<br>Progress: %{y:.1%}<extra></extra>'
        ))
        
        # Actual progress line
        fig.add_trace(go.Scatter(
            x=self.analysis_df["Date"],
            y=self.analysis_df["CumulativeActual"],
            mode='lines+markers',
            name='Actual Progress',
            line=dict(color='#2ca02c', width=3, dash='dot'),
            marker=dict(size=6, color='#2ca02c'),
            hovertemplate='<b>Actual</b><br>Date: %{x|%Y-%m-%d}<br>Progress: %{y:.1%}<extra></extra>'
        ))
        
        fig.update_layout(
            title="S-Curve: Planned vs Actual Progress",
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
            )
        )
        
        return fig

    def generate_deviation_chart(self) -> go.Figure:
        """
        Generate progress deviation chart
        """
        if self.analysis_df is None:
            self.compute_analysis()
        
        fig = go.Figure()
        
        # Deviation area chart
        fig.add_trace(go.Scatter(
            x=self.analysis_df["Date"],
            y=self.analysis_df["ProgressDeviation"],
            fill='tozeroy',
            mode='lines',
            name='Progress Deviation',
            line=dict(color='#ff7f0e', width=2),
            hovertemplate='<b>Deviation</b><br>Date: %{x|%Y-%m-%d}<br>Deviation: %{y:.3f}<extra></extra>'
        ))
        
        # Zero reference line
        fig.add_hline(y=0, line_dash="dash", line_color="red", opacity=0.5)
        
        fig.update_layout(
            title="Progress Deviation (Actual - Planned)",
            xaxis_title="Date",
            yaxis_title="Deviation",
            hovermode='x unified',
            template="plotly_white",
            height=400
        )
        
        return fig

    def generate_performance_dashboard(self) -> go.Figure:
        """
        Generate comprehensive performance dashboard
        """
        if self.analysis_df is None:
            self.compute_analysis()
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'S-Curve Analysis', 
                'Progress Deviation',
                'Performance Metrics', 
                'Trend Analysis'
            ),
            specs=[
                [{"colspan": 2}, None],
                [{"type": "indicator"}, {"type": "indicator"}]
            ],
            vertical_spacing=0.15,
            horizontal_spacing=0.1
        )
        
        # S-Curve
        fig.add_trace(
            go.Scatter(
                x=self.analysis_df["Date"],
                y=self.analysis_df["PlannedProgress"],
                name='Planned',
                line=dict(color='blue')
            ), row=1, col=1
        )
        fig.add_trace(
            go.Scatter(
                x=self.analysis_df["Date"],
                y=self.analysis_df["CumulativeActual"],
                name='Actual',
                line=dict(color='green', dash='dot')
            ), row=1, col=1
        )
        
        # Current performance metrics
        current_deviation = self.analysis_df["ProgressDeviation"].iloc[-1]
        current_percentage = self.analysis_df["DeviationPercentage"].iloc[-1]
        
        # Performance indicator
        fig.add_trace(
            go.Indicator(
                mode="delta",
                value=current_percentage,
                delta={'reference': 0, 'relative': False, 'valueformat': '.1f'},
                title={"text": "Deviation %"},
                domain={'row': 2, 'column': 0}
            ), row=2, col=1
        )
        
        # Status indicator
        status_color = "green" if current_deviation >= 0 else "red"
        fig.add_trace(
            go.Indicator(
                mode="number",
                value=current_deviation,
                number={'valueformat': '.3f'},
                title={"text": "Current Deviation"},
                domain={'row': 2, 'column': 1}
            ), row=2, col=2
        )
        
        fig.update_layout(
            height=600,
            title_text="Project Performance Dashboard",
            template="plotly_white"
        )
        
        return fig

    def get_performance_metrics(self) -> Dict[str, float]:
        """
        Calculate key performance metrics
        """
        if self.analysis_df is None:
            self.compute_analysis()
        
        latest = self.analysis_df.iloc[-1]
        max_deviation = self.analysis_df["ProgressDeviation"].max()
        min_deviation = self.analysis_df["ProgressDeviation"].min()
        
        return {
            "current_deviation": latest["ProgressDeviation"],
            "current_deviation_percentage": latest["DeviationPercentage"],
            "max_positive_deviation": max_deviation,
            "max_negative_deviation": min_deviation,
            "current_planned_progress": latest["PlannedProgress"],
            "current_actual_progress": latest["CumulativeActual"],
            "overall_performance": "AHEAD" if latest["ProgressDeviation"] > 0 else "BEHIND"
        }

    def export_analysis_to_excel(self, file_path: str) -> str:
        """
        Export complete monitoring analysis to Excel
        """
        if self.analysis_df is None:
            self.compute_analysis()
        
        try:
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                # Main analysis data
                self.analysis_df.to_excel(writer, sheet_name="Progress Analysis", index=False)
                
                # Performance metrics
                metrics = self.get_performance_metrics()
                metrics_df = pd.DataFrame([metrics])
                metrics_df.to_excel(writer, sheet_name="Performance Metrics", index=False)
                
                # Summary statistics
                summary_data = {
                    "Metric": [
                        "Analysis Period Start",
                        "Analysis Period End", 
                        "Total Days Analyzed",
                        "Average Daily Deviation",
                        "Performance Status"
                    ],
                    "Value": [
                        self.analysis_df["Date"].min().strftime('%Y-%m-%d'),
                        self.analysis_df["Date"].max().strftime('%Y-%m-%d'),
                        len(self.analysis_df),
                        self.analysis_df["ProgressDeviation"].mean(),
                        metrics["overall_performance"]
                    ]
                }
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name="Summary", index=False)
            
            self.logger.info(f"✅ Monitoring analysis exported to: {file_path}")
            return file_path
            
        except Exception as e:
            self.logger.error(f"❌ Failed to export monitoring analysis: {e}")
            raise

    def generate_weekly_report(self) -> pd.DataFrame:
        """
        Generate weekly progress report
        """
        if self.analysis_df is None:
            self.compute_analysis()
        
        # Resample to weekly frequency
        weekly_df = self.analysis_df.set_index('Date').resample('W-MON').agg({
            'PlannedProgress': 'last',
            'CumulativeActual': 'last',
            'ProgressDeviation': 'last',
            'DeviationPercentage': 'last'
        }).reset_index()
        
        # Calculate weekly changes
        weekly_df['WeeklyPlannedChange'] = weekly_df['PlannedProgress'].diff()
        weekly_df['WeeklyActualChange'] = weekly_df['CumulativeActual'].diff()
        weekly_df['WeeklyDeviationChange'] = weekly_df['ProgressDeviation'].diff()
        
        return weekly_df