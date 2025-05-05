from flask import Flask, render_template, request
import pyodbc
import pandas as pd

app = Flask(__name__)

# Configuration de la connexion SQL Server
DATABASE_CONFIG = {
    'server': '10.8.15.162',
    'database': 'Dashboard_PM',
    'driver': 'ODBC Driver 17 for SQL Server'
}

# Liste des opérateurs à afficher
DISPLAYED_OPERATORS = [
    'FIXE EXPRESSO', 'FIXE FREE', 'FIXE HAYO', 'FIXE SONATEL',
    'MSP-GREEN NUMBER', 'MSP-KIOSQUE',
    'MSP-NUMERO COURT DZ Et Services Clients V1', 'MSP-NUMERO COURT DZ Et Services Clients',
    'ORANGE', 'PROMOBILE', 'FREE', 'HAYO', 'ETRANGER', 'EXPRESSO',
    '17', '18', '118', '112', '119'
]


def get_connection():
    """Établit la connexion avec SQL Server."""
    conn_str = f"DRIVER={{{DATABASE_CONFIG['driver']}}};SERVER={DATABASE_CONFIG['server']};DATABASE={DATABASE_CONFIG['database']};Trusted_Connection=yes;"
    return pyodbc.connect(conn_str)


def get_data(operators=None, date_start=None, date_end=None):
    """Récupère les données avec un filtre sur l'opérateur et les dates."""
    conn = get_connection()
    query = """
        SELECT [DATE], [type_appel], [SERVICE], [dest_appel], [OPERATEUR],
               CAST([volume] AS INT) AS volume, 
               CAST(REPLACE([DURATION], ',', '.') AS FLOAT) AS [DURATION]
        FROM [Dashboard_PM].[dbo].[voix_sms]
        WHERE [OPERATEUR] IN ('FIXE EXPRESSO', 'FIXE FREE', 'FIXE HAYO', 'FIXE SONATEL',
                              'MSP-GREEN NUMBER', 'MSP-KIOSQUE',
                              'MSP-NUMERO COURT DZ Et Services Clients V1', 
                              'MSP-NUMERO COURT DZ Et Services Clients', 'ORANGE', 
                              'PROMOBILE', 'FREE', 'HAYO', 'ETRANGER', 'EXPRESSO', 
                              '17', '18', '118', '112', '119')
    """

    if operators and 'ALL' not in operators:
        query += f" AND [OPERATEUR] IN ({', '.join([f"'{op}'" for op in operators])})"

    # Filtrer les dates si spécifié
    if date_start:
        query += f" AND [DATE] >= '{date_start}'"
    if date_end:
        query += f" AND [DATE] <= '{date_end}'"

    query += " ORDER BY [DATE]"

    df = pd.read_sql(query, conn)
    conn.close()

    # Agréger les données
    df_aggregated = df.groupby(['DATE', 'type_appel', 'SERVICE', 'dest_appel', 'OPERATEUR']).agg(
        volume=('volume', 'sum'),
        DURATION=('DURATION', 'sum')
    ).reset_index()

    return df_aggregated


def get_operators():
    """Récupère la liste des opérateurs à afficher (uniquement ceux spécifiés)."""
    return DISPLAYED_OPERATORS


@app.route('/', methods=['GET'])
def index():
    selected_operators = request.args.getlist('operateur')
    date_start = request.args.get('date_start')
    date_end = request.args.get('date_end')

    # Récupérer les données avec les filtres appliqués
    df = get_data(selected_operators, date_start, date_end)

    operators = get_operators()

    # Calculs des métriques pour le dashboard
    total_volume = df['volume'].sum()
    total_duration = df['DURATION'].sum()

    return render_template('index.html',
                           tables=df.to_html(classes='table table-striped', index=False, escape=False),
                           operators=operators,
                           selected_operators=selected_operators,
                           total_volume=total_volume,
                           total_duration=total_duration,
                           date_start=date_start,
                           date_end=date_end)


if __name__ == '__main__':
    app.run(debug=True)
