# coding=utf-8
import pandas as p
import config as conf
import pyodbc as db
import os
import logging as logger
import persondatabase_repository as repo
from datetime import datetime
import numpy as np


# set up file logger
logger.basicConfig(level=logger.INFO, filename='ExcelETL.log'
                   , format='[%(asctime)s] %(levelname)s - %(lineno)s %(message)s', datefmt='%m/%d/%y - %H:%M:%S')
# set up console logger for debugging
console = logger.StreamHandler()
console.setLevel(logger.DEBUG)
console.setFormatter(logger.Formatter('[%(asctime)s] %(levelname)s - %(lineno)s %(message)s', datefmt='%m/%d/%y - %H:%M:%S'))
# add the handler to the root logger
logger.getLogger('').addHandler(console)


def execute_excel_etl():
    """
    Main script to etl all excel files deposited in a given (config file) directory
    """
    connection_path = 'Driver={driver};Server={server};Database={db};UID={user};Trusted_Connection=yes;'.format(
        driver=conf.sql_server['driver'], server=conf.sql_server['server'], db=conf.sql_server['db'],
        user=conf.sql_server['user'])
    conn = db.connect(connection_path)
    cursor = conn.cursor()
    try:
        logger.info('creating destination tables if they do not exist')
        cursor.execute(repo.createTablesForImport)
        conn.commit()

        loop_files(conf.files_location, cursor)
    except Exception as e:
        logger.info(e)
    finally:
        logger.info('closing connection')
        cursor.close()
        conn.close()


def loop_files(filepath, cursor):
    """
    get excel files to read
    :param cursor:
    :param filepath:str
    :return:
    """
    for filename in os.listdir(filepath):
        if filename.endswith('.xls') or filename.endswith('xlsx'):
            logger.info('--------------------------------------------------------')
            logger.info('loading file {}'.format(filename))
            provider_name, file_date = name_logic(filename)

            raw_data = p.read_excel(filepath + '\\' + filename, skiprows=3, skipfooter=3)
            logger.info('transform demographics')
            demographic_data = demographics(raw_data)

            logger.info('insert demographics')
            for index, row in demographic_data.iterrows():
                cursor.execute(repo.insert_demographics.format(row['ID'], row['First Name'], row['Middle Name']
                                                               , row['Last Name'], row['DOB[1]'], row['Sex']
                                                               , row['Favorite Color'], provider_name, file_date))
                cursor.commit()

            logger.info('transform quarters and risk')
            merged = risk_quarters(raw_data)

            logger.info('insert quarters and risk')
            for index, row in merged.iterrows():
                cursor.execute(repo.insert_riskquarters.format(row['ID'], row['Quarter'], row['Attributed']
                                                               , row['RiskScore'], file_date))
                cursor.commit()
            logger.info('--------------------------------------------------------')
        else:
            continue


def demographics(raw_data):
    """
    read dataframe, pull demographic information, transform middle name and sex columns
    :param raw_data:dataframe
    :return:dataframe
    """
    demographic_data = p.DataFrame(raw_data, columns=['ID', 'First Name', 'Middle Name', 'Last Name', 'DOB[1]',
                                                      'Sex', 'Favorite Color'])

    demographic_data['Middle Name'] = demographic_data['Middle Name'].str[:1].replace({np.nan: ''})
    demographic_data['Sex'] = demographic_data['Sex'].map({0: 'M', 1: 'F'})
    return demographic_data


def risk_quarters(raw_data):
    """
    read dataframe, pull risk and quarters information, combine into single dataframe
    :param raw_data:dataframe
    :return:dataframe
    """
    quarters_risk_data = p.DataFrame(raw_data, columns=['ID', 'Attributed Q1', 'Attributed Q2', 'Risk Q1'
                                                        , 'Risk Q2 ', 'Risk Increased Flag'])

    quarters_risk_data.drop(quarters_risk_data[quarters_risk_data['Risk Increased Flag'] != 'Yes'].index
                            , inplace=True)
    quarters = quarters_risk_data[['ID', 'Attributed Q1', 'Attributed Q2']].melt(id_vars='ID'
                                                                                 , var_name='Quarter'
                                                                                 , value_name='Attributed')
    quarters['Quarter'] = quarters['Quarter'].map({'Attributed Q1': 'Q1', 'Attributed Q2': 'Q2'})

    risk = quarters_risk_data[['ID', 'Risk Q1', 'Risk Q2 ']].melt(id_vars='ID', var_name='Quarter'
                                                                  , value_name='RiskScore')
    risk['Quarter'] = risk['Quarter'].map({'Risk Q1': 'Q1', 'Risk Q2 ': 'Q2'})

    return quarters.merge(risk, on=['ID', 'Quarter'])


def name_logic(filename):
    """
    given a filename return provider and date
    :param filename: str
    :return:
    """
    remove_ext = os.path.splitext(filename)[0]
    date_str = remove_ext[len(remove_ext) - 6:]
    file_date = datetime.strptime(date_str, '%m%d%y').date()
    provider_name = remove_ext[:len(remove_ext) - 6].strip()
    return provider_name, file_date


if __name__ == '__main__':
    execute_excel_etl()
