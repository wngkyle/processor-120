Kyle Wang
ww2301@nyu.edu
N17024217

The assignment is fully completed. It simulates a E20 processor with either one-level cache, or two-level cache. The only resources used to 
complete this project is the E20 manual and lecture slides. The strength of this simulator is it is capacble of simulating up to 
two caches, and the configurations of the cache are not fixed. They can be customized and are specified by the users. However, the 
weakness is when incorrect cache size, associativity, or blocksize are passed into the parameters, the program does not automatically
corrects or detects the error. Users have to ensure the right values are passed to prevent any error or crash. 

Since the fetch stage is not considered in this project, the only instructions that can modify and read memory is the lw and sw instructions.
The two instructions have their own helper functions to help keep track and update the current status of the memory and caches. For lw, 
lw_two_caches is used when two caches are initialized, and lw_one_cache is used when only one cache is initialized. Similarly, for sw, 
sw_two_caches is used when there is two caches, and sw_one_cache is used when there is only one cache. For both instructions, when called, 
the program will determine if one or two caches are initialized and then calculate the row and tag of the address in each cache. 

For lw, with row and tag computed, the program will then the help functions to see if the value exist in the caches. For instance, when two 
caches are initialized, if miss in L1, it will search L2. If miss again in L2, then it will pull the value from memory. If hit in L1, then 
it will stop the search and return. The same concept applies when there is only one cache. Any search in cache that results in a miss will 
end up calling the update_cache_and_status function. This function will update the missed value into the cache either from an upper level 
cache or from main memory.  In addition, update_cache_and_status also update the order in which block have been used to help implement the 
LRU policy for eviction.

For sw, the update_cache_and_status function is called immediately after entering function. The sw instruction also uses the write-through
with write-allocate policy for writing values. Lastly, the helper functions for both instructions also update the cache log whenever they 
are called regardless of the search result.

The reason why I use different functions to implement the whole cache simulation instead writing everything in the simulation 
function is because lw and sw have somewhat similar behaviors when updating cache and keep track of block order. Therefore, using 
update_cache_and_status, I was able to produce the same result without the writing the same code multiple times. This not only produce less
work but also increase readability, which helps a lot in debugging errors. 

