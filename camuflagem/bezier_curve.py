import math
import random
import time
import random
import matplotlib.pyplot as plt

from datetime import datetime 

# from selenium import webdriver
# from selenium.webdriver.common.action_chains import ActionChains

# Baseado em:
#   - https://en.wikipedia.org/wiki/B%C3%A9zier_curve

def binomial_coef(n: float, i: float) -> float:
    ''' Returns the binomial coefficient of n and i
    '''
    return math.factorial(n) / math.factorial(i) / math.factorial(n - i)

def bernstein(i: float, n: float, t: float):
    ''' Returns the bernstein basis polynomials of degree n 
    '''
    return binomial_coef(n, i) * (t ** i) * ((1 - t) ** (n - i))

def generate(control_points: list, intervals: int = 10) -> list:
    ''' Generates Bézier curve points for the control points.

    Keywords arguments:
        intervals -- Number of points between the start and end points (default 10)
        control_points -- List of control points 
    '''
    if len(control_points) < 2 or len(control_points[0]) != 2:
        # At least two points are required and must be in 2-d
        return

    n = len(control_points)
    n_dec = n - 1

    points = list()
    for interval in range(intervals + 1):
        t = interval / intervals

        point = [0, 0]
        for i in range(n):
            control_point = control_points[i]

            bern = bernstein(i, n_dec, t)
            point[0] += bern * control_point[0]
            point[1] += bern * control_point[1]

        # coordenadas de pixels devem ser inteiros
        point = (round(point[0]), round(point[1]))
        if point not in points:
            points.append(point)

    return points

def plot(points: list) -> None:
    '''Generates the graph for the points.
    '''
    fig, ax = plt.subplots(figsize=(5, 3))

    xs = list()
    ys = list()

    for point in points:
        xs.append(point[0])
        ys.append(point[1])

    ax.plot(xs, ys)

    filename = 'bezier_curve_' + str(datetime.now()).split('.')[0].replace(' ','_') + '.png'
    plt.savefig(filename)

# if __name__ == "__main__":
#     driver = webdriver.Firefox()
#     driver.get('https://www.autodraw.com/')
#     # find_element_by_css_selector('html')
#     driver.find_element_by_css_selector(".buttons > .green").click()
#     root = driver.find_element_by_id("main-canvas")

#     window_size = root.size    
#     width = int(window_size['width'])
#     height = int(window_size['height'])
    
#     x_range = [x for x in range(width)]
#     y_range = [x for x in range(height)]
    
#     n_ctrl_pts = 5
#     ctrl_points = list()
#     for _ in range(n_ctrl_pts):
#         x = random.choice(x_range)
#         y = random.choice(y_range)

#         ctrl_points.append((x, y))

#     points = generate(ctrl_points)

#     action = ActionChains(driver)
    
#     xoffset = points[0][0]
#     yoffset = points[0][1]

#     action.move_to_element_with_offset(root, xoffset, yoffset)
#     action.click_and_hold()

#     last_point = [xoffset, yoffset]
#     for point in points[1:]:
#         xoffset = point[0] - last_point[0]
#         yoffset = point[1] - last_point[1]
        
#         action.move_by_offset(xoffset, yoffset)
        
#         last_point[0] = point[0]
#         last_point[1] = point[1]
    
#     action.release()
#     action.perform()

#     plot(points)
#     # print(root.location)
#     # print(root.size)

