from matplotlib import pyplot as plt
from matplotlib import cm
from matplotlib import pylab
from matplotlib.colors import ListedColormap
import pandas as pd
import numpy as np
import seaborn as sns
import os
from utility import *


class Plotter():
    """ This class enables us to save plots of the results obtained in our 
    machine learning process. Its main utility is to ease the handling of folder path
    and avoid code repetition.
    @plot_dir : directory in which all plots will be saved
    @subject_ids : range of the subjects ids (e.g. range(2,5) if we want to observe subjects 2,3 and 4)
    @cv_scores_dir : directory in which to save plots for the cross validation (plots for the cross 
    validation scores will be saved in : self.plot_dir/cv_scores_dir)
    @p_values_dir : directory in which to save plots for the p-values
    @perms_scores_dir : directory in which to save plots for the permutations
    @bootstrap_dir : directory in which to save plots regarding bootstrap
    @color : color for the different plots (must be one of matplotlib.cm's colormaps) """

    def __init__(self, plot_dir, subject_ids, cv_scores_dir="cv_scores", conf_matrixes_dir = "conf_matrixes", bootstrap_dir="bootstrap"):
        self.plot_dir = plot_dir
        self.subject_ids = subject_ids
        self.cv_scores_dir = cv_scores_dir
        self.bootstrap_dir = bootstrap_dir
        self.conf_matrixes_dir  = conf_matrixes_dir
        self.color = ListedColormap(cm.get_cmap("brg")(np.linspace(0, 0.5, 256)))
        colors = self.color(np.linspace(0, 1, 3))
        self.modality_to_color = {"vis": colors[2], "aud": colors[0], "cro": colors[1]}
        self.name_to_color = {"Vision": colors[2], "Audition": colors[0], "Cross-modal": colors[1]}
        self.translation = {"vis": ["vision", "visual"], "aud": ["audition", "auditive"], "cro": "cross-modal",
                            "R": "right", "L": "left"}

        # create the necessary directories
        for di in [cv_scores_dir, bootstrap_dir, conf_matrixes_dir]:
            if not os.path.exists(plot_dir + "/" + di):
                os.makedirs(plot_dir + "/" + di)

        plt.rcParams.update({'font.size': 12})

    def save(self, label, sub_dir, ylabel, xlabel="subject id", legend=True):
        """ function that adds the legend, title, label axes and saves a plot in self.plot_dir/sub_dir/label.jpg.
        @param label : the title of the plot and name of the file in which the plot will be saved
        @param sub_dir : the directory in which the plot will be saved
        @param ylabel : label for the y axis
        @param xlabel : label for the x axis
        @param legend : boolean to tell if need of a legend or not """

        if legend is not None:
            if legend is True:
                plt.legend(loc="lower center")
            else :
                plt.legend(loc=legend)
        plt.title(label, wrap=True)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.savefig(self.plot_dir + "/" + sub_dir + "/" + label + ".jpg", bbox_inches='tight')
        plt.close()

    def bar_plot_with_points(self, df, chance_level, pvals):
        if df["Region"].nunique() <= 2 :
            plt.figure(figsize=(10, 10))
        else :
            plt.figure(figsize=(23, 10))

        hue_order = ["Vision", "Audition"]
        if df["Modality"].nunique() <= 1 :
            hue_order = ["Cross-modal"]

        # Draw the bar chart
        sns.catplot(
            data=df,
            kind="bar",
            ci=None,
            x="Region",
            y="Score",
            hue="Modality",
            hue_order=hue_order,
            palette=self.name_to_color,
            alpha=.7,
        )
        g = sns.stripplot(
            data=df,
            x="Region",
            y="Score",
            hue="Modality",
            hue_order=hue_order,
            dodge=True,
            palette=self.name_to_color,
            alpha=0.6,
            size=7
        )
        bplot = sns.barplot(
            data=df,
            ci="sd",
            capsize=0.1,
            errcolor="black",
            errwidth=1.0,
            x="Region",
            y="Score_mean_dev",
            hue="Modality",
            hue_order=hue_order,
            palette=self.name_to_color,
            alpha=0.3,
        )

        i = 0
        for bar in bplot.patches[:len(pvals)]:
            star = stars(pvals[i])
            if star != "ns":
                bplot.annotate(star,
                    (bar.get_x() + bar.get_width() / 2, 0), 
                    ha="center", va="center",
                    size=12, xytext=(0, 8),
                    textcoords="offset points",
                    color = "white")
            i += 1

        g.legend_.remove()

        if chance_level:
            plt.axhline(0.25, label="chance level", color="black", alpha=0.5)

    def plot_cv_score_with_points(self, df, pvals, chance_level=False):
        """ function to plot the results of the cross validation, with individual points.
        @param df : the dataframe containing the cross val results
        @param chance_level : defaults to False, set to True if you want a line y = 0.25 to be added to the plot """
        ylabel = "CV score"

        for region in ["PT", "V5"]:
            labels = ["aud_"+region+"_L", "aud_"+region+"_R", "vis_"+region+"_L", "vis_"+region+"_R"]
            labels_pvals = ["vis_"+region+"_L", "vis_"+region+"_R", "aud_"+region+"_L", "aud_"+region+"_R"]
            df_within = verbose_dataframe(df[labels], self.subject_ids)
            self.bar_plot_with_points(df_within, chance_level, [pvals[l] for l in labels_pvals])
            self.save("Decoding within modality in "+region, self.cv_scores_dir, ylabel, xlabel="analysis", legend=None)

            labels = ["cross_"+region+"_L", "cross_"+region+"_R"]
            df_cross = verbose_dataframe(df[labels], self.subject_ids)
            self.bar_plot_with_points(df_cross, chance_level, [pvals[l] for l in labels])
            self.save("Decoding across modalities in "+region, self.cv_scores_dir, ylabel, xlabel="analysis", legend=None)

        labels = ["aud_V5_L", "aud_V5_R", "vis_V5_L", "vis_V5_R", "aud_PT_L", "aud_PT_R", "vis_PT_L", "vis_PT_R"]
        labels_pvals = ["vis_V5_L", "vis_V5_R", "vis_PT_L", "vis_PT_R", "aud_V5_L", "aud_V5_R", "aud_PT_L", "aud_PT_R"]
        df_within_all = verbose_dataframe(df[labels], self.subject_ids)
        self.bar_plot_with_points(df_within_all, chance_level, [pvals[k] for k in labels_pvals])
        self.save("Decoding within modality", self.cv_scores_dir, ylabel, xlabel="analysis", legend=None)

    def generate_title(self, begin, modality, pval):
        """ function that generates the title for bootstrap plots
        @param modality :  the modality (e.g. "aud_V5_R")
        @param pval : the estimated p-value """

        if modality[:3] == "cro":
            beginning = begin + " for cross-modal decoding in "
        else:
            beginning = begin + " for " + self.translation[modality[:3]][1] + " motion in "
        title = beginning + self.translation[modality[-1:]] + " " + modality[-4:-2]
        
        if pval > 0 : return title + " (estimated p-value = " + str(min(round(pval, 6),1)) + ")"
        else : return title

    def plot_bootstrap(self, df_bootstrap, df_group_results, pvals, n_bins):
        """ function to plot the bootstrap results. we plot a histogram of the bootstrap results for each modality and 
        add a vertical line that represents the group result for this modality.
        @param df_bootstrap : the dataframe containing the bootstrap scores
        @param df_group_results : the dataframe containing the group results
        @param pvals : a dictionnary containing the estimated p-value for each modality
        @param n_bins : the numbers of bins for the bootstrap histogram"""

        for modality in df_bootstrap:
            color = self.modality_to_color[modality[:3]]
            plt.hist(df_bootstrap[modality], bins=n_bins, color=color)
            plt.axvline(df_group_results[modality][0], label="group-level score", color="green")
            title = self.generate_title("Bootstrap", modality, pvals[modality])
            self.save(title, self.bootstrap_dir, "density", xlabel="score")

    def plot_group_confusion_matrix(self, group_cfm, classes):
        for modality in group_cfm:
            mean_cfm = np.zeros((len(classes), len(classes)))
            var_cfm = np.zeros((len(classes), len(classes)))
            cfm = group_cfm[modality]
            for i in range(len(classes)):
                for j in range(len(classes)):
                    mean_cfm[i][j] = np.mean(cfm[i][j])
                    var_cfm[i][j] = np.var(cfm[i][j])

            for stat, values in zip(["mean", "variance"], [mean_cfm, var_cfm]):
                df = pd.DataFrame(values, index = classes, columns = classes)
                pylab.figure(figsize=(8,8))
                sns.heatmap(df, linewidth = 1, annot = True, cmap = cm.YlOrRd)
                title = self.generate_title("Confusion Matrix "+stat, modality, -1)
                self.save(title, self.conf_matrixes_dir, "true label", "predicted label", None)


def plot_average_voxel_intensities(maps, classes, n_subjects):
    region = "V5_R"
    colors = ["red", "tomato", "coral", "orange", "deepskyblue", "cyan", "blue", "royalblue"]
    n_voxels = maps[0]["vis"][0][region].shape[1]
    mean_aud = dict()
    mean_vis = dict()

    for cla in classes:
        mean_aud[cla] = np.zeros(n_voxels)
        mean_vis[cla] = np.zeros(n_voxels)

    for i in range(n_subjects):
        for j, cla in enumerate(classes):
            mean_vis[cla] += np.mean(maps[i]["vis"][0][region][j * 12:(j + 1) * 12], axis=0) / n_subjects
            mean_aud[cla] += np.mean(maps[i]["aud"][0][region][j * 12:(j + 1) * 12], axis=0) / n_subjects

    plt.rcParams.update({'font.size': 15})
    plt.figure(figsize=(12, 8))

    idx = 0
    for cla in classes:
        plt.plot(range(n_voxels), mean_vis[cla], label="vis - " + cla, color=colors[idx])
        idx += 1

    for cla in classes:
        plt.plot(range(n_voxels), mean_aud[cla], label="aud - " + cla, color=colors[idx])
        idx += 1

    plt.xlabel("voxel id")
    plt.ylabel("intensity")
    plt.title("Average voxel intensities for " + region)
    plt.legend()
    plt.savefig("plots/average_voxel_intensities" + region + ".png")


def str_to_array(str_array, length):
    vals = [0] * length
    i = 0
    for v in str_array.split(" "):
        if "\n" in v:
            vals[i] = float(v[0:-2])
            i += 1
        elif v != "":
            vals[i] = float(v)
            i += 1
    return vals


def stars(pval):
    if pval > 0.05 : return "ns"
    if pval <= 0.0001 : return "****"
    if pval <= 0.001 : return "***"
    if pval <= 0.01 : return "**"
    else: return "*"