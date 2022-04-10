# Inverted_Yield_Curves
An inverse yield structure exists when long-term interest rates on the capital market are lower than short-term interest rates. Normally, the exact opposite is the case.  Inverse yield curves rarely occur and are considered a quite solid signal for an upcoming economic recession.

## Import libraries
```python
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
```

## Download Yield data
We obtain the Treasury Par Yield Curve Rates from the official site of the U.S. DEPARTMENT OF THE TREASURY
```python
%%time
yield_ = pd.DataFrame(columns=['1Mo','2Mo','3Mo','6Mo','1Yr','2Yr','3Yr','5Yr','7Yr','10Yr','20Yr','30Yr'])
time_range = range(1990,2023,1)
base_url = "https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?type=daily_treasury_yield_curve&field_tdr_date_value="

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
yield_.to_pickle("yield_data.pkl")
yield_.to_csv("yield_data.csv")
```

|                     |    1Mo |    2Mo |    3Mo |    6Mo |    1Yr |    2Yr |    3Yr |    5Yr |    7Yr |   10Yr |   20Yr |   30Yr |
|:--------------------|-------:|-------:|-------:|-------:|-------:|-------:|-------:|-------:|-------:|-------:|-------:|-------:|
| 1990-01-02 00:00:00 | nan    | nan    |   7.83 |   7.89 |   7.81 |   7.87 |   7.9  |   7.87 |   7.98 |   7.94 | nan    |   8    |
| 1990-01-03 00:00:00 | nan    | nan    |   7.89 |   7.94 |   7.85 |   7.94 |   7.96 |   7.92 |   8.04 |   7.99 | nan    |   8.04 |
| 1990-01-04 00:00:00 | nan    | nan    |   7.84 |   7.9  |   7.82 |   7.92 |   7.93 |   7.91 |   8.02 |   7.98 | nan    |   8.04 |
| ----- |   ----- |   ----- |   ----- |   ----- |   ----- |   ----- |   ----- |   ----- |   ----- |   ----- |   ----- |   ----- |
| ----- |   ----- |   ----- |   ----- |   ----- |   ----- |   ----- |   ----- |   ----- |   ----- |   ----- |   ----- |   ----- |
| 2022-04-06 00:00:00 |   0.21 |   0.44 |   0.67 |   1.15 |   1.79 |   2.5  |   2.67 |   2.7  |   2.69 |   2.61 |   2.81 |   2.63 |
| 2022-04-07 00:00:00 |   0.21 |   0.5  |   0.68 |   1.15 |   1.78 |   2.47 |   2.66 |   2.7  |   2.73 |   2.66 |   2.87 |   2.69 |
| 2022-04-08 00:00:00 |   0.2  |   0.49 |   0.7  |   1.19 |   1.81 |   2.53 |   2.73 |   2.76 |   2.79 |   2.72 |   2.94 |   2.76 |


## Calculation - Proportion how many yield curves are inverted?
```python
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
```

### One specific date

```python
yield_ = pd.read_pickle("yield_data.pkl")
considered_date = "2022-04-08"
considered_yield_data = yield_.loc[considered_date]
print("Proportion how many yield curves are inverted: " + str(calculate_matrix()[0]) + "%")
calculate_matrix()[1]
```

|      |    1Mo |    2Mo |    3Mo |    6Mo |    1Yr |    2Yr |    3Yr |    5Yr |    7Yr |   10Yr |   20Yr |   30Yr |
|:-----|-------:|-------:|-------:|-------:|-------:|-------:|-------:|-------:|-------:|-------:|-------:|-------:|
| 1Mo  | nan    | nan    | nan    | nan    | nan    | nan    | nan    | nan    | nan    | nan    | nan    |    nan |
| 2Mo  |   0.29 | nan    | nan    | nan    | nan    | nan    | nan    | nan    | nan    | nan    | nan    |    nan |
| 3Mo  |   0.5  |   0.21 | nan    | nan    | nan    | nan    | nan    | nan    | nan    | nan    | nan    |    nan |
| 6Mo  |   0.99 |   0.7  |   0.49 | nan    | nan    | nan    | nan    | nan    | nan    | nan    | nan    |    nan |
| 1Yr  |   1.61 |   1.32 |   1.11 |   0.62 | nan    | nan    | nan    | nan    | nan    | nan    | nan    |    nan |
| 2Yr  |   2.33 |   2.04 |   1.83 |   1.34 |   0.72 | nan    | nan    | nan    | nan    | nan    | nan    |    nan |
| 3Yr  |   2.53 |   2.24 |   2.03 |   1.54 |   0.92 |   0.2  | nan    | nan    | nan    | nan    | nan    |    nan |
| 5Yr  |   2.56 |   2.27 |   2.06 |   1.57 |   0.95 |   0.23 |   0.03 | nan    | nan    | nan    | nan    |    nan |
| 7Yr  |   2.59 |   2.3  |   2.09 |   1.6  |   0.98 |   0.26 |   0.06 |   0.03 | nan    | nan    | nan    |    nan |
| 10Yr |   2.52 |   2.23 |   2.02 |   1.53 |   0.91 |   0.19 |  -0.01 |  -0.04 |  -0.07 | nan    | nan    |    nan |
| 20Yr |   2.74 |   2.45 |   2.24 |   1.75 |   1.13 |   0.41 |   0.21 |   0.18 |   0.15 |   0.22 | nan    |    nan |
| 30Yr |   2.56 |   2.27 |   2.06 |   1.57 |   0.95 |   0.23 |   0.03 |   0    |  -0.03 |   0.04 |  -0.18 |    nan |


### Time period

```python
%%time
yield_ = pd.read_pickle("yield_data.pkl")
inverted_percentage = [] 
for u in range(0,(yield_.shape[0])):
    considered_yield_data = yield_.iloc[u]
    inverted_percentage.append(calculate_matrix()[0])
yield_["inverted_percentage"] = inverted_percentage
yield_
```


|                     |    1Mo |    2Mo |    3Mo |    6Mo |    1Yr |    2Yr |    3Yr |    5Yr |    7Yr |   10Yr |   20Yr |   30Yr |   inverted_percentage |
|:--------------------|-------:|-------:|-------:|-------:|-------:|-------:|-------:|-------:|-------:|-------:|-------:|-------:|----------------------:|
| 1990-01-02  | nan    | nan    |   7.83 |   7.89 |   7.81 |   7.87 |   7.9  |   7.87 |   7.98 |   7.94 | nan    |   8    |                  16.7 |
| 1990-01-03  | nan    | nan    |   7.89 |   7.94 |   7.85 |   7.94 |   7.96 |   7.92 |   8.04 |   7.99 | nan    |   8.04 |                  16.7 |
| 1990-01-04  | nan    | nan    |   7.84 |   7.9  |   7.82 |   7.92 |   7.93 |   7.91 |   8.02 |   7.98 | nan    |   8.04 |                  13.9 |
| -- |   -- |   -- |   -- |   -- |   -- |   -- |   -- |   -- |   -- |   -- |   -- |   -- |
| -- |   -- |   -- |   -- |   -- |   -- |   -- |   -- |   -- |   -- |   -- |   -- |   -- |
| 2022-04-06  |   0.21 |   0.44 |   0.67 |   1.15 |   1.79 |   2.5  |   2.67 |   2.7  |   2.69 |   2.61 |   2.81 |   2.63 |                  12.1 |
| 2022-04-07  |   0.21 |   0.5  |   0.68 |   1.15 |   1.78 |   2.47 |   2.66 |   2.7  |   2.73 |   2.66 |   2.87 |   2.69 |                   7.6 |
| 2022-04-08  |   0.2  |   0.49 |   0.7  |   1.19 |   1.81 |   2.53 |   2.73 |   2.76 |   2.79 |   2.72 |   2.94 |   2.76 |                   7.6 |


## Recessions 
When did economic recessions take place
```python
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
```


```python
fig,ax = plt.subplots(figsize=(35,10))
ax.plot(yield_.index, yield_["inverted_percentage"], label='Amount of inverted yield curves', linewidth=1.5, color = "blue")
ax.axhline(y=50, linewidth = 1.5, linestyle='--', color = "blue")
ax.set_ylim(-5,100)

# add recessions as a rectangle inside the figure
for i,_ in enumerate(recessions):
    add_patch(recessions[i][0],recessions[i][1])
    
# Annotation - current value
ax.annotate('%0.2f' % yield_["inverted_percentage"].iloc[-1], xy=(1, yield_["inverted_percentage"].iloc[-1]), xytext=(-80, 0), 
                     xycoords=('axes fraction', 'data'), textcoords='offset points')


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
pdf_name = "Yield.pdf"
plt.savefig(pdf_name)
```
![Screenshot](Figure1.png)



## Banks Tightening Standards for Commercial and Industrial Loans

Net Percentage of Domestic Banks Tightening Standards for Commercial and Industrial LoansNet Percentage of Domestic Banks Tightening Standards for Commercial and Industrial Loans

Number of regional banks in the U.S. that stop lending (Thightening Standards).
If a bank fears bad times are coming, then it will lend less. If banks hold back to the maximum, then there will potentially a crash

```python
# https://fred.stlouisfed.org/series/DRTSCILM
Tightening_Standards_csv = r"****/DRTSCILM.csv"
Tightening_Standards_df = pd.read_csv(Tightening_Standards_csv, sep=',')

Tightening_Standards_df.index = pd.to_datetime(Tightening_Standards_df["DATE"])
Tightening_Standards_df.drop(['DATE'], axis=1,inplace = True)
fig,ax = plt.subplots(figsize=(35,10))
ax.plot(Tightening_Standards_df.index, Tightening_Standards_df["DRTSCILM"], label='Tightening_Standards', linewidth=1.5)
ax.axhline(y=0, color='k', linewidth = 1.2, linestyle='--')
for i,_ in enumerate(recessions):
    add_patch(recessions[i][0],recessions[i][1])
    
plt.ylabel('Percentage')
plt.xlabel("Date")
legend = ax.legend(loc='upper right')
```
![Screenshot](Figure2.png)

## Combination of Yields and Banks Tightening Standards for Commercial and Industrial Loans
```python
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
pdf_name = "Yield.pdf"
plt.savefig(pdf_name)
```

![Screenshot](Figure3.png)