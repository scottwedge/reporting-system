# -*- coding:utf-8 -*
# 八大品类报表
import datetime
import re
from flask_restful import Resource
from reporting_api.extensions import db
from eggit.flask_restful_response import ok
from reporting_api.utils.requests_utils import get_argument
from reporting_api.utils.response_utils import obj_to_dict
from reporting_api.models.sales_models.sales_analysis_report import (
    SalesAnalysisReportModel as SalesM,
    ProProductModel as ProductM
)


class GlobalTyprSaleFirstLog(Resource):
    def fob_maoli(self, factoryfee, fob):
        # 换汇 = 出厂价 / fob
        swap = factoryfee / fob
        # FOB毛利 = FOB金额 * (汇率 + 0.17 * 换汇 / 1.17 - 换汇)
        fob_maoli = fob * (swap + 0.17 * swap / 1.17 - swap)
        return "{}%".format(round(fob_maoli * 100), 2)

    def rate_maoli(self, maoli, mount):
        rate_maoli = maoli / mount
        return "{}%".format(round(rate_maoli * 100, 2))

    def get(self):
        start_time = get_argument("start_time", default='2020-08-15')
        end_time = get_argument("end_time", default='2020-10-01')
        pro_type = get_argument("pro_type", default="height adjustable desk")
        results = SalesM.query.filter(
            SalesM.ord_pay_time.between(start_time, end_time),
            SalesM.pro_sec_type == pro_type)

        tmp_dic = {}
        tmp_list = []
        for result in results:
            obj_dict = obj_to_dict(result, keys=[], display=False)
            print(obj_dict)
            pay_time = re.match(r'(\d+-\d+-\d+)', obj_dict.get("ord_pay_time"))[0]
            state = obj_dict.get("ord_sitecode")
            if pay_time not in tmp_list:
                tmp_list.append(pay_time)
                tmp_dic.update({
                    pay_time: {
                        "state": [],
                        "state_dic": {
                        }
                    }
                })
            if state not in tmp_dic[pay_time]["state"]:
                tmp_dic[pay_time]["state"].append(state)
                tmp_dic[pay_time]["state_dic"].update({
                    state: {
                        "sale_num": 0,
                        "sale_amount": 0,
                        "sale_factoryfee": 0,
                        "sale_fobfee": 0,
                        "sale_maoli": 0,
                    }})

            tmp_dic[pay_time]["state_dic"][state]["sale_num"] += float(obj_dict.get("ord_salenum")) if obj_dict.get(
                "ord_salenum") else 0
            tmp_dic[pay_time]["state_dic"][state]["sale_amount"] += float(
                obj_dict.get("ord_sale_amount")) if obj_dict.get(
                "ord_sale_amount") else 0
            tmp_dic[pay_time]["state_dic"][state]["sale_fobfee"] += float(obj_dict.get("ord_fobfee")) if obj_dict.get(
                "ord_fobfee") else 0
            tmp_dic[pay_time]["state_dic"][state]["sale_maoli"] += float(obj_dict.get("ord_maoli")) if obj_dict.get(
                "ord_maoli") else 0
            tmp_dic[pay_time]["state_dic"][state]["sale_factoryfee"] += float(
                obj_dict.get("ord_factoryfee")) if obj_dict.get(
                "ord_factoryfee") else 0
        args = {
            "JP": "Japan",
            "CAN": "Canada",
            "EU": "European",
            "India": "INEI",
            "US": "US",
        }
        total_dic = {}
        total_list = {}
        res_data = []
        for tmp_time in tmp_dic:
            day_tmp_str = str(tmp_dic[tmp_time])
            sale_amount = round(sum(list(float(i) for i in re.findall('sale_amount\': (\\d+.\\d+)', day_tmp_str))), 2)
            sale_fob = round(sum(list(float(i) for i in re.findall('sale_fobfee\': (\\d+.\\d+)', day_tmp_str))), 2)
            sale_factoryfee = round(
                sum(list(float(i) for i in re.findall('sale_factoryfee\': (\\d+.\\d+)', day_tmp_str))), 2)
            day_txt = ["{},今日{}总销售{}美金，其中".format(tmp_time, pro_type, sale_amount)]
            for states in tmp_dic[tmp_time]["state_dic"]:
                states_city = args.get(states)
                sale_day_mount = round(tmp_dic[tmp_time]["state_dic"][states]["sale_amount"], 2)
                day_txt.append('{}销售{}美金，'.format(states_city, sale_day_mount))
                if args.get(states) not in total_list:
                    total_dic.update({
                        args.get(states): 0
                    })
                total_dic[args.get(states)] += sale_day_mount
            day_txt.append('FOB金额{}美金,FOB毛利{}.'.format(sale_fob, self.fob_maoli(sale_factoryfee, sale_fob)))
            res_data.append(''.join(day_txt))
        tmp_src = str(tmp_dic)
        total_sale_amount = round(sum(list(float(i) for i in re.findall('sale_amount\': (\\d+.\\d+)', tmp_src))), 2)
        total_sale_fob = round(sum(list(float(i) for i in re.findall('sale_fobfee\': (\\d+.\\d+)', tmp_src))), 2)
        total_sale_maoli = round(sum(list(float(i) for i in re.findall('sale_maoli\': (\\d+.\\d+)', tmp_src))), 2)
        total_sale_factoryfee = round(
            sum(list(float(i) for i in re.findall('sale_factoryfee\': (\\d+.\\d+)', tmp_src))), 2)
        print(self.rate_maoli(total_sale_maoli, total_sale_amount))
        total_data_txt = ["{}-{}. 今日总计销售{}美金, 毛利率{}.其中".format(start_time.replace('-', '/'),
                                                               end_time.replace('-', '/'),
                                                               total_sale_amount,
                                                               self.rate_maoli(total_sale_maoli, total_sale_amount))]
        for ctype_amount in total_dic:
            total_data_txt.append('{}销售{}美金，'.format(ctype_amount, total_dic[ctype_amount]))
        total_data_txt.append(
            'FOB金额{}美金,FOB毛利{}.'.format(total_sale_fob, self.fob_maoli(total_sale_factoryfee, total_sale_fob)))
        total_data_txt = ''.join(total_data_txt)
        return ok({"total_title": total_data_txt, "sale_list": res_data})



class GlobalTyprSaleLostLog(Resource):
    def get(self):
        table = db.session.query(SalesM, ProductM).join(SalesM, SalesM.pro_fname == ProductM.bsname)
        start_time = get_argument('start_time', default='2019-09-01')
        end_time = get_argument('end_time', default='2019-09-21')

        # start_time = datetime.date.today() - datetime.timedelta(days=170)
        #
        # end_time = datetime.date.today()
        pro_type = get_argument("pro_type", default="height adjustable desk")

        results = table.filter(SalesM.ord_pay_time.between(start_time, end_time),
                               SalesM.pro_sec_type == pro_type)
        tmp_list = []
        tmp_dic = {}
        for sales_table, product_table in results:
            obj_dict = obj_to_dict(sales_table, keys=[], display=False)
            obj_dict.update({"pro_image_path": product_table.pro_image_path})
            model_name = "{}_{}".format(obj_dict.get('pro_fname'), obj_dict.get('pro_bsname'))
            if model_name not in tmp_list:
                tmp_dic.update({
                    model_name: {
                        "image": '',  # 图
                        "sale_num": 0,  # 销售数
                        "sale_amount": 0,  # 销售额
                        "sale_price": 0,  # 售价 (销售额 / 销量)
                        "sale_expfee": 0,  # 快递费/均值（快递费/销量）
                        "sale_platfee": 0,  # 平台费
                        "sale_factoryfee": 0,  # 出厂费
                        "sale_fobfee": 0,  # fob费用
                        "sale_huanhui": 0,  # 换汇（出厂价/fob）
                        "sale_costfee": 0,  # 成本费
                        "sale_rate_platfee": 0,  # 成本率（成本费 / 销售额 ）
                        "sale_rate_expfee": 0,  # 物流率（快递费 / 销售额 ）
                        "sale_rate_materialrate": [],  # 材料率
                        "sale_alone_maoli": 0,  # 单毛利（ 毛利 / 销量）
                        "sale_maoli": 0,  # 毛利
                    }
                })

            if not tmp_dic[model_name]["image"]:
                pass
            else:
                image = obj_dict.get("pro_image_path")
                tmp_dic[model_name]["image"] = image

            sale_num = obj_dict.get('ord_salenum')
            tmp_dic[model_name]["sale_num"] += int(sale_num) if sale_num else 0

            sale_amount = obj_dict.get('ord_sale_amount')
            tmp_dic[model_name]["sale_amount"] += round(float(sale_amount), 2) if sale_amount else 0

            sale_expfee = obj_dict.get('ord_factoryfee')
            tmp_dic[model_name]["sale_expfee"] += round(float(sale_expfee), 2) if sale_expfee else 0

            sale_factoryfee = obj_dict.get('ord_salenum')
            tmp_dic[model_name]["sale_factoryfee"] += round(float(sale_factoryfee), 2) if sale_amount else 0

            sale_fobfee = obj_dict.get('ord_fobfee')
            tmp_dic[model_name]["sale_fobfee"] += round(float(sale_fobfee), 2) if sale_fobfee else 0

            sale_costfee = obj_dict.get('ord_costfee')
            tmp_dic[model_name]["sale_costfee"] += round(float(sale_costfee), 2) if sale_costfee else 0
            try:
                sale_rate_materialrate = obj_dict.get('pro_materialrate')
                tmp_dic[model_name]["sale_rate_materialrate"].append(
                    round(float(sale_rate_materialrate), 2) if sale_costfee else 0)
            except:
                tmp_dic[model_name]["sale_rate_materialrate"].append(0)

            try:
                sale_platfee = obj_dict.get('ord_platfee')
                tmp_dic[model_name]["sale_platfee"] += round(float(sale_platfee), 2) if sale_costfee else 0
            except Exception as e:
                pass
            try:
                sale_maoli = obj_dict.get('ord_maoli')
                tmp_dic[model_name]["sale_maoli"] += round(float(sale_maoli), 2) if sale_maoli else 0
            except Exception as e:
                pass

        res_dic = {"data": []}
        for tmp_name in tmp_dic:
            sale_amount = tmp_dic[tmp_name]["sale_amount"]
            sale_num = tmp_dic[tmp_name]["sale_num"]
            sale_expfee = tmp_dic[tmp_name]["sale_expfee"]
            sale_factoryfee = tmp_dic[tmp_name]["sale_factoryfee"]
            sale_fobfee = tmp_dic[tmp_name]["sale_fobfee"]
            sale_costfee = tmp_dic[tmp_name]["sale_costfee"]
            sale_maoli = tmp_dic[tmp_name]["sale_maoli"]
            sale_materialrate = list(float(i) for i in tmp_dic[tmp_name]["sale_rate_materialrate"])
            model_dic = {
                "fname": tmp_name.split('_')[0],  # 销售型号
                "bsname": tmp_name.split('_')[1],  # 乐歌型号
                "image": tmp_dic[tmp_name]["image"],
                'sale_num': sale_num,
                'sale_amount': sale_amount,
                'sale_price': round(sale_amount / sale_num, 2),
                'sale_platfee': round(tmp_dic[tmp_name]["sale_platfee"], 2),
                'sale_expfee': round(sale_expfee / sale_num, 2),
                'sale_factoryfee': round(sale_factoryfee, 2),
                'sale_fobfee': round(sale_fobfee, 2),
                'sale_swap': round(sale_factoryfee / sale_fobfee, 2),  # 换汇（出厂价/fob）
                'sale_rate_platfee': round(sale_costfee / sale_amount, 4),  # 成本率（成本费 / 销售额 ）
                "sale_rate_expfee": round(sale_expfee / sale_amount, 4),  # 物流率
                "sale_rate_materialrate": round(sum(sale_materialrate) / len(sale_materialrate), 4),  # 材料率
                'sale_alone_maoli': round(sale_maoli / sale_amount, 0),  # 单毛利（ 毛利 / 销量）
                'sale_maoli': round(sale_maoli, 0),  # 毛利
            }
            res_dic["data"].append(model_dic)
        data_src = str(res_dic)
        total_num = sum(int(i) for i in re.findall('sale_num\': (\\d+)', data_src))  # 总销量
        if not total_num:
            return ok(res_dic)
        total_amount = sum(float(i) for i in re.findall('sale_amount\': (\\d+.\\d+)', data_src))
        total_expfee = sum(float(i) for i in re.findall('sale_expfee\': (\\d+.\\d+)', data_src))
        total_factoryfee = sum(float(i) for i in re.findall('sale_factoryfee\': (\\d+.\\d+)', data_src))
        total_fobfee = sum(float(i) for i in re.findall('sale_fobfee\': (\\d+.\\d+)', data_src))
        total_costfee = sum(float(i) for i in re.findall('sale_costfee\': (\\d+.\\d+)', data_src))
        total_maoli = sum(float(i) for i in re.findall('sale_maoli\': (\\d+.\\d+)', data_src))
        total_materialrate = list(float(i) for i in re.findall('sale_rate_materialrate\': (\\d+.\\d+)', data_src))
        res_dic.update({
            "total_sale_num": total_num,
            "total_sale_amount": round(total_amount, 2),
            "total_sale_price": round(total_amount / total_num, 2),
            "total_sale_platfee": round(sum(float(i) for i in re.findall('sale_platfee\': (\\d+.\\d+)', data_src)), 2),
            "total_sale_expfee": round(
                total_expfee / len(list(float(i) for i in re.findall('sale_expfee\': (\\d+.\\d+)', data_src))), 2),
            "total_sale_factoryfee": round(total_factoryfee, 2),
            "total_sale_fobfee": round(total_fobfee, 2),
            "total_sale_swap": round(total_factoryfee / total_fobfee, 2),
            'total_sale_rate_platfee': round(total_costfee / total_amount, 4),  # 成本率（成本费 / 销售额 ）
            'total_sale_rate_expfee': round(total_expfee / total_amount, 4),  # 物流率
            'total_sale_rate_materialrate': round(sum(total_materialrate) / len(total_materialrate), 4),  # 材料率
            "total_sale_maoli": round(total_maoli, 2),
            'total_sale_alone_maoli': round(total_maoli / total_num, 2),  # 单毛利（ 毛利 / 销量）
        })

        return ok(res_dic)


class GlobalTyprSaleMiddleLog(Resource):
    def get(self):
        table = db.session.query(SalesM, ProductM).join(SalesM, SalesM.pro_fname == ProductM.bsname)
        start_time = get_argument("start_time", default='2020-10-01')
        end_time = get_argument("end_time", default='2020-10-10')
        pro_type = get_argument("pro_type", default="height adjustable desk")
        results = table.filter(
            SalesM.ord_pay_time.between(start_time, end_time),
            SalesM.pro_sec_type == pro_type)
        table_dic = {}
        table_list = []
        ret_dic = {"data": []}
        tem_ls = []
        self.num = 0

        def table_analysis(obj_dict):
            """处理表格数据"""
            store_code = obj_dict.get('source_code', '')
            if store_code not in table_list:
                table_list.append(store_code)
                table_dic[store_code] = {
                    "model": [],  # 执享型号 and 乐歌型号
                    "model_dic": {},
                }
            model_key = "{}_{}".format(obj_dict.get('pro_fname'), obj_dict.get('pro_bsname'))
            if model_key not in table_dic[store_code]['model']:
                table_dic[store_code]['model'].append(model_key)
                table_dic[store_code]["model_dic"][model_key] = {
                    "ord_salenum": 0,  # 销量
                    "ord_sale_amount": 0,  # 销售额
                    "ord_platfee": 0,  # 平台扣点
                    "ord_factoryfee": 0,  # 出厂价
                    "ord_fobfee": 0,  # fob费
                    "pro_materialrate": [],  # 材料率
                    "ord_expfee": 0,  # 快递费
                    "ord_maoli": 0,  # 毛利
                    "image_path": '',
                    "ord_costfee": 0
                }

            ord_salenum = float(obj_dict.get("ord_salenum")) if obj_dict.get("ord_salenum") else 0
            table_dic[store_code]["model_dic"][model_key]["ord_salenum"] += ord_salenum

            ord_sale_amount = float(obj_dict.get("ord_sale_amount")) if obj_dict.get("ord_sale_amount") else 0
            table_dic[store_code]["model_dic"][model_key]["ord_sale_amount"] += ord_sale_amount

            ord_platfee = float(obj_dict.get("ord_platfee")) if obj_dict.get("ord_platfee") else 0
            table_dic[store_code]["model_dic"][model_key]["ord_platfee"] += ord_platfee

            ord_factoryfee = float(obj_dict.get("ord_factoryfee")) if obj_dict.get("ord_factoryfee") else 0
            table_dic[store_code]["model_dic"][model_key]["ord_factoryfee"] += ord_factoryfee

            ord_fobfee = float(obj_dict.get("ord_factoryfee")) if obj_dict.get("ord_fobfee") else 0
            table_dic[store_code]["model_dic"][model_key]["ord_fobfee"] += ord_fobfee

            pro_materialrate = float(obj_dict.get("pro_materialrate")) if obj_dict.get("pro_materialrate") else 0
            table_dic[store_code]["model_dic"][model_key]["pro_materialrate"].append(pro_materialrate)

            ord_expfee = float(obj_dict.get("ord_expfee")) if obj_dict.get("ord_expfee") else 0
            table_dic[store_code]["model_dic"][model_key]["ord_expfee"] += ord_expfee

            ord_maoli = float(obj_dict.get("ord_maoli")) if obj_dict.get("ord_maoli") else 0
            table_dic[store_code]["model_dic"][model_key]["ord_maoli"] += ord_maoli

            ord_costfee = float(obj_dict.get("ord_costfee")) if obj_dict.get("ord_costfee") else 0
            table_dic[store_code]["model_dic"][model_key]["ord_costfee"] += ord_costfee

            if table_dic[store_code]["model_dic"][model_key]["image_path"]:
                table_dic[store_code]["model_dic"][model_key]["image_path"] = obj_dict.get("pro_image_path")

        for sales_table, product_table in results:
            obj_dict = obj_to_dict(sales_table, keys=[], display=False)
            obj_dict.update({
                'pro_image_path': product_table.pro_image_path,
            })
            table_analysis(obj_dict)
        for stop_n in table_dic:
            for mode_k in table_dic[stop_n]["model_dic"]:
                self.num += 1
                shop_name = stop_n
                if shop_name in tem_ls:
                    shop_name = ''
                else:
                    tem_ls.append(shop_name)
                sale_num = int(table_dic[stop_n]["model_dic"][mode_k]["ord_salenum"])
                sale_amount = float(table_dic[stop_n]["model_dic"][mode_k]["ord_sale_amount"])
                sale_expfee = float(table_dic[stop_n]["model_dic"][mode_k]["ord_expfee"])
                sale_factoryfee = float(table_dic[stop_n]["model_dic"][mode_k]["ord_factoryfee"])
                sale_fobfee = float(table_dic[stop_n]["model_dic"][mode_k]["ord_fobfee"])
                sale_materialrate = table_dic[stop_n]["model_dic"][mode_k]["pro_materialrate"]
                sale_maoli = table_dic[stop_n]["model_dic"][mode_k]["ord_maoli"]
                sale_costfee = table_dic[stop_n]["model_dic"][mode_k]["ord_costfee"]
                mode_dic = {
                    "id": self.num,
                    "shop_name": shop_name,  # 商铺名
                    "fname": mode_k.split('_')[0],  # 销售型号
                    "bsname": mode_k.split('_')[1],  # 乐歌型号
                    "sale_num": sale_num,  # 销售数
                    "sale_amount": round(sale_amount, 1),  # 销售额
                    "sale_price": round(sale_amount / sale_num, 1),  # 售价
                    "sale_platfee": round(table_dic[stop_n]["model_dic"][mode_k]["ord_platfee"], 1),  # 平台扣点
                    "sale_expfee": round(sale_expfee / sale_num, 1),  # 快递费
                    "sale_factoryfee": round(sale_factoryfee, 1),  # 出厂价
                    "sale_fobfee": round(sale_fobfee, 1),  # fob
                    "sale_swap": round(sale_factoryfee / sale_fobfee, 1),  # 换汇
                    "sale_costfee": round(sale_costfee),  # 成本费=fob仓对应的值
                    "sale_rate_costfee": round(sale_costfee / sale_amount, 3),  # 成本率
                    "sale_rate_expfee": round(sale_expfee / sale_amount, 3),  # 物流率
                    "sale_rate_logistics": round(sum(sale_materialrate) / len(sale_materialrate), 3),  # 材料率
                    "sale_alone_maoli": round(sale_maoli / sale_num, 1),  # 单毛利
                    "sale_maoli": round(sale_maoli, 1),  # 毛利
                    "sale_image": table_dic[stop_n]["model_dic"][mode_k]["image_path"]  # 图
                }
                if mode_dic.get("shop_name"):
                    mode_dic['children'] = []
                    ret_dic['data'].append(mode_dic)
                else:
                    ret_dic['data'][-1]['children'].append(mode_dic)

        data_src = str(ret_dic)
        total_num = sum(float(i) for i in re.findall('sale_num\': (\\d+)', data_src))  # 总销量
        if not total_num:
            return ok(ret_dic)
        total_amount = sum(float(i) for i in re.findall('sale_amount\': (\\d+.\\d+)', data_src))  # 总销售额
        total_platfee = sum(float(i) for i in re.findall('sale_platfee\': (\\d+.\\d+)', data_src))  # 总平台费
        total_factoryfee = sum(float(i) for i in re.findall('sale_factoryfee\': (\\d+.\\d+)', data_src))  # 总出厂价
        total_fobfee = sum(float(i) for i in re.findall('sale_fobfee\': (\\d+.\\d+)', data_src))  # 总fob
        total_costfee = sum(float(i) for i in re.findall('sale_costfee\': (\\d+.\\d+)', data_src))  # 成本费=fob仓对应的值
        total_expfee = sum(float(i) for i in re.findall('sale_expfee\': (\\d+.\\d+)', data_src))
        total_rate_logistics = sum(float(i) for i in re.findall('sale_rate_logistics\': (\\d+.\\d+)', data_src))
        total_maoli = sum(float(i) for i in re.findall('sale_maoli\': (\\d+.\\d+)', data_src))
        total_sale_swap = round(total_factoryfee / total_fobfee, 2),  # 换汇
        total_rate_costfee = total_costfee / total_amount,  # 成本率
        total_rate_expfee = total_expfee / total_amount,  # 物流率
        # total_rate_logistics = round(sum(total_rate_logistics) / len(total_rate_logistics), 3),  # 材料率
        ret_dic.update({
            "total_sale_num": round(total_num, 1),
            "total_sale_amount": round(total_amount, 1),
            "total_sale_platfee": round(total_platfee, 1),
            "total_sale_factoryfee": round(total_factoryfee, 1),
            "total_sale_fobfee": round(total_fobfee, 1),
            "total_sale_costfee": round(total_costfee, 1),
            "total_sale_expfee": round(total_expfee, 1),
            "total_sale_rate_logistics": round(total_rate_logistics, 1),
            "total_sale_swap": round(total_sale_swap[0], 3),
            "total_sale_rate_costfee": round(total_rate_costfee[0], 3),
            "total_sale_rate_expfee": round(total_rate_expfee[0], 3),
            "total_sale_alone_maoli": round(total_maoli / total_num, 1),
            "total_sale_maoli": round(total_maoli, 1)
        })

        return ok(ret_dic)

