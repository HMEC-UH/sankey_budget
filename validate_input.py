import math

def get_flows(data, flow_type):
    """Return all flow entries matching a specified type."""
    return [
        flow for flow in data["flows"]
        if flow["type"].lower() == flow_type.lower()
    ]

def validate_data(data):
    """
    Validate the structure and physical consistency of power-budget data.

    Parameters
    ----------
    data : dict
        Power-budget data containing a ``flows`` list. Each flow must define
        ``name``, ``type``, and ``value``.

    Raises
    ------
    ValueError
        If the input data are incomplete, invalid, or physically inconsistent.
    TypeError
        If the input data contain values of the wrong type.
    """

    allowed_types = {"input", "output", "loss", "storage"}
    required_fields = {"name", "type", "value"}

    # -----------------------------------------------------------------
    # Validate top-level structure
    # -----------------------------------------------------------------
    if not isinstance(data, dict):
        raise TypeError("Power-budget data must be a dictionary.")

    if "flows" not in data:
        raise ValueError("Power-budget data must contain a 'flows' field.")

    if not isinstance(data["flows"], list):
        raise TypeError("'flows' must be a list.")

    if not data["flows"]:
        raise ValueError("'flows' must contain at least one flow.")

    # -----------------------------------------------------------------
    # Validate individual flows
    # -----------------------------------------------------------------
    for i, flow in enumerate(data["flows"]):

        if not isinstance(flow, dict):
            raise TypeError(
                f"Flow {i} must be a dictionary."
            )

        missing_fields = required_fields - flow.keys()

        if missing_fields:
            raise ValueError(
                f"Flow {i} is missing required field(s): "
                f"{', '.join(sorted(missing_fields))}."
            )

        # Name
        if not isinstance(flow["name"], str):
            raise TypeError(
                f"Flow {i} 'name' must be a string."
            )

        if not flow["name"].strip():
            raise ValueError(
                f"Flow {i} 'name' cannot be empty."
            )

        # Type
        if not isinstance(flow["type"], str):
            raise TypeError(
                f"Flow {i} 'type' must be a string."
            )

        flow_type = flow["type"].lower()

        if flow_type not in allowed_types:
            raise ValueError(
                f"Flow '{flow['name']}' has invalid type "
                f"'{flow['type']}'. Allowed types are: "
                f"{', '.join(sorted(allowed_types))}."
            )

        # Value
        if not isinstance(flow["value"], (int, float)):
            raise TypeError(
                f"Flow '{flow['name']}' value must be numeric."
            )

        if flow["value"] < 0:
            raise ValueError(
                f"Flow '{flow['name']}' value cannot be negative."
            )

    # -----------------------------------------------------------------
    # Validate system configuration
    # -----------------------------------------------------------------
    inputs = get_flows(data, "input")
    outputs = get_flows(data, "output")
    losses = get_flows(data, "loss")
    storage = get_flows(data, "storage")

    if not inputs:
        raise ValueError(
            "At least one input flow is required."
        )

    if not outputs:
        raise ValueError(
            "At least one output flow is required."
        )

    if len(storage) > 1:
        raise ValueError(
            "Only one storage element is currently supported."
        )

    # -----------------------------------------------------------------
    # Validate steady-state power balance
    # -----------------------------------------------------------------
    P_in = sum(flow["value"] for flow in inputs)
    P_out = sum(flow["value"] for flow in outputs)
    P_loss = sum(flow["value"] for flow in losses)

    # Storage is an internal recirculating flow and therefore does not
    # contribute to the external steady-state power balance.
    if not math.isclose(P_in, P_out + P_loss, rel_tol=1e-9, abs_tol=1e-9):
        raise ValueError(
            "Power budget does not balance: "
            f"input = {P_in}, "
            f"output + losses = {P_out + P_loss}."
        )