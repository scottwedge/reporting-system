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


class MonthlySalesData(Resource):
    def get(self):
        start_time = get_argument('start_time', default='2020-09-15')
        end_time = get_argument('end_time', default='2020-09-16')
        year = re.findall(r'(\d+)', start_time)
        year_end = re.findall(r'(\d+)', end_time)
        pr = pd.period_range(start=start_time, end=end_time, freq='M')
        prTupes = tuple([(period.month, period.year) for period in pr])
        difference = len(prTupes)

        last_month_start_time = ((datetime.datetime.strptime(start_time, '%Y-%m-%d') -
                                  relativedelta(months=difference))).strftime('%Y-%m-%d')
        last_month_start_end = ((datetime.datetime.strptime(end_time, '%Y-%m-%d') -
                                 relativedelta(months=difference))).strftime('%Y-%m-%d')

        last_year_start_time = str(int(year[0]) - 1) + '-' + year[1] + '-' + year[2]
        last_year_end_time = str(int(year_end[0]) - 1) + '-' + year_end[1] + '-' + year_end[2]

        this_month_data, tmp_this_month = monthly_sales(start_time, end_time)
        last_month_data, tmp_last_month = monthly_sales(last_month_start_time, last_month_start_end)
        last_year_month_data, tmp_last_year = monthly_sales(last_year_start_time, last_year_end_time)

        for tmp in tmp_this_month:
            if tmp in tmp_last_month:
                this_month_data[tmp_this_month.index(tmp)].update({
                    'last_month_ord_sale_amount': last_month_data[tmp_last_month.index(tmp)]['ord_sale_amount'],
                    'month_on_month_ratio': this_month_data[tmp_this_month.index(tmp)]['ord_sale_amount'] -
                                            last_month_data[tmp_last_month.index(tmp)]['ord_sale_amount'] /
                                            last_month_data[tmp_last_month.index(tmp)]['ord_sale_amount']
                })
            else:
                this_month_data[tmp_this_month.index(tmp)].update({
                    'last_month_ord_sale_amount': 0,
                    'month_on_month_ratio': 0
                })
            if tmp in tmp_last_year:
                this_month_data[tmp_this_month.index(tmp)].update({
                    'last_year_ord_sale_amount': last_year_month_data[tmp_last_year.index(tmp)]['ord_sale_amount'],
                    'year_on_year_basis': last_year_month_data[tmp_this_month.index(tmp)]['ord_sale_amount'] -
                                          last_year_month_data[tmp_last_year.index(tmp)]['ord_sale_amount'] /
                                          last_year_month_data[tmp_last_year.index(tmp)]['ord_sale_amount']
                })
            else:
                this_month_data[tmp_this_month.index(tmp)].update({
                    'last_year_ord_sale_amount': 0,
                    'year_on_year_basis': 0
                })
        total_dic = {}
        # 计算客单价、销售占比
        for dic in this_month_data:
            dic.update({
                'solo_price': dic['ord_sale_amount'] / dic['count'],
                'sales_rate': dic['ord_sale_amount'] / dic.pop('total_ord_sale_amount')
            })
            if total_dic:
                total_dic.update({
                    'total_count': total_dic['total_count'] + dic['count'],
                    'total_ord_salenum': total_dic['total_ord_salenum'] + dic['ord_salenum'],
                    'total_ord_sale_amount': total_dic['total_ord_sale_amount'] + dic['ord_sale_amount'],
                })
            else:
                total_dic.update({
                    'total_count': dic['count'],
                    'total_ord_salenum': dic['ord_salenum'],
                    'total_ord_sale_amount': dic['ord_sale_amount'],
                })
        # 总环比和总同比
        total_dic.update({
            'total_last_year_ord_sale_amount': last_year_month_data[1]['total_ord_sale_amount'],
            'total_year_on_year_basis': (total_dic['total_ord_sale_amount'] -
                                         last_year_month_data[1]['total_ord_sale_amount']) /
                                        last_year_month_data[1]['total_ord_sale_amount'],
            'total_last_month_ord_sale_amount': last_month_data[1]['total_ord_sale_amount'],
            'month_on_month_ratio': (total_dic['total_ord_sale_amount'] -
                                     last_month_data[1]['total_ord_sale_amount']) /
                                    last_month_data[1]['total_ord_sale_amount'],
            'total_true_total_ord_sale_amount': total_dic['total_ord_sale_amount'],
            'total_solo_price': total_dic['total_ord_sale_amount'] / total_dic['total_count']
        })
        return ok(data={'data': this_month_data, **total_dic})
