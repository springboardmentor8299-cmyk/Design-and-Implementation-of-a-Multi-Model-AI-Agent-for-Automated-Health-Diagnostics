def clean_data(parameters):

    clean = []

    for p in parameters:
        if p["value"] is not None:
            clean.append(p)

    return clean