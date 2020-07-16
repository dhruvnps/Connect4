import pickle
import time
import bisect
import random

# with open('cachetable.pickle', 'rb') as f:
#     CACHE_TABLE = pickle.load(f)

arr = list(range(500000))
random.shuffle(arr)

arr2 = [[i, i, i, i] for i in range(500000)]


def binarySearch(arr, l, r, x):
    if r >= l:
        mid = l + (r - l) // 2
        if arr[mid] == x:
            return mid
        elif arr[mid] > x:
            return binarySearch(arr, l, mid-1, x)
        else:
            return binarySearch(arr, mid + 1, r, x)
    else:
        return -1


print(len(arr))

start = time.process_time()
new = sorted(arr)
print("sort:     ", "{:e}".format(time.process_time() - start))

n = 1

start = time.process_time()
if n in arr:
    pass
print("search:   ", "{:e}".format(time.process_time() - start))

start = time.process_time()
if binarySearch(new, 0, len(new)-1, n) != -1:
    pass
print("binary:   ", "{:e}".format(time.process_time() - start))

elem = new[len(new) // 4]
start = time.process_time()
bisect.insort(new, elem)
print("insort:   ", "{:e}".format(time.process_time() - start))

elem = arr[len(arr) // 4]
start = time.process_time()
arr.append(elem)
print("insert:   ", "{:e}".format(time.process_time() - start))

elem = new[len(new) // 4]
start = time.process_time()
new.index(elem)
print("index:    ", "{:e}".format(time.process_time() - start))

start = time.process_time()
a = [i[0] for i in arr2]
print("extract:  ", "{:e}".format(time.process_time() - start))

# li = CACHE_TABLE
# indices = list(range(len(li[0])))
# indices.sort(key=li[0].__getitem__)
# for i, sublist in enumerate(li):
#     li[i] = [sublist[j] for j in indices]
# CACHE_TABLE = li
# print(CACHE_TABLE[0][:10])
