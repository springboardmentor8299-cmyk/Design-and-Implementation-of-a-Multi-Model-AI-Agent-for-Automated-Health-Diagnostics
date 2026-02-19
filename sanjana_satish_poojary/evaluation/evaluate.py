def evaluate_single_report(predicted_df, ground_truth_dict):

    total_extraction = 0
    correct_extraction = 0

    total_classification = 0
    correct_classification = 0

    for index, row in predicted_df.iterrows():
        param = row["Parameter"]
        predicted_value = row["Value"]
        predicted_status = row["Status"]

        if param in ground_truth_dict:

            total_extraction += 1
            total_classification += 1

            true_value = ground_truth_dict[param]["Value"]
            true_status = ground_truth_dict[param]["Status"]

            # Extraction Accuracy
            if abs(predicted_value - true_value) < 0.01:
                correct_extraction += 1

            # Classification Accuracy
            if predicted_status == true_status:
                correct_classification += 1

    extraction_accuracy = (
        (correct_extraction / total_extraction) * 100
        if total_extraction > 0 else 0
    )

    classification_accuracy = (
        (correct_classification / total_classification) * 100
        if total_classification > 0 else 0
    )

    return extraction_accuracy, classification_accuracy
