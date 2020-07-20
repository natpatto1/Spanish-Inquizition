import matplotlib.pyplot as plt
import numpy

#capped 180
#x = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
#y = [0, 1, 2, 3, 6, 15, 43, 134, 180, 180, 180, 180]

#a = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
#b = [0, 1, 2, 3, 5, 10, 22, 52, 128, 180, 180, 180]

#n = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
#m = [0, 1, 2, 3, 4, 6, 10, 16, 26, 40, 58, 80]

#Upcapped graph
# x1 = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
# y1 = [0, 1, 2, 3, 6, 15, 43, 134, 439, 1489, 5208]

# plt.plot(x1, y1, label = 'Quality 5')
#
# x2 = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
# y2= [0, 1, 2, 3, 5, 10, 22, 52, 128, 318, 792]
# plt.plot(x2, y2, label = 'Quality 4')
#
# x3 = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
# y3 = [0, 1, 2, 3, 4, 6, 10, 16, 26, 40, 58]
#
# plt.plot(x3, y3, label = 'Quality 3')
# plt.legend()
#
#
# plt.xlabel('Time(s) seen by user')
# plt.ylabel('Review intervals in day(s)')

# plt.title('Item intervals when a user consistently \n scores correctness(quality) 5(best), 4 or 3')
#
# plt.show()

### quality 5, answered 2
x = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
y = [0, 1, 2, 3, 6, 15, 43, 134, 1, 2, 3, 7, 22, 78, 293]

plt.plot(x, y)

plt.xlabel('Time(s) seen by user')
plt.ylabel('Review intervals in day(s)')

plt.title('Item intervals when a user fails to recall an item \n once despite consistently scoring correctly (quality 5)')

plt.show()