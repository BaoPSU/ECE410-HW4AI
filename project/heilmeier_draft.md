# Heilmeier Questions Draft
Bao Nguyen  
ECE 410/510 Spring 2026  

## 1. What are you trying to do?
I am trying to understand how neural networks work at a hardware level. This includes looking at how much computation they require (like MAC operations), how much memory they use, and how efficient they are. The goal is to see how we can improve performance when running AI models on real hardware.

## 2. How is it done today, and what are the limits?
Today, neural networks are usually run on CPUs and GPUs using software frameworks like PyTorch. These tools make it easy to build and run models, but they hide what is really happening underneath. For example, they do not clearly show how much data is being moved or how hardware limits performance. This can make it hard to understand bottlenecks like memory bandwidth and efficiency.

## 3. What is new in your approach?
My approach is to combine simple hand calculations with tool-based profiling. By calculating things like MACs, memory usage, and arithmetic intensity myself, and then comparing that with real model profiling, I can better understand how neural networks behave. This helps connect what we learn in class to how systems actually work in practice.
