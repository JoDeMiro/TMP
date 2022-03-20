import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.cm as cm

from sklearn.linear_model import LinearRegression
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import MinMaxScaler

import os
import pickle

from debils import Printer
from environments import Road
from plotters import PostPlotter, Plotter
from storages import Storage

from IPython.display import clear_output

class TestCar():
  def __init__(self, road, plotter, storage):
    self.plot_frequency = 9
    self.plot_detailed_frequency = 32
    self.plot_history_flag = 0                          # 0 - disable, 1 - plot, 2 - save, 3 - both
    self.plot_trace_flag = 0                            # 0 - disable, 1 - plot, 2 - save, 3 - both
    self.plotter_mlp_flag = 0                           # 0 - disable, 1 - plot, 2 - save, 3 - both

    self.road = road
    self.plotter = plotter
    self.storage = storage

    self.sensor_center_enable = True

    self.x = 0
    self.y = self.road.wall_center[0]
    self.sight = 400           # ennyit lát előre 300, 54, 154
    self.sight_center = 400    # ennyit lát előre 150

    self.y_history  = []
    self.x_history  = []
    self.y_center   = self.road.wall_center
    self.y_distance = []
    self.y_distance_real = []
    self.y_distance_predicted = []
    self.y_distance_predicted_inv = []

    self.regression = LinearRegression(fit_intercept=False)

    # Load MLP from file
    self.storage.load_mlp()
    self.mlp = self.storage.mlp

    # Load Regression from file
    self.storage.load_regression
    self.regression_left = self.storage.regression_left
    self.regression_center = self.storage.regression_center
    self.regression_right = self.storage.regression_right

    # Load MinMaxScaler from file
    self.storage.load_minmaxscaler()
    self.x_minmaxscaler = self.storage.x_minmaxscaler
    self.y_minmaxscaler = self.storage.y_minmaxscaler

    # data holders
    self.sensor_center = []
    self.sensor_left   = []
    self.sensor_right  = []
    self.before  = []
    self.after   = []

    self.mesterseges_coutner = 0

    # logger helyett
    global printer
    printer = Printer()
    printer._ac = False


  def calculate_distances(self):
    # ha bármikor kevesebb a faltól mért távolsága bármelyik szenzoron akkor a szenzorokon mért távolság is ennyi lesz

    k = self.x; d = 0
    while(k < self.x + self.sight_center):
      k += 1; d += 1
      self.distance_center_from_wall = d
      # v.24 - new
      if( self.sensor_center_enable == True ):
        if(int(self.road.wall_left[k]) < self.y):
          printer.sr('Sensor center = ', self.distance_center_from_wall)
          break
        if(int(self.road.wall_right[k]) > self.y):
          printer.sr('Sensor center = ', self.distance_center_from_wall)
          break

    k = self.x; d = 0
    while(k < self.x + self.sight):
      k += 1;  d += 1
      self.distance_left_from_wall = d
      if(int(self.road.wall_left[k]) < self.y + d):
        printer.sr('Sensor from left wall = ', self.distance_left_from_wall)
        break

    k = self.x; d = 0
    while(k < self.x + self.sight):
      k += 1; d += 1
      self.distance_right_from_wall = d
      if(int(self.road.wall_right[k]) > self.y - d):
        printer.sr('Sensor from right wall = ', self.distance_right_from_wall)
        break

    self.distance_from_top     = abs(self.road.wall_left[self.x] - self.y)
    self.distance_from_bottom  = abs(self.road.wall_right[self.x] - self.y)
    printer.sr('most távolsagra van a felső faltól = ', self.distance_from_top)
    printer.sr('most távolsagra van az alsó faltól = ', self.distance_from_bottom)



    # ezt az értéket fogom becsülni, a középértéktől való eltérés mértéke, ha pozitív akkor fölfelé, ha negatív akkor lefelé tér el
    self.vertical_distance_from_middle = self.y - self.road.wall_center[self.x]




  def append(self):
    self.y_distance.append(self.vertical_distance_from_middle)

    self.sensor_left.append(self.distance_left_from_wall)
    self.sensor_center.append(self.distance_center_from_wall)
    self.sensor_right.append(self.distance_right_from_wall)



  def plot_history(self, flag):
    if( flag != 0 ):
      fig, ax = self.road.show()
      circle = plt.Circle((self.x, self.y), 5, color='black')
      ax.add_patch(circle)
      # v.24 - add standardized color -> left = green, rigth = orange
      ax.plot(range(int(self.x), int(self.x+self.distance_center_from_wall)), np.repeat(self.y, self.distance_center_from_wall))
      ax.plot(range(int(self.x), int(self.x+self.distance_left_from_wall)), range(int(self.y), int(self.y+self.distance_left_from_wall)), c='green')
      ax.plot(range(int(self.x), int(self.x+self.distance_right_from_wall)), range(int(self.y), int(self.y-self.distance_right_from_wall), -1), c='orange')
      if( len(self.y_history) > 0 ):
        ax.plot(self.y_history)
        ax.set_title('#i = ' + str(self.x), fontsize=18, fontweight='bold')
      if( flag == 1 or flag == 3 ): plt.show();
      if( flag == 2 or flag == 3 ): fig.savefig('test_history{0:04}'.format(self.x)+'.png'); plt.close('all'); fig.clf(); ax.cla(); plt.close('all');


  def save_plots(self):
    plt.figure(figsize=(12, 5)); plt.scatter(self.y_distance_real, self.y_distance_predicted)
    plt.ylabel('y_distance_predicted'); plt.xlabel('y_distance_real');
    plt.title('#i = ' + str(self.x), fontsize=18, fontweight='bold');
    plt.savefig('test_y_distance_vs_y_distance_predicted_{0:04}'.format(self.x)+'.png')
    plt.close()


  def cond1(self, x):
    if (x % 3 == 1):
      return True
    else:
      return False

  def cond2(self, x):
    if (x > -1):
      return True
    else:
      return False

  def cond3(self, x):
    if(x < 500):
      return True
    else:
      return False

  def cond4(self, x):
    # a cond4 egyébként sehol nem hasznája fel x-ként megadott paramétert de a signatura miatt kell neki, hogy illeszkedjen a többivel
    if( self.sensor_right[-1] < 10 or self.sensor_left[-1] < 10 or self.sensor_center[-1] < 10 ):
      return True
    else:
      return False


  def run(self, run_length, cond = 1):
    # Mi alapján legyen végrehajtva a tényleges action
    if cond == 1:
      condition_for_action = self.cond1
    if cond == 2:
      condition_for_action = self.cond2
    if cond == 3:
      condition_for_action = self.cond3
    if cond == 4:
      condition_for_action = self.cond4


    for i in range(0, run_length, 1):
      printer.util('# A run ciklus eleje --------------------------------------------------------------------------------------------------------------------')
      printer.util('# i = ', i)
      _summary_mlp_prediction_was_taken = 0
      _summary_mlp_fit_was_taken = 0
      _summary_mesterseges_mozgatas = 0
      _summary_action_was_taken = 0

      self.x = i
      self.calculate_distances()
      self.append()



# Itt kezdődik a lényeg
      if ( i >= 0 ):

        # A helyzet az, hogy a TestCar nem tanul, ezért erre a részre nem lesz szükségünk
        # --------------------------------------- A NEURÁLIS HÁLÓ TANÍTÁSA (1) ---------------------------------------
        

        # Élhetünk ezzel a lehetőséggel, bár lehet, hogy a végén kiveszünk mindent és csak a döntés marad majd bent
        # --------------------------------------- A NEURÁLIS HÁLÓ MINŐSÉGÉNEK VISSZAMÉRÉSE, TESZTELÉSE (2) ---------------------------------------


        # Igazából ezt a mesterséges mozgatást is kiveszem
        # Tulajdonképpen első körben ezt most benne hagyhatom, de alapvetően majd ki kéne venni
        # ----------------------------------------- MESTERSÉGES MOZGATÁS (3) -----------------------------------------



        # Itt jön a lényeg
        # ------------------------------------------------ ACTION (X) ------------------------------------------------

        action = 0


        # if( i % 3 == 0 ):
        if( i > -1 ):

          if( len(self.before) > 9 ):

            printer.info('------------------------------ IF len(self.before) > 9 ------------------------------')
            printer.info('\n')


            # most ki kell számolni, hogy mennyi lenne a szenzorok értéke, ha fel le lépkednénk

            move = np.array([-7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7])


            printer.action('\t # Az egyes lépések várható kimeneteinek kiszámolása ----------------------------------------------')

            printer.action('\t\t # Ennyivel mozdulna el egy szenzor adat 1 egység változással ha 1 lenne a before értéke')

            
            action = 0; tmp = 999999990

            for j in move:

              _X_left   = np.array([[self.distance_left_from_wall, j]])
              _X_center = np.array([[self.distance_center_from_wall, j]])
              _X_right  = np.array([[self.distance_right_from_wall, j]])

              predicted_left   = self.regression_left.predict(_X_left)
              predicted_center = self.regression_center.predict(_X_center)
              predicted_right  = self.regression_right.predict(_X_right)

              # nekünk majd azt az értéket kell választanunk amelyik segítségével a legközelebb jutunk a 0 értékhez

              _X = np.array([predicted_left.ravel(), predicted_center.ravel(), predicted_right.ravel()]).T    # figyelni kell rá, hogy eredetileg is ez volt-e a változók sorrendje

              _X_scaled = self.x_minmaxscaler.transform(_X)

# Neurális háló becslése
              predicted_position_scaled = self.mlp.predict(_X_scaled)
# Vissza kell transzformálnom eredeti formájába
              predicted_position = self.y_minmaxscaler.inverse_transform(predicted_position_scaled.reshape(-1, 1))

              # legyünk bátrak és módosítsuk az autó self.y pozicióját

              # azzal az értékkel amely abszolút értékben a legkissebb, helyett
              # mivel a célváltozónk akkor jó ha 0, mivel a középvonaltól mért eltérés
              # ezért itt azt az értéket kell kiválasztani ami a legközelebb van 0-hoz

              # természetesen ezen változtatni kell ha nem a középvonaltól való eltérés mértékét akarjuk becsülni
              # de ahhoz fent is át kell állítani hogy mi legyen a self.y_distance számítása

              if( abs(0 - predicted_position) < tmp):       # rossz - javítva - tesztelés alatt
                action = j
                tmp = abs(0 - predicted_position)
                printer.action('\t\t ---------------------')
                printer.action('\t\t  action = ', action)
                printer.action('\t\t  predicted_position = ', predicted_position)
                printer.action('\t\t  absolute distance from 0 (tmp) = ', tmp)
                printer.action('\t\t ---------------------')

              printer.action('\t\t adott j-re {0} kiszámoltuk az előrejelzést de még nem hoztunk döntést -----------------------------------------------------------------'.format(j))
              printer.action('\t\t --------------------------------------------------------------------------------------------------------------------------------------')
            
            printer.action('\t minden j-re kiszámoltuk az előrejelzést de még nem hoztunk döntést -------------------------------------------------\n')


# a döntés azonban csak akkor fut le ha az alábbi feltétel teljesül, de igazából korábban már be van ágyazva ugyan ebbe a feltételbe

# version 20. if( i % 3 == 0 ) -> version 22. if( i % 3 == 1 )
# eddig csak akkor engedtem neki lépést, ha ( i % 3 == 0 ):
# most viszont mindíg

## Na most egy olyat is bele tudok írni, hogy csak akkor lépjen ha (mondjuk túl közel van a falhoz)

#          if( i % 3 == 0 ):
#          if( i > -1 ):
#          if( self.sensor_right[-1] < 10 or self.sensor_left[-1] < 10 or self.sensor_center[-1] < 10 ):
          take_action = condition_for_action(self.x)
          if( take_action == True ):
            print('take_action == True')

          if( take_action == True ):

            print('------------------------------ IF i % 3 == 0 ------------------------------')
            _summary_action_was_taken = 1
            print('=================== TAKE ACTION ===================')
            self.before.append(np.array([self.y, self.distance_left_from_wall, self.distance_center_from_wall, self.distance_right_from_wall]))
            print('-------- ennyivel módosítom self.y értékét --------')
            print('self.y régi értéke = ', self.y)
            self.y = self.y + action
            self.calculate_distances()
            self.after.append(np.array([self.y, self.distance_left_from_wall, self.distance_center_from_wall, self.distance_right_from_wall]))
            print('self.y új értéke   = ', self.y)
            print('action             = ', action)
            print('----------------- módosítás vége -----------------')



      # adjuk hozzá az értéket a self.y_history-hoz
      print('# A run ciklus vége ------------------------------------------------------------------------------------------------------------------------------------------')
      print('#   itt adom hozzás a self.y a self.y_history-hoz')
      self.y_history.append(self.y)
      print('#    self.y :')
      print(self.y)
      print('# \t\t\t --------------- Summary ---------------')
      print('# \t\t\t _summary_mlp_fit_was_taken         = ', _summary_mlp_fit_was_taken)
      print('# \t\t\t _summary_mlp_prediction_was_taken  = ', _summary_mlp_prediction_was_taken)
      print('# \t\t\t _summary_mesterseges_mozgatas      = ', _summary_mesterseges_mozgatas)
      print('# \t\t\t _summary_action_were_taken         = ', _summary_action_was_taken)
      print('# ')
      print('# A run ciklus vége ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')

    if ( i % 10 == 0 ):
      clear_output(wait=True)
      