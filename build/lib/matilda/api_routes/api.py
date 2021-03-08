# import distutils
# from collections import Callable
# from distutils import util
# from datetime import datetime, timedelta
# from functools import partial
#
# from flask import request, jsonify, Blueprint
#
# # import fundamental_analysis.accounting_ratios as ratios
#
#
# def parse_request(fun: Callable, request):
#     if 'stock' not in request.args:
#         return 'Error: No stock ticker provided. Please specify.'
#     stock = request.args['stock']
#     date = datetime.strptime(request.args['date'], '%d/%m/%y') if 'date' in request.args else datetime.now()
#     lookback_period = timedelta(
#         days=int(request.args['lookback_period'])) if 'lookback_period' in request.args else timedelta(days=0)
#     annual = distutils.util.strtobool(request.args['annual']) if 'annual' in request.args else True
#     ttm = distutils.util.strtobool(request.args['ttm']) if 'ttm' in request.args else True
#     return partial(fun, stock=stock, date=date, lookback_period=lookback_period, annual=annual, ttm=ttm)
#
#
# '''
# Income Statement Items
# '''
#
# '''
# Balance Sheet Items
# '''
#
# '''
# Cash Flow Statement Items
# '''
#
# '''
# Liquidity Ratios
# '''
#
#
# @app.route('/data/fundamental_data/accounting_ratios/current_ratio', methods=['GET'])
# def current_ratio():
#     return jsonify(parse_request(fun=ratios.current_ratio, request=request)())
#
#
# @app.route('/data/fundamental_data/accounting_ratios/acid_test_ratio', methods=['GET'])
# def acid_test_ratio():
#     return jsonify(parse_request(fun=ratios.acid_test_ratio, request=request)())
#
#
# @app.route('/data/fundamental_data/accounting_ratios/cash_ratio', methods=['GET'])
# def cash_ratio():
#     return jsonify(parse_request(fun=ratios.cash_ratio, request=request)())
#
#
# @app.route('/data/fundamental_data/accounting_ratios/operating_cash_flow_ratio', methods=['GET'])
# def operating_cash_flow_ratio():
#     return jsonify(parse_request(fun=ratios.operating_cash_flow_ratio, request=request)())
#
#
# '''
# Leverage Ratios
# '''
#
#
# @app.route('/data/fundamental_data/accounting_ratios/debt_to_assets', methods=['GET'])
# def debt_to_assets():
#     return jsonify(parse_request(fun=ratios.debt_to_assets, request=request)())
#
#
# @app.route('/data/fundamental_data/accounting_ratios/asset_to_equity', methods=['GET'])
# def asset_to_equity():
#     return jsonify(parse_request(fun=ratios.asset_to_equity, request=request)())
#
#
# @app.route('/data/fundamental_data/accounting_ratios/debt_to_equity', methods=['GET'])
# def debt_to_equity():
#     return jsonify(parse_request(fun=ratios.debt_to_equity, request=request)())
#
#
# @app.route('/data/fundamental_data/accounting_ratios/debt_to_capital', methods=['GET'])
# def debt_to_capital():
#     return jsonify(parse_request(fun=ratios.debt_to_capital, request=request)())
#
#
# @app.route('/data/fundamental_data/accounting_ratios/interest_coverage_ratio', methods=['GET'])
# def interest_coverage_ratio():
#     return jsonify(parse_request(fun=ratios.interest_coverage, request=request)())
#
#
# @app.route('/data/fundamental_data/accounting_ratios/debt_service_coverage', methods=['GET'])
# def debt_service_coverage():
#     return jsonify(parse_request(fun=ratios.debt_service_coverage, request=request)())
#
#
# '''
# Efficiency Ratios
# '''
#
#
# @app.route('/data/fundamental_data/accounting_ratios/asset_turnover_ratio', methods=['GET'])
# def asset_turnover_ratio():
#     return jsonify(parse_request(fun=ratios.asset_turnover_ratio, request=request)())
#
#
# @app.route('/data/fundamental_data/accounting_ratios/inventory_turnover_ratio', methods=['GET'])
# def inventory_turnover_ratio():
#     return jsonify(parse_request(fun=ratios.inventory_turnover_ratio, request=request)())
#
#
# @app.route('/data/fundamental_data/accounting_ratios/receivables_turnover_ratio', methods=['GET'])
# def receivables_turnover_ratio():
#     return jsonify(parse_request(fun=ratios.receivables_turnover_ratio, request=request)())
#
#
# @app.route('/data/fundamental_data/accounting_ratios/days_sales_in_inventory_ratio', methods=['GET'])
# def days_sales_in_inventory_ratio():
#     return jsonify(parse_request(fun=ratios.days_sales_in_inventory_ratio, request=request)())
#
#
# @app.route('/data/fundamental_data/accounting_ratios/return_on_capital', methods=['GET'])
# def return_on_capital():
#     return jsonify(parse_request(fun=ratios.return_on_capital, request=request)())
#
#
# @app.route('/data/fundamental_data/accounting_ratios/retention_ratio', methods=['GET'])
# def retention_ratio():
#     return jsonify(parse_request(fun=ratios.retention_ratio, request=request)())
#
#
# '''
# Profitability Ratios
# '''
#
#
# @app.route('/data/fundamental_data/accounting_ratios/profit_margin', methods=['GET'])
# def profit_margin():
#     return jsonify(parse_request(fun=ratios.profit_margin, request=request)())
#
#
# @app.route('/data/fundamental_data/accounting_ratios/gross_profit_margin', methods=['GET'])
# def gross_profit_margin():
#     return jsonify(parse_request(fun=ratios.gross_profit_margin, request=request)())
#
#
# @app.route('/data/fundamental_data/accounting_ratios/operating_profit_margin', methods=['GET'])
# def operating_profit_margin():
#     return jsonify(parse_request(fun=ratios.operating_profit_margin, request=request)())
#
#
# @app.route('/data/fundamental_data/accounting_ratios/return_on_assets', methods=['GET'])
# def return_on_assets():
#     return jsonify(parse_request(fun=ratios.return_on_assets, request=request)())
#
#
# @app.route('/data/fundamental_data/accounting_ratios/return_on_equity', methods=['GET'])
# def return_on_equity():
#     return jsonify(parse_request(fun=ratios.return_on_equity, request=request)())
#
#
# '''
# Market Value Ratios
# '''
#
#
# @app.route('/data/fundamental_data/accounting_ratios/book_value_per_share', methods=['GET'])
# def book_value_per_share():
#     return jsonify(parse_request(fun=ratios.book_value_per_share, request=request)())
#
#
# @app.route('/data/fundamental_data/accounting_ratios/earnings_per_share', methods=['GET'])
# def earnings_per_share():
#     return jsonify(parse_request(fun=ratios.earnings_per_share, request=request)())
#
#
# @app.route('/data/fundamental_data/accounting_ratios/price_to_earnings', methods=['GET'])
# def price_to_earnings():
#     return jsonify(parse_request(fun=ratios.price_to_earnings, request=request)())
#
#
# @app.route('/data/fundamental_data/accounting_ratios/price_to_earnings_to_growth', methods=['GET'])
# def price_to_earnings_to_growth():
#     return jsonify(parse_request(fun=ratios.price_to_earnings_to_growth, request=request)())
#
#
# @app.route('/data/fundamental_data/accounting_ratios/earnings_yield', methods=['GET'])
# def earnings_yield():
#     return jsonify(parse_request(fun=ratios.earnings_yield, request=request)())
#
#
# @app.route('/data/fundamental_data/accounting_ratios/adjusted_earnings_yield', methods=['GET'])
# def adjusted_earnings_yield():
#     return jsonify(parse_request(fun=ratios.adjusted_earnings_yield, request=request)())
#
#
# @app.route('/data/fundamental_data/accounting_ratios/greenblatt_earnings_yield', methods=['GET'])
# def greenblatt_earnings_yield():
#     return jsonify(parse_request(fun=ratios.greenblatt_earnings_yield, request=request)())
