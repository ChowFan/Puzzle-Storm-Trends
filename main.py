import requests
import bs4
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as md

STORM_URL = "https://lichess.org/storm/dashboard"
BASE_URL = "https://lichess.org"

username = input("Enter username: ")
next_link = STORM_URL + "/" + username

dfs = []

while(next_link):
    r = requests.get(next_link)
    # print(r.url, r)
    if r.status_code != 200:
        raise Exception("Problem with lichess or nonexistent account")
    soup = bs4.BeautifulSoup(r.text, "html.parser")
    trs = soup.select("tr")

    page_data = []

    for tr in trs:
        row = []
        for elem in tr:
            row.append(elem.text)
            next_link = elem.a
        if next_link:
            next_link = BASE_URL + next_link["href"]
            break
        page_data.append(row)
    col_names = page_data[0]
    # Remove table headers
    page_data.pop(0)
    # Remove the last row -- contains link to next page
    page_data.pop()
    dfs.append(pd.DataFrame(page_data, columns=col_names))

# Combine the dfs created from each page to a single df
df = pd.concat(dfs, axis=0).reset_index(drop=True)
# Turn as many cols to numeric dtypes if possible for graphing compatibility
df = df.apply(pd.to_numeric, errors="ignore")
df["Best run of day"] = pd.to_datetime(df["Best run of day"])
# Strip '%' or 's' to turn the column into one of numeric dtype
df_objs = df.select_dtypes("object")
df[df_objs.columns] = df_objs.applymap(lambda x: x[:-1]).apply(pd.to_numeric)

# print(df.info())

fig = plt.figure(layout="constrained")
spec = fig.add_gridspec(2, 4)
axs = [[0 for i in range(4)] for i in range(2)]
for row in range(2):
    for col in range(4):
        ax = fig.add_subplot(spec[row, col])
        ax.xaxis.set_major_locator(md.YearLocator())
        axs[row][col] = ax

axs[1][1].set_subplotspec(spec[1, 1:3])
fig.delaxes(axs[1][2])

sns.scatterplot(x="Best run of day", y="Highest solved", data=df, ax=axs[0][0])
sns.scatterplot(x="Best run of day", y="Moves", data=df, ax=axs[0][1])
sns.scatterplot(x="Best run of day", y="Accuracy", data=df, ax=axs[0][2])
sns.scatterplot(x="Best run of day", y="Combo", data=df, ax=axs[0][3])
sns.scatterplot(x="Best run of day", y="Time", data=df, ax=axs[1][0])
sns.scatterplot(x="Best run of day", y="Score", data=df, ax=axs[1][1])
sns.scatterplot(x="Best run of day", y="Runs", data=df, ax=axs[1][3])
plt.show()