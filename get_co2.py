# import necessary packages
import pandas as pd

# plotting packages
import matplotlib.pyplot as plt
from matplotlib import patches
from matplotlib import font_manager
from matplotlib import rcParams

# set constants
NOAA_URL = "ftp://aftp.cmdl.noaa.gov/products/trends/co2/co2_trend_gl.csv"
# number of rows to skip in noaa csv
SKIPROWS = 60
# number of years to plot
NUMBER_OF_YEARS = 10


def get_noaa_data(url, skiprows, number_of_years):
  '''download, clean noaa data and compute statistics'''

  # get data from NOAA website
  data = pd.read_csv(url, skiprows=skiprows)

  # clean data
  # create datetime index and drop extra columns
  data.set_index(pd.to_datetime(data.iloc[:, 0:3]), inplace=True)
  data.drop(['year', 'month', 'day'], axis=1, inplace=True)

  # compute monthly ppm averages
  data['monthly_mean'] = data.groupby(pd.Grouper(freq='M'))['smoothed'].mean()

  # select the desired number of years
  end_date = pd.Timestamp.today().date() # today
  start_date = end_date.replace(year=end_date.year - number_of_years)
  data = data.loc[start_date:end_date,:].copy()

  yesterday = data.iloc[-1,:]
  year_ago = data.iloc[-366,:]
  
  return data, start_date, end_date, yesterday, year_ago


def plot(data, start_date, end_date, yesterday, year_ago):
  # figure settings
  title_size = 35
  subtitle_size = 30
  caption_size = 15
  label_size = 20
  trend_size = 5
  highlight_size = 15
  month_size = 15
  highlight_width = 3
  month_marker_width = 2

  month_color = "#cccccc"
  trend_color = "#ff9999"
  highlight_color = "#ffcc99"
  text_color = "#666666"

  rcParams['xtick.labelsize'] = 30
  rcParams['ytick.labelsize'] = 30
  rcParams['xtick.labelcolor'] = "#666666"
  rcParams['ytick.labelcolor'] = "#666666"
  rcParams['grid.linewidth'] = 2
  rcParams['grid.color'] = "#F7F7F7"
  rcParams['axes.labelsize'] = 20
  rcParams['figure.figsize'] = (14, 10)
  rcParams['figure.dpi'] = 300

  month_marker = "o" # circle
  
  # Add every font at the specified location
  font_dir = ['/Users/tushar/Library/Fonts']
  for font in font_manager.findSystemFonts(font_dir):
    # use font_manager.FontProperties(fname=font).get_name() to get the name
    font_manager.fontManager.addfont(font)

  # make the figure
  fig, ax = plt.subplots()

  # mean values
  ax.plot(data.index, data['monthly_mean'], markersize=month_size, marker=month_marker,
          markeredgecolor=month_color, markerfacecolor='none', markeredgewidth=month_marker_width)

  # trend
  ax.plot(data.index, data['trend'], c=trend_color, linewidth=trend_size)

  # daily values
  ax.plot(yesterday.name, yesterday['smoothed'], c=highlight_color,
          markersize=highlight_size, marker=month_marker)
  ax.plot(year_ago.name, year_ago['smoothed'], c=highlight_color,
          markersize=highlight_size, marker=month_marker)

  # curves
  xlims = ax.get_xlim()
  ylims = ax.get_ylim()

  arrow = patches.ArrowStyle.CurveB(head_length=30, head_width=12)
  curve1 = patches.FancyArrowPatch(posA=(yesterday.name - pd.Timedelta(365*0.7, 'days'), yesterday['smoothed'] - 14.5),
                                   posB=(yesterday.name, yesterday['smoothed'] - 1),
                                   connectionstyle=patches.ConnectionStyle.Arc3(rad=0.2),
                                   color=highlight_color, linewidth=highlight_width,
                                   arrowstyle=arrow)
  curve2 = patches.FancyArrowPatch(posA=(year_ago.name - pd.Timedelta(365*2, 'days'), year_ago['smoothed'] + 1.25),
                                   posB=(year_ago.name - pd.Timedelta(60, 'days'), year_ago['smoothed'] + 0.4),
                                   connectionstyle=patches.ConnectionStyle.Arc3(rad=-0.2),
                                   color=highlight_color, linewidth=highlight_width,
                                   arrowstyle=arrow)

  #ax.autoscale(False)
  ax.add_patch(curve1)
  ax.add_patch(curve2)
  
  # tick labels
  tick_font = font_manager.FontProperties(family='Roboto Mono')
  for label in ax.get_yticklabels() :
      label.set_fontproperties(tick_font)
  ax.tick_params(axis='y', labelsize=label_size)
  for label in ax.get_xticklabels() :
      label.set_fontproperties(tick_font)
  ax.tick_params(axis='x', labelsize=label_size)
  ax.tick_params(left=False)

  # text
  ax.text(yesterday.name - pd.Timedelta(365*1.8, 'days'), yesterday['smoothed'] - 17.5,
          s="Yesterday:\n" + str(round(yesterday['smoothed'], 2)) + " ppm", fontsize=label_size,
          fontstyle='italic', fontfamily='Overpass', color=text_color)
  ax.text(year_ago.name - pd.Timedelta(365*4.2, 'days'), year_ago['smoothed'],
          s="One year ago:\n" + str(round(year_ago['smoothed'], 2)) + " ppm", fontsize=label_size,
          fontstyle='italic', fontfamily='Overpass', color=text_color)

  # clear spines
  ax.spines['right'].set_visible(False)
  ax.spines['left'].set_visible(False)
  ax.spines['top'].set_visible(False)

  # add agrid
  ax.grid(visible=True, which='major', axis='y')
  ax.set_axisbelow(True)

  # titles and captions
  ax.text(s="Carbon dioxide: current global average", fontsize=title_size, y=1.15,
          x=-0.06, transform=ax.transAxes, fontfamily='Overpass', fontweight=600)
  ax.text(s="Atmospheric CO$_{2}$, parts per million", fontsize=subtitle_size, y=1.07,
          x=-0.06, transform=ax.transAxes, fontfamily='Overpass', fontweight=400)
  ax.text(s=("Source: NOAA/ESRL | Graphic: Tushar Khurana (credit: Clayton Aldern) | Generated: " +
             pd.Timestamp.today().strftime('%B %d, %Y')), fontsize=caption_size, y=-0.12,
          x=-0.06, transform=ax.transAxes, fontstyle='italic', fontfamily='Overpass', color=text_color)

  # create filename and save
  filename = pd.Timestamp.today().strftime('%Y-%m-%d')
  fig.savefig('figures/' + filename + '.jpg', bbox_inches='tight', pad_inches=0.4)  


if __name__ == "__main__":
  data, start_date, end_date, yesterday, year_ago = get_noaa_data(NOAA_URL, SKIPROWS, NUMBER_OF_YEARS)
  plot(data, start_date, end_date, yesterday, year_ago)