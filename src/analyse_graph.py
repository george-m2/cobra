import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import MaxNLocator


def plot_ACPL_graph(acpl_array):
    """
    Plot the ACPL graph for the game with a UI style similar to the provided image.

    Args:
        acpl_array (list): List of ACPL values for the game.
    """
    # normalise ACPL magnitude to 0-1 range
    # normalisation occurs at the client side when rendering the ACPL text as well
    max_acpl_abs = max(abs(acpl) for acpl in acpl_array)
    normalized_acpl = [acpl / max_acpl_abs for acpl in acpl_array]

    plt.style.use('dark_background')  # Use a dark theme for the plot
    fig, ax = plt.subplots(figsize=(8, 6))

    ax.plot(normalized_acpl, marker='o', markersize=8, linestyle='-', color='w', linewidth=2, alpha=0.7)

    # Setting the title and labels
    ax.set_title('Accuracy of your moves compared to Stockfish', color='w', fontweight='bold')
    ax.set_xlabel('Move', color='w')
    ax.set_ylabel('Accuracy', color='w')

    # Ensuring the grid, tick labels, and spines are properly formatted
    ax.grid(True, linestyle='--', linewidth=0.5, alpha=0.5)
    ax.tick_params(colors='w', which='both')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Setting up the y-axis to properly display negative values
    ax.axhline(0, color='grey', linewidth=0.75, alpha=1)  # Add a horizontal line at y=0
    ax.set_ylim([-1, 1])  # Ensure the y-axis spans from -1 to 1

    # Ensure x-axis has integer ticks only
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))

    plt.show()

