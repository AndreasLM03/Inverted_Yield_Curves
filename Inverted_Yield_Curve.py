import pandas as pd
import numpy as np
from matplotlib.dates import MonthLocator, YearLocator
import matplotlib.pyplot as plt
from datetime import date
from dateutil.relativedelta import relativedelta
import requests
from bs4 import BeautifulSoup
import datetime
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle


yield_ = pd.DataFrame(columns=['1Mo','2Mo','3Mo','6Mo','1Yr','2Yr','3Yr','5Yr','7Yr','10Yr','20Yr','30Yr'])
time_range = range(1990,2023,1)
base_url = "https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?type=daily_treasury_yield_curve&field_tdr_date_value="
path = "/home/pi/Dokumente/Programme/Inverted_Yield_Curves/"

for i,year in enumerate(time_range):
    url = base_url + str(year)
    data = requests.get(url).text
    soup = BeautifulSoup(data, 'html.parser')
    table = soup.find('table')
    df_soup = pd.read_html(str(table))[0]
    # rearrange 
    df_soup = df_soup[['1 Mo','2 Mo','3 Mo','6 Mo','1 Yr','2 Yr','3 Yr','5 Yr','7 Yr','10 Yr','20 Yr','30 Yr']]
    df_soup.columns = ['1Mo','2Mo','3Mo','6Mo','1Yr','2Yr','3Yr','5Yr','7Yr','10Yr','20Yr','30Yr']
    df_soup.index = pd.to_datetime(pd.read_html(str(table))[0]['Date'])
    # append and delete duplicates
    yield_ = yield_.append(df_soup, ignore_index=False)
yield_.to_pickle(path  + "yield_data.pkl")
yield_.to_csv(path  + "yield_data.csv")
print("download completed")

def highlight_negative_values(cell):
    if type(cell) != str and cell < 0 :
        return 'color: red'
    else:
        return 'color: black'

def time_ft(time):
    return str(time.strftime("%Y%m%d"))

def calculate_matrix():
    df = pd.DataFrame(np.zeros((len(yield_.columns),len(yield_.columns))))
    df.index = considered_yield_data.index
    df.columns = df.index 
    df[:] = np.nan
    for hor in range(0,len(df.index)):
        for ver in range(0,len(df.index)):
            if hor>ver:
                df.iloc[hor,ver] = considered_yield_data.iloc[hor]-considered_yield_data.iloc[ver]
    available_entries = (len(df))**2 - df.isna().sum().sum()
    negative_entries = np.sum((df < 0).values.ravel())
    inverted_percentage = round(negative_entries/available_entries*100,1)
    return inverted_percentage, df.style.applymap(highlight_negative_values)

def add_patch(startdate,enddate):
    start = mdates.date2num(startdate)
    end = mdates.date2num(enddate)
    width = end - start
    range_in_days = (enddate-startdate).days
    rect = Rectangle((start, ax.get_ylim()[0]), width, ax.get_ylim()[1] - ax.get_ylim()[0], color='yellow',alpha = 0.15)
    ax.add_patch(rect)

yield_ = pd.read_pickle("yield_data.pkl")
inverted_percentage = [] 
for u in range(0,(yield_.shape[0])):
    considered_yield_data = yield_.iloc[u]
    inverted_percentage.append(calculate_matrix()[0])
yield_["inverted_percentage"] = inverted_percentage
print("calculation completed")

### https://en.wikipedia.org/wiki/List_of_recessions_in_the_United_States
from datetime import date
r1_start,r1_end = date(1990,7,1), date(1991,3,1)
r2_start,r2_end = date(2001,3,1), date(2001,11,1)
r3_start,r3_end = date(2007,12,1), date(2009,6,1)
r4_start,r4_end = date(2020,2,1), date(2020,4,1)

recessions = [[r1_start,r1_end],
              [r2_start,r2_end],
              [r3_start,r3_end],
              [r4_start,r4_end]]

# https://fred.stlouisfed.org/series/DRTSCILM
Tightening_Standards_csv = path + "DRTSCILM.csv"
Tightening_Standards_df = pd.read_csv(Tightening_Standards_csv, sep=',')
Tightening_Standards_df.index = pd.to_datetime(Tightening_Standards_df["DATE"])
Tightening_Standards_df.drop(['DATE'], axis=1,inplace = True)


yield_part = pd.read_pickle("yield_data.pkl")
fig,ax = plt.subplots(figsize=(35,10))
ax.plot(yield_.index, yield_["inverted_percentage"], label='Amount of inverted yield curves', linewidth=1.5, color = "blue")
ax.axhline(y=50, linewidth = 1.5, linestyle='--', color = "blue")
ax.set_ylim(-30,100)

# add recessions as a rectangle inside the figure
for i,_ in enumerate(recessions):
    add_patch(recessions[i][0],recessions[i][1])
    
# Annotation - current value
ax.annotate('%0.2f' % yield_["inverted_percentage"].iloc[-1], xy=(1, yield_["inverted_percentage"].iloc[-1]), xytext=(-80, 0), 
                     xycoords=('axes fraction', 'data'), textcoords='offset points')

ax.plot(Tightening_Standards_df.index, Tightening_Standards_df["DRTSCILM"], label='Tightening_Standards', linewidth=1.5,color = "green")
ax.axhline(y=0, linewidth = 1.5, linestyle='--',color = "green")
## critical area
treshold = 50
ax.fill_between(yield_.index, yield_["inverted_percentage"], treshold,
                      where=(treshold < yield_["inverted_percentage"]),
                      facecolor='orange', edgecolor='orange', alpha=1)

legend = ax.legend(loc='upper right')

mloc = MonthLocator()
ax.xaxis.set_major_locator(mloc)
ax.grid(True,linewidth=2,alpha = 0.3)

# Labeling
plt.xticks(fontsize=4, rotation=90)
ax.set_title('Amount of inverse yield curves over time')
plt.ylabel('Percentage')
plt.xlabel("Date")

# save figure
pdf_name = path + "Yield.pdf"
plt.savefig(pdf_name)

### Upload und Bild danach löschen
os.system("/home/pi/Dropbox-Uploader/dropbox_uploader.sh upload  " + CSVpath + " /YieldRatio/")
os.system("/home/pi/Dropbox-Uploader/dropbox_uploader.sh upload  " + pdf_name + " /Inverted_Yield_Curve/")