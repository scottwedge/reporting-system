"""
source_code 横向标题
ord_pay_time 付款日期
ord_sale_amount 销售额
ord_salenum 销量
ord_maoli 毛利率
"""
import datetime
from collections import Counter
import copy
from eggit.flask_restful_response import ok
from flask import jsonify
from flask_restful import Resource

from reporting_api.exceptions.service_error import ServiceError
from reporting_api.exceptions.service_exception import ServiceException
from reporting_api.models.sales_models.sales_analysis_report import SalesAnalysisReportModel
from reporting_api.utils.requests_utils import get_argument
from reporting_api.utils.response_utils import obj_to_dict
from reporting_api.utils.sales_report_utils import time_range, time_range2


class IndependentStationNationalSalesAnalysisPhoto(Resource):
    def get(self):
        start_time = get_argument('start_time', default='2020-09-01')
        end_time = get_argument('end_time', default='2020-09-20')

        if start_time > end_time:
            raise ServiceException(ServiceError.INVALID_VALUE)

        user = SalesAnalysisReportModel.query

        if all([start_time, end_time]):
            user = user.filter(SalesAnalysisReportModel.ord_pay_time.between(start_time, end_time))

        source_code = ['FlexispotUS', 'FleximountsUS', 'FlexiSpotUK', 'FlexiSpotDE', 'FlexiSpotFR', 'FlexiSpotJP',
                       'FleximountsJP']

        user = user.filter(SalesAnalysisReportModel.source_code.in_(source_code)).all()

        data = []
        tmp = []

        for item in user:
            arg = obj_to_dict(item, [''], display=False, format_time='%Y-%m-%d')
            pay_date = arg['ord_pay_time']
            ord_sale_amount = arg['ord_sale_amount']
            source = arg['source_code']
            args = {
                f'pay_date': pay_date,
                f'ord_sale_amount_{source}': ord_sale_amount,
                f'ord_maoli_{source}': arg['ord_maoli'],
                f'ord_salenum': arg['ord_salenum']
            }
            for k, v in args.items():
                if not args[k]:
                    args[k] = 0
            if pay_date not in tmp:
                tmp.append(pay_date)
                data.append(args)
            if f'ord_sale_amount{source}' not in data[tmp.index(pay_date)]:
                data[tmp.index(pay_date)].update(args)

            else:
                data[tmp.index(pay_date)].update({
                    f'ord_sale_amount_{source}': round(args['ord_sale_amount_' + source] + data[tmp.index(pay_date)][
                        'ord_sale_amount_' + source], 2),
                    f'ord_salenum_{source}': args['ord_salenum_' + source] + data[tmp.index(pay_date)][
                        'ord_salenum_' + source],
                    f'ord_maoli_{source}': args['ord_maoli_' + source] + data[tmp.index(pay_date)][
                        'ord_maoli_' + source],
                })
        if not data:
            return ok(data={'data': []})

        for dic in data:
            dic['ord_sale_amount_Global'] = sum(
                [v for k, v in dic.items() if k.startswith('ord_sale_amount_') and v])
            dic['ord_salenum_Global'] = sum([v for k, v in dic.items() if k.startswith('ord_salenum_') and v])
            dic['ord_maoli_Global'] = sum([v for k, v in dic.items() if k.startswith('ord_maoli_') and v]) / dic[
                'ord_sale_amount_Global'] if dic['ord_sale_amount_Global'] else 0

        source_code = ['FlexispotUS', 'FleximountsUS', 'FlexiSpotUK', 'FlexiSpotDE', 'FlexiSpotFR', 'FlexiSpotJP',
                       'FleximountsJP', 'Global']

        for dic in data:
            for source in source_code:
                if f'ord_salenum_{source}' in dic.keys():
                    dic.update({
                        f'ord_maoli_rate_{source}': round(dic.get(f'ord_maoli_{source}', 0) /
                                                          dic[f'ord_sale_amount_{source}']
                                                          if dic[f'ord_sale_amount_{source}'] else 0, 4)
                    })

        create_dict = {}
        for code in source_code:
            line_list = {'date': tmp,
                         code: [{'keyword': "销售额", 'data': []}, {'keyword': "销量", 'data': []},
                                {'keyword': "毛利率", 'data': []}]}
            create_dict.update(line_list)
        for temp_dict in data:
            for source in source_code:
                create_dict[source][0]['data'].append(temp_dict.get(f'ord_sale_amount_{source}', 0))
                create_dict[source][1]['data'].append(temp_dict.get(f'ord_salenum_{source}', 0))
                create_dict[source][2]['data'].append(temp_dict.get(f'ord_maoli_rate_{source}', 0))

        return ok(create_dict)
