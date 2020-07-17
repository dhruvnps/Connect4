# initialises zob table and cache table
# cache table hashes depend on zob table

import random
import pickle

ROW_LEN, COLUMN_LEN = 6, 7

# zob table --> random table for zobrist hashing
ZOB_TABLE = []
for _ in range(ROW_LEN):
    ZOB_TABLE.append([[random.randint(1, 2**64 - 1)
                       for _ in range(2)] for _ in range(COLUMN_LEN)])
with open('zobtable.pickle', 'wb') as f:
    pickle.dump(ZOB_TABLE, f)

# cache table --> contains: board hash, calculation depth, score, best column
CACHE_TABLE = [[], [], [], []]
with open('cachetable.pickle', 'wb') as f:
    pickle.dump(CACHE_TABLE, f)
