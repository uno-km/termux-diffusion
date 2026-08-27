# 📱 Galaxy A35 vs Galaxy S21 Physical Benchmark Report

> **Document Version:** `v1.0.0`  
> **Devices Under Test:** Samsung Galaxy A35 5G (`SM-A356N`) vs Samsung Galaxy S21 5G (`SM-G991N`)  
> **Engine:** `termux-diffusion` v1.3.0 Optimized NDK C++ Runtime (`armv8.2-a+dotprod+fp16`)  
> **Date:** 2026-08-25 – 2026-08-26  

---

## 📌 1. Executive Summary

| Device | SoC | GPU | Precision | Resolution | Latency (s/it) | Total Time (20 steps) |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: |
| **Galaxy S21 5G** | Exynos 2100 | Mali-G78 MP14 | FP16 | 512x512 | 2.14s | ~43.2s |
| **Galaxy A35 5G** | Exynos 1380 | Mali-G68 MP5 | FP16 | 512x512 | 4.82s | ~96.5s |
| **Galaxy S21 5G** | Exynos 2100 | CPU (Oryon/Cortex-X1) | Q4_0 | 512x512 | 5.31s | ~106.2s |
| **Galaxy A35 5G** | Exynos 1380 | CPU (Cortex-A78) | Q4_0 | 512x512 | 8.95s | ~179.0s |
