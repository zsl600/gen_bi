schema = [
    {
        "dataset": "demo",
        "table_name": "t_demo_un_comtrade",
        "table_formal_name": "UN Comtrade Goods Trade",
        "foreign_keys": [
            "t_demo_un_comtrade.reporter_iso3_code = t_demo_country.country_iso3_code",
            "t_demo_un_comtrade.partner_iso3_code = t_demo_country.country_iso3_code"
        ],
        "primary_keys": [
            "reporter_iso3_code",
            "partner_iso3_code",
            "trade_flow",
            "year"
        ],
        "sample_queries": [
            {
                "question": "What is the total export between Singapore and Malaysia for the last 5 years in SGD?",
                "answer": "I will first get the results in terms of USD for the last 5 years, then get the currency code of Singapore (SGD), then get the yearly exchange rate between USD and SGD for the last 5 years, then convert the trade value to SGD as the final answer."
            },
            {
                "question": "What is the trade between Singapore and USA for 2021?",
                "answer": "SELECT SUM(trade_value_usd) WHERE reporter_iso3_code = 'SGP' AND partner_iso3_code = 'USA' WHERE year = 2021; Once I have the results in USD, I will convert them to SGD based on 2021 value."
            }
        ],
        "description": "This data can be useful for understanding trade patterns over time, identifying key trading partners, and analyzing the flow and value of goods between the different countries. Always filter by partner_iso3_code and reporter_iso3_code using the required countries' ISO 3166 Alpha-3 Code, IF NOT the country will NOT be FOUND IF acronyms ARE used.",
        "columns": [
            "reporter_country_name",
            "reporter_iso3_code",
            "partner_country_name",
            "partner_iso3_code",
            "trade_flow",
            "year",
            "trade_value_usd"
        ],
        "column_types": [
            "STRING",
            "STRING",
            "STRING",
            "STRING",
            "STRING",
            "STRING",
            "DOUBLE"
        ],
        "last_updated_date": "2023"
    },
    {
        "dataset": "demo",
        "table_name": "t_demo_country",
        "table_formal_name": "Countries",
        "foreign_keys": [],
        "primary_keys": [
            "country_iso3_code"
        ],
        "sample_queries": [],
        "description": "Dimension table of countries",
        "columns": [
            "country_name",
            "country_iso3_code",
            "country_iso2_code",
            "currency_name",
            "currency_alpha_code"
        ],
        "column_types": [
            "STRING",
            "STRING",
            "STRING",
            "STRING",
            "STRING"
        ],
        "last_updated_date": "2023"
    },
    {
        "dataset": "demo",
        "table_formal_name": "Exchange Rate",
        "table_name": "t_demo_currency_exchange_rate",
        "foreign_keys": [
            "t_demo_currency_exchange_rate.currency = t_demo_country.currency_alpha_code"
        ],
        "primary_keys": [
            "currency",
            "year"
        ],
        "sample_queries": [
            {
                "question": "How much SGD can I exchange for 100 MYR in 2022?",
                "answer": "SELECT 100/exchange_rate_to_one_sgd FROM t_demo_currency_exchange_rate WHERE year = 2022 AND currency = 'MYR'"
            }
        ],
        "description": "Average yearly exchange rate between different countries and Singapore in SGD",
        "columns": [
            "currency",
            "year",
            "exchange_rate_to_one_sgd"
        ],
        "column_types": [
            "STRING",
            "STRING",
            "DOUBLE"
        ],
        "last_updated_date": "2023"
    }
]