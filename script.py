import mdl
from display import *
from matrix import *
from draw import *

num_frames = 0
basename = "animation"
animate = False
knobs = []

"""======== first_pass( commands, symbols ) ==========

  Checks the commands array for any animation commands
  (frames, basename, vary)

  Should set num_frames and basename if the frames
  or basename commands are present

  If vary is found, but frames is not, the entire
  program should exit.

  If frames is found, but basename is not, set name
  to some default value, and print out a message
  with the name being used.
  ==================== """
def first_pass(commands):
  global num_frames
  global basename
  global animate

  exist_basename = False

  for command in commands:
    op = command["op"]
    args = command["args"]

    if (op == "frames"):
      num_frames = args[0]
      animate = True

      if (not exist_basename):
        print "setting basename to default 'animation'"

    elif (op == "basename"):
      basename = args[0]
      animate = True
      exist_basename = True

    elif (op == "vary"):
      animate = True
      if (num_frames == 0):
        print "vary found without frames"
        return

"""======== second_pass( commands ) ==========

  In order to set the knobs for animation, we need to keep
  a seaprate value for each knob for each frame. We can do
  this by using an array of dictionaries. Each array index
  will correspond to a frame (eg. knobs[0] would be the first
  frame, knobs[2] would be the 3rd frame and so on).

  Each index should contain a dictionary of knob values, each
  key will be a knob name, and each value will be the knob's
  value for that frame.

  Go through the command array, and when you find vary, go
  from knobs[0] to knobs[frames-1] and add (or modify) the
  dictionary corresponding to the given knob with the
  appropirate value.
  ===================="""
def second_pass(commands, num_frames):
  global knobs

  for frame in range(int(num_frames)):
    knobs.append({})

  for command in commands:
    op = command["op"]
    args = command["args"]

    if (op == "vary"):
      knob = command["knob"]
      startf = args[0]
      endf = args[1]
      startv = args[2]
      endv = args[3]
      increment = (endv - startv) / (endf - startf)
      currv = startv

      for frame in range(int(startf), int(endf + 1)):
        if (frame == endf):
          currv = endv
        knobs[frame][knob] = currv
        currv += increment


def run(filename):
  """
  This function runs an mdl script
  """
  view = [0,
      0,
      1];
  ambient = [50,
         50,
         50]
  light = [[0.5,
        0.75,
        1],
       [0,
        255,
        255]]
  areflect = [0.1,
        0.1,
        0.1]
  dreflect = [0.5,
        0.5,
        0.5]
  sreflect = [0.5,
        0.5,
        0.5]

  color = [0, 0, 0]
  tmp = new_matrix()
  ident( tmp )

  stack = [ [x[:] for x in tmp] ]
  screen = new_screen()
  zbuffer = new_zbuffer()
  tmp = []
  step_3d = 20
  consts = ''
  coords = []
  coords1 = []

  p = mdl.parseFile(filename)

  if p:
    (commands, symbols) = p
  else:
    print "Parsing failed."
    return

  first_pass(commands)
  second_pass(commands, num_frames)

  for frame in range(int(num_frames)):
    for knob in knobs[frame]:
      symbols[knob][1] = knobs[frame][knob]

    for command in commands:
      c = command['op']
      args = command['args']

      if (not args == None):
        args = command['args'][:]

      if ((not args == None) and "knob" in command and (not command["knob"] == None) and c in ["move", "scale", "rotate"]):
        knob = command["knob"]
        for i in range(len(args)):
          if (not isinstance(args[i], basestring)):
            args[i] = args[i] * symbols[knob][1]

      if c == 'box':
        if isinstance(args[0], str):
          consts = args[0]
          args = args[1:]
        if isinstance(args[-1], str):
          coords = args[-1]
        add_box(tmp,
            args[0], args[1], args[2],
            args[3], args[4], args[5])
        matrix_mult( stack[-1], tmp )
        draw_polygons(tmp, screen, zbuffer, view, ambient, light, areflect, dreflect, sreflect)
        tmp = []
      elif c == 'sphere':
        add_sphere(tmp,
               args[0], args[1], args[2], args[3], step_3d)
        matrix_mult( stack[-1], tmp )
        draw_polygons(tmp, screen, zbuffer, view, ambient, light, areflect, dreflect, sreflect)
        tmp = []
      elif c == 'torus':
        add_torus(tmp,
              args[0], args[1], args[2], args[3], args[4], step_3d)
        matrix_mult( stack[-1], tmp )
        draw_polygons(tmp, screen, zbuffer, view, ambient, light, areflect, dreflect, sreflect)
        tmp = []
      elif c == 'line':
        if isinstance(args[0], str):
          consts = args[0]
          args = args[1:]
        if isinstance(args[3], str):
          coords = args[3]
          args = args[:3] + args[4:]
        if isinstance(args[-1], str):
          coords1 = args[-1]
        add_edge(tmp,
             args[0], args[1], args[2], args[3], args[4], args[5])
        matrix_mult( stack[-1], tmp )
        draw_lines(tmp, screen, zbuffer, color)
        tmp = []
      elif c == 'move':
        tmp = make_translate(args[0], args[1], args[2])
        matrix_mult(stack[-1], tmp)
        stack[-1] = [x[:] for x in tmp]
        tmp = []
      elif c == 'scale':
        tmp = make_scale(args[0], args[1], args[2])
        matrix_mult(stack[-1], tmp)
        stack[-1] = [x[:] for x in tmp]
        tmp = []
      elif c == 'rotate':
        theta = args[1] * (math.pi/180)
        if args[0] == 'x':
          tmp = make_rotX(theta)
        elif args[0] == 'y':
          tmp = make_rotY(theta)
        else:
          tmp = make_rotZ(theta)
        matrix_mult( stack[-1], tmp )
        stack[-1] = [ x[:] for x in tmp]
        tmp = []
      elif c == 'push':
        stack.append([x[:] for x in stack[-1]] )
      elif c == 'pop':
        stack.pop()
      elif c == 'display':
        display(screen)
      elif c == 'save':
        save_extension(screen, args[0])

    if (animate):
      save_extension(screen, ("./anim/" + basename + ("%03d.png" % int(frame))))

    tmp = new_matrix()
    ident( tmp )
    stack = [ [x[:] for x in tmp] ]
    screen = new_screen()
    zbuffer = new_zbuffer()
    tmp = []
    step_3d = 20

  if (animate):
    make_animation(basename)