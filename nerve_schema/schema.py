schema = [
    {
        "table_name": "vw_genbi_seabury_cargo",
        "foreign_keys": [],
        "primary_keys": [
            "trade_reported_month",
            "product_type_hs6_cd",
            "trade_origin_country_derived_name",
            "trade_destination_country_derived_name"
        ],
        "sample_queries": [
            {
                "question": "What are the top 5 countries that traded with Singapore in 2022",
                "answer": "SELECT country_name, SUM(import_value) as import_value, SUM(export_value) as export_value, SUM(import_value + export_value) as total_value FROM (SELECT trade_origin_country_derived_name as country_name, product_total_value_amount as import_value, 0 as export_value FROM vw_genbi_seabury_cargo WHERE trade_destination_country_iso_3_abbr = 'SGP' AND LEFT(trade_reported_month,4) = '2022' UNION ALL SELECT trade_destination_country_derived_name as country_name, 0 as import_value, product_total_value_amount as export_value FROM vw_genbi_seabury_cargo WHERE trade_origin_country_iso_3_abbr = 'SGP' AND LEFT(trade_reported_month,4) = '2022') raw GROUP BY country_name ORDER BY total_value DESC LIMIT 5"
            }
        ],
        "description": "Global Trade (HS6) by Country - Seabury.",
        "columns": [
            "trade_reported_month",
            "product_type_hs6_code",
            "trade_origin_country_derived_name",
            "trade_destination_country_derived_name",
            "trade_origin_country_iso_3_code",
            "trade_destination_country_iso_3_code",
            "product_type_hs2_cd",
            "product_type_hs4_cd",
            "product_type_hs6_desc",
            "product_type_hs4_desc",
            "product_type_hs2_desc",
            "product_sea_weight",
            "product_sea_value_amount",
            "product_air_weight",
            "product_air_value_amount",
            "product_surface_weight",
            "product_surface_value_amount",
            "product_total_weight",
            "product_total_value_amount"
        ],
        "column_types": [
            "DATE",
            "STRING",
            "STRING",
            "STRING",
            "STRING",
            "STRING",
            "STRING",
            "STRING",
            "STRING",
            "STRING",
            "STRING",
            "DOUBLE",
            "DOUBLE",
            "DOUBLE",
            "DOUBLE",
            "DOUBLE",
            "DOUBLE",
            "DOUBLE",
            "DOUBLE"
        ],
        "column_samples": [
            [
                "2018-04-01",
                "010612",
                "Japan",
                "China",
                "JPN",
                "CHN",
                "01",
                "0106",
                "LIVE WHALES DOLPHINS PORPOISES MANATEES DUGONGS SEALS SEA LIONS & WALRUSES",
                "OTHER LIVE ANIMALS",
                "LIVE ANIMALS",
                "0.0",
                "0.0",
                "638.135",
                "553233.006",
                "0.0",
                "0.0",
                "638.135",
                "553233.006"
            ],
            [
                "2018-04-01",
                "010612",
                "Russian Federation",
                "China",
                "RUS",
                "CHN",
                "01",
                "0106",
                "LIVE WHALES DOLPHINS PORPOISES MANATEES DUGONGS SEALS SEA LIONS & WALRUSES",
                "OTHER LIVE ANIMALS",
                "LIVE ANIMALS",
                "0.0",
                "0.0",
                "2000.0",
                "440000.0",
                "0.0",
                "0.0",
                "2000.0",
                "440000.0"
            ],
            [
                "2018-04-01",
                "010612",
                "South Korea",
                "China",
                "KOR",
                "CHN",
                "01",
                "0106",
                "LIVE WHALES DOLPHINS PORPOISES MANATEES DUGONGS SEALS SEA LIONS & WALRUSES",
                "OTHER LIVE ANIMALS",
                "LIVE ANIMALS",
                "0.0",
                "0.0",
                "250.0",
                "247500.0",
                "0.0",
                "0.0",
                "250.0",
                "247500.0"
            ]
        ]
    },
    {
        "table_name": "vw_ref_product",
        "foreign_keys": [],
        "primary_keys": [
            "product_type_hs6_cd"
        ],
        "sample_queries": [],
        "description": "Harmonized System (HS) nomenclature, is used worldwide for the uniform classification of goods traded internationally. Each row consists of their unique HS6 Code and description, and their corresponding HS4 and HS2 Codes and their description which is a superset of their HS6 classification.",
        "columns": [
            "product_type_hs2_cd",
            "product_type_hs4_cd",
            "product_type_hs6_cd",
            "product_type_hs2_desc",
            "product_type_hs4_desc",
            "product_type_hs6_desc"
        ],
        "column_types": [
            "STRING",
            "STRING",
            "STRING",
            "STRING",
            "STRING",
            "STRING"
        ],
        "column_samples": [
            [
                "01",
                "0101",
                "010121",
                "LIVE ANIMALS",
                "LIVE HORSES ASSES MULES & HINNIES",
                "PURE BRED BREEDING HORSES"
            ],
            [
                "01",
                "0101",
                "010129",
                "LIVE ANIMALS",
                "LIVE HORSES ASSES MULES & HINNIES",
                "OTHER LIVE HORSES"
            ],
            [
                "01",
                "0101",
                "010130",
                "LIVE ANIMALS",
                "LIVE HORSES ASSES MULES & HINNIES",
                "LIVE ASSES"
            ]
        ]
    }
]