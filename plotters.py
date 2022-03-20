class PostPlotter():
  def __init__(self, car):
    self.car = car

# new v.25
#  def_plot_lr_weights(self, flag):
#    # a lineáris regresszió súlyainak idővonalon való ábrázolása a cél
#    fig = plt.figure(figsize=(10, 6))
#    ax = fig.add_subplot()
#    ax.plot()
#    plt.show()

  def plot_history(self, flag):
    '''
    A PostPlotter osztály inicializálásánál kapott Car objektum
    plot_history(falg) metódusát hívja meg
    '''
    self.car.plot_history(flag)

  def plot_y_distance(self):
    'A Car objektum y_distace atributumát rajzolja ki'
    plt.plot(self.car.y_distance)
    plt.show()

  def plot_mlp(self):

    num_input_varialbe = ['sensor_left','sensor_center', 'sensor_right']

    # Define the structure of the network
    network_structure = np.hstack(([len(num_input_varialbe)], np.asarray(self.car.mlp.hidden_layer_sizes), [1]))

    print(network_structure)

    # Draw the Neural Network with weights
    network = DrawNN(network_structure, self.car.mlp.coefs_, num_input_varialbe)
    network.draw()

  def plot_y_move_v2(self, car, x, flag, height = 6):

    if( flag != 0 ):

      fileName = 'PostPlotter_y_move_v2'
      fig = plt.figure(figsize=(26, height))
      ax = fig.add_subplot()
      y_move = np.zeros((car.road.length))
      y_move[0:len(car.y_history)] = np.diff(np.array(car.y_history), 1, -1, prepend=0)
      y_move[0] = 0
      y_tick_labels = [-8, -6,-4, -2, '-0.00', 2, 4, 6]
      ax.set_yticklabels(y_tick_labels)
      ax.plot(y_move)
      ax.hlines(0, 0, 100)
      ax.set_title('#i = ' + str(x))
      if( flag == 1 or flag == 3 ): plt.show();
      if( flag == 2 or flag == 3 ): fig.savefig(fileName + '_{0:04}'.format(x)+'.png', bbox_inches='tight'); plt.close('all'); fig.clf(); ax.cla(); plt.close('all');

  def plot_sensors_distibution(self, bins = 30):

    left = np.array(self.car.sensor_left)
    center = np.array(self.car.sensor_center)
    right = np.array(self.car.sensor_right)

    latextext1 = '\n'.join((
    r'$\sigma_{left}  =%.4f$' % (np.std(left)),
    r'$\sigma_{center}=%.4f$' % (np.std(center)),
    r'$\sigma_{right} =%.4f$' % (np.std(right))
    ))

    latextext2 = '\n'.join((
    r'$\overline{x}_{left}=%.4f$' % (np.mean(left)),
    r'$\overline{x}_{center}=%.4f$' % (np.mean(center)),
    r'$\overline{x}_{right}=%.4f$' % (np.mean(right))
    ))

    fig, axes = plt.subplots(1, 2, figsize=(10, 5))

    # print(plt.rcParams['axes.prop_cycle'].by_key()['color'])

    # ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']

    ax = axes[0]
    ax.hist(left, bins=bins, density=True, histtype='step', label='left', color = '#1f77b4')
    ax.hist(center, bins=bins, density=True, histtype='step', label='center', color = '#2ca02c')
    ax.hist(right, bins=bins, density=True, histtype='step', label='right', color = '#ff7f0e')
    ax.legend(loc='upper right')
    ax.text(0.05, 0.81, latextext1, transform=ax.transAxes, bbox=dict(facecolor='white', edgecolor='black'))
    ax.set_ylabel('Density')

    ax = axes[1]
    ax.hist(left, bins=bins, density=True, histtype='step', label='left', color='#1f77b4')
    ax.hist(right, bins=bins, density=True, histtype='step', label='right', color='#ff7f0e')
    ax.legend(loc='upper right')
    ax.text(0.05, 0.81, latextext2, transform=ax.transAxes, bbox=dict(facecolor='white', edgecolor='black'))
    # ax.set_ylabel('Density')

    fig.suptitle('Distribution of the values of the sensors')
    fig.text(0.5, -0.0, '$\max_{x \in [a,b]}f(x)$', ha='center')
    plt.show()

  def plot_mlp_surface_prediction_v2(self, resolution = 10):
    # fogja meg az auto left és rigth sensor értékeit
    # vegye a minimumot és a maximumát külön külön
    # csináljon rajtuk egy np.linspace-t
    sl = np.array(self.car.sensor_left); sl_min = sl.min(); sl_max = sl.max()
    print('sl.shape = ', sl.shape); print('sl.min() = ', sl_min); print('sl.max() = ', sl_max)
    sr = np.array(self.car.sensor_right); sr_min = sr.min(); sr_max = sr.max()
    print('sr.shape = ', sr.shape); print('sr.min() = ', sr_min); print('sr.max() = ', sr_max)
    sc = np.array(self.car.sensor_center); sc_min = sc.min(); sc_max = sc.max()
    print('sc.shape = ', sc.shape); print('sc.min() = ', sc_min); print('sc.max() = ', sc_max)

    sensor_center = 100
    _sl = np.linspace(sl_min, sl_max, num = resolution)
    _sr = np.linspace(sr_min, sr_max, num = resolution)
    _sc = np.linspace(sensor_center, sensor_center, num = resolution)

    # kell csinálni egy mesh gridet a plothoz
    _left, _right = np.meshgrid(_sl, _sr)

    print('_left.shape   = ', _left.shape); print('_right.shapes = ', _right.shape)

    # a bemeneti vectorhoz -> itt mátrixhoz -> kell csinálnom néhány átalakítást

    _left_input = _left.flatten()
    _right_input = _right.flatten()
    _center_input = np.full((resolution, resolution), sensor_center).flatten()

    # create an input vector
    _X_input = np.array([_left_input, _center_input, _right_input]).T

    # normlaize it
    _X_input_scaled = self.car.x_minmaxscaler.transform(_X_input)

    # predict
    _Y_output_predicted = self.car.mlp.predict(_X_input_scaled)

    # transform
    _Y_predicted_inverse = self.car.y_minmaxscaler.inverse_transform(_Y_output_predicted.reshape(1, -1))

    # vissza kell alakítanom mátrix formába
    _Y_predicted = _Y_predicted_inverse.reshape(resolution, resolution)

    plt.contourf(_left, _right, _Y_predicted, levels = 30)
    plt.colorbar(label='level')
    plt.show()

  # valamiért ez a kettő
  # ha kicsit is de eltérő eredményt ad
  def plot_mlp_surface_prediction_v1(self, resolution = 10):
    # fogja meg az auto left és rigth sensor értékeit
    # vegye a minimumot és a maximumát külön külön
    # csináljon rajtuk egy np.linspace-t
    sl = np.array(self.car.sensor_left); sl_min = sl.min(); sl_max = sl.max()
    print('type(sl) = ', type(sl))
    print('sl.shape = ', sl.shape)
    print('sl.size  = ', sl.size)
    print('sl.min() = ', sl_min)
    print('sl.max() = ', sl_max)
    sr = np.array(self.car.sensor_right); sr_min = sr.min(); sr_max = sr.max()
    print('sr.shape = ', sr.shape)
    print('sr.size  = ', sr.size)
    print('sr.min() = ', sr_min)
    print('sr.max() = ', sr_max)
    sc = np.array(self.car.sensor_center); sc_min = sc.min(); sc_max = sc.max()
    print('sc.shape = ', sc.shape)
    print('sc.size  = ', sc.size)
    print('sc.min() = ', sc_min)
    print('sc.max() = ', sc_max)

    set_sensor_center = 100
    _sl = np.linspace(sl_min, sl_max, num = resolution)
    _sr = np.linspace(sr_min, sr_max, num = resolution)
    _sc = np.linspace(set_sensor_center, set_sensor_center, num = resolution)

    # kell csinálni egy mesh gridet
    _x, _y = np.meshgrid(_sl, _sr)

    print('_x.shape  = ', _x.shape)
    print('_y.shapes = ', _y.shape)

    # az iterációnál vigyezni kell, mert _x és _y rohadtul nem egész számok
    # ugyan ez de most for loop-al csináltam meg
    _z = np.zeros((resolution,resolution))

    for i in range(1, resolution):
      for j in range(1, resolution):
        _left = _x[i][j]
        _right = _y[i][j]
        _center = set_sensor_center
        # meg kell csinálni a prediction ami nem lesz könnyű mert több lépésből áll
        # 1.
        # rakjuk össze a beneti vectort
        _X_input = np.array([_left, _center, _right])
        # print(_X_input)

        # 2.
        # normalizáljuk
        _X_input_scaled = self.car.x_minmaxscaler.transform(_X_input.reshape(1, -1))

        # 3.
        # becsüljünk
        _Y_output_predicted = self.car.mlp.predict(_X_input_scaled)

        # 4.
        # transformáljuk vissza a becsült értékeket
        _Y_predicted_inverse = self.car.y_minmaxscaler.inverse_transform(_Y_output_predicted.reshape(-1, 1))

        # 3.
        # egyébként rájöttem, hogy ezt nem így egyenként kéne megcsinálnom,
        # megcsinálhatnám úgy is, hogy az egészet egyben állítom elő
        # tehát nem lenne szükség erre a nested for loop ciklusra
        _z[i][j] = _Y_predicted_inverse

    plt.contourf(_x, _y, _z, levels = 30)
    plt.colorbar(label='level')
    plt.show()

  def plot_mlp_surface_prediction_v3(self, flag = 1, resolution = 10, transparency = 1, cmap = 'viridis', elevation = 20, azimuth = -35, i = 1):
    # fogja meg az auto left és rigth sensor értékeit vegye a minimumot és a maximumát külön külön
    # csináljon rajtuk egy np.linspace-t
    sl = np.array(self.car.sensor_left); sl_min = sl.min(); sl_max = sl.max()
    # print('sl.shape = ', sl.shape); print('sl.min() = ', sl_min); print('sl.max() = ', sl_max)
    sr = np.array(self.car.sensor_right); sr_min = sr.min(); sr_max = sr.max()
    # print('sr.shape = ', sr.shape); print('sr.min() = ', sr_min); print('sr.max() = ', sr_max)
    sc = np.array(self.car.sensor_center); sc_min = sc.min(); sc_max = sc.max()
    # print('sc.shape = ', sc.shape); print('sc.min() = ', sc_min); print('sc.max() = ', sc_max)

    sensor_center = 100
    _sl = np.linspace(sl_min, sl_max, num = resolution)
    _sr = np.linspace(sr_min, sr_max, num = resolution)
    _sc = np.linspace(sensor_center, sensor_center, num = resolution)

    # kell csinálni egy mesh gridet a plothoz
    _left, _right = np.meshgrid(_sl, _sr)

    print('_left.shape   = ', _left.shape); print('_right.shapes = ', _right.shape)

    # a bemeneti vectorhoz -> itt mátrixhoz -> kell csinálnom néhány átalakítást
    _left_input = _left.flatten()
    _right_input = _right.flatten()
    _center_input = np.full((resolution, resolution), sensor_center).flatten()

    # create an input vector
    _X_input = np.array([_left_input, _center_input, _right_input]).T

    # normlaize it
    _X_input_scaled = self.car.x_minmaxscaler.transform(_X_input)

    # predict
    _Y_output_predicted = self.car.mlp.predict(_X_input_scaled)

    # transform
    _Y_predicted_inverse = self.car.y_minmaxscaler.inverse_transform(_Y_output_predicted.reshape(1, -1))

    # vissza kell alakítanom mátrix formába
    _Y_predicted = _Y_predicted_inverse.reshape(resolution, resolution)

    fileName = 'PostPlotter_3D_MLP_Prediction_'
    fig = plt.figure(figsize=(10,10))
    ax = fig.add_subplot(projection = '3d')
    ax.view_init(elev = elevation, azim = azimuth)  
    # x axist direction ascending descending
    # ax.invert_xaxis()
    # labels
    ax.set_xlabel('sensor left')
    ax.set_ylabel('sensor right')
    ax.set_zlabel('y_distance')
    # color
    szin = np.arange(len(self.car.sensor_right))
    # scatter
    scat = ax.scatter(self.car.sensor_left, self.car.sensor_right, self.car.y_distance, c=szin)
    # surface
    surf = ax.plot_surface(_left, _right, _Y_predicted, cmap=cmap, alpha = transparency)
    # wireframe
    wire = ax.plot_wireframe(_left, _right, _Y_predicted, rstride=20, cstride=20)
    # colorbar -> scatter
    # fig.colorbar(surf, label='level')

    
    if( flag == 1 or flag == 3 ): plt.show()
    if( flag == 2 or flag == 3 ):
      fig.savefig(fileName + '_3D_v1_{0:04}'.format(i)+'.png'); plt.close(fig);
      plt.close('all'); fig.clf(); ax.cla(); plt.close('all');


  def plot_mlp_surface_prediction_v4(self, flag = 1, limit = False, resolution = 10, transparency = 1, cmap = 'viridis', elevation = 20, azimuth = -35, center = 100, i = 1):
    
    if ( flag != 0 ):
    
      # fogja meg az auto left és rigth sensor értékeit vegye a minimumot és a maximumát külön külön
      # csináljon rajtuk egy np.linspace-t
      sl = np.array(self.car.sensor_left); sl_min = sl.min(); sl_max = sl.max()
      # print('sl.shape = ', sl.shape); print('sl.min() = ', sl_min); print('sl.max() = ', sl_max)
      sr = np.array(self.car.sensor_right); sr_min = sr.min(); sr_max = sr.max()
      # print('sr.shape = ', sr.shape); print('sr.min() = ', sr_min); print('sr.max() = ', sr_max)
      sc = np.array(self.car.sensor_center); sc_min = sc.min(); sc_max = sc.max()
      # print('sc.shape = ', sc.shape); print('sc.min() = ', sc_min); print('sc.max() = ', sc_max)

      if ( limit == True ):
        __x_min = 0; __x_max = 200;
        __y_min = 0; __y_max = 200;
        __z_min = -50; __z_max = 50;
        sl_min = __x_min; sl_max = __x_max
        sr_min = __y_min; sr_max = __y_max
        sc_min = sc.min(); sc_max = sc.max()

      sensor_center = center
      _sl = np.linspace(sl_min, sl_max, num = resolution)
      _sr = np.linspace(sr_min, sr_max, num = resolution)
      _sc = np.linspace(sensor_center, sensor_center, num = resolution)

      # kell csinálni egy mesh gridet a plothoz
      _left, _right = np.meshgrid(_sl, _sr)

      # print('_left.shape   = ', _left.shape); print('_right.shapes = ', _right.shape)

      # a bemeneti vectorhoz -> itt mátrixhoz -> kell csinálnom néhány átalakítást
      _left_input = _left.flatten()
      _right_input = _right.flatten()
      _center_input = np.full((resolution, resolution), sensor_center).flatten()

      # create an input vector
      _X_input = np.array([_left_input, _center_input, _right_input]).T

      # normlaize it
      _X_input_scaled = self.car.x_minmaxscaler.transform(_X_input)

      # predict
      _Y_output_predicted = self.car.mlp.predict(_X_input_scaled)

      # transform
      _Y_predicted_inverse = self.car.y_minmaxscaler.inverse_transform(_Y_output_predicted.reshape(1, -1))

      # vissza kell alakítanom mátrix formába
      _Y_predicted = _Y_predicted_inverse.reshape(resolution, resolution)

      fileName = 'PostPlotter_3D_MLP_Prediction_'
      fig = plt.figure(figsize=(10,10))
      ax = fig.add_subplot(projection = '3d')
      ax.view_init(elev = elevation, azim = azimuth)  
      # x axist direction ascending descending
      # ax.invert_xaxis()
      # labels
      ax.set_xlabel('sensor left')
      ax.set_ylabel('sensor right')
      ax.set_zlabel('y_distance')
      # limit
      if (limit == True ):
        ax.set_xlim(__x_min, __x_max)
        ax.set_ylim(__y_min, __y_max)
        ax.set_zlim(__z_min, __z_max)
      # color
      szin = np.arange(len(self.car.sensor_right))
      # scatter
      scat = ax.scatter(self.car.sensor_left, self.car.sensor_right, self.car.y_distance, c=szin)
      # surface
      surf = ax.plot_surface(_left, _right, _Y_predicted, cmap=cmap, alpha = transparency)
      # wireframe
      wire = ax.plot_wireframe(_left, _right, _Y_predicted, rstride=20, cstride=20)

      # contour
      ax.contour3D(_left, _right, _Y_predicted, 70)
      # colorbar -> scatter
      # fig.colorbar(surf, label='level')
      
      if( flag == 1 or flag == 3 ): plt.show()
      if( flag == 2 or flag == 3 ):
        fig.savefig(fileName + '_3D_v1_{0:04}'.format(i)+'.png'); plt.close(fig);
        plt.close('all'); fig.clf(); ax.cla(); plt.close('all');


  