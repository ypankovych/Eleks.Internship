import matplotlib as mpl
import matplotlib.pyplot as plt


def show_charts(data_names, data_values, chart_name):
    data_names = data_names
    data_values = data_values
    dpi = 80
    fig = plt.figure(dpi = dpi, figsize = (512 / dpi, 384 / dpi))
    mpl.rcParams.update({'font.size': 11})
    plt.title(chart_name)
    plt.pie(data_values,
            labels = data_values,
            autopct='%.1f',
            radius = 1.1,
            explode = [0.15] + [0 for _ in range(len(data_names) - 1)],
            shadow=True)
    plt.legend(bbox_to_anchor = (-0.16, 0.45, 0.25, 0.25),
            loc = 'lower left',
            labels = data_names)
    plt.show()