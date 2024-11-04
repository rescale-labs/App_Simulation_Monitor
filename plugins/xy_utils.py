import plotly.graph_objects as go


def get_columns(df):
    if df.empty:
        return []
    else:
        return df.columns.to_list()


def create_plot(df, x_axis_value, y_axis_values, x_scale, y_scale):
    fig = go.Figure()

    for y_col in y_axis_values:
        fig.add_trace(
            go.Scatter(
                x=df[x_axis_value], y=df[y_col], mode="lines+markers", name=y_col
            )
        )

    fig.update_layout(
        title=f'Plot: {", ".join(y_axis_values)} vs. {x_axis_value}',
        xaxis=dict(title=x_axis_value, type=x_scale),
        yaxis=dict(title="Value", type=y_scale),
    )

    return fig
