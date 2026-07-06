import streamlit as st
import numpy as np
import plotly.graph_objects as go

def get_polar_gyroid(res, freq_r, freq_t, z_scale):
    # Create coordinate grid
    x = np.linspace(-3, 3, res)
    y = np.linspace(-3, 3, res)
    z = np.linspace(-2, 2, res)
    X, Y, Z = np.meshgrid(x, y, z)

    # Polar Transformation
    r = np.sqrt(X**2 + Y**2)
    theta = np.arctan2(Y, X)

    # Gyroid equation mapped to polar coordinates
    # Field = sin(freq_r * r) * cos(freq_t * theta) + sin(freq_t * theta) * cos(Z * z_scale)
    field = np.sin(freq_r * r) * np.cos(freq_t * theta) + \
            np.sin(freq_t * theta) * np.cos(Z * z_scale)
    return X, Y, Z, field

# --- Streamlit Interface ---
st.title("Interactive Polar Field Generator")
st.sidebar.header("Parameters")

freq_r = st.sidebar.slider("Radial Frequency", 1.0, 10.0, 3.0)
freq_t = st.sidebar.slider("Angular Frequency", 1, 10, 5)
z_scale = st.sidebar.slider("Vertical Scale", 0.1, 5.0, 1.0)

# Generate data
res = 40  # Keep low for web performance
X, Y, Z, field = get_polar_gyroid(res, freq_r, freq_t, z_scale)

# Visualization using Plotly
fig = go.Figure(data=go.Isosurface(
    x=X.flatten(), y=Y.flatten(), z=Z.flatten(),
    value=field.flatten(),
    isomin=-0.5, isomax=0.5,
    opacity=0.6, surface_count=2
))

st.plotly_chart(fig, use_container_width=True)