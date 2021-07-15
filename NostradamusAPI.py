import requests
import pandas as pd
from io import StringIO
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.options.display.max_rows


def get_data(data):
    data = requests.get(f'http://vianenflowers.nostradamus.nu/index2.php?option=com_webservices&controller=csv&method=hours.board.fetch&element={data}',
                        headers={ 'api-key': '>)nb2wfxem*hi2#i6nji?2?tr6u37*}?<_1ud}p]0[54' }
                        )
    data = StringIO(data.text)
    df = pd.read_csv(data)
    return df

def clean_df(df, state):
    if state == 'staff':
        df = df[['office_id', 'card_name', 'card_department']]
        print(df)
    elif state == 'departments':
        df = df.sort_values(by=['department_id'])
        print(df)

def main():
    staff_df = get_data('staff')
    departments_df = get_data('staff')

    clean_df(staff_df, 'staff')
    # clean_df(departments_df, 'departments')

    for column in staff_df.columns:
        print(column)
    print(departments_df)
    for column in departments_df.columns:
        print(column)

if __name__ == "__main__":
    main()