import datetime
import pandas as pandas
# import pandas as pd

from eggit.flask_restful_response import ok
from flask_restful import Resource

from reporting_api.exceptions.service_error import ServiceError
from reporting_api.exceptions.service_exception import ServiceException
from reporting_api.models.sales_models.sales_analysis_report import SalesAnalysisReportModel
from reporting_api.utils.requests_utils import get_argument
from reporting_api.utils.response_utils import obj_to_dict


class IndependentStationNationalSalesAnalysis(Resource):
    def get(self):
        start_time = get_argument('start_time', default='2020-09-01')
        end_time = get_argument('end_time', default='2020-09-21')

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
                'date': pay_date,
                f'ord_sale_amount_{source}': ord_sale_amount,
                f'ord_salenum_{source}': arg['ord_salenum'],
                f'ord_maoli_{source}': arg['ord_maoli']
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
                    f'ord_sale_amount_{source}': args['ord_sale_amount_' + source] + data[tmp.index(pay_date)][
                        'ord_sale_amount_' + source],
                    f'ord_salenum_{source}': args['ord_salenum_' + source] + data[tmp.index(pay_date)][
                        'ord_salenum_' + source],
                    f'ord_maoli_{source}': args['ord_maoli_' + source] + data[tmp.index(pay_date)][
                        'ord_maoli_' + source],
                })
        tmp_dic = {}
        if not data:
            return ok(data={'data': []})

        for dic in data:
            dic['ord_sale_amount_Global'] = sum([v for k, v in dic.items() if k.startswith('ord_sale_amount_') and v])
            dic['ord_salenum_Global'] = sum([v for k, v in dic.items() if k.startswith('ord_salenum_') and v])
            dic['ord_maili_Global'] = sum([v for k, v in dic.items() if k.startswith('ord_maoli_') and v])
            dic['ord_maoli_rate_Global'] = sum([v for k, v in dic.items() if k.startswith('ord_maoli_') and v]) / dic[
                'ord_sale_amount_Global'] if dic['ord_sale_amount_Global'] else 0

        total_dic = {}
        for dic in data:
            for source in source_code:
                if f'ord_salenum_{source}' in dic.keys():  # ord_maoli /  ord_sale_amount
                    dic.update({
                        f'ord_maoli_rate_{source}': dic.get(f'ord_maoli_{source}', 0) /
                                                    dic[f'ord_sale_amount_{source}'] if dic[
                            f'ord_sale_amount_{source}'] else 0,
                        f'market_share_{source}': dic[f'ord_sale_amount_{source}'] /
                                                  dic['ord_sale_amount_Global'] if dic['ord_sale_amount_Global'] else 0
                    })
                    total_dic.update({
                        f'total_ord_sale_amount_{source}': dic.get(f'ord_sale_amount_{source}', 0) +
                                                           total_dic.get(f'total_ord_sale_amount_{source}', 0),
                        f'total_ord_salenum_{source}': dic.get(f'ord_salenum_{source}', 0) +
                                                       total_dic.get(f'total_ord_salenum_{source}', 0),
                        f'total_ord_maoli_{source}': dic.get(f'ord_maoli_{source}', 0) +
                                                     total_dic.get(f'total_ord_maoli_{source}', 0),
                    })

        total_dic['total_ord_salenum_Global'] = sum([v for k, v in total_dic.items() if k.startswith('total_ord_salenum_') and v])
        total_dic['total_ord_sale_amount_Global'] = sum([v for k, v in total_dic.items() if
                                                         k.startswith('total_ord_sale_amount_') and v])
        total_dic['total_ord_maoli_Global'] = sum([v for k, v in total_dic.items() if
                                                   k.startswith('total_ord_maoli_') and v])
        total_dic['total_ord_maoli_rate_Global'] = total_dic['total_ord_maoli_Global'] / \
                                                   total_dic['total_ord_sale_amount_Global']

        for source in source_code:
            if f'ord_salenum_{source}' in total_dic.keys():
                total_dic[f'total_ord_maoli_rate_{source}'] = (total_dic.get(f'total_ord_maoli_{source}', 0) / total_dic.get(f'total_ord_sale_amount_{source}', 0))
        return ok(data={'data': data, **total_dic})
