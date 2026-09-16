import json
import matplotlib.pyplot as plt
from matplotlib.sankey import Sankey

from validate_input import get_flows, validate_data


def plot_power_budget(data):
    """
    Plot a steady-state power-budget Sankey diagram.

    Inputs and outputs define the external system power balance. Losses are
    displayed as individual branches. If a storage element is present, it is
    represented as an internal recirculating power flow.
    """
    # -----------------------------------------------------------------
    # Validate input data
    # -----------------------------------------------------------------
    validate_data(data)

    # -----------------------------------------------------------------
    # Parse input data
    # -----------------------------------------------------------------
    inputs = get_flows(data, "input")
    outputs = get_flows(data, "output")
    losses = get_flows(data, "loss")
    storage = get_flows(data, "storage")

  
    has_storage = bool(storage)


    # -----------------------------------------------------------------
    # Create figure
    # -----------------------------------------------------------------
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(1, 1, 1, xticks=[], yticks=[])

    sankey = Sankey(
        ax=ax,
        scale=0.005,
        offset=0.0 if has_storage else 0.5,
        head_angle=120
    )

    # -----------------------------------------------------------------
    # Build main system
    # -----------------------------------------------------------------
    main_flows = []
    main_labels = []
    main_orientations = []
    main_pathlengths = []

    # External inputs
    for flow in inputs:
        main_flows.append(flow["value"])
        main_labels.append(flow["name"])
        main_orientations.append(0)
        main_pathlengths.append(0.0)

    # Storage return
    if has_storage:
        P_store = storage[0]["value"]

        main_flows.append(P_store)
        main_labels.append(None)
        main_orientations.append(-1)
        main_pathlengths.append(0.2)

    # Useful outputs
    for flow in outputs:
        main_flows.append(-flow["value"])
        main_labels.append(flow["name"])
        main_orientations.append(0)
        main_pathlengths.append(0.4 if has_storage else 0.2)

    # Losses
    for flow in losses:
        main_flows.append(-flow["value"])
        main_labels.append(flow["name"])
        main_orientations.append(-1)
        main_pathlengths.append(0.4 if has_storage else 0.2)

    # Storage outlet
    if has_storage:
        storage_index = len(main_flows)

        main_flows.append(-P_store)
        main_labels.append(storage[0]["name"])
        main_orientations.append(-1)
        main_pathlengths.append(0.2)

    # Add main system
    sankey.add(
        flows=main_flows,
        labels=main_labels,
        orientations=main_orientations,
        pathlengths=main_pathlengths,
        facecolor="#1f77b4",
        label="Main System"
    )

    # -----------------------------------------------------------------
    # Add storage return loop
    # -----------------------------------------------------------------
    if has_storage:
        sankey.add(
            flows=[P_store, -P_store],
            labels=[None, "Return"],
            orientations=[-1, -1],
            pathlengths=[0.2, 0.2],
            facecolor="#ff7f0e",
            prior=0,
            connect=(storage_index, 0),
            label="Storage"
        )

    # -----------------------------------------------------------------
    # Finish diagram
    # -----------------------------------------------------------------
    diagrams = sankey.finish()

    if has_storage:
        diagrams[-1].patch.set_hatch("//")
        diagrams[0].patch.set_zorder(3)

    plt.title(
        data.get("title", "Power Budget Flow"),
        fontsize=12,
        fontweight="bold",
        pad=20
    )

    plt.show()


def main(filename):
    """Read a JSON power-budget file and generate its Sankey diagram."""

    with open(filename, "r") as file:
        data = json.load(file)

    plot_power_budget(data)


if __name__ == "__main__":
    main("input.json")