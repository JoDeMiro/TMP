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


    printer.info('cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc')
    printer.info('self.x                       = ', self.x)
    printer.info('cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc')

    # ezt az értéket fogom becsülni, a középértéktől való eltérés mértéke, ha pozitív akkor fölfelé, ha negatív akkor lefelé tér el
    self.vertical_distance_from_middle = self.y - self.road.wall_center[self.x]

    printer.info('KKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKK')
    printer.info('self.vertical_distance_from_middle = ', self.vertical_distance_from_middle)
    printer.info('KKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKK')
    printer.info('ezt fogjuk becsülni, ez a középértéktől való eltérés mértéke = ', self.vertical_distance_from_middle)

    printer.debug('\t\t\t ---------------- Teszt ----------------')
    printer.debug('\t\t\t len(self.y_distance)    = ', len(self.y_distance))
    printer.debug('\t\t\t len(self.sensor_left)   = ', len(self.sensor_left))
    printer.debug('\t\t\t len(self.sensor_center) = ', len(self.sensor_center))
    printer.debug('\t\t\t len(self.sensor_right)  = ', len(self.sensor_right))
    printer.debug('\t\t\t self.x                  = ', self.x)
    printer.debug('\t\t\t -------------- Teszt End --------------')

  def append(self):
    self.y_distance.append(self.vertical_distance_from_middle)

    self.sensor_left.append(self.distance_left_from_wall)
    self.sensor_center.append(self.distance_center_from_wall)
    self.sensor_right.append(self.distance_right_from_wall)

    printer.debug('\t\t\t ---------------- Append ----------------')
    printer.debug('\t\t\t len(self.y_distance)    = ', len(self.y_distance))
    printer.debug('\t\t\t len(self.sensor_left)   = ', len(self.sensor_left))
    printer.debug('\t\t\t len(self.sensor_center) = ', len(self.sensor_center))
    printer.debug('\t\t\t len(self.sensor_right)  = ', len(self.sensor_right))
    printer.debug('\t\t\t self.x                  = ', self.x)
    printer.debug('\t\t\t -------------- Append End --------------')

  def plot_history(self, flag):
    if( flag != 0 ):
      fig, ax = self.road.show()
      circle = plt.Circle((self.x, self.y), 5, color='black')
      ax.add_patch(circle)
      # v.24 - add standardized color -> left = green, rigth = orange
      ax.plot(range(int(self.x), int(self.x+self.distance_center_from_wall)), np.repeat(self.y, self.distance_center_from_wall))
      # ax.plot(range(int(self.x), int(self.x+self.distance_left_from_wall)), range(int(self.y), int(self.y+self.distance_left_from_wall)))
      # ax.plot(range(int(self.x), int(self.x+self.distance_right_from_wall)), range(int(self.y), int(self.y-self.distance_right_from_wall), -1))
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


  def run(self, run_length):
    for i in range(0, run_length, 1):
      printer.util('# A run ciklus eleje --------------------------------------------------------------------------------------------------------------------')
      printer.util('# i = ', i)
      _summary_mlp_prediction_was_taken = 0
      _summary_mlp_fit_was_taken = 0
      _summary_mesterseges_mozgatas = 0
      _summary_action_was_taken = 0

# Beállítja az x értékét az éppen aktuális ciklusváltozó értékére
      self.x = i
# Kiszámoja a szenzoroknak a faltól mért távolságát
      self.calculate_distances()
# Eltárolja a kiszámolt értékeket
      self.append()

# Csak néha plottoljunk ne mindíg, egyébként a függvény is megkapja hogy mikor plottoljon
      if ( i % self.plot_frequency == 0 ):
        
        # Show history plot - Save history plot
        self.plot_history(self.plot_history_flag)
        
        # New
#        self.plot_trace(self.plot_frequency, self.plot_trace_flag)
#        print(' --------------- plot trace --------------- ')



# Itt kezdődik a lényeg
      if ( i >= 0 ):

        # A helyzet az, hogy a TestCar nem tanul, ezért erre a részre nem lesz szükségünk
        # --------------------------------------- A NEURÁLIS HÁLÓ TANÍTÁSA (1) ---------------------------------------
        
        if ( i % 3 == 0 and i >= 12 ):
          
          self.plotter.plot_mlp(mlp = self.mlp ,flag = self.plotter_mlp_flag)


        # Élhetünk ezzel a lehetőséggel, bár lehet, hogy a végén kiveszünk mindent és csak a döntés marad majd bent
        # --------------------------------------- A NEURÁLIS HÁLÓ MINŐSÉGÉNEK VISSZAMÉRÉSE, TESZTELÉSE (2) ---------------------------------------

        if( i % 3 == 1 and i >= 22 ):

          print('# i = ', i)
          print('Ezt is kivettük nem ellenörizzük a neurális háló becslését')


        # Igazából ezt a mesterséges mozgatást is kiveszem
        # Tulajdonképpen első körben ezt most benne hagyhatom, de alapvetően majd ki kéne venni
        # ----------------------------------------- MESTERSÉGES MOZGATÁS (3) -----------------------------------------

        if( i % 3 == 2 ):

          print('# i = ', i)
          print('Ezt is kevettük nincs mesterséges mozgatás')




        # Itt jön a lényeg
        # ------------------------------------------------ ACTION (X) ------------------------------------------------



        # atcion változó fogja tárolni, hogy mi lenne az optimizer szerint a helyes döntés -> fontos, hogy ezt a döntést meg is lépi
        action = 0


        # if( i % 3 == 0 ):
        if( i > -1 ):

          # Elvileg most arra kéne rájönnöm, hogy kell-e neki before after adat ahhoz, hogy ki tudja számolni
          # szenzrokra készített modell alapján, hogy mi lenne az új érték
          # szerintem nem kell hozzá de ez az amit most ki kell derítenem

          # Igen az már látszik, hogy korábban itt történt a befre after tanítás is
          # De mivel most nincs tanítás erre nem lesz szükség





          if( len(self.before) > 9 ):

            printer.info('------------------------------ IF len(self.before) > 9 ------------------------------')
            printer.info('\n')
            printer.info('  Ha már van elég before after adatunk')
            printer.info('# 3. Tanulás itt kerül kiszámításra a lineáris regresszió minden egyes metrikára')


            # oké megvan a before és megvan az after (self.y, left, center, right)
            # a before és az after array egyébként úgy épül fel, hogy a sorok a megfigyelések
            # 0-ik oszlop !!! Nem az ót közepétől vett eltérés mértéke, hanem az Y tengelyen mért távolság !!!
            # 1    oszlop sensor_left
            # 2    oszlop sensor_center
            # 3    oszlop sensor_right
#            before_array = np.array(self.before)
#            after_array  = np.array(self.after)
#            y_delta = after_array[:,0] - before_array[:,0]
#            delta_array = after_array - before_array




  # -------------- right
#            _X_right = np.array([before_array[:,3], delta_array[:,0]]).T # right és delta_y (before)
#            _y_right = after_array[:,3].reshape(-1, 1)                   # right (after)
#            regression_right = self.regression_right
#            regression_right.fit(_X_right, _y_right)
#            printer.ba('\t\t ------------------------------- valyon mennyire jó a right  metrikának a becslése -----------------------------')
#            printer.ba('\t\t regression_right.coef_ = ', regression_right.coef_)
#            printer.ba('\t\t regression_right.intercept_ = ', regression_right.intercept_)
#            _predicted_right = regression_right.predict(_X_right)




            # most ki kell számolni, hogy mennyi lenne a szenzorok értéke, ha fel le lépkednénk

            # mondjuk maximalizáljuk a fel le lépkedés mértékét 5-ben

            move = np.array([-7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7])





            printer.action('\t # Az egyes lépések várható kimeneteinek kiszámolása ----------------------------------------------')

            printer.action('\t\t # Ennyivel mozdulna el egy szenzor adat 1 egység változással ha 1 lenne a before értéke')

            proba_X_metrika   = np.array([1,1]).reshape(1, -1)
            printer.action('proba_X_metrika   = ', proba_X_metrika)
            predicted_proba_left = self.regression_left.predict(proba_X_metrika)
            predicted_proba_center = self.regression_center.predict(proba_X_metrika)
            predicted_proba_right = self.regression_right.predict(proba_X_metrika)
            printer.action('-------- 1 y up ->  left   = ', predicted_proba_left)
            printer.action('-------- 1 y up ->  center = ', predicted_proba_center)
            printer.action('-------- 1 y up ->  right  = ', predicted_proba_right)
            printer.action('\n')








            # EGY KURVA NAGY ELMÉLETI DILLEMMÁHOZ ÉRKEZTEM.
            
            action = 0; tmp = 999999990

            for j in move:
              printer.action('\n')
              printer.action('\t\t minden j-re kiszámolom a regressziót és be is helyetessítjük a kapott értékekekt a modellbe')
              printer.action('\t\t j = ', j)

              _X_left   = np.array([[self.distance_left_from_wall, j]])
              _X_center = np.array([[self.distance_center_from_wall, j]])
              _X_right  = np.array([[self.distance_right_from_wall, j]])

              printer.action('\t\t ------------------------ a regresszió bemenetei az éppen aktuális értékek -------------------')
              printer.action('\t\t _X_left   = ', _X_left)
              printer.action('\t\t _X_center = ', _X_center)
              printer.action('\t\t _X_right  = ', _X_right)

              predicted_left   = self.regression_left.predict(_X_left)
              predicted_center = self.regression_center.predict(_X_center)
              predicted_right  = self.regression_right.predict(_X_right)

              printer.action('\t\t predicted_left   = ', predicted_left)
              printer.action('\t\t predicted_center = ', predicted_center)
              printer.action('\t\t predicted_right  = ', predicted_right)

              printer.action('\t\t --------------------- a regression úgy tűnik, hogy jó és pontos ----------------------')
# hhh              printer.action('\t\t regression_left.coef_   = ', regression_left.coef_)
              printer.action('\t\t self.regression_left.coef_   = ', self.regression_left.coef_)
              printer.action('\t\t regression_center.coef_ = ', self.regression_center.coef_)
              printer.action('\t\t regression_right.coef_  = ', self.regression_right.coef_)
# hhh              printer.action('\t\t regression_left.intercept_   = ', regression_left.intercept_)
              printer.action('\t\t self.regression_left.intercept_   = ', self.regression_left.intercept_)
              printer.action('\t\t regression_center.intercept_ = ', self.regression_center.intercept_)
              printer.action('\t\t regression_right.intercept_  = ', self.regression_right.intercept_)

              # nekünk majd azt az értéket kell választanunk amelyik segítségével a legközelebb jutunk a 0 értékhez

              _X = np.array([predicted_left.ravel(), predicted_center.ravel(), predicted_right.ravel()]).T    # figyelni kell rá, hogy eredetileg is ez volt-e a változók sorrendje

              _X_scaled = self.x_minmaxscaler.transform(_X)

              printer.action('\t\t # Ez lesz a bemenete a neurális hálónak')
              printer.action('\t\t -------------------------X-------------------------')
              printer.action('\t\t ', _X)
              printer.action('\t\t -------------------------X_scaled------------------')
              printer.action('\t\t ', _X_scaled)
              
              printer.action('\t\t ---------------Brutálisan hülye dolgot jelez előre ezért ellenőrizni kell, hogy mi a gond. Esetleg a bemeneti adatok?-----------------')

# Neurális háló becslése
              predicted_position_scaled = self.mlp.predict(_X_scaled)
              printer.action('\t\t predicted_position neural net model scaled = ', predicted_position_scaled)
# Vissza kell transzformálnom eredeti formájába
              predicted_position = self.y_minmaxscaler.inverse_transform(predicted_position_scaled.reshape(-1, 1))
              printer.action('\t\t predicted_position neural net model inverz = ', predicted_position)

              printer.action('\t\t --------------------------------------------------------------------------------------------------------------------------------------')

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

          if( i % 3 == 0 ):                                                       # ugyan ez a feltétel amikor tanítom az út közepének a becslésére
            print('------------------------------ IF i % 3 == 0 ------------------------------')
            _summary_action_was_taken = 1
            print('=================== TAKE ACTION ===================')
# ez lett új az ML Auto 10.ipynb-hoz képest
            self.before.append(np.array([self.y, self.distance_left_from_wall, self.distance_center_from_wall, self.distance_right_from_wall]))
            print('-------- ennyivel módosítom self.y értékét --------')
            print('self.y régi értéke = ', self.y)
            self.y = self.y + action
# ez lett új az ML Auto 10.ipynb-hoz képest
            self.calculate_distances()
            self.after.append(np.array([self.y, self.distance_left_from_wall, self.distance_center_from_wall, self.distance_right_from_wall]))

            print('self.y új értéke   = ', self.y)
            print('action             = ', action)
            print('----------------- módosítás vége -----------------')




          # újra kell gondolni az egészet, ugyanis akkor is ki kell számolni a before after értéket amikor modosítom a pozicióját,
          # vagyis végig kell gondolni ezt az egészet.
          # az első elképzelésem az volt, hogy a poziciót csak bizonyos esetben modosíthatom, csak akkor amikor nincs tanítás, és nincs szimulált emelés, vagy csökkentés sem
          # utóbbit az if( i % 3 == 2) feltétellel szűrtem



      # adjuk hozzá az értéket a self.y_history-hoz
      print('# A run ciklus vége ------------------------------------------------------------------------------------------------------------------------------------------')
      print('#   itt adom hozzás a self.y a self.y_history-hoz')
      self.y_history.append(self.y)
      print('#    self.y :')
      print(self.y)
#      print('#   self.y_history after append :')
#      print(self.y_history)
      print('# \t\t\t --------------- Summary ---------------')
      print('# \t\t\t _summary_mlp_fit_was_taken         = ', _summary_mlp_fit_was_taken)
      print('# \t\t\t _summary_mlp_prediction_was_taken  = ', _summary_mlp_prediction_was_taken)
      print('# \t\t\t _summary_mesterseges_mozgatas      = ', _summary_mesterseges_mozgatas)
      print('# \t\t\t _summary_action_were_taken         = ', _summary_action_was_taken)
      print('# ')
      print('# A run ciklus vége ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')



