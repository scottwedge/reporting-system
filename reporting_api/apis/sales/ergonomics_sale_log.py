import datetime
import pandas as pandas
# import pandas as pd

from eggit.flask_restful_response import ok
from flask_restful import Resource

from reporting_api.models.sales_models.sales_analysis_report import SalesAnalysisReportModel
from reporting_api.utils.requests_utils import get_argument
from reporting_api.utils.response_utils import obj_to_dict


class ErgonomicsSaleLog(Resource):
    def get(self):
        start_time = get_argument('start_time', default='2019-09-01')
        end_time = get_argument('end_time', default='2019-09-30')

        user = SalesAnalysisReportModel.query

        if all([start_time, end_time]):
            user = user.filter(SalesAnalysisReportModel.ord_pay_time.between(start_time, end_time))

        pro_sec_types = ['height adjustable desk', 'Desktop Riser', 'Spacemaster mounts', 'Fitness',
                         'Monitor mounts', 'TV mounts', 'Monitor Stand', 'healthcare']

        user = user.filter(SalesAnalysisReportModel.pro_sec_type.in_(pro_sec_types)).all()
        print(len(user), 123)
        data = []
        tmp = []
        temp_dict = {}
        for item in user:
            arg = obj_to_dict(item, [''], display=False, format_time='%Y-%m-%d')
            pay_date = arg['ord_pay_time']
            ord_sale_amount = arg['ord_sale_amount']
            pro_sec_type = arg['pro_sec_type'].replace(' ', '_')
            args = {
                'pay_date': pay_date,
                f'ord_sale_amount_{pro_sec_type}': ord_sale_amount,
                f'ord_salenum_{pro_sec_type}': arg['ord_salenum'],
            }

            for k, v in args.items():
                if not args[k]:
                    args[k] = 0
            if pay_date not in tmp:
                tmp.append(pay_date)
                data.append(args)
            if f'ord_sale_amount{pro_sec_type}' not in data[tmp.index(pay_date)]:
                data[tmp.index(pay_date)].update(args)
            else:
                data[tmp.index(pay_date)].update({
                    f'ord_sale_amount_{pro_sec_type}': args['ord_sale_amount_' + pro_sec_type] +
                                                       data[tmp.index(pay_date)]['ord_sale_amount_' + pro_sec_type],
                    f'ord_salenum_{pro_sec_type}': args['ord_salenum_' + pro_sec_type] +
                                                   data[tmp.index(pay_date)]['ord_salenum_' + pro_sec_type],
                })

        if not data:
            return ok(data={[]})
        for dic in data:
            dic['ord_sale_amount_all'] = sum([v for k, v in dic.items() if k.startswith('ord_sale_amount_') and v])
            dic['ord_salenum_all'] = sum([v for k, v in dic.items() if k.startswith('ord_salenum_') and v])

        total_dic = {}
        for dic in data:
            for pro_sec_type in pro_sec_types:
                pro_sec_type = pro_sec_type.replace(' ', '_')
                dic.update({
                    f'ord_sale_amount_{pro_sec_type}_rate': round(dic.get(f'ord_sale_amount_{pro_sec_type}', 0) /
                                                                  dic['ord_sale_amount_all'], 4)
                })
                total_dic.update({
                    f'total_ord_sale_amount_{pro_sec_type}': round(dic.get(f'ord_sale_amount_{pro_sec_type}', 0) +
                                                                   total_dic.get(
                                                                       f'total_ord_sale_amount_{pro_sec_type}', 0), 2),
                    f'total_ord_salenum_{pro_sec_type}': round(dic.get(f'ord_salenum_{pro_sec_type}', 0) +
                                                               total_dic.get(f'total_ord_salenum_{pro_sec_type}', 0), 2)
                })
        total_dic['total_ord_sale_amount_all'] = sum([v for k, v in total_dic.items() if
                                                      k.startswith('total_ord_sale_amount_') and v])
        total_dic['total_ord_salenum_all'] = sum([v for k, v in total_dic.items() if
                                                  k.startswith('total_ord_salenum_') and v])
        for pro_sec_type in pro_sec_types:
            pro_sec_type = pro_sec_type.replace(' ', '_')
            total_dic[f'total_ord_sale_amount_{pro_sec_type}_rate'] = round(total_dic[
                                                                                f'total_ord_sale_amount_{pro_sec_type}'] / \
                                                                            total_dic['total_ord_sale_amount_all'], 4)
        return ok(data={'data': data, **total_dic})
