from components.heatmap_page import render_heatmap
from theme import load_css

def render(analysis=None, risk=None):
    load_css("base", "predictive", "heatmap")
    render_heatmap()