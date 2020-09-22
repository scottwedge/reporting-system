import datetime

import pandas as pd

from reporting_api.models.sales_models.sales_analysis_report import SalesAnalysisReportModel
from reporting_api.utils.response_utils import obj_to_dict


def time_range(start_time, end_time):
    start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d')
    end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d')
    day_list = []
    for i in range((end_time - start_time).days + 1):
        day = start_time + datetime.timedelta(days=i)
        day_list.append(day)
    return day_list


def time_range2(start_time, end_time):
    start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d')
    end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d')
    day_list = []
    for i in range((end_time - start_time).days + 1):
        day = start_time + datetime.timedelta(days=i)
        day_list.append(day.strftime('%Y-%m-%d'))
    return day_list


def monthly_sales(start_time, end_time):
    pr = pd.period_range(start=start_time, end=end_time, freq='M')
    prTupes = tuple([(period.month, period.year) for period in pr])

    month_date = []
    for prTupe in prTupes:
        date_time = str(prTupe[1]) + '-' + str(prTupe[0])
        if prTupe[0] < 10:
            date_time = str(prTupe[1]) + '-0' + str(prTupe[0])
        month_date.append(date_time)

    user = SalesAnalysisReportModel.query.filter(SalesAnalysisReportModel.yyyymm.in_(month_date)).all()

    data = []
    tmp = []
    total_ord_sale_amount = 0
    for item in user:
        arg = obj_to_dict(item, [''], display=False, format_time='%Y-%m-%d')
        source_code = arg['source_code']
        args = {
            'ord_salenum': arg['ord_salenum'],  # 销量
            'ord_sale_amount': arg['ord_sale_amount'],  # 销售额
            'source_code': arg['source_code'],
            'count': 1
        }
        for k, v in args.items():
            if not args[k]:
                args[k] = 0
        total_ord_sale_amount += args['ord_sale_amount']
        if source_code not in tmp:
            tmp.append(source_code)
            data.append(args)
            total_ord_sale_amount += args['ord_sale_amount']
        else:
            data[tmp.index(source_code)].update({
                'ord_salenum': args['ord_sale_amount'] + data[tmp.index(source_code)]['ord_sale_amount'],
                'ord_sale_amount': args['ord_salenum'] + data[tmp.index(source_code)]['ord_salenum'],
                'count': args['count'] + data[tmp.index(source_code)]['count'],
            })
        data[tmp.index(source_code)].update({'total_ord_sale_amount': total_ord_sale_amount})
    # data.append(total_ord_sale_amount)
    return data, tmp


def get_salenum_sale_amount(user):
    tmp = []
    data = []
    for item in user:
        arg = obj_to_dict(item, [''], display=False, format_time='%Y-%m-%d')
        source_code = arg['source_code']
        args = {
            'source_code': source_code,
            'ord_sale_amount': arg['ord_sale_amount'],
            'ord_salenum': arg['ord_salenum']
        }
        # BUG of None
        for k, v in args.items():
            if not args[k]:
                args[k] = 0
        if source_code not in tmp:
            tmp.append(source_code)
            data.append(args)
        else:
            data[tmp.index(source_code)].update({
                'ord_sale_amount': (data[tmp.index(source_code)]['ord_sale_amount'] + args['ord_sale_amount']),
                'ord_salenum': data[tmp.index(source_code)]['ord_salenum'] + args['ord_salenum'],
            })
    return data, tmp
