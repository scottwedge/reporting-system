# -*- coding:utf-8 -*
#
import re
from eggit.flask_restful_response import ok
from flask_restful import Resource, reqparse, marshal
from reporting_api.utils.requests_utils import get_argument
from reporting_api.exceptions.service_error import ServiceError
from reporting_api.exceptions.service_exception import ServiceException
from reporting_api.models.sales_models.sales_analysis_report import OrdSourceAdfeeModel
from reporting_api.utils.response_utils import obj_to_dict


class EntrySourceFee(Resource):
    def get(self):
        start_time = get_argument("start_time", default="2019-07-01", required=True)
        end_time = get_argument("end_time", default="2020-10-01")
        results = OrdSourceAdfeeModel.query.filter(
            OrdSourceAdfeeModel.order_pay_time.between(start_time, end_time))
        city_list = ["total_us_fee",
                     "total_japan_fee",
                     "total_europe_fee",
                     "total_canada_fee",
                     "total_loctek_fee",
                     "total_google_fee",
                     "total_india_fee", ]
        sorts_list = [
            "TV mounts",
            "Monitor mounts",
            "Fitness",
            "Spacemaster mounts",
            "Desktop Riser",
            "height adjustable desk",
            "Monitor Stand",
            "healthcare",
            "offacc",
        ]
        day_list = []
        tmp_dic = {}
        for result in results:
            store_code = obj_to_dict(result, keys=[], display=False)
            ord_pay_time = "{}({})".format(re.match(r'(\d+-\d+-\d+)', store_code.get("order_pay_time"))[0],
                                           store_code.get("week"))
            if ord_pay_time not in day_list:
                day_list.append(ord_pay_time)
                tmp_dic.update({
                    ord_pay_time: {
                        "total_amount": 0, }
                })
                for sorts in sorts_list:
                    tmp_dic[ord_pay_time].update({
                        sorts.lower().replace(' ', '_'): 0,
                    })
                for city in city_list:
                    tmp_dic[ord_pay_time].update({
                        city: 0,
                    })
            for sort in city_list:
                try:
                    amount = store_code.get(sort)
                    tmp_dic[ord_pay_time][sort] += float(amount) if amount else 0
                except Exception as e:
                    pass

            total_ad_fee = store_code.get('total_ad_fee')
            ad_fee_pro_type = store_code.get('ad_fee_pro_type')
            if ad_fee_pro_type in sorts_list:
                dmp_key = ad_fee_pro_type.lower().replace(' ', '_')
                tmp_dic[ord_pay_time][dmp_key] += float(total_ad_fee) if total_ad_fee else 0
                tmp_dic[ord_pay_time]["total_amount"] += float(total_ad_fee) if total_ad_fee else 0
        res_list = []
        num = 0
        for tmp in tmp_dic:
            num += 1
            args = {
                "id": num,
                "data_time": tmp,
                "desktop_riser": round(tmp_dic[tmp]["desktop_riser"], 2),
                "fitness": round(tmp_dic[tmp]["fitness"], 2),
                "healthcare": round(tmp_dic[tmp]["healthcare"], 2),
                "height_adjustable_desk": round(tmp_dic[tmp]["height_adjustable_desk"], 2),
                "monitor_mounts": round(tmp_dic[tmp]["monitor_mounts"], 2),
                "monitor_stand": round(tmp_dic[tmp]["monitor_stand"], 2),
                "offacc": round(tmp_dic[tmp]["offacc"], 2),
                "spacemaster_mounts": round(tmp_dic[tmp]["spacemaster_mounts"], 2),
                "total_amount": round(tmp_dic[tmp]["total_amount"], 2),
                "total_canada_fee": round(tmp_dic[tmp]["total_canada_fee"], 2),
                "total_europe_fee": round(tmp_dic[tmp]["total_europe_fee"], 2),
                "total_google_fee": round(tmp_dic[tmp]["total_google_fee"], 2),
                "total_india_fee": round(tmp_dic[tmp]["total_india_fee"], 2),
                "total_japan_fee": round(tmp_dic[tmp]["total_japan_fee"], 2),
                "total_loctek_fee": round(tmp_dic[tmp]["total_loctek_fee"], 2),
                "total_us_fee": round(tmp_dic[tmp]["total_us_fee"], 2),
                "tv_mounts": round(tmp_dic[tmp]["tv_mounts"], 2),
            }
            res_list.append(args)
        return ok(res_list)
