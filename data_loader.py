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
    def list_dates(self):
        self.connect_server()
        sql_command="select  CAST(updated_at AS DATE) as date,count(invoice_number) as invoice_counts from {} where is_coordinate=1 group by date".format(self.table)
        self.cursor.execute(sql_command)
        df = pd.DataFrame(self.cursor.fetchall(), columns=['dates','invoice_counts'])
        self.close_connection()
        return df
    def list_slots(self,dates):
        self.connect_server()
        sql_command='select  time_slot,count(invoice_number)  from {} where is_coordinate=1 and CAST(updated_at AS DATE)  IN("{}") group by time_slot'.format(self.table,'","'.join(dates))

        self.cursor.execute(sql_command)
        df = pd.DataFrame(self.cursor.fetchall(), columns=['time_slot','invoice_count'])
        self.close_connection()
        return df
    def load_data(self,dates,time_slots):
        self.connect_server()
        if len(time_slots)==0:
            sql_command = 'select {} from {} where is_coordinate=1 and CAST(updated_at AS DATE)  IN("{}") '.format(
                self.data_columns(), self.table, '","'.join(dates))
        else:
            sql_command='select {} from {} where is_coordinate=1 and CAST(updated_at AS DATE)  IN("{}") and time_slot IN("{}")'.format(self.data_columns(),self.table,'","'.join(dates),'","'.join(time_slots))
        print(sql_command)
        self.cursor.execute(sql_command)
        df = pd.DataFrame(self.cursor.fetchall(),columns=self.columns)
        self.close_connection()
        return df