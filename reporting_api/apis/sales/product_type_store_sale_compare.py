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
from reporting_api.utils.sales_report_utils import get_salenum_sale_amount


class ProductTypeStoreSaleCompare(Resource):
    def get(self):
        start_time = get_argument('start_time', required=True)
        end_time = get_argument('end_time', required=True)
        start_time_add = (datetime.datetime.strptime(start_time, '%Y-%m-%d') +
                          datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        end_time_add = (datetime.datetime.strptime(end_time, '%Y-%m-%d') +
                        datetime.timedelta(days=1)).strftime('%Y-%m-%d')

        start_user = SalesAnalysisReportModel.query.filter(SalesAnalysisReportModel.ord_pay_time >= start_time,
                                                           SalesAnalysisReportModel.ord_pay_time <= start_time_add).all()

        end_user = SalesAnalysisReportModel.query.filter(SalesAnalysisReportModel.ord_pay_time >= end_time,
                                                         SalesAnalysisReportModel.ord_pay_time <= end_time_add).all()

        start_data, start_source = get_salenum_sale_amount(start_user)
        end_data, end_source = get_salenum_sale_amount(end_user)

        total_dic = {
            'total_start_ord_sale_amount': 0,
            'total_start_ord_salenum': 0,
            'total_end_ord_sale_amount': 0,
            'total_end_ord_salenum': 0
        }
        for source in start_source:
            if source in end_source:
                start_data[start_source.index(source)].update({
                    'end_ord_sale_amount': end_data[end_source.index(source)]['ord_sale_amount'],
                    'end_ord_salenum': end_data[end_source.index(source)]['ord_salenum'],

                    'compare_ord_sale_amount': end_data[end_source.index(source)]['ord_sale_amount'] -
                                               start_data[start_source.index(source)]['ord_sale_amount'],
                    'compare_ord_salenum': end_data[end_source.index(source)]['ord_salenum'] -
                                           start_data[start_source.index(source)]['ord_salenum'],
                })
                total_dic.update({
                    'total_start_ord_sale_amount': total_dic['total_start_ord_sale_amount'] +
                                                   start_data[start_source.index(source)]['ord_sale_amount'],
                    'total_start_ord_salenum': total_dic['total_start_ord_salenum'] +
                                               start_data[start_source.index(source)]['ord_salenum'],

                    'total_end_ord_sale_amount': total_dic['total_end_ord_sale_amount'] +
                                                 end_data[end_source.index(source)]['ord_sale_amount'],
                    'total_end_ord_salenum': total_dic['total_end_ord_salenum'] +
                                             end_data[end_source.index(source)]['ord_salenum']

                })
        total_dic.update({
            'total_compare_ord_sale_amount': total_dic['total_end_ord_sale_amount'] -
                                             total_dic['total_start_ord_sale_amount'],
            'total_compare_ord_salenum': total_dic['total_end_ord_salenum'] -
                                         total_dic['total_start_ord_salenum'],
        })
        return ok(data={'data': start_data, **total_dic})
