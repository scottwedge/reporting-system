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


class MonthSalelogList(Resource):
    def get(self):
        start_time = get_argument('start_time', default='2019-01-15')
        end_time = get_argument('end_time', default='2019-02-16')
        source_code = get_argument('source_code')
        ord_sitecode = get_argument('ord_sitecode')
        pro_sec_type = get_argument('pro_sec_type')

        pr = pd.period_range(start=start_time, end=end_time, freq='M')
        prTupes = tuple([(period.month, period.year) for period in pr])
        data = []
        tmp = []
        month_date = []

        for prTupe in prTupes:
            date_time = str(prTupe[1]) + '-' + str(prTupe[0])
            if prTupe[0] < 10:
                date_time = str(prTupe[1]) + '-0' + str(prTupe[0])
            month_date.append(date_time)

        user = SalesAnalysisReportModel.query.filter(SalesAnalysisReportModel.yyyymm.in_(month_date))
        if source_code:
            user = user.filter(SalesAnalysisReportModel.source_code == source_code)
        if ord_sitecode:
            user = user.filter(SalesAnalysisReportModel.ord_sitecode == ord_sitecode)
        if pro_sec_type:
            user = user.filter(SalesAnalysisReportModel.pro_sec_type == pro_sec_type)
        user = user.all()
        total_dic = {}
        count_dic = {}
        for item in user:
            arg = obj_to_dict(item, [''], display=False, format_time='%Y-%m-%d')
            date_month = arg['yyyymm']
            ord_sale_amount = arg['ord_sale_amount']

            args = {
                'ord_salenum': arg['ord_salenum'],  # 销量
                'ord_sale_amount': ord_sale_amount,  # 销售额
                'ord_platfee': arg['ord_platfee'],  # 平台费
                'ord_expfee': arg['ord_expfee'],  # 运费
                'ord_factoryfee': arg['ord_factoryfee'],  # 出厂额
                'ord_fobfee': arg['ord_fobfee'],  # FOB金额
                'ord_costfee': arg['ord_costfee'],  # 成本
                'ord_maoli': arg['ord_maoli'],  # 毛利
                'ord_volumefee': arg['ord_volumefee'],
                'ord_pgrossfee': arg['ord_pgrossfee'],
                'pro_materialrate': arg['pro_materialrate'],  # 材料率
                'count': 1
            }
            for k, v in args.items():
                if not args[k]:
                    args[k] = 0
            if date_month not in tmp:
                tmp.append(date_month)
                data.append(args)
            else:
                data[tmp.index(date_month)] = dict(Counter(args) + Counter(data[tmp.index(date_month)]))

            if total_dic:
                total_dic = dict(Counter(args) + Counter(total_dic))

            else:
                total_dic.update(args)
        if not data:
            return ok('没有数据')
        for tmp_dic in data:
            tmp_dic.update({
                'date_month': tmp.pop(0),
                'average_price': '%.2f' % (tmp_dic['ord_sale_amount'] / tmp_dic['ord_salenum']),
                'ord_huanhui': '%.2f' % (tmp_dic['ord_factoryfee'] / tmp_dic['ord_fobfee']),
                'ord_costfee_rate': '%.4f' % (tmp_dic['ord_costfee'] / tmp_dic['ord_sale_amount']),  # 成本率
                'ord_expfee_rate': '%.4f' % (tmp_dic['ord_expfee'] / tmp_dic['ord_sale_amount']),  # 物流率
                'ord_maoli_rate': '%.4f' % (tmp_dic['ord_maoli'] / tmp_dic['ord_sale_amount']),
                'pro_materialrate_rate': '%.4f' % (tmp_dic['pro_materialrate'] / tmp_dic['count']),  # ???
                'ord_volumefee': round(tmp_dic['ord_volumefee'] / tmp_dic['count'], 4),  # ???
                'ord_pgrossfee': round(tmp_dic['ord_pgrossfee'] / tmp_dic['count'], 4),  # ???

                'ord_costfee': round(tmp_dic['ord_costfee'], 2),
                'ord_expfee': round(tmp_dic['ord_expfee'], 2),
                'ord_factoryfee': round(tmp_dic['ord_factoryfee'], 2),
                'ord_fobfee': round(tmp_dic['ord_fobfee'], 2),
                'ord_platfee': round(tmp_dic['ord_platfee'], 2),
                'ord_sale_amount': round(tmp_dic['ord_sale_amount'], 2),
                'pro_materialrate': round(tmp_dic['pro_materialrate'], 2),
                'ord_maoli': round(tmp_dic['ord_maoli'], 2),
            })
        total_dic.update({
            'average_price': '%.2f' % (total_dic['ord_sale_amount'] / total_dic['ord_salenum']),
            'ord_huanhui': '%.2f' % (total_dic['ord_factoryfee'] / total_dic['ord_fobfee']),
            'ord_costfee_rate': '%.4f' % (total_dic['ord_costfee'] / total_dic['ord_sale_amount']),  # 成本率
            'ord_expfee_rate': '%.4f' % (total_dic['ord_expfee'] / total_dic['ord_sale_amount']),  # 物流率
            'ord_maoli_rate': '%.4f' % (total_dic['ord_maoli'] / total_dic['ord_sale_amount']),
            'pro_materialrate': round(total_dic['pro_materialrate'] / len(user), 4),  # ???

            'ord_costfee': round(total_dic['ord_costfee'], 2),
            'ord_maoli': round(total_dic['ord_maoli'], 2),
            'ord_expfee': round(total_dic['ord_expfee'], 2),
            'ord_factoryfee': round(total_dic['ord_factoryfee'], 2),
            'ord_fobfee': round(total_dic['ord_fobfee'], 2),
            'ord_platfee': round(total_dic['ord_platfee'], 2),
            'ord_sale_amount': round(total_dic['ord_sale_amount'], 2),
            'ord_volumefee': None,
            'ord_pgrossfee': None
        })
        new_total_dic = {}
        for k, v in total_dic.items():
            new_total_dic.update({f'total_{k}': v})
        return ok(data={'data': data, **new_total_dic})


class YearOnYearBasis(Resource):
    def get(self):
        start_time = get_argument('start_time', default='2020-10-01')
        end_time = get_argument('end_time', default='2020-10-29')
        year = re.findall(r'(\d+)', start_time)
        year_end = re.findall(r'(\d+)', end_time)
        last_year_start_time = str(int(year[0]) - 1) + '-' + year[1] + '-' + year[2]
        last_year_end_time = str(int(year_end[0]) - 1) + '-' + year_end[1] + '-' + year_end[2]
        this_year_data = get_data(start_time, end_time)
        last_year_data = get_data(last_year_start_time, last_year_end_time)
        year_on_year_basis = {}
        for k, v in this_year_data.items():
            if k != 'date':
                year_on_year_basis.update({
                    'basis_' + k: (this_year_data[k] - last_year_data[k]) / this_year_data[k]
                })
        return ok(data={'data': [last_year_data, this_year_data], **year_on_year_basis})


class MonthOnMonthRatio(Resource):

    def get(self):
        start_time = get_argument('start_time', default='2019-01-01')
        end_time = get_argument('end_time', default='2019-01-29')

        pr = pd.period_range(start=start_time, end=end_time, freq='M')

        prTupes = tuple([(period.month, period.year) for period in pr])
        difference = len(prTupes)
        last_month_start_time = \
            ((datetime.datetime.strptime(start_time, '%Y-%m-%d') -
              relativedelta(months=difference))).strftime(
                '%Y-%m-%d')
        last_month_start_end = \
            ((datetime.datetime.strptime(end_time, '%Y-%m-%d') -
              relativedelta(months=difference))).strftime('%Y-%m-%d')

        this_month_data = get_data(start_time, end_time)
        last_month_data = get_data(last_month_start_time, last_month_start_end)
        month_on_month_ratio = {}
        for k, v in this_month_data.items():
            if k != 'date':
                month_on_month_ratio.update({
                    'basis_' + k: (this_month_data[k] - last_month_data[k]) / last_month_data[k]
                })
        return ok(data={'data': [last_month_data, this_month_data], **month_on_month_ratio})


def get_data(start_time, end_time):
    user = SalesAnalysisReportModel.query
    source_code = get_argument('source_code')
    ord_sitecode = get_argument('ord_sitecode')
    pro_sec_type = get_argument('pro_sec_type')
    # if all([start_time, end_time]):
    tmp_dict = {}
    total_dict = {}
    if all([start_time, end_time]):
        user = user.filter(SalesAnalysisReportModel.ord_pay_time.between(start_time, end_time))
    if source_code:
        user = user.filter(SalesAnalysisReportModel.source_code == source_code)
    if ord_sitecode:
        user = user.filter(SalesAnalysisReportModel.ord_sitecode == ord_sitecode)
    if pro_sec_type:
        user = user.filter(SalesAnalysisReportModel.pro_sec_type == pro_sec_type)
    user = user.all()

    for item in user:
        arg = obj_to_dict(item, [''], display=False, format_time='%Y-%m-%d')
        ord_sale_amount = arg['ord_sale_amount']
        ord_salenum = arg['ord_salenum']
        args = {
            'ord_salenum': ord_salenum,  # 销量
            'ord_sale_amount': ord_sale_amount,  # 销售额
            'ord_platfee': arg['ord_platfee'],  # 平台费
            'ord_expfee': arg['ord_expfee'],  # 运费
            'ord_factoryfee': arg['ord_factoryfee'],  # 出厂额
            'ord_fobfee': arg['ord_fobfee'],  # FOB金额
            'ord_costfee': arg['ord_costfee'],  # 成本
            'ord_maoli': arg['ord_maoli'],  # 毛利
        }
        for k, v in args.items():
            if not args[k]:
                args[k] = 0
            if not total_dict:
                for key in args.keys():
                    total_dict.update({key: 0})
        if tmp_dict:
            X, Y = Counter(tmp_dict), Counter(args)
            tmp_dict = dict(X + Y)
        else:
            tmp_dict.update(args)
    for k, v in tmp_dict.items():
        if isinstance(v, float):
            tmp_dict[k] = round(v, 2)
    tmp_dict.update({
        'date': f'{start_time}至{end_time}'
    })
    return tmp_dict
