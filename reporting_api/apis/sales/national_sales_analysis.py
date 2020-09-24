import datetime
import re
from collections import Counter
import pandas as pd
from dateutil.relativedelta import relativedelta

from eggit.flask_restful_response import ok
from flask_restful import Resource
from sqlalchemy import func, extract

from reporting_api.utils.requests_utils import get_argument
from reporting_api.models.sales_models.sales_analysis_report import SalesAnalysisReportModel
from reporting_api.utils.response_utils import obj_to_dict
from reporting_api.utils.sales_report_utils import monthly_sales


class NationalSalesAnalysis(Resource):
    def get(self):
        start_time = get_argument('start_time', default='2019-09-01')
        end_time = get_argument('end_time', default='2019-09-21')

        user = SalesAnalysisReportModel.query

        if all([start_time, end_time]):
            user = user.filter(SalesAnalysisReportModel.ord_pay_time.between(start_time, end_time))

        ord_sitecode = ['US', 'EU', 'IN', 'JP', 'CAN']

        user = user.filter(SalesAnalysisReportModel.ord_sitecode.in_(ord_sitecode)).all()

        data = []
        tmp = []

        for item in user:
            arg = obj_to_dict(item, [''], display=False, format_time='%Y-%m-%d')
            pay_date = arg['ord_pay_time']
            ord_sale_amount = arg['ord_sale_amount']
            sitecode = arg['ord_sitecode']

            args = {
                'date': pay_date,
                f'ord_sale_amount_{sitecode}': ord_sale_amount,
                f'ord_salenum_{sitecode}': arg['ord_salenum'],
                f'ord_maoli_{sitecode}': arg['ord_maoli']
            }
            for k, v in args.items():
                if not args[k]:
                    args[k] = 0
            if pay_date not in tmp:
                tmp.append(pay_date)
                data.append(args)
            if f'ord_sale_amount{sitecode}' not in data[tmp.index(pay_date)]:
                data[tmp.index(pay_date)].update(args)

            else:
                data[tmp.index(pay_date)].update({
                    f'ord_sale_amount_{sitecode}': round(args['ord_sale_amount_' + sitecode] + data[tmp.index(pay_date)][
                        'ord_sale_amount_' + sitecode],2),
                    f'ord_salenum_{sitecode}': args['ord_salenum_' + sitecode] + data[tmp.index(pay_date)][
                        'ord_salenum_' + sitecode],
                    f'ord_maoli_{sitecode}': args['ord_maoli_' + sitecode] + data[tmp.index(pay_date)][
                        'ord_maoli_' + sitecode],
                })
        tmp_dic = {}
        if not data:
            return ok(data={'data': []})

        for dic in data:
            dic['ord_sale_amount_Global'] = round(
                sum([v for k, v in dic.items() if k.startswith('ord_sale_amount_') and v]), 2)
            dic['ord_salenum_Global'] = sum([v for k, v in dic.items() if k.startswith('ord_salenum_') and v])
            dic['ord_maili_Global'] = round(sum([v for k, v in dic.items() if k.startswith('ord_maoli_') and v]), 2)
            dic['ord_maoli_rate_Global'] = round(
                sum([v for k, v in dic.items() if k.startswith('ord_maoli_') and v]) / dic[
                    'ord_sale_amount_Global'] if dic['ord_sale_amount_Global'] else 0, 4)

        total_dic = {}
        for dic in data:
            for sitecode in ord_sitecode:
                if f'ord_salenum_{sitecode}' in dic.keys():  # ord_maoli /  ord_sale_amount
                    dic.update({
                        f'ord_maoli_rate_{sitecode}': round(dic.get(f'ord_maoli_{sitecode}', 0) /
                                                            dic[f'ord_sale_amount_{sitecode}'] if dic[
                            f'ord_sale_amount_{sitecode}'] else 0, 4),
                        f'market_share_{sitecode}': round(dic[f'ord_sale_amount_{sitecode}'] /
                                                          dic['ord_sale_amount_Global'] if dic[
                            'ord_sale_amount_Global'] else 0, 4)
                    })
                    total_dic.update({
                        f'total_ord_sale_amount_{sitecode}': round(dic.get(f'ord_sale_amount_{sitecode}', 0) +
                                                                   total_dic.get(f'total_ord_sale_amount_{sitecode}',
                                                                                 0), 2),
                        f'total_ord_salenum_{sitecode}': dic.get(f'ord_salenum_{sitecode}', 0) +
                                                         total_dic.get(f'total_ord_salenum_{sitecode}', 0),
                        f'total_ord_maoli_{sitecode}': dic.get(f'ord_maoli_{sitecode}', 0) +
                                                       total_dic.get(f'total_ord_maoli_{sitecode}', 0),
                    })

        total_dic['total_ord_salenum_Global'] = sum(
            [v for k, v in total_dic.items() if k.startswith('total_ord_salenum_') and v])
        total_dic['total_ord_sale_amount_Global'] = sum([v for k, v in total_dic.items() if
                                                         k.startswith('total_ord_sale_amount_') and v])
        total_dic['total_ord_maoli_Global'] = sum([v for k, v in total_dic.items() if
                                                   k.startswith('total_ord_maoli_') and v])
        total_dic['total_ord_maoli_rate_Global'] = round(total_dic['total_ord_maoli_Global'] / \
                                                         total_dic['total_ord_sale_amount_Global'], 2)

        for sitecode in ord_sitecode:
            if f'total_ord_salenum_{sitecode}' in total_dic.keys():
                total_dic[f'total_ord_maoli_rate_{sitecode}'] = round((
                        total_dic.get(f'total_ord_maoli_{sitecode}', 0) / total_dic.get(
                    f'total_ord_sale_amount_{sitecode}', 0)), 4)
                total_dic[f'total_market_share_{sitecode}'] = round(total_dic[f'total_ord_sale_amount_{sitecode}'] / \
                                                                    total_dic['total_ord_sale_amount_Global'], 4)
        return ok(data={'data': data, **total_dic})
