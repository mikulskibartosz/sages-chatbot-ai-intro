import sqlite3
import pandas as pd
from langchain.agents import Tool


DATA_SOURCE = "https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv"

DB_DESCRIPTION = """
* "survivors" Table:
Columns:
PassengerId: A unique identifier for each passenger.
Survived: Indicates whether the passenger survived the sinking of the Titanic (typically coded as 1 for survived and 0 for did not survive).

* "tickets" Table:
Columns:
PassengerId: A unique identifier for each passenger, linking to the survivors table.
Ticket: The ticket number associated with each passenger.
Pclass: The passenger class; reflects the socio-economic status of the passenger (values: 1, 2, 3).
Fare: The amount of money paid for the ticket.
Cabin: The cabin number where the passenger stayed.
Embarked: The port at which the passenger embarked (C = Cherbourg; Q = Queenstown; S = Southampton).

* "passengers" Table:
Columns:
PassengerId: A unique identifier for each passenger, linking to the survivors table.
Name: The full name of the passenger.
Sex: The gender of the passenger.
Age: The age of the passenger at the time of the Titanic's voyage."""


class Tools:
    def __init__(self):
        df = pd.read_csv(DATA_SOURCE)
        survivors = df[['PassengerId', 'Survived']]
        tickets = df[['PassengerId', 'Ticket', 'Pclass', 'Fare', 'Cabin', 'Embarked']]
        passengers = df[['PassengerId', 'Name', 'Sex', 'Age']]

        con = sqlite3.connect('../titanic.db')
        survivors.to_sql('survivors', con, if_exists='replace')
        tickets.to_sql('tickets', con, if_exists='replace')
        passengers.to_sql('passengers', con, if_exists='replace')

    def run_query(self, sql_query):
        con = sqlite3.connect('../titanic.db')
        try:
            response = pd.read_sql_query(sql_query, con)
            return response.to_markdown()
        finally:
            con.close()

    def as_tool(self):
        return Tool(
            name="ask_db",
            func=self.run_query,
            description=DB_DESCRIPTION
        )
