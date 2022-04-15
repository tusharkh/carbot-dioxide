# import necessary packages
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import patches
from matplotlib import font_manager

# set constants
NOAA_URL = "ftp://aftp.cmdl.noaa.gov/products/trends/co2/co2_trend_gl.csv"
SKIP_ROWS = 60
NUMBER_OF_YEARS = 10

# get data from NOAA website
data = pd.read_csv(NOAA_URL, skiprows=SKIP_ROWS)

# clean data: create datetime index and drop extra columns
data.set_index(pd.to_datetime(data.iloc[:, 0:3]), inplace=True)
data.drop(['year', 'month', 'day'], axis=1, inplace=True)

# compute monthly ppm averages
data['monthly_mean'] = data.groupby(pd.Grouper(freq='M'))['smoothed'].mean()

# select the desired number of years
end_date = pd.Timestamp.today().date() # today
start_date = end_date.replace(year=end_date.year - NUMBER_OF_YEARS)
data = data.loc[start_date:end_date,:].copy()

# find yesterday's and a year ago's data
yesterday = data.iloc[-1,:]
year_ago = data.iloc[-366,:]

# select the fonts manually (probably a better way to do this) replace filenames with system font locations
num_font = font_manager.FontProperties(fname='/Users/tushar/Downloads/Roboto_Mono/static/RobotoMono-Regular.ttf')
text_font = font_manager.FontProperties(fname='/Users/tushar/Downloads/Overpass/static/Overpass-Regular.ttf')
bold_text_font = font_manager.FontProperties(fname='/Users/tushar/Downloads/Overpass/static/Overpass-Medium.ttf')
italic_text_font = font_manager.FontProperties(fname='/Users/tushar/Downloads/Overpass/static/Overpass-Italic.ttf')

# figure settings
MONTH_COLOR = "#cccccc"
TREND_COLOR = "#ff9999"
TEXT_COLOR = "#666666"
TICK_COLOR = "#666666"
HIGHLIGHT_COLOR = "#ffcc99"
GRID_COLOR = "#F7F7F7"

TREND_SIZE = 5
MONTH_ALPHA = 0.66
MONTH_SIZE = 15
HIGHLIGHT_SIZE = 15
HIGHLIGHT_WIDTH = 3
MONTH_MARKER = "o" # circle
MONTH_MARKER_WIDTH = 2
GRID_LINEWIDTH = 2
TITLE_SIZE = 35
SUBTITLE_SIZE = 30
CAPTION_SIZE = 15
LABEL_SIZE = 20

TITLE = "Carbon dioxide: current global average"
SUBTITLE = "Atmospheric CO$_{2}$, parts per million"
CAPTION = ("Source: NOAA/ESRL | Graphic + Bot: Clayton Aldern (@compatibilism) | Generated: " +
           pd.Timestamp.today().strftime('%B %d, %Y'))

# make the figure
fig, ax = plt.subplots(figsize=(14, 10))

# mean values
ax.plot(data.index, data['monthly_mean'], markersize=MONTH_SIZE, marker=MONTH_MARKER,
        markeredgecolor=MONTH_COLOR, markerfacecolor='none', markeredgewidth=MONTH_MARKER_WIDTH)

# trend
ax.plot(data.index, data['trend'], c=TREND_COLOR, linewidth=TREND_SIZE)

# daily values
ax.plot(yesterday.name, yesterday['smoothed'], c=HIGHLIGHT_COLOR, markersize=HIGHLIGHT_SIZE,
        marker=MONTH_MARKER)
ax.plot(year_ago.name, year_ago['smoothed'], c=HIGHLIGHT_COLOR, markersize=HIGHLIGHT_SIZE,
        marker=MONTH_MARKER)

# curves
xlims = ax.get_xlim()
ylims = ax.get_ylim()

arrow = patches.ArrowStyle.CurveB(head_length=30, head_width=12)
curve1 = patches.FancyArrowPatch(posA=(yesterday.name - pd.Timedelta(365*0.7, 'days'), yesterday['smoothed'] - 14.5),
                                 posB=(yesterday.name, yesterday['smoothed'] - 1),
                                 connectionstyle=patches.ConnectionStyle.Arc3(rad=0.2),
                                 color=HIGHLIGHT_COLOR, linewidth=HIGHLIGHT_WIDTH,
                                 arrowstyle=arrow)
curve2 = patches.FancyArrowPatch(posA=(year_ago.name - pd.Timedelta(365*2, 'days'), year_ago['smoothed'] + 1.25),
                                 posB=(year_ago.name - pd.Timedelta(60, 'days'), year_ago['smoothed'] + 0.4),
                                 connectionstyle=patches.ConnectionStyle.Arc3(rad=-0.2),
                                 color=HIGHLIGHT_COLOR, linewidth=HIGHLIGHT_WIDTH,
                                 arrowstyle=arrow)

#ax.autoscale(False)
ax.add_patch(curve1)
ax.add_patch(curve2)

# text
ax.text(yesterday.name - pd.Timedelta(365*1.8, 'days'), yesterday['smoothed'] - 17.5,
        s="Yesterday:\n" + str(round(yesterday['smoothed'], 2)) + " ppm", fontsize=LABEL_SIZE,
        fontstyle='italic', fontproperties=italic_text_font, color=TEXT_COLOR)
ax.text(year_ago.name - pd.Timedelta(365*4.2, 'days'), year_ago['smoothed'],
        s="One year ago:\n" + str(round(year_ago['smoothed'], 2)) + " ppm", fontsize=LABEL_SIZE,
        fontstyle='italic', fontproperties=italic_text_font, color=TEXT_COLOR)

# tick labels
for label in ax.get_yticklabels() :
    label.set_fontproperties(num_font)
ax.tick_params(axis='y', labelsize=LABEL_SIZE, labelcolor=TICK_COLOR)
for label in ax.get_xticklabels() :
    label.set_fontproperties(num_font)
ax.tick_params(axis='x', labelsize=LABEL_SIZE, labelcolor=TICK_COLOR)
ax.tick_params(left=False)

# titles and captions
ax.text(s=TITLE, fontsize=TITLE_SIZE, y=1.15, x=-0.06, transform=ax.transAxes,
        fontproperties=bold_text_font)
ax.text(s=SUBTITLE, fontsize=SUBTITLE_SIZE, y=1.07, x=-0.06, transform=ax.transAxes,
        fontproperties=text_font)
ax.text(s=CAPTION, fontsize=CAPTION_SIZE, y=-0.12, x=-0.06, transform=ax.transAxes,
        fontproperties=italic_text_font, color=TEXT_COLOR)

# add a grid
ax.grid(visible=True, which='major', axis='y', linewidth=GRID_LINEWIDTH, color=GRID_COLOR)
ax.set_axisbelow(True)

# clear spines
ax.spines['right'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.spines['top'].set_visible(False)

# create filename and save
filename = pd.Timestamp.today().strftime('%Y-%m-%d')
fig.savefig('figures/' + filename + '.jpg', bbox_inches='tight', pad_inches=0.4)