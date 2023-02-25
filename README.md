# Transaction Log App

1 install packages

2 cp .env

3 create db

4 run app

# Requirements

- As a user I want to be able to login and see the transactions, listed from most recent to least recent.
- As a user I can return my balance as a mathematical result of the executed transactions.
- As a user I want to be able to list the transactions in a range of dates.
- As a user I want to be able to list the transactions by type
- As a user I want to be able to filter the expenses by merchant.

System Requirements

- You must ensure that a user cannot see the transactions of other users
- There are three types of transactions in this simple system which are deposits, withdrawals and expenses.
- The results of the transactions must be paged being the page size passed as a query parameter, if no parameter present then assume 10 as page size
- You cannot withdraw/waste more money than the account has, therefore negative balances are not allowed.
- If a transaction results in a negative balance, it must be rejected.
- Validate that the date ranges make sense for the transaction filter.

# Clarification

You may think that there is a big system involved to solve this problem but the reality is that we want to load the list of transactions automatically so you can choose and design the loading method. (hint: seeds, cvs, txt, json, yaml). That is, given a user who registered in the system, choose a transaction loading method. We will not build the CRUD of these transactions, we only need to list them following the requirements expressed above (with a REST API).
