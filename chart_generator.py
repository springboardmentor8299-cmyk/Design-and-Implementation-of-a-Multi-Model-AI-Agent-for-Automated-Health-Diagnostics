import matplotlib.pyplot as plt

def generate_chart(parameters):

    names = [p["name"] for p in parameters]
    values = [p["value"] for p in parameters]

    plt.figure()
    plt.bar(names, values)

    path = "static/chart.png"
    plt.savefig(path)

    return path