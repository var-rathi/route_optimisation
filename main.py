# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
# from ortools.constraint_solver import routing_enums_pb2
# from ortools.constraint_solver import pywrapcp
import os
import mysql.connector
import pandas as pd


# Press the green button in the gutter to run the script.
class data_loader_opsvone:
    def __init__(self):
        self.host="ops-solution.c44vbudlur4p.ap-south-1.rds.amazonaws.com"
        self.host="ops-solution.c44vbudlur4p.ap-south-1.rds.amazonaws.com"
        self.user="masteradmin"
        self.password="unorgopsdb123"
        self.database="opsvone"
        self.table="accounts_orderinfo"
    def connect_server(self):
        self.mydb = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
        )
        self.cursor = self.mydb.cursor()
    def close_connection(self):
        self.mydb.close()

    def data_columns(self,columns=['invoice_number','time_slot', 'location_coordinates', 'weight', 'updated_at']):
        self.columns=columns
        if len(columns)==0:
            return "*"
        else:
            return ", ".join(columns)
    def select_dates(self):
        self.connect_server()
        sql_command="select  CAST(updated_at AS DATE) as date,count(invoice_number) as invoice_counts from {} where is_coordinate=1 group by date".format(self.table)
        self.cursor.execute(sql_command)
        df = pd.DataFrame(self.cursor.fetchall(), columns=['dates','invoice_counts'])
        self.close_connection()
        return df
    def select_slots(self,dates):
        self.connect_server()
        sql_command='select  time_slot,count(invoice_number)  from {} where is_coordinate=1 and CAST(updated_at AS DATE)  IN("{}") group by time_slot'.format(self.table,'","'.join(dates))

        self.cursor.execute(sql_command)
        df = pd.DataFrame(self.cursor.fetchall(), columns=['time_slot','invoice_count'])
        self.close_connection()
        return df
    def load_data(self,dates,time_slots):
        self.connect_server()
        sql_command='select {} from {} where is_coordinate=1 and CAST(updated_at AS DATE)  IN("{}") and time_slot IN("{}")'.format(self.data_columns(),self.table,'","'.join(dates),'","'.join(time_slots))
        print(sql_command)
        self.cursor.execute(sql_command)
        df = pd.DataFrame(self.cursor.fetchall(),columns=self.columns)
        self.close_connection()
        return df
if __name__ == '__main__':
    data_loader=data_loader_opsvone()
    # print(data_loader.select_dates())
    # print(data_loader.select_slots(['2023-02-01','2023-02-02']))
    print(data_loader.load_data(['2023-02-01', '2023-02-02'],['5:31 PM to 8:30 PM','5:31 PM to 8:30 PM']))
    # print(os.getcwd())
    # mydb = mysql.connector.connect(
    #     host="ops-solution.c44vbudlur4p.ap-south-1.rds.amazonaws.com",
    #     user="masteradmin",
    #     password="unorgopsdb123",
    #     database="opsvone"
    # )
    #
    # # Printing the connection object
    # cursor = mydb.cursor()
    # table_name = 'accounts_orderinfo'
    # columns = ['invoice_number','time_slot', 'location_coordinates', 'weight', 'updated_at']
    # sql_command = "select invoice_number,time_slot, location_coordinates,weight,updated_at from accounts_orderinfo where is_coordinate=1"
    # cursor.execute(sql_command)
    # df=pd.DataFrame(cursor.fetchall(),columns=columns)
    # mydb.close()
    # df['updated_at']=df['updated_at'].dt.date
    # orders_avg=df.groupby(['updated_at','time_slot']).agg({'invoice_number':'count'}).reset_index()
    # print(max(orders_avg['invoice_number']))
    # print(sum(orders_avg['invoice_number'])/len(orders_avg))
    # print(df.groupby('updated_at').agg({'invoice_number':'count'}))
    # print(df.location_coordinates)
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
