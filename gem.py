import streamlit as st
import numpy as np
import plotly.graph_objects as go
from skimage import measure
from stl import mesh
import io

# --- Field Generation Functions ---

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
    field = np.sin(freq_r * r) * np.cos(freq_t * theta) + \
            np.sin(freq_t * theta) * np.cos(Z * z_scale)
    return X, Y, Z, field

def get_sphere(res, radius):
    # Create coordinate grid
    x = np.linspace(-3, 3, res)
    y = np.linspace(-3, 3, res)
    z = np.linspace(-2, 2, res)
    X, Y, Z = np.meshgrid(x, y, z)

    # Sphere equation
    field = X**2 + Y**2 + Z**2 - radius**2
    return X, Y, Z, field

# --- STL Conversion ---

def create_stl_file(field, level=0):
    """Generates an STL file from a 3D field using marching cubes."""
    # Use marching cubes to obtain vertices and faces.
    # The `spacing` parameter is important for the STL to have the correct scale.
    verts, faces, _, _ = measure.marching_cubes(field, level=level, spacing=(0.2, 0.2, 0.2))

    # Create the mesh object
    stl_mesh = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
    for i, f in enumerate(faces):
        for j in range(3):
            stl_mesh.vectors[i][j] = verts[f[j],:]

    # Save mesh to a binary buffer
    with io.BytesIO() as buffer:
        stl_mesh.save('streamlit_mesh', buffer)
        return buffer.getvalue()

# --- Streamlit Interface ---
st.title("Interactive Field Generator")
st.sidebar.header("Parameters")

shape = st.sidebar.selectbox("Shape", ["Gyroid", "Sphere"])

res = 40  # Keep low for web performance

if shape == "Gyroid":
    freq_r = st.sidebar.slider("Radial Frequency", 1.0, 10.0, 3.0)
    freq_t = st.sidebar.slider("Angular Frequency", 1, 10, 5)
    z_scale = st.sidebar.slider("Vertical Scale", 0.1, 5.0, 1.0)
    X, Y, Z, field = get_polar_gyroid(res, freq_r, freq_t, z_scale)
    isomin, isomax = -0.5, 0.5
    stl_level = 0
elif shape == "Sphere":
    radius = st.sidebar.slider("Radius", 0.5, 2.5, 1.5)
    X, Y, Z, field = get_sphere(res, radius)
    isomin, isomax = -0.1, 0.1 # A thin shell around the surface
    stl_level = 0

# --- Visualization ---
fig = go.Figure(data=go.Isosurface(
    x=X.flatten(), y=Y.flatten(), z=Z.flatten(),
    value=field.flatten(),
    isomin=isomin, isomax=isomax,
    opacity=0.6, surface_count=2
))
st.plotly_chart(fig, use_container_width=True)


# --- Download Button ---
st.sidebar.header("Download")
stl_data = create_stl_file(field, level=stl_level)
st.sidebar.download_button(
    label="Download STL",
    data=stl_data,
    file_name=f"{shape.lower()}.stl",
    mime="model/stl"
)
