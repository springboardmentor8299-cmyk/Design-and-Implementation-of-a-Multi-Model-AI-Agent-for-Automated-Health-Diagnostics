def compare_with_ranges(df, reference_ranges):
    status_list = []

    for index, row in df.iterrows():
        param = row["Parameter"]
        value = row["Value"]

        if value is None:
            status = None   # 👈 don't assign Normal
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
