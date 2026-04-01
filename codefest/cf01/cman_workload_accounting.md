# Codefest 1 CMAN  
Bao Nguyen  

---

### a.) For each layer, compute the number of multiply-accumulate operations (MACs).  
Show the formula and the substituted values.

input x output = MAC  

784 x 256 = 200704  
256 x 128 = 32768  
128 x 10 = 1280  

---

### b.) Sum the MACs across all three layers to get the total MACs for one forward pass.

200704 + 32768 + 1280 = 234752 total MAC  

---

### c.) Compute the total number of trainable parameters (weights only, no biases).

200704 + 32768 + 1280 = 234752  

---

### d.) Compute the total weight memory in bytes (FP32).

234752 x 4 bytes = 939008 weight  

---

### e.) Compute the total activation memory in bytes needed to store the input and all layer outputs simultaneously (FP32).

784 + 256 + 128 + 10 = 1178  

1178 x 4 = 4712  

---

### f.) Compute arithmetic intensity:

(2 x 234752) / (939008 + 4712) = 0.4975  
