import os
import requests
import pandas as pd
from datetime import datetime, timedelta
import re
import io

TARGET_DATE = datetime.today()
NUM_DAYS = 3

class HabiticaData:
    def __init__(self,user_id,api_key):
        """
        Initializes the HabiticaData class.

        Retrieves the user_id and api_key from environment variables, sets up the Habitica API URL,
        and creates a session with necessary headers.
        """
        self.user_id = user_id
        self.api_key = api_key
        self.api_url = "https://habitica.com/api/v3"
        self.habitica_session = requests.Session()
        self.habitica_session.headers.update({
            "x-api-user": self.user_id,
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        })
        
    def get_user_data(self):
        """
        Retrieves the user data from Habitica account.

        Fetches the user data in CSV format from the Habitica API and stores it in a pandas DataFrame.
        Drops the 'Task ID' column and converts the 'Date' column to datetime format.

        Returns:
        - csv_file: Pandas DataFrame containing the user data.
        """
        response = self.habitica_session.get('https://habitica.com/export/history.csv')
        response.raise_for_status()
        csv_data = response.text
        self.csv_file = pd.read_csv(io.StringIO(csv_data))
        self.csv_file.drop('Task ID', axis=1, inplace=True)
        self.csv_file.drop('Value', axis=1, inplace=True)
        self.csv_file.drop('Task Type', axis=1, inplace=True)
        self.csv_file['Date'] = pd.to_datetime(self.csv_file['Date'])
        self.csv_file =  self.csv_file.sort_values(by='Date')

        return self.csv_file

    def get_date(self, target_date):
        """
        Filters the user data based on a specific date.

        Args:
        - target_date (str or datetime): Target date to filter the user data.

        Returns:
        - filtered_df: Pandas DataFrame containing the user data filtered by the target date.
        """
        filtered_df = self.csv_file[self.csv_file['Date'].dt.date == pd.to_datetime(target_date).date()]
        return filtered_df

    def get_past_dates(self, target_date,num_days):
        """
        Filters the user data by the last five days from the target date.

        Args:
        - target_date (str or datetime): Target date to retrieve the past five days from.

        Returns:
        - filtered_df: Pandas DataFrame containing the user data for the last five days from the target date.
        """
        target_date = pd.to_datetime(target_date).date()
        start_date = target_date - timedelta(days=num_days)
        end_date = target_date

        filtered_df = self.csv_file[(self.csv_file['Date'].dt.date >= start_date) & (self.csv_file['Date'].dt.date <= end_date)]
        return filtered_df
    def execute(self,target_date=TARGET_DATE,num_days=NUM_DAYS):
        self.get_user_data()
        habitica = self.get_past_dates(target_date,num_days).to_string()
        habits = habitica.replace('\n', ', ').split(', ')
        habits = [habit.split(' ', 1)[1].strip() for habit in habits]
        return habits

