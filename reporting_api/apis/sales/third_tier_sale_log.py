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
        start_time = get_argument("start_time",
                                  default="2020-10-1")
        end_time = get_argument("end_time", default="2020-10-2")
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
                    "total_num": 0,
                    "total_amount": 0,
                    "Monitor mounts": {"sale_amount": 0, "sale_num": 0, "sale_make_up": 0},
                    "TV mounts": {"sale_amount": 0, "sale_num": 0, "sale_make_up": 0},
                    "Tablet mounts": {"sale_amount": 0, "sale_num": 0, "sale_make_up": 0},
                    "TV carts": {"sale_amount": 0, "sale_num": 0, "sale_make_up": 0},
                    "Laptopmounts": {"sale_amount": 0, "sale_num": 0, "sale_make_up": 0},
                }

            sale_amount = obj_dict.get("ord_sale_amount", 0)
            tmp_dic[pay_time][obj_dict.get("pro_sec_type")]["sale_amount"] += float(sale_amount) if sale_amount else 0
            tmp_dic[pay_time]["total_amount"] += float(sale_amount) if sale_amount else 0

            sale_num = obj_dict.get("ord_salenum", 0)
            tmp_dic[pay_time][obj_dict.get("pro_sec_type")]["sale_num"] += int(sale_num) if sale_num else 0
            tmp_dic[pay_time]["total_num"] += float(sale_num) if sale_num else 0

        res_data = []
        num = 0
        for tmp in tmp_dic:
            num += 1
            total_num = tmp_dic[tmp]['total_num']
            total_amount = tmp_dic[tmp]['total_amount']
            if not total_amount:
                continue
            res_dic = {
                "id": num,
                "data_time": tmp,
                "total_num": int(total_num),
                "total_amount": round(float(total_amount), 2),

            }
            for mounts in ["Monitor mounts", "TV mounts", "Tablet mounts", "TV carts", "Laptopmounts"]:
                res_key = mounts.lower().replace(' ', '_')
                sale_make_up = round(tmp_dic[tmp][mounts]["sale_amount"] / total_amount, 4)
                res_dic.update({
                    "sale_{}_num".format(res_key): tmp_dic[tmp][mounts]["sale_num"],
                    "sale_{}_amount".format(res_key): round(tmp_dic[tmp][mounts]["sale_amount"], 2),
                    "sale_{}_make_up".format(res_key): sale_make_up
                })
            res_data.append(res_dic)

        return ok({"result": res_data})
