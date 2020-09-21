import matplotlib.pyplot as plt
import numpy

# #capped 180
# x = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
# y = [0, 1, 2, 3, 6, 15, 43, 134, 180, 180, 180]
#
# plt.plot(x, y, label = 'Quality 5')
#
# a = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
# b = [0, 1, 2, 3, 5, 10, 22, 52, 127, 180, 180]
#
# plt.plot(a, b, label = 'Quality 4')
#
#
# n = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
# m = [0, 1, 2, 3, 4, 5, 7, 9, 11, 13, 16]
#
# plt.plot(n, m, label = 'Quality 3')
#
# plt.legend()
# plt.xlabel('Time(s) seen by user')
# plt.ylabel('Review intervals in day(s)')
#
# plt.title('Item intervals when a user consistently \n scores correctness(quality) 5(best), 4 or 3')
# plt.show()
# #Upcapped graph
# x1 = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
# y1 = [0, 1, 2, 3, 6, 15, 43, 134, 439, 1489]
#
# plt.plot(x1, y1, label = 'Quality 5')
#
# x2 = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
# y2= [0, 1, 2, 3, 5, 10, 22, 52, 127, 315, 785]
# plt.plot(x2, y2, label = 'Quality 4')
#
# x3 = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
# y3 = [0, 1, 2, 3, 4, 5, 7, 9, 11, 13, 16]
#
# plt.plot(x3, y3, label = 'Quality 3')
# plt.legend()
#
#
# plt.xlabel('Time(s) seen by user')
# plt.ylabel('Review intervals in day(s)')
#
# plt.title('Item intervals when a user consistently \n scores correctness(quality) 5(best), 4 or 3')
#
# plt.show()
#
# ### quality 5, answered 2
x = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,15]
y = [0, 1, 2, 3, 6, 15, 43, 134, 0, 1, 2, 3, 7, 22, 80, 308]
#
#a = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
#b = [2.5, 2.6, 2.7, 2.8, 2.9, 3, 3.1, 3.2, 3.2, 3.3, 3.4, 3.5,3.6, 3.7, 3.8]
# #
plt.plot(x, y)
# #
plt.xlabel('Time(s) seen by user')
plt.ylabel('Review interval in day(s)')
# #

plt.title('Item intervals when a user fails to recall an item \n once after consistently answering correctly')
#
plt.show()