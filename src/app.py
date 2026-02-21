import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash
from dash import dcc, html


def load_data(path: str) -> pd.DataFrame:
    """
    Load and prepare the dataset.

    Args:
        path: Path to the CSV file.

    Returns:
        DataFrame with computed columns.
    """
    df = pd.read_csv(path)

    # Date conversion
    df['invoice_date'] = pd.to_datetime(df['invoice_date'], format='%d/%m/%Y', errors='coerce')

    # Revenue calculation
    df['total_revenue'] = df['qty'] * df['amount']

    return df



def analyze_bcg_matrix(df: pd.DataFrame, top_pct: float = 0.2) -> pd.DataFrame:
    """
    Build a BCG-style product matrix with a top X% threshold (Pareto-like).

    Args:
        df: Input invoices DataFrame.
        top_pct: Proportion of products considered as "top" for volume/revenue thresholds.

    Returns:
        DataFrame with BCG category and market share per product.
    """
    analysis = df.groupby('product_id').agg({
        'total_revenue': 'sum',
        'qty': 'sum',
        'email': 'nunique'
    }).rename(columns={'email': 'nb_customers'})

    # Top X% thresholds
    revenue_threshold = analysis['total_revenue'].quantile(1 - top_pct)
    volume_threshold = analysis['qty'].quantile(1 - top_pct)

    def classify(row):
        high_rev = row['total_revenue'] > revenue_threshold
        high_vol = row['qty'] > volume_threshold

        if high_rev and high_vol:
            return 'Star'
        elif high_rev:
            return 'Premium'
        elif high_vol:
            return 'Volume'
        else:
            return 'Standard'

    analysis['category'] = analysis.apply(classify, axis=1)
    analysis['market_share'] = (analysis['total_revenue'] / analysis['total_revenue'].sum()) * 100

    return analysis.reset_index()



def viz_bcg(bcg: pd.DataFrame) -> go.Figure:
    """
    Scatter plot for the BCG product matrix.
    """
    fig = px.scatter(
        bcg,
        x='qty',
        y='total_revenue',
        color='category',
        size='nb_customers',
        hover_data=['product_id', 'market_share'],
        color_discrete_map={
            'Star':'#2ecc71',
            'Premium': '#3498db',
            'Volume': '#f39c12',
            'Standard': '#95a5a6'
        },
        title='Strategic Product Matrix (BCG)',
        labels={'qty': 'Sales volume (units)', 'total_revenue': 'Total revenue ($)'}
    )

    # Threshold lines (approximate top 20% on this aggregated table)
    volume_threshold = bcg['qty'].quantile(0.8)
    revenue_threshold = bcg['total_revenue'].quantile(0.8)

    fig.add_vline(
        x=volume_threshold,
        line_dash='dash',
        line_color='gray',
        annotation_text='Top 20% volume'
    )
    fig.add_hline(
        y=revenue_threshold,
        line_dash='dash',
        line_color='gray',
        annotation_text='Top 20% revenue'
    )

    fig.update_layout(template='plotly_white', height=500)

    return fig


def analyze_abc(df: pd.DataFrame) -> pd.DataFrame:
    """
    ABC analysis by product based on total revenue.

    Args:
        df: Input invoices DataFrame.

    Returns:
        DataFrame with ABC class and rank per product.
    """
    products = (
        df.groupby('product_id')
        .agg({'total_revenue': 'sum'})
        .sort_values('total_revenue', ascending=False)
    )

    products['contrib_pct'] = (products['total_revenue'] / products['total_revenue'].sum()) * 100
    products['contrib_cumul'] = products['contrib_pct'].cumsum()

    def abc_class(cumulative_pct):
        if cumulative_pct <= 80:
            return 'A (80% revenue)'
        elif cumulative_pct <= 95:
            return 'B (15% revenue)'
        else:
            return 'C (5% revenue)'

    products['class'] = products['contrib_cumul'].apply(abc_class)

    products = products.reset_index()
    products['rank'] = range(1, len(products) + 1)

    return products


def analyze_geography(df: pd.DataFrame, top_n: int = 15) -> pd.DataFrame:
    """
    Geographic performance by city (top N cities).

    Args:
        df: Input invoices DataFrame.
        top_n: Number of top cities to keep based on total revenue.

    Returns:
        DataFrame with geographic metrics per city.
    """
    geo = df.groupby('city').agg({
        'total_revenue': 'sum',
        'email': 'nunique',
        'product_id': 'count'
    }).rename(columns={
        'total_revenue': 'total_revenue_city',
        'email': 'nb_customers',
        'product_id': 'nb_transactions'
    })

    geo['avg_basket'] = geo['total_revenue_city'] / geo['nb_transactions']
    geo['revenue_per_customer'] = geo['total_revenue_city'] / geo['nb_customers']

    # Composite potential score (normalized)
    geo['score'] = (
        (geo['total_revenue_city'] / geo['total_revenue_city'].max()) * 0.4 +
        (geo['avg_basket'] / geo['avg_basket'].max()) * 0.3 +
        (geo['nb_customers'] / geo['nb_customers'].max()) * 0.3
    ) * 10

    return geo.nlargest(top_n, 'total_revenue_city').reset_index()


def viz_geo(geo: pd.DataFrame) -> go.Figure:
    """
    Geographic bubble chart for top cities.
    """
    fig = px.scatter(
        geo,
        x='avg_basket',
        y='total_revenue_city',
        size='nb_customers',
        color='score',
        hover_data=['city'],
        text='city',
        color_continuous_scale='Viridis',
        title='Geographic Performance (Top 15 Cities)',
        labels={
            'avg_basket': 'Average basket ($)',
            'total_revenue_city': 'Total revenue ($)',
            'score': 'Potential score'
        }
    )

    fig.update_traces(textposition='top center')
    fig.update_layout(template='plotly_white', height=500)

    return fig



def analyze_profiles(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """
    Top professions by total revenue.

    Args:
        df: Input invoices DataFrame.
        top_n: Number of top professions to keep based on total revenue.

    Returns:
        DataFrame with metrics per profession.
    """
    profiles = df.groupby('job').agg({
        'total_revenue': ['sum', 'mean'],
        'email': 'nunique'
    })

    profiles.columns = ['total_revenue', 'avg_spend', 'nb_customers']
    profiles = profiles.nlargest(top_n, 'total_revenue').reset_index()

    return profiles


def viz_profiles(profiles: pd.DataFrame) -> go.Figure:
    """
    Horizontal bar chart for professions.
    """
    fig = px.bar(
        profiles,
        y='job',
        x='total_revenue',
        orientation='h',
        color='avg_spend',
        color_continuous_scale='Blues',
        title='Top 10 Professions by Revenue',
        labels={
            'total_revenue': 'Total revenue ($)',
            'job': 'Profession',
            'avg_spend': 'Average spend ($)'
        },
        text='total_revenue'
    )

    fig.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
    fig.update_layout(template='plotly_white', height=500)

    return fig



def viz_abc(abc: pd.DataFrame) -> go.Figure:
    """
    Cumulative revenue plot for ABC analysis.
    """
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=abc['rank'],
        y=abc['contrib_cumul'],
        mode='lines+markers',
        name='Cumulative revenue (%)'
    ))

    fig.add_hline(
        y=80,
        line_dash='dash',
        line_color='green',
        annotation_text='80% (end of class A)',
        annotation_position='top left'
    )
    fig.add_hline(
        y=95,
        line_dash='dash',
        line_color='orange',
        annotation_text='95% (end of class B)',
        annotation_position='bottom left'
    )

    fig.update_layout(
        title='ABC Analysis - Cumulative Revenue',
        xaxis_title='Products (sorted by decreasing revenue)',
        yaxis_title='Cumulative revenue (%)',
        yaxis=dict(range=[0, 105]),
        template='plotly_white',
        height=500
    )

    return fig



def analyze_distribution(df: pd.DataFrame) -> dict:
    """
    Distribution statistics for order amounts.

    Args:
        df: Input invoices DataFrame.

    Returns:
        Dict with descriptive stats and normalized data.
    """
    stats = {
        'mean': df['total_revenue'].mean(),
        'median': df['total_revenue'].median(),
        'std': df['total_revenue'].std(),
        'min': df['total_revenue'].min(),
        'max': df['total_revenue'].max(),
        'q25': df['total_revenue'].quantile(0.25),
        'q75': df['total_revenue'].quantile(0.75)
    }

    # Min–Max normalization
    df_norm = df.copy()
    df_norm['revenue_norm'] = (
        (df['total_revenue'] - stats['min']) / (stats['max'] - stats['min'])
    )

    return {'stats': stats, 'data': df_norm}



def viz_distribution(result: dict) -> go.Figure:
    """
    Histogram + boxplot for order amounts.
    """
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Amount distribution', 'Box plot'),
        column_widths=[0.7, 0.3]
    )

    # Histogram
    fig.add_trace(
        go.Histogram(
            x=result['data']['total_revenue'],
            nbinsx=50,
            name='Frequency'
        ),
        row=1, col=1
    )

    # Box plot
    fig.add_trace(
        go.Box(
            y=result['data']['total_revenue'],
            name='Distribution'
        ),
        row=1, col=2
    )

    fig.update_xaxes(title_text='Amount ($)', row=1, col=1)
    fig.update_yaxes(title_text='Frequency', row=1, col=1)
    fig.update_yaxes(title_text='Amount ($)', row=1, col=2)

    fig.update_layout(
        title_text='Order amount distribution analysis',
        template='plotly_white',
        showlegend=False,
        height=500
    )
    
    return fig



def create_dashboard(bcg, abc, geo, profiles, distrib):
    """
    Dash dashboard with 5 indicators.
    """
    app = dash.Dash(__name__)

    # Reusable style for indicator boxes
    style_box = {
        'padding': '20px',
        'backgroundColor': 'white',
        'margin': '10px',
        'borderRadius': '10px',
        'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
    }

    app.layout = html.Div([
        # Header
        html.Div([
            html.H1(
                "E-Commerce Analysis Dashboard",
                style={'textAlign': 'center', 'color': '#2c3e50'}
            ),
            html.H3(
                "Dataset: invoices.csv (10,000 transactions)",
                style={'textAlign': 'center', 'color': '#7f8c8d'}
            ),
            html.P(
                "Team: [Your names]",
                style={'textAlign': 'center', 'color': '#95a5a6'}
            )
        ], style={'padding': '20px', 'backgroundColor': '#ecf0f1', 'marginBottom': '20px'}),

        # Indicator 1: BCG
        html.Div([
            html.H3("Indicator 1: BCG Product Matrix", style={'color': '#2980b9'}),
            html.P("Action: Focus on Stars/Premium (top 20%), monitor Standard products."),
            dcc.Graph(figure=viz_bcg(bcg))
        ], style=style_box),

        # Indicator 2: ABC
        html.Div([
            html.H3("Indicator 2: ABC Analysis (Pareto)", style={'color': '#27ae60'}),
            html.P("Action: Prioritize management of Class A products (up to 80% of revenue)."),
            dcc.Graph(figure=viz_abc(abc))
        ], style=style_box),

        # Indicator 3: Geography
        html.Div([
            html.H3("Indicator 3: Geographic Performance", style={'color': '#8e44ad'}),
            html.P("Action: Invest in cities with high potential scores."),
            dcc.Graph(figure=viz_geo(geo))
        ], style=style_box),

        # Indicator 4: Profiles
        html.Div([
            html.H3("Indicator 4: Top Professions by Revenue", style={'color': '#d35400'}),
            html.P("Action: B2B targeting by profession and corporate partnerships."),
            dcc.Graph(figure=viz_profiles(profiles))
        ], style=style_box),

        # Indicator 5: Distribution
        html.Div([
            html.H3("Indicator 5: Amount Distribution", style={'color': '#c0392b'}),
            html.P("Action: Segment customers by basket size (small / medium / large)."),
            dcc.Graph(figure=viz_distribution(distrib))
        ], style=style_box)
    ], style={'backgroundColor': '#f5f6fa', 'padding': '10px'})

    return app



df = load_data('../data/invoices.csv')

bcg = analyze_bcg_matrix(df)
abc = analyze_abc(df)
geo = analyze_geography(df)
profiles = analyze_profiles(df)
distrib = analyze_distribution(df)

app = create_dashboard(bcg, abc, geo, profiles, distrib)

if __name__ == "__main__":
    app.run_server(debug=True, port=8051)
