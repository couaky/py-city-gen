from PIL import Image

import heat
import display
import roads


# Map setup
# Need to be n^2+1
size = 129
min_heat = -0.3
max_heat = 1.3
middle = int((size - 1) / 2)

# Heat generation
heat_map = heat.generate(size, min_heat, max_heat)

# Roads generation
roads_map = roads.generate(size, middle, heat_map)

# Display result
heat_map_img = display.heat(heat_map, size)
roads_map_img = display.roads(roads_map, size)
complete_map = Image.blend(heat_map_img, roads_map_img, 0.5)
complete_map.show()

# TODO:
# New avenue algo, dont always continue straight until join another crossed avenue or map limit
# Add streets: from bottom, process avenues left->right bottom->up
# if we have another avenue somewhere upside
# then we can spawn street between the two avenue acording the heat value

# A street is just a vertical straight road between 2 avenues
