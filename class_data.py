import pandas as pd
import numpy as np

from utilities import *

class BACI():
    
    dict_industries = {"Agri_Food": [1, 24], "Mineral products": [25, 27], "Chemical": [28, 38],
                   "Plastic/Rubbers": [39, 40], "Raw Hide": [41, 43], "Wood Products": [44, 49],
                   "Textiles": [50, 63], "Footwears": [64, 71], "Base metal": [72, 83],
                   "Machinery/Elec. Equip": [84, 85], "Vehicle": [86, 89], "Optical/Photo. Instr.": [90, 92],
                   "Other": [93, 99]}
    
    eu28 = ["Austria", "Belgium-Luxembourg", "Bulgaria", "Croatia", "Cyprus", "Czechia",
            "Denmark", "Estonia", "Finland", "France", "Germany", "Greece",
            "Hungary", "Ireland", "Italy", "Latvia", "Lithuania", "Malta", "Netherlands",
            "Poland", "Portugal", "Romania", "Slovakia", "Slovenia", "Spain", "Sweden", "United Kingdom"]
    
    eu27 = ["Austria", "Belgium-Luxembourg", "Bulgaria", "Croatia", "Cyprus", "Czechia",
            "Denmark", "Estonia", "Finland", "France", "Germany", "Greece",
            "Hungary", "Ireland", "Italy", "Latvia", "Lithuania", "Malta", "Netherlands",
            "Poland", "Portugal", "Romania", "Slovakia", "Slovenia", "Spain", "Sweden"]
    
    def __init__(self, input, df_country_codes):
        self.data = input.copy()
        self.country_names = df_country_codes
        self.log = logs('BACI_dataframes', input)
    
    def info(self):
        print(self.data.dtypes)
        print(self.data.head())
        print(self.data.tail())
        print(self.data.shape)

    def adjust_columns(self):
        self.data = self.data.astype({'t': 'int32', 'i': 'str', 'j': 'str', 'k': 'str'})
        self.data.rename(columns = {'t': 'year', 'i': 'origin', 'j': 'destination', 'k': 'product_code', 'v': 'value', 'q': 'quantity'}, inplace = True)
        self.data['product_code'] = self.data['product_code'].apply(lambda x: '0' + x if len(x) < 6 else x)

    def match_country_codes(self, subscript):
        """Function to merge BACI dataset with country names, based on country codes.
        The country codes are matched for origin or destination, depending on value passed as argument.
        This function applies changes to the self.data dataframe.

        Args:
            subscript (str): This argument accepts only "origin" or "destination" as values.
        """
        self.data = self.data.merge(self.country_names, how = 'left', left_on = subscript, right_on = 'country_code')
        self.data.drop(columns = ['country_code', 'country_name_full', 'iso_2digit_alpha'], inplace = True)
        self.data.rename(columns = {'country_name_abbreviation': f'{subscript}_name', 'iso_3digit_alpha': f'{subscript}_iso3'}, inplace = True)

    def trade_flow_class(self, dict_filters):
        self.data['trade_flow'] = ''
        for arg in dict_filters:
            if 'origin' in arg:
                flow = 'Export'
            elif 'destination' in arg:
                flow = 'Import'
            self.data.at[self.data[arg] == dict_filters[arg], 'trade_flow'] = flow
    
    def slice_countries(self, subscript, dict_filters):
        col_names = list(dict_filters.keys())
        try:
            if subscript == "and":
                self.data = self.data[(self.data[col_names[0]] == dict_filters[col_names[0]]) & (self.data[col_names[1]] == dict_filters[col_names[1]])]
            elif subscript == "or":
                self.data = self.data[(self.data[col_names[0]] == dict_filters[col_names[0]]) | (self.data[col_names[1]] == dict_filters[col_names[1]])]
            else:
                self.data = self.data[self.data[col_names[0]] == dict_filters[col_names[0]]]
        except Exception as e:
            self.log.info(f'{e}')
    
    def total_flow(self):
        raw_df = self.data.copy()
        temp_df = raw_df.copy()
        temp_df = temp_df.groupby(['year', 'origin_name', 'destination_name'], as_index = False).agg({"value": "sum", "origin": "first", "destination": "first",
                                                                                                      "quantity": "sum", "origin_iso3": "first", "destination_iso3": "first", "trade_flow": "first"})
        temp_df['product_code'] = 'total'
        temp_df['chapters'] = ''
        temp_df['industry'] = ''
        self.data = self.data.append(temp_df, ignore_index = True)
        temp_df = raw_df.copy()
        temp_df = temp_df.groupby(['year', 'origin_name', 'destination_name', 'chapters'], as_index = False).agg({"value": "sum", "origin": "first", "destination": "first",
                                                                                                      "quantity": "sum", "origin_iso3": "first", "destination_iso3": "first", "trade_flow": "first"})
        temp_df['product_code'] = temp_df['chapters']
        temp_df['industry'] = ''
        self.data = self.data.append(temp_df, ignore_index = True)
        temp_df = raw_df.copy()
        temp_df = temp_df.groupby(['year', 'origin_name', 'destination_name', 'industry'], as_index = False).agg({"value": "sum", "origin": "first", "destination": "first",
                                                                                                      "quantity": "sum", "origin_iso3": "first", "destination_iso3": "first", "trade_flow": "first"})
        temp_df['product_code'] = temp_df['industry']
        temp_df['chapters'] = ''
        self.data = self.data.append(temp_df, ignore_index = True)
    
    def aggregate_country(self, country_list, country_name, country_code):
        temp_df = self.data.copy()
        temp_df = temp_df[(temp_df['origin_name'].isin(country_list)) | (temp_df['destination_name'].isin(country_list))]
        temp_df = temp_df.groupby(['year', 'product_code', 'trade_flow'], as_index = False).agg({"value": "sum", "origin": "first", "destination": "first", "destination_name": 'first', "origin_name": 'first',
                                                                                                    "quantity": "sum", "origin_iso3": "first", "destination_iso3": "first", "trade_flow": "first"})
        for flow in [("Import", "origin"), ("Export", "destination")]:
            temp_df.at[temp_df["trade_flow"] == flow[0], f"{flow[1]}_name"] = country_name
            temp_df.at[temp_df["trade_flow"] == flow[0], f"{flow[1]}"] = country_code
            temp_df.at[temp_df["trade_flow"] == flow[0], f"{flow[1]}_iso3"] = country_name
        self.data = self.data.append(temp_df, ignore_index = True)
    
    @staticmethod
    def match_industry(row, dictionary):
        for industry, chapter in dictionary.items():
            if row["chapters"] >= chapter[0] and row["chapters"] <= chapter[1]:
                row["industry"] = industry
        return row
    
    def industry_classification(self):
        self.data["chapters"] = self.data["product_code"].str[:2]
        self.data = self.data.astype({'chapters': 'int32'})
        self.data["industry"] = ""
        self.data = self.data.apply(BACI.match_industry, dictionary = BACI.dict_industries, axis = 1)
        