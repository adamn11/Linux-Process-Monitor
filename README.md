# Linux Process Monitor

A simple command line application that monitors process memory.

## Features

- Monitors a process's memory usage 
- Graphs data into a png once monitoring process is done
- Converts text data into an excel file

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

You will need the following installed:
- Python 2.7

The following packages are optional. The program will still run without these installed.
- matplotlib (in order to plot memory data) and python tkinter (required to display GUI for plot chart)
- xlwt (in order to convert text data into an excel file)

### Installing Program

Clone this repo to your local machine using

```
git clone https://github.com/adamn11/Linux-Process-Monitor.git
```

### Installing Optional Packages

To install the packages, run the following commands inside your terminal

```
sudo apt-get install python-matplotlib
```

```
sudo apt-get install python-tk
```

```
sudo apt-get install xlwt
```

## Versioning

We use [SemVer](http://semver.org/) for versioning. To view the version history, look at version.py.

## Authors

* **Adam Nguyen** - [adamn11](https://github.com/adamn11)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
