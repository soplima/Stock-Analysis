# Stock Data Analysis and Visualization

This repository contains Python code to analyze and visualize stock data. It provides functions for downloading stock data, performing basic statistical analysis, and plotting various stock metrics like returns, volatility, and performance.

## Table of Contents
1. [Installation](#installation)
2. [API Key Setup](#api-key-setup)
3. [Usage](#usage)
4. [Functions Overview](#functions-overview)
5. [Classes Overview](#classes-overview)
6. [Examples](#examples)
7. [License](#license)

## Installation

Before using this repository, make sure you have Python installed along with the necessary dependencies.

To install the required libraries, use `pip`:

```bash
pip install -r requirements.txt

API Key Setup
To fetch stock data, you need an API token from EOD Historical Data. Place your API token in a file named api_token.txt in the root directory of the project.

Usage
Fetch Stock Data: The main function Stock.get_data() fetches the stock data and stores it in a pandas DataFrame.
Plot Returns Distribution: Use Stock.plot_return_dist() to visualize the distribution of stock returns.
Plot Volatility: Use Stock.plot_volatility() to visualize the relationship between returns and volatility.
Plot Stock Performance: Use Stock.plot_performance() to visualize the performance of a stock.
Low Volatility Duration: Use Stock.low_vol_duration() to analyze the periods where the stock exhibits low volatility.


Classes Overview
Stock
The Stock class encapsulates methods for working with individual stock data. The class includes the following methods:

__init__(self, symbol, key, date=DEFAULT_DATA, folder=None)
Initializes the stock object with the stock symbol, API key, date range, and folder where the data is stored.
get_data(self)
Fetches the stock data either from a local folder or by downloading from the API.
calc_vol(self, df)
Calculates various metrics like returns, volatility, and magnitude for the stock data.
plot_return_dist(self)
Plots the distribution of returns for the stock.
plot_volatility(self)
Plots the volatility of returns for the stock.
plot_performance(self)
Plots the relative performance of the stock.
option_expiry(self)
Returns a filtered DataFrame with data for option expiry weeks.
low_vol_duration(self)
Analyzes and returns the periods with low volatility.
Examples


License
This project is licensed under the MIT License - see the LICENSE file for details.

