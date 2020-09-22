# -*- coding:utf-8 -*
# 支架三级类销售分析
import re
import datetime
from eggit.flask_restful_response import ok
from flask_restful import Resource, reqparse, marshal
from reporting_api.utils.requests_utils import get_argument
from reporting_api.exceptions.service_error import ServiceError
from reporting_api.exceptions.service_exception import ServiceException
from reporting_api.models.sales_models.sales_analysis_report import SalesAnalysisReportModel
from reporting_api.utils.response_utils import obj_to_dict


class ThirdTierSaleLog(Resource):
    def get(self):
        start_time = get_argument("start_time",default='2020-10-01')
        end_time = get_argument("end_time", default='2020-10-02')
        if start_time > end_time:
            raise ServiceException(ServiceError.INVALID_VALUE)
        sources = ["Monitor mounts", "TV mounts", "Tablet mounts", "TV carts", "Laptopmounts"]

        results = SalesAnalysisReportModel.query.filter(
            SalesAnalysisReportModel.ord_pay_time.between(start_time, end_time),
            SalesAnalysisReportModel.pro_sec_type.in_(sources))
        tmp_time = list()
        tmp_dic = dict()
        for result in results:
            obj_dict = obj_to_dict(result, keys=[], display=False)
            pay_time = obj_dict['ord_pay_time']
            pay_time = re.match(r'(\d+-\d+-\d+)', pay_time)[0]
            if pay_time not in tmp_time:
                tmp_time.append(pay_time)
                tmp_dic[pay_time] = {
                    "salenum_mount_day": 0,
                    "amount_mount_day": 0,
                    "Monitor mounts": {"ord_sale_amount": 0.00, "ord_salenum": 0, "accounted": 0},
                    "TV mounts": {"ord_sale_amount": 0.00, "ord_salenum": 0, "accounted": 0},
                    "Tablet mounts": {"ord_sale_amount": 0.00, "ord_salenum": 0, "accounted": 0},
                    "TV carts": {"ord_sale_amount": 0.00, "ord_salenum": 0, "accounted": 0},
                    "Laptopmounts": {"ord_sale_amount": 0.00, "ord_salenum": 0, "accounted": 0},
                }
            tmp_dic[pay_time][obj_dict.get("pro_sec_type")]["ord_sale_amount"] += float(
                obj_dict.get("ord_sale_amount", 0))
            tmp_dic[pay_time][obj_dict.get("pro_sec_type")]["ord_salenum"] += int(obj_dict.get("ord_salenum", 0))

        for tmp in tmp_dic:
            day_tmp = str(tmp_dic[tmp])
            day_amount = re.findall('ord_sale_amount\': (\\d+.\\d+)', day_tmp)
            day_salenum = re.findall('ord_salenum\': (\\d+)', day_tmp)
            day_amount = sum([float(amount) for amount in day_amount])
            tmp_dic[tmp]["amount_mount_day"] = day_amount
            tmp_dic[tmp]["salenum_mount_day"] = sum([int(amount) for amount in day_salenum])
            for source in sources:
                tmp_dic[tmp][source]["accounted"] = round(tmp_dic[tmp][source]["ord_sale_amount"] / day_amount, 4)
        day_data = []
        for tmp_time_key in tmp_dic:
            day_data.append({
                "date": tmp_time_key,
                "total_sales": round(tmp_dic[tmp_time_key]["amount_mount_day"], 4),
                "total_mount": tmp_dic[tmp_time_key]["salenum_mount_day"],

                "sales_mm": round(tmp_dic[tmp_time_key]['Monitor mounts']["ord_sale_amount"], 4),
                "mount_mm": tmp_dic[tmp_time_key]['Monitor mounts']["ord_salenum"],
                "accounted_mm": tmp_dic[tmp_time_key]['Monitor mounts']["accounted"],

                "sales_tvm": round(tmp_dic[tmp_time_key]['TV mounts']["ord_sale_amount"], 4),
                "mount_tvm": tmp_dic[tmp_time_key]['TV mounts']["ord_salenum"],
                "accounted_tvm": tmp_dic[tmp_time_key]['TV mounts']["accounted"],

                "sales_tbm": round(tmp_dic[tmp_time_key]['Tablet mounts']["ord_sale_amount"], 4),
                "mount_tbm": tmp_dic[tmp_time_key]['Tablet mounts']["ord_salenum"],
                "accounted_tbm": tmp_dic[tmp_time_key]['Tablet mounts']["accounted"],

                "sales_tvc": round(tmp_dic[tmp_time_key]['TV carts']["ord_sale_amount"], 4),
                "mount_tvc": tmp_dic[tmp_time_key]['TV carts']["ord_salenum"],
                "accounted_tvc": tmp_dic[tmp_time_key]['TV carts']["accounted"],

                "sales_lm": round(tmp_dic[tmp_time_key]['Laptopmounts']["ord_sale_amount"], 4),
                "mount_lm": tmp_dic[tmp_time_key]['Laptopmounts']["ord_salenum"],
                "accounted_lm": tmp_dic[tmp_time_key]['Laptopmounts']["accounted"],
            })
        data_src = str(day_data)
        sales_all = sum(float(i) for i in re.findall('total_sales\': (\\d+.\\d+)', data_src))
        sales_mm_all = sum(float(i) for i in re.findall('sales_mm\': (\\d+.\\d+)', data_src)) / sales_all
        sales_tvm_all = sum(float(i) for i in re.findall('sales_tvm\': (\\d+.\\d+)', data_src)) / sales_all
        sales_tbm_all = sum(float(i) for i in re.findall('sales_tbm\': (\\d+.\\d+)', data_src)) / sales_all
        sales_tvc_all = sum(float(i) for i in re.findall('sales_tvc\': (\\d+.\\d+)', data_src)) / sales_all
        sales_lm_all = sum(float(i) for i in re.findall('sales_lm\': (\\d+.\\d+)', data_src)) / sales_all
        accounted = {
            "content_day": day_data,
            "total_accounted_mm": round(sales_mm_all, 4),
            "total_accounted_tvm": round(sales_tvm_all, 4),
            "total_accounted_tbm": round(sales_tbm_all, 4),
            "total_accounted_tvc": round(sales_tvc_all, 4),
            "total_accounted_lm": round(sales_lm_all, 4),
        }
        return ok(accounted)
