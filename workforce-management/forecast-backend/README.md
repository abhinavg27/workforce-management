# Rakuten Workforce Forecasting App

This application provides a robust solution for forecasting workforce needs for Rakuten's Supersale events. It leverages historical data, a machine learning model (Linear Regression), and an LLM (Large Language Model) for intuitive insights and actionable summaries.

## Table of Contents

1.  [Overview](#overview)
2.  [Features](#features)
3.  [Project Structure](#project-structure)
4.  [Prerequisites](#prerequisites)
5.  [Installation & Setup](#installation--setup)
    *   [1. Clone the Repository](#1-clone-the-repository)
    *   [2. Set up Python Virtual Environment](#2-set-up-python-virtual-environment)
    *   [3. Install Python Dependencies](#3-install-python-dependencies)
    *   [4. OpenAI API Key & Base URL Configuration](#4-openai-api-key--base-url-configuration)
    *   [5. Historical Data Setup](#5-historical-data-setup)
6.  [Running the Application](#running-the-application)
7.  [Using the Application](#using-the-application)
8.  [Troubleshooting](#troubleshooting)
9.  [Technologies Used](#technologies-used)

## Overview

The application consists of a Flask backend (Python) that handles data loading, model training, forecasting logic, and interaction with the OpenAI LLM. A simple HTML/CSS frontend consumes the API from the backend to display results.

## Features

*   **Workforce Forecasting:** Predicts total labor hours and required workers based on expected orders and historical trends.
*   **Task-Specific Allocation:** Breaks down total workforce needs into individual tasks (e.g., Receive, Stow, Pack) based on historical proportions.
*   **Confidence Intervals:** Provides a range for the worker forecast to indicate prediction uncertainty.
*   **LLM-Powered Summaries:** Generates concise, actionable insights and operational implications using an OpenAI Large Language Model.
*   **Historical Data Management:** Loads data from a CSV file; includes a synthetic data generator for testing if no historical data is available.
*   **User-Friendly Interface:** A simple web interface for inputting forecast parameters and viewing results.


Install Python Dependencies
With your virtual environment activated, install all necessary Python packages using the provided requirements.txt file.

First, create the requirements.txt file inside your backend/ directory with the following content:

backend/requirements.txt content:

Flask
pandas
numpy
scikit-learn
openai~=1.0  # Or a specific version like openai==1.35.13
httpx
Flask-Cors
Then, install them:

#   pip install -r requirements.txt 

 To Start Application please run 
#   python3 app.py