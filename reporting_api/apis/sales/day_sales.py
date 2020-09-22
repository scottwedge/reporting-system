import datetime
import pandas as pandas
# import pandas as pd

from eggit.flask_restful_response import ok
from flask_restful import Resource

from reporting_api.models.sales_models.sales_analysis_report import SalesAnalysisReportModel
from reporting_api.utils.requests_utils import get_argument
from reporting_api.utils.response_utils import obj_to_dict


class DaySales(Resource):
    def get(self):
        start_time = get_argument('start_time', default='2019-10-01')
        end_time = get_argument('end_time', default='2019-12-02')
        pro_sec_type = get_argument('pro_sec_type')
        user = SalesAnalysisReportModel.query
        if all([start_time, end_time]):
            user = user.filter(SalesAnalysisReportModel.ord_pay_time.between(start_time, end_time))

        if pro_sec_type:
            user = user.filter(SalesAnalysisReportModel.pro_sec_type == pro_sec_type).all()
        else:
            user = user.all()

        data = []
        tmp = []
        temp_dict = {
            'total_ord_sale_amount': 0,
            'total_ord_salenum': 0,
            'total_ord_expfee': 0,
            'total_ord_costfee': 0,
            'total_ord_platfee': 0,
            'total_ord_maoli': 0,
            # 'total_ord_adfee': 0
        }

        for item in user:
            arg = obj_to_dict(item, [''], display=False, format_time='%Y-%m-%d')
            pay_date = arg['ord_pay_time']
            ord_sale_amount = arg['ord_sale_amount']

            args = {
                'pay_date': pay_date,
                'ord_sale_amount': ord_sale_amount,
                'ord_salenum': arg['ord_salenum'],
                'ord_expfee': arg['ord_expfee'],  # 运费
                'ord_costfee': arg['ord_costfee'],  # 成本
                'ord_platfee': arg['ord_platfee'],  # 平台费
                'ord_maoli': arg['ord_maoli'],  # 毛利
                # 'ord_adfee': arg['ord_adfee'],  # ad
            }
            for k, v in args.items():
                if not args[k]:
                    args[k] = 0

            if pay_date not in tmp:
                tmp.append(pay_date)
                data.append(args)
            else:
                data[tmp.index(pay_date)].update({
                    'ord_sale_amount': round((data[tmp.index(pay_date)]['ord_sale_amount'] +
                                              args['ord_sale_amount']), 2),
                    'ord_salenum': round(data[tmp.index(pay_date)]['ord_salenum'] + args['ord_salenum'], 2),
                    'ord_expfee': round(data[tmp.index(pay_date)]['ord_expfee'] + args['ord_expfee'], 2),
                    'ord_costfee': round(data[tmp.index(pay_date)]['ord_costfee'] + args['ord_costfee'], 2),
                    'ord_platfee': round(data[tmp.index(pay_date)]['ord_platfee'] + args['ord_salenum'], 2),
                    'ord_maoli': round(data[tmp.index(pay_date)]['ord_maoli'] + args['ord_maoli'], 2),
                    # 'ord_adfee': data[tmp.index(pay_date)]['ord_adfee'] + args['ord_adfee'],
                })

        if not data:
            return ok([])

        for num in range(len(data)):
            data[num].update({
                'ord_expfee_rate': round(data[num]['ord_expfee'] / data[num]['ord_sale_amount'], 2),
                'ord_costfee_rate': round(data[num]['ord_costfee'] / data[num]['ord_sale_amount'], 2),
                'ord_platfee_rate': round(data[num]['ord_platfee'] / data[num]['ord_sale_amount'], 2),
                'ord_maoli_rate': round(data[num]['ord_maoli'] / data[num]['ord_sale_amount'], 2),
                # 'ord_platfee_rate': '%.4f' % (data[num]['ord_platfee'] / data[num]['ord_sale_amount']),
            })

            temp_dict.update({
                'total_ord_sale_amount': round(data[num]['ord_sale_amount'] + temp_dict['total_ord_sale_amount'], 2),
                'total_ord_salenum': round(data[num]['ord_salenum'] + temp_dict['total_ord_salenum'], 2),
                'total_ord_expfee': round(data[num]['ord_expfee'] + temp_dict['total_ord_expfee'], 2),
                'total_ord_costfee': round(data[num]['ord_costfee'] + temp_dict['total_ord_costfee'], 2),
                'total_ord_platfee': round(data[num]['ord_platfee'] + temp_dict['total_ord_platfee'], 2),
                'total_ord_maoli': round(data[num]['ord_maoli'] + temp_dict['total_ord_maoli'], 2),
            })
        temp_dict.update({
            'total_ord_expfee_rate': round(temp_dict['total_ord_expfee'] / temp_dict['total_ord_sale_amount'], 4),
            'total_ord_costfee_rate': round(temp_dict['total_ord_costfee'] / temp_dict['total_ord_sale_amount'], 4),
            'total_ord_platfee_rate': round(temp_dict['total_ord_platfee'] / temp_dict['total_ord_sale_amount'], 4),
            'total_ord_maoli_rate': round(temp_dict['total_ord_maoli'] / temp_dict['total_ord_sale_amount'], 4),
        })
        return ok(data={'data': data, **temp_dict})
