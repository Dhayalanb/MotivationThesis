import sys, getopt
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

STRATEGIES = ['GradientDescentStrategy', 'MagicByteStrategy' , 'OneByteStrategy', 'LengthTaintStrategy', 'ConcolicStrategy', 'RandomStrategy', 'RandomTaintStrategy']
VARIABLES_TO_TEST = ['oviedo', 'cyclomatic' , 'nrOfOffsets', 'cases', 'chain_size', 'depth2', 'trace_length']
PROGRAMS = [#"gif2png", 
"file", "nm", "djpeg", "jhead", #"xmlwf",
]

def process_file():
    all_data = []
    for program in PROGRAMS:
        print("Reading " + "../results/%s_raw_depth.csv" % program)
        program_data = pd.read_csv("../results/%s_raw_depth.csv" % program, index_col=False)
        program_data["program"] = program
        all_data.append(program_data)
    data = pd.concat(all_data)
    #set right types
    data["program"] = data["program"].astype('category')
    data["status"] = data["status"].astype('category')
    data["Strategy"] = data["Strategy"].astype('category')

    #add new column
    data["relative_depth"] = data["depth2"]/data["trace_length"]
    return data

def process_df(df):
    columns = set(['relative_depth', 'program'])
    columns.update(set(VARIABLES_TO_TEST))
    df_copy = df[columns].copy()
    for column in columns:
        df_copy = df_copy[df_copy[column] != '-']
    programs = df_copy.program.unique()
    for variable in VARIABLES_TO_TEST:
        df_copy[variable] = df_copy[variable].astype('float')
    fig, axs = plt.subplots(nrows=programs.size, figsize=(8, programs.size * 8))
    for ax, f in zip(axs, df_copy.program.unique()):
        ax.set_title(f)
        ax = sns.heatmap(df_copy[df_copy.program == f].corr(),
                        fmt=".2f", annot=True, ax=ax, cmap="RdBu_r", vmin=-1, vmax=1)
    fig.savefig("output.png", dpi=300)

    #g = sns.FacetGrid(df[df["flipped"] == 1], col="program", margin_titles=True)
    #g = g.map(sns.countplot, "Strategy", order=df.Strategy.cat.categories, color="k")
    #g.savefig("output.png")

def main(argv):
    print("Processing data...")
    df = process_file()
    process_df(df)
    print("Done!")

if __name__ == "__main__":
   main(sys.argv[1:])