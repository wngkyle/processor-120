def update_cache_and_status(row, tag, cache, status):
    LRU_index = find_LRU_index(status[row])
    for i in range(len(status[row])):
        if status[row][i] < status[row][LRU_index]:
            status[row][i] += 1
    status[row][LRU_index] = 0
    cache[row][LRU_index] = tag 
    return cache, status

def find_LRU_index(list):
    temp = list[0]
    index = 0
    for i in range(len(list)):
        if list[i] > temp:
            temp = list[i]
            index = i
    return index


cache = [[-1, 7], [6, -1], [-1, 6], [6, -1]]
status = [[1, 0], [1, 0], [1, 0], [1, 0]]
address = 112
cache_size = 32
cache_blocksize = 4
cache_assoc = 2
cache_rows = 4
row = (address//4)%cache_rows
tag = (address//4)//cache_rows
print(row)
print(tag)
