# LogAnalyzer++ (C++17)

This is a self-contained single-machine prototype of LogAnalyzer++ written for C++17.
It demonstrates modern STL usage: containers, algorithms, regex, filesystem, threads,
condition_variable, optional, move semantics, and structured code layout.

## Build
```bash
mkdir build && cd build
cmake ..
make
./LogAnalyzer
```

Requires a C++17-capable compiler (g++ 9+ recommended) and CMake >= 3.15.
