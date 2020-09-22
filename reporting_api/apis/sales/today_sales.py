import datetime
import pandas as pandas
# import pandas as pd

from eggit.flask_restful_response import ok
from flask_restful import Resource

from reporting_api.models.sales_models.sales_analysis_report import SalesAnalysisReportModel
from reporting_api.utils.requests_utils import get_argument
from reporting_api.utils.response_utils import obj_to_dict


class TodaySales(Resource):
    def get(self):
        today_real = datetime.date.today()
        today = datetime.date.today() + datetime.timedelta(days=1)
        last_month_day = today - datetime.timedelta(days=30)
        start_time = last_month_day.strftime('%Y-%m-%d')
        end_time = today.strftime('%Y-%m-%d')

        user = SalesAnalysisReportModel.query

        if all([start_time, end_time]):
            user = user.filter(SalesAnalysisReportModel.ord_pay_time.between(start_time, end_time))

        source_list = ['RMA', 'sponsor', 'FBA-RMA', 'EMPTY PACKAGE', 'PRODUCT REVIEW', 'StockTransfer', 'FBA',
                       'SEARS-FBS', 'B2B', 'SampleOrder', 'ODM SAMPLE', 'Free-Trial-Riser', 'Synnex', 'OfflineCA',
                       'OfflineTN']

        user = user.filter(SalesAnalysisReportModel.source_code.notin_(source_list)).all()

        data = []
        tmp = []
        temp_dict = {
            'month_ord_sale_amount': 0,
            'month_ord_salenum': 0
        }
        for item in user:
            arg = obj_to_dict(item, [''], display=False, format_time='%Y-%m-%d')
            pay_date = arg['ord_pay_time']
            ord_sale_amount = arg['ord_sale_amount']
            args = {
                'pay_date': pay_date,
                'ord_sale_amount': ord_sale_amount,
                'ord_salenum': arg['ord_salenum'],
                'count': 1
            }

            if pay_date not in tmp:
                tmp.append(pay_date)
                data.append(args)
            else:
                data[tmp.index(pay_date)].update({
                    'ord_sale_amount': round(args['ord_sale_amount'] + data[tmp.index(pay_date)]['ord_sale_amount'], 2),
                    'ord_salenum': round(args['ord_salenum'] + data[tmp.index(pay_date)]['ord_salenum'], 2),
                    'count': args['count'] + data[tmp.index(pay_date)]['count'],
                })

        for dic in data:
            temp_dict = {
                'month_ord_sale_amount': round(temp_dict['month_ord_sale_amount'] + dic['ord_sale_amount'], 2),
                'month_ord_salenum': temp_dict['month_ord_salenum'] + dic['ord_salenum'],
            }
        if today_real.strftime('%Y-%m-%d') in tmp:
            temp_dict.update({
                'month_count': len(user),
                'today_ord_sale_amount': data[tmp.index(today_real.strftime('%Y-%m-%d'))]['ord_sale_amount'],
                'today_ord_salenum': data[tmp.index(today_real.strftime('%Y-%m-%d'))]['ord_salenum'],
                'today': today_real.strftime('%Y-%m-%d')
            })
        else:
            temp_dict.update({
                'month_count': len(user),
                'today_ord_sale_amount': 0,
                'today_ord_salenum': 0,
                'today': today_real.strftime('%Y-%m-%d')
            })

        count = []
        ord_sale_amount = []
        ord_salenum = []
        pay_date = []
        for i_dic in data:
            count.append(i_dic['count'])
            ord_sale_amount.append(i_dic['ord_sale_amount'])
            ord_salenum.append(i_dic['ord_salenum'])
            pay_date.append(i_dic['pay_date'])
        data = {
            'count': count,
            'ord_sale_amount': ord_sale_amount,
            'ord_salenum': ord_salenum,
            'pay_date': pay_date
        }

        temp_list = [temp_dict]
        return ok(data={'line': data, 'table': temp_list})
