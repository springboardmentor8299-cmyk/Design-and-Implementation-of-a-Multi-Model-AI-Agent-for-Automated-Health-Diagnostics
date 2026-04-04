def compare_with_ranges(df, reference_ranges):
    status_list = []

    for index, row in df.iterrows():
        param = row["Parameter"]
        value = row["Value"]

  
        if value is None:
            status = None

  
        elif param in reference_ranges:
            ref_low = reference_ranges[param]["low"]
            ref_high = reference_ranges[param]["high"]

            if value < ref_low:
                status = "Low"
            elif value > ref_high:
                status = "High"
            else:
                status = "Normal"

        else:
            status = "Unknown"

        status_list.append(status)

    df["Status"] = status_list
    return df

def compare_parameters(df):
    """
    Converts DataFrame to dictionary:
    {parameter: status}
    """

    result = {}

    for _, row in df.iterrows():
        param = str(row["Parameter"]).lower() 
        status = str(row["Status"]).lower() if row["Status"] else None

        result[param] = status

    return result