class Road():
  def __init__(self, wide, length, type=1, v=124):
    self.length      = length # 3000
    self.distance    = np.arange(0, self.length, 1)
    self.wide        = wide
    self.wall_right  = 30*(np.sin(self.distance/180)) + self.distance * 0.3 + 30 * np.cos(self.distance/30) + 50 * np.sin(self.distance/90)
    self.wall_right[0:100] = 60
    self.wall_left   = self.wall_right + self.wide
    self.wall_center = ( self.wall_left + self.wall_right ) / 2
    
    if(type == 2):
        # v = 124
        u = 0
        a = 41
        b = 0.3
        c = 30
        d = 30
        e = 50
        f = 90
        self.wall_left   = 30*(np.sin(self.distance/180)) + self.distance * 0.3 + 30 * np.cos(self.distance/30) + 50 * np.sin(self.distance/90)
        self.distance += u
        self.wall_right  = a*(np.sin(self.distance/180)) + self.distance * b + c * np.cos(self.distance/d) + e * np.sin(self.distance/f)
        self.wall_right  += v
        self.wall_center = ( 1.3 * self.wall_left + 0.7 * self.wall_right ) / 2
        self.wall_left[0:100]   = self.wall_left[101]
        self.wall_center[0:100] = self.wall_center[101]
        self.wall_right[0:100]  = self.wall_right[101]
        
    if(type == 3):
        v = 224
        u = 0
        a = 41
        b = 0.3
        c = 30
        d = 46
        e = 50
        f = 90
        self.wall_left   = 30*(np.sin(self.distance/180)) + self.distance * 0.3 + 30 * np.cos(self.distance/30) + 50 * np.sin(self.distance/90)
        self.distance += u
        self.wall_right  = a*(np.sin(self.distance/180)) + self.distance * b + c * np.cos(self.distance/d) + e * np.sin(self.distance/f)
        self.wall_right  += v
        self.wall_center = ( self.wall_left + self.wall_right ) / 2
        self.wall_left[0:100]   = self.wall_left[101]
        self.wall_center[0:100] = self.wall_center[101]
        self.wall_right[0:100]  = self.wall_right[101]
    
    if(type == 4): # wizu
        # v = 200
        u = 0
        a = 41
        b = 0.3
        c = 30
        d = 43
        e = 50
        f = 90
        n = 2
        self.wall_left   = 30*(np.sin(self.distance/180)) + self.distance * 0.3 + 30 * np.cos(self.distance/30) + 50 * np.sin(self.distance/90)
        self.wall_left[0:100] = 60
        self.distance += u
        self.wall_right  = a*(np.sin(self.distance/180)) + self.distance * b + c * np.cos(self.distance/d) + e * np.sin(self.distance/f)
        self.wall_right  += v
        self.wall_center = ( self.wall_left + self.wall_right ) / n
        self.wall_left[0:100]   = self.wall_left[101]
        self.wall_center[0:100] = self.wall_center[101]
        self.wall_right[0:100]  = self.wall_right[101]

    if(type == 5): # wizu
        # v = 200
        u = 0
        a = 41
        b = 0.3
        c = 30
        d = 43
        e = 50
        f = 90
        n = 3
        self.wall_left   = 30*(np.sin(self.distance/180)) + self.distance * 0.3 + 30 * np.cos(self.distance/30) + 50 * np.sin(self.distance/90)
        self.wall_left[0:100] = 60
        self.distance += u
        self.wall_right  = a*(np.sin(self.distance/180)) + self.distance * b + c * np.cos(self.distance/d) + e * np.sin(self.distance/f)
        self.wall_right  += v
        self.wall_center = ( self.wall_left + self.wall_right ) / n
        self.wall_left[0:100]   = self.wall_left[101]
        self.wall_center[0:100] = self.wall_center[101]
        self.wall_right[0:100]  = self.wall_right[101]

    self.description()



  def wizu(u = 100, v = 100, a=30, b=0.3, c=30, d=30, e=50, f=90, n=2):
    distance    = np.arange(0, 1000, 1)
    road        = 100
    wall_left   = 30*(np.sin(distance/180)) + distance * 0.3 + 30 * np.cos(distance/30) + 50 * np.sin(distance/90)
    # wall_left[0:100] = 60
    # wall_right  = wall_left + road
    distance += u
    wall_right  = a*(np.sin(distance/180)) + distance * b + c * np.cos(distance/d) + e * np.sin(distance/f)
    wall_right  += v
    wall_center = ( 1.3 * wall_left + 0.7 * wall_right ) / n

    plt.figure(figsize=(20,5)); plt.plot(wall_left); plt.plot(wall_right); plt.plot(wall_center); plt.show()



  def show(self):
    # fig, ax = plt.subplots(figsize=(26,10)); ax.set_ylim(40, 1000); ax.plot(self.wall_left); ax.plot(self.wall_right); ax.plot(self.wall_center);
    _y_max = np.max(self.wall_left)
    fig, ax = plt.subplots(figsize=(26,10)); ax.set_ylim(40, _y_max); ax.plot(self.wall_left); ax.plot(self.wall_right); ax.plot(self.wall_center);
    return fig, ax
  
  def description(self):
    print('# ----------------------------------------- road Description -----------------------------------------')
    print('  \t\t road.length = ', self.length)
    print('  \t\t minimum slope (descending) = ', np.min(np.diff(self.wall_center, 1, -1, prepend=self.wall_center[0])))
    print('  \t\t maximum slope (ascending)  =  ', np.max(np.diff(self.wall_center, 1, -1, prepend=self.wall_center[0])))
    print('# ----------------------------------------------------------------------------------------------------')
