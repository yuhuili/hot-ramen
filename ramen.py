import csv
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

from collections import Counter
from matplotlib.collections import PatchCollection
from matplotlib.patches import Polygon
from matplotlib.colors import LinearSegmentedColormap
from mpl_toolkits.basemap import Basemap

print_stats = True

csvfile = 'data/data.csv'
shapefile = 'data/ne_10m_admin_0_countries_lakes/ne_10m_admin_0_countries_lakes'

style_col_index = 3
country_col_index = 4
rating_col_index = 5

max_rating = 5.
rating_shift = -2;

ramen_styles = [[["Pack"], "Pack"], [["Bowl", "Cup"], "Bowl and Cup"]]

active_color = '#06c100'
inactive_color = '#aaaaaa'

colors = ['#ffffff', active_color]

def obtain_data():
  data = []
  with open(csvfile, 'rU') as datafile:
    reader = csv.reader(datafile)
    for row in reader:
      try:
        rating = float(row[rating_col_index])
        row[rating_col_index] = rating
        row[country_col_index] = 'United States of America' if row[country_col_index] == 'United States' else row[country_col_index]
        data.append(row)
      except:
        pass

  if print_stats:
    print("===== obtain_data =====")
    print("number_of_ratings:"+ str(len(data)))
  return data

def build_ratings_by_country_map(data):
  total_ratings = {}
  ratings_count = {}

  for row in data:
    country = row[country_col_index]
    rating = row[rating_col_index]
    total_ratings[country] = total_ratings.get(country, 0.) + rating
    ratings_count[country] = ratings_count.get(country, 0.) + 1.

  result = { k: total_ratings[k] / ratings_count[k] for k in set(total_ratings) & set(ratings_count)}
  ratings = result.values()

  if print_stats:
    print("===== build_ratings_by_country_map =====")
    print("max_avg_rating:"+ str(max(ratings)))
    print("min_avg_rating:"+ str(min(ratings)))
    print("avg_avg_rating_per_country:"+ str(sum(ratings) / len(ratings)))

    freq = Counter(result)
    print("Countries (highest rating)")
    for k, v in freq.most_common(5):
      print '%s with avg_rating %.2f, number of samples %i' % (k, v, ratings_count[k])

    print("Countries (lowest rating)")
    for k, v in freq.most_common()[::-1][:5]:
      print '%s with avg_rating %.2f, number of samples %i' % (k, v, ratings_count[k])

  return result

def build_ratings_by_style_by_country_map(data):
  result = {}
  for styles in ramen_styles:
    ratings_by_country_map = build_ratings_by_country_map([x for x in data if x[style_col_index] in styles[0]])
    result[styles[1]] = ratings_by_country_map
  return result

def draw_map(ratings_data, title, save_name):
  fig = plt.figure(figsize=(16,9))
  fig.suptitle(title, fontsize=20, y=.90)
  ax = fig.add_subplot(111, facecolor='w', frame_on=False)
  m = Basemap(lon_0=0, projection='robin')
  m.drawmapboundary(color='w')
  m.readshapefile(shapefile, 'units', color='#888888', linewidth=.2)

  for info, shape in zip(m.units_info, m.units):
    country = info["NAME"]
    if country not in ratings_data:
      color = inactive_color
    else:
      color = active_color
      try:
        non_visited_country.remove(country)
      except:
        pass

    pc = PatchCollection([Polygon(np.array(shape), True)])
    pc.set_facecolor(color)
    if country in ratings_data:
      pc.set_alpha((ratings_data[country]+rating_shift) / (max_rating+rating_shift))
    ax.add_collection(pc)

  ax.axhspan(0, 1000 * 1800, facecolor='w', edgecolor='w', zorder=2)

  ax_legend = fig.add_axes([0.35, 0.14, 0.3, 0.03], zorder=3)
  index  = [0.0, 1.0]
  cm = LinearSegmentedColormap.from_list('ramen_colormap', zip(index, colors))
  cb = mpl.colorbar.ColorbarBase(ax_legend, cmap=cm, ticks=[0, 1], orientation='horizontal')
  cb.ax.set_xticklabels(["3/5 Stars", "5/5 Stars"])

  plt.savefig("output/%s.png" % save_name, bbox_inches='tight', pad_inches=.2)

def main():
  data = obtain_data()
  
  draw_map(build_ratings_by_country_map(data), "Average Ramen Ratings", "avg")

  style_data = build_ratings_by_style_by_country_map(data)
  for k, v in style_data.iteritems():
    draw_map(v, "Average %s Ramen Ratings" % k, "%s_avg" % k)

if __name__ == "__main__":
  main()
