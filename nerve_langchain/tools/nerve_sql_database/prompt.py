# flake8: noqa
QUERY_CHECKER = """
{query}
Double check the {dialect} query above for common mistakes, including:
- Using NOT IN with NULL values
- Using UNION when UNION ALL should have been used
- Using BETWEEN for exclusive ranges
- Data type mismatch in predicates
- Properly quoting identifiers
- Using the correct number of arguments for functions
- Casting to the correct data type
- Using the proper columns for joins

If there are any of the above mistakes, rewrite the query. If there are no mistakes, just reproduce the original query.

Output the final SQL query only.

SQL Query: """

CHART_DECISION = """
For the following query, decide which chart is the most appropriate.

If none of them are applicable, or a normal table would be suitable, just answer "Not applicable"

- table
- line plot
- vertical bar plot
- horizontal bar plot
- histogram
- boxplot
- Kernel Density Estimation plot
- area plot
- pie plot
- scatter plot
- hexbin plot

Example:

Query: What are the trends for investment for the last 10 years
Answer: line plot

Lets think step by step.

Query: {query}
"""